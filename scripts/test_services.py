#!/usr/bin/env python3
"""用临时进程验证服务启停，不访问真实硬件；下载站点使用本文件的同步副本。"""
import contextlib
from datetime import datetime, timedelta, timezone
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "friday-services.py"
# 同一套测试也验证用户手册中发布的平铺下载包。
if not RUNNER.is_file():
    RUNNER = ROOT / "docs/assets/scripts/friday-services.py"
spec = importlib.util.spec_from_file_location("lifecycle", RUNNER)
lifecycle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lifecycle)

FIXTURE = r'''
import argparse, json, os, signal, subprocess, sys, time
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
p=argparse.ArgumentParser(); p.add_argument('role'); p.add_argument('directory'); p.add_argument('port',type=int); p.add_argument('--ignore-term',action='store_true'); a=p.parse_args()
d=Path(a.directory)
if a.role=='child':
 def stop(*_):
  time.sleep(1.0); (d/'child-cleanup').write_text('complete'); sys.exit(0)
 signal.signal(signal.SIGTERM,stop)
 while True: time.sleep(.1)
child=subprocess.Popen([sys.executable,__file__,'child',a.directory,str(a.port)],start_new_session=True)
(d/'child.pid').write_text(str(child.pid))
stopping=False
def stop(*_):
 global stopping
 if not a.ignore_term: stopping=True
signal.signal(signal.SIGTERM,stop)
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  payload=d/'responses.json'
  value=json.loads(payload.read_text()).get(self.path,{}) if payload.exists() else {'ready':True}
  self.send_response(200); self.end_headers(); self.wfile.write(json.dumps(value).encode())
 def log_message(self,*_): pass
server=HTTPServer(('127.0.0.1',a.port),Handler); server.timeout=.1
while not stopping: server.handle_request()
server.server_close(); child.send_signal(signal.SIGTERM)
(d/'parent-cleanup').write_text('complete')
'''

