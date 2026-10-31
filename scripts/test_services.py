#!/usr/bin/env python3
"""Exercise lifecycle failure cases with disposable processes, never hardware."""
import contextlib
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

RUNNER = Path(__file__).resolve().parents[1] / "docs/assets/scripts/friday-services.py"
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
  self.send_response(200); self.end_headers(); self.wfile.write(b'{"ready":true}')
 def log_message(self,*_): pass
server=HTTPServer(('127.0.0.1',a.port),Handler); server.timeout=.1
while not stopping: server.handle_request()
server.server_close(); child.send_signal(signal.SIGTERM)
(d/'parent-cleanup').write_text('complete')
'''

SERVICE = r'''
import json, os, signal, sys
from pathlib import Path
p=Path(sys.argv[2])
if sys.argv[1]=='status': print(json.dumps(p.exists()))
elif sys.argv[1]=='status-pid': print(json.dumps({'running':p.exists(),'pid':int(Path(sys.argv[3]).read_text())}))
elif sys.argv[1]=='status-needs-host':
 if not Path(sys.argv[3]).exists(): sys.exit(2)
 print(json.dumps(p.exists()))
elif sys.argv[1]=='start': p.touch()
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
        # Only disposable fixture PIDs are ever force-cleaned by this test harness.
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

    def test_unrelated_pid_is_never_signalled(self):
        unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            (self.root / "friday.pid").write_text(str(unrelated.pid))
            result = self.call("stop", success=False)
            self.assertIn("pid_identity_mismatch", result.stdout)
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