SERVICE = r'''
import json, os, signal, subprocess, sys
from pathlib import Path
p=Path(sys.argv[2])
if sys.argv[1]=='status': print(json.dumps(p.exists()))
elif sys.argv[1]=='status-pid': print(json.dumps({'running':p.exists(),'pid':int(Path(sys.argv[3]).read_text())}))
elif sys.argv[1]=='status-needs-host':
 if not Path(sys.argv[3]).exists(): sys.exit(2)
 print(json.dumps(p.exists()))
elif sys.argv[1]=='start': p.touch()
elif sys.argv[1]=='start-error-late-ready':
 count=p.with_suffix('.starts'); count.write_text(str(int(count.read_text())+1) if count.exists() else '1')
 code="import sys,time; from pathlib import Path; p=Path(sys.argv[1]); p.touch(); time.sleep(.6); p.with_suffix('.ready').touch()"
 subprocess.Popen([sys.executable,'-c',code,str(p)],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
 sys.exit(1)
elif sys.argv[1]=='start-error-not-ready': p.touch(); sys.exit(1)
elif sys.argv[1]=='ready': sys.exit(0 if p.with_suffix('.ready').exists() else 1)
elif sys.argv[1]=='stop': p.unlink(missing_ok=True)
elif sys.argv[1]=='term':
 os.kill(int(Path(sys.argv[3]).read_text()),signal.SIGTERM); p.unlink(missing_ok=True)
'''


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="friday-lifecycle-")
        self.root = Path(self.temporary.name).resolve()
        self.fixture = self.root / "fixture.py"
        self.fixture.write_text(FIXTURE)
        self.helper = self.root / "dependency.py"
        self.helper.write_text(SERVICE)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            self.port = sock.getsockname()[1]
        self.config = self.root / "services.json"
        self.service = {
            "id": "friday", "kind": "process", "cwd": str(self.root),
            "start": [sys.executable, str(self.fixture), "parent", str(self.root), str(self.port)],
            "command_contains": [str(self.fixture), "parent"],
            "pid_file": str(self.root / "friday.pid"), "log_file": str(self.root / "friday.log"),
            "listen": {"host": "127.0.0.1", "port": self.port},
            "ready": {"url": f"http://127.0.0.1:{self.port}/", "json_equals": {"ready": True}},
            "stop_timeout": 4, "start_timeout": 5,
        }
        self.write_config()

    def write_config(self, services=None):
        self.config.write_text(json.dumps({"version": 1, "state_dir": str(self.root / "state"),
                                           "services": services or [self.service]}))

    def call(self, action, success=True):
        result = subprocess.run([sys.executable, str(RUNNER), action, "--config", str(self.config)],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0 if success else 1, result.stdout + result.stderr)
        return result

    def tearDown(self):
        # 此测试框架只强制清理归属已核对的临时测试进程。
        for filename in ("friday.pid", "child.pid"):
            path = self.root / filename
            if path.exists():
                pid = int(path.read_text())
                current = lifecycle.identity(pid)
                if current and str(self.fixture) in current["command"]:
                    with contextlib.suppress(ProcessLookupError):
                        os.kill(pid, signal.SIGKILL)
        self.temporary.cleanup()

    def test_start_stop_restart_and_repeat_wait_for_child_cleanup(self):
        self.call("start")
        old = (self.root / "friday.pid").read_text()
        self.call("start")
        self.assertEqual((self.root / "friday.pid").read_text(), old)
        self.call("restart")
        self.assertNotEqual((self.root / "friday.pid").read_text(), old)
        (self.root / "child-cleanup").unlink()
        started = time.monotonic()
        self.call("stop")
        self.assertGreater(time.monotonic() - started, .8)
        self.assertTrue((self.root / "child-cleanup").exists())
        self.call("stop")

    def test_shell_entries_work_from_another_directory_and_only_preview(self):
        """根目录与平铺下载包的入口均能定位同目录程序，并保留显式配置。"""
        directory = self.root / "other directory"
        directory.mkdir()
        before = self.config.read_bytes()
        environment = {**os.environ, "FRIDAY_PYTHON": sys.executable,
                       "FRIDAY_SERVICE_CONFIG": str(self.config)}
        for action, expected in [("start", ["would_start"]), ("stop", ["would_stop"]),
                                 ("restart", ["would_stop", "would_start"])]:
            with self.subTest(action=action):
                result = subprocess.run(["sh", str(RUNNER.with_name(action + "-friday.sh")), "--dry-run"],
                                        cwd=directory, env=environment, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual([json.loads(line)["state"] for line in result.stdout.splitlines()], expected)
                self.assertFalse((self.root / "friday.pid").exists())
                self.assertEqual(self.config.read_bytes(), before)
    def test_start_client_error_can_wait_for_independent_readiness(self):
        """客户端失败后后台稍晚就绪，健康检查通过才继续，启动命令只执行一次。"""
        marker = self.root / "delayed-service"
        external = {"id": "external", "kind": "service", "cwd": str(self.root),
                    "start": [sys.executable, str(self.helper), "start-error-late-ready", str(marker)],
                    "stop": [sys.executable, str(self.helper), "stop", str(marker)],
                    "probe": {"argv": [sys.executable, str(self.helper), "status", str(marker)]},
                    "ready": {"argv": [sys.executable, str(self.helper), "ready", str(marker)]},
                    "start_timeout": 3}
        self.write_config([external, self.service])
        result = self.call("start")
        self.assertIn("checking_after_start_error", result.stdout)
        self.assertTrue(marker.with_suffix('.ready').exists())
        self.assertEqual(marker.with_suffix('.starts').read_text(), '1')
        self.assertTrue((self.root / "friday.pid").exists())
        self.assertLess(result.stdout.index('"service": "external", "state": "ready"'),
                        result.stdout.index('"service": "friday", "state": "starting"'))
        self.call("stop")

    def test_start_client_error_without_health_never_starts_dependents(self):
        """进程存在但健康检查未通过时仍失败，后续服务保持停止。"""
        marker = self.root / "unready-service"
        external = {"id": "external", "kind": "service", "cwd": str(self.root),
                    "start": [sys.executable, str(self.helper), "start-error-not-ready", str(marker)],
                    "stop": [sys.executable, str(self.helper), "stop", str(marker)],
                    "probe": {"argv": [sys.executable, str(self.helper), "status", str(marker)]},
                    "ready": {"argv": [sys.executable, str(self.helper), "ready", str(marker)]},
                    "start_timeout": .5}
        self.write_config([external, self.service])
        result = self.call("start", success=False)
        self.assertIn("external:start_command_failed", result.stdout)
        self.assertFalse((self.root / "friday.pid").exists())

    def test_start_client_error_requires_explicit_readiness_check(self):
        """未配置独立就绪检查时，不允许用进程存在覆盖启动失败。"""
        marker = self.root / "unchecked-service"
        external = {"id": "external", "kind": "service", "cwd": str(self.root),
                    "start": [sys.executable, str(self.helper), "start-error-not-ready", str(marker)],
                    "stop": [sys.executable, str(self.helper), "stop", str(marker)],
                    "probe": {"argv": [sys.executable, str(self.helper), "status", str(marker)]}}
        self.write_config([external, self.service])
        result = self.call("start", success=False)
        self.assertIn("external:start_command_failed", result.stdout)
        self.assertNotIn("checking_after_start_error", result.stdout)
        self.assertFalse((self.root / "friday.pid").exists())

    def test_unrelated_pid_is_never_signalled(self):
        unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            (self.root / "friday.pid").write_text(str(unrelated.pid))
            result = self.call("stop", success=False)
            self.assertIn("pid_identity_mismatch", result.stdout)
            self.assertIsNone(unrelated.poll())
        finally:
            unrelated.terminate(); unrelated.wait(timeout=5)

    def test_preboot_pid_reuse_can_restart_without_signalling_unrelated_process(self):
        unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            pid_file = self.root / "friday.pid"
            pid_file.write_text(str(unrelated.pid))
            os.utime(pid_file, (1, 1))
            self.call("restart")
            self.assertIsNone(unrelated.poll())
            self.assertNotEqual(int(pid_file.read_text()), unrelated.pid)
            self.call("stop")
            self.assertIsNone(unrelated.poll())
        finally:
            unrelated.terminate(); unrelated.wait(timeout=5)

    def test_unknown_boot_time_cannot_ignore_foreign_pid_even_with_old_file(self):
        unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            pid_file = self.root / "friday.pid"
            pid_file.write_text(str(unrelated.pid))
            os.utime(pid_file, (1, 1))
            with patch.object(lifecycle, "boot_time", return_value=None):
                runner = lifecycle.Runner(json.loads(self.config.read_text()))
            with self.assertRaisesRegex(lifecycle.LifecycleError, "pid_identity_mismatch"):
                runner.stop_one(self.service)
            self.assertIsNone(unrelated.poll())
        finally:
            unrelated.terminate(); unrelated.wait(timeout=5)

    def test_service_cli_return_does_not_skip_child_cleanup(self):
        self.call("start")
        marker = self.root / "service-running"; marker.touch()
        external = {"id":"external", "kind":"service", "cwd":str(self.root),
                    "start":[sys.executable,str(self.helper),"start",str(marker)],
                    "stop":[sys.executable,str(self.helper),"term",str(marker),self.service["pid_file"]],
                    "probe":{"argv":[sys.executable,str(self.helper),"status-pid",str(marker),self.service["pid_file"]],"path":["running"],"pid_path":["pid"]},
                    "command_contains":[str(self.fixture),"parent"],"stop_timeout":4}
        self.write_config([external])
        self.call("stop")
        self.assertTrue((self.root / "child-cleanup").exists())

    def test_service_cli_refuses_unexpected_process_before_stop(self):
        self.call("start")
        marker = self.root / "service-running"; marker.touch()
        external = {"id":"external", "kind":"service", "cwd":str(self.root),
                    "start":[sys.executable,str(self.helper),"start",str(marker)],
                    "stop":[sys.executable,str(self.helper),"term",str(marker),self.service["pid_file"]],
                    "probe":{"argv":[sys.executable,str(self.helper),"status-pid",str(marker),self.service["pid_file"]],"path":["running"],"pid_path":["pid"]},
                    "command_contains":["unrelated-server-identity"],"stop_timeout":4}
        self.write_config([external])
        self.assertIn("service_pid_identity_mismatch",self.call("stop",success=False).stdout)
        self.assertTrue(marker.exists())
        self.assertTrue(lifecycle.port_open(self.service["listen"]))

    def test_unrelated_port_is_not_adopted_or_killed(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", self.port)); sock.listen()
            self.assertIn("port_in_use", self.call("start", success=False).stdout)
            self.assertIn("port_still_in_use", self.call("stop", success=False).stdout)
            self.assertTrue(lifecycle.port_open(self.service["listen"]))

    def test_timeout_keeps_process_and_dependency_and_does_not_restart(self):
        marker = self.root / "dependency-running"
        marker.touch()
        dependency = {"id": "dependency", "kind": "service", "cwd": str(self.root),
                      "start": [sys.executable, str(self.helper), "start", str(marker)],
                      "stop": [sys.executable, str(self.helper), "stop", str(marker)],
                      "probe": {"argv": [sys.executable, str(self.helper), "status", str(marker)]}}
        self.service["start"].append("--ignore-term")
        self.service["stop_timeout"] = .5
        self.write_config([dependency, self.service])
        self.call("start")
        original = int((self.root / "friday.pid").read_text())
        result = self.call("restart", success=False)
        self.assertIn("descendants_still_running", result.stdout)
        self.assertTrue(marker.exists())
        self.assertIsNotNone(lifecycle.identity(original))
        self.assertEqual(int((self.root / "friday.pid").read_text()), original)

    def test_pending_descendants_survive_retry_after_parent_exit(self):
        self.service["stop_timeout"] = .2
        self.write_config()
        self.call("start")
        self.call("stop", success=False)
        self.assertTrue((self.root / "state/friday-pending.json").exists())
        self.service["stop_timeout"] = 4
        self.write_config()
        self.call("stop")
        self.assertTrue((self.root / "child-cleanup").exists())
        self.assertFalse((self.root / "state/friday-pending.json").exists())

    def test_preflight_failure_leaves_running_service_alone(self):
        self.call("start")
        pid = int((self.root / "friday.pid").read_text())
        self.service["start"][0] = str(self.root / "missing-python")
        self.write_config()
        self.assertIn("executable_missing", self.call("restart", success=False).stdout)
        self.assertIsNotNone(lifecycle.identity(pid))

    def test_concurrent_operation_is_refused(self):
        state = self.root / "state"; state.mkdir()
        with (state / "operation.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertIn("another_lifecycle_command_is_running", self.call("stop", success=False).stdout)

    def test_restart_prepares_managed_host_before_checking_stopped_service(self):
        host = self.root / "host-running"; app = self.root / "app-running"
        host_service = {"id":"host", "kind":"service", "keep_running":True, "cwd":str(self.root),
                        "start":[sys.executable,str(self.helper),"start",str(host)],
                        "probe":{"argv":[sys.executable,str(self.helper),"status",str(host)]}}
        app_service = {"id":"app", "kind":"service", "cwd":str(self.root),
                       "start":[sys.executable,str(self.helper),"start",str(app)],
                       "stop":[sys.executable,str(self.helper),"stop",str(app)],
                       "probe":{"argv":[sys.executable,str(self.helper),"status-needs-host",str(app),str(host)]}}
        self.write_config([host_service,app_service])
        self.call("restart")
        self.assertTrue(host.exists() and app.exists())
        self.call("stop")
        self.assertTrue(host.exists()); self.assertFalse(app.exists())

    def test_http_ready_rejects_unavailable_binding_then_accepts_healthy_state(self):
        self.call("start")
        self.service["ready"]["verify_saved_gestures"] = True
        data = readiness_data()
        responses = {"/":{"ready":True}, "/api/home/interactions":{"config":data[0]},
                     "/api/embodied/infrastructure":{"policy":data[1]}, "/api/snapshot":data[2]}
        responses["/api/snapshot"]["states"][0]["quality"] = "unknown"
        responses["/api/snapshot"]["states"][0]["value"] = "unavailable"
        response_file = self.root / "responses.json"
        response_file.write_text(json.dumps(responses))
        runner = lifecycle.Runner(json.loads(self.config.read_text()))
        self.assertFalse(runner.ready(self.service))
        responses["/api/snapshot"]["states"][0]["quality"] = "healthy"
        responses["/api/snapshot"]["states"][0]["value"] = "closed"
        response_file.write_text(json.dumps(responses))
        self.assertTrue(runner.ready(self.service))
        self.call("stop")


def readiness_data():
    now = datetime.now(timezone.utc)
    return ({"enabled":True,"bindings":[{"target":"simulated-cover","enabled":True}]},
            {"enabled":True,"recognition":True,"interaction":True},
            {"mode":"ha-read-only","action_targets":["simulated-cover"],
             "states":[{"id":"simulated-cover:cover.state","value":"closed","quality":"healthy",
                        "valid_until":(now+timedelta(seconds=60)).isoformat()}]}, now)


class GestureReadinessTests(unittest.TestCase):
    def test_target_presence_does_not_qualify_unknown_or_unavailable_state(self):
        config, policy, snapshot, now = readiness_data()
        self.assertTrue(lifecycle.gesture_targets_ready(config,policy,snapshot,now))
        snapshot["states"][0].update(value="unavailable",quality="unknown")
        self.assertFalse(lifecycle.gesture_targets_ready(config,policy,snapshot,now))

    def test_expired_state_and_missing_control_scope_are_rejected(self):
        config, policy, snapshot, now = readiness_data()
        self.assertFalse(lifecycle.gesture_targets_ready(config,policy,snapshot,now+timedelta(seconds=61)))
        snapshot["action_targets"] = []
        self.assertFalse(lifecycle.gesture_targets_ready(config,policy,snapshot,now))

    def test_paused_controls_and_no_enabled_bindings_do_not_require_live_targets(self):
        config, policy, snapshot, now = readiness_data()
        snapshot["states"] = []
        policy["interaction"] = False
        self.assertTrue(lifecycle.gesture_targets_ready(config,policy,snapshot,now))
        config["bindings"][0]["enabled"] = False
        self.assertTrue(lifecycle.gesture_targets_ready(config,{}, {},now))

    def test_real_rules_cannot_qualify_from_simulator_or_malformed_policy(self):
        config, policy, snapshot, now = readiness_data()
        snapshot["mode"] = "simulator"
        self.assertFalse(lifecycle.gesture_targets_ready(config,policy,snapshot,now))
        self.assertFalse(lifecycle.gesture_targets_ready(config,{},snapshot,now))


class BootTimeTests(unittest.TestCase):
    def test_kernel_boot_times_and_unavailable_probe(self):
        with patch.object(lifecycle.sys, "platform", "linux"), patch.object(lifecycle.Path, "read_text", return_value="cpu 1 2 3\nbtime 12345\n"):
            self.assertEqual(lifecycle.boot_time(), 12345)
        result = subprocess.CompletedProcess([], 0, stdout="{ sec = 12345, usec = 250000 } synthetic")
        with patch.object(lifecycle.sys, "platform", "darwin"), patch.object(lifecycle.subprocess, "run", return_value=result):
            self.assertEqual(lifecycle.boot_time(), 12345.25)
        with patch.object(lifecycle.sys, "platform", "darwin"), patch.object(lifecycle.subprocess, "run", side_effect=subprocess.TimeoutExpired("sysctl", 5)):
            self.assertIsNone(lifecycle.boot_time())


if __name__ == "__main__":
    unittest.main(verbosity=2)
