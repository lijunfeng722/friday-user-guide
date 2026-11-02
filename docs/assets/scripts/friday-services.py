#!/usr/bin/env python3
"""按本机服务清单正常启动、停止或重新启动 Friday。

仅使用 Python 标准库，支持 macOS / Linux。配置保留在本机；不安装依赖、
按进程名结束程序、操作设备、删除数据或自动发送 SIGKILL。
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit


class LifecycleError(Exception):
    pass


def emit(service, state):
    print(json.dumps({"service": service, "state": state}, ensure_ascii=False), flush=True)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w") as stream:
        os.chmod(temporary, 0o600)
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def boot_time():
    """读取内核开机时间；无法确认时继续严格检查进程身份。"""
    try:
        if sys.platform.startswith("linux"):
            for line in Path("/proc/stat").read_text().splitlines():
                if line.startswith("btime "):
                    return float(line.split()[1])
        elif sys.platform == "darwin":
            result = subprocess.run(["/usr/sbin/sysctl", "-n", "kern.boottime"],
                                    text=True, capture_output=True, check=True, timeout=5)
            match = re.search(r"\bsec\s*=\s*(\d+),\s*usec\s*=\s*(\d+)", result.stdout)
            if match:
                return int(match[1]) + int(match[2]) / 1_000_000
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        pass
    return None


def identity(pid):
    if not isinstance(pid, int) or pid <= 1:
        return None
    if sys.platform.startswith("linux"):
        try:
            directory = Path(f"/proc/{pid}")
            fields = (directory / "stat").read_text().rsplit(") ", 1)[1].split()
            command = (directory / "cmdline").read_bytes().replace(b"\0", b" ").decode().strip()
            if fields[0] == "Z" or not command:
                return None
            born = Path("/proc/sys/kernel/random/boot_id").read_text().strip() + ":" + fields[19]
            return {"pid": pid, "born": born, "digest": hashlib.sha256(command.encode()).hexdigest(), "command": command}
        except (OSError, IndexError, UnicodeError):
            return None
    result = subprocess.run(["ps", "-p", str(pid), "-o", "lstart=", "-o", "stat=", "-o", "command="],
                            text=True, capture_output=True, timeout=5)
    fields = result.stdout.strip().split(None, 6)
    if result.returncode or len(fields) != 7 or fields[5].startswith("Z"):
        return None
    return {"pid": pid, "born": " ".join(fields[:5]),
            "digest": hashlib.sha256(fields[6].encode()).hexdigest(), "command": fields[6]}


def same(record, *, command=False):
    current = identity(record["pid"])
    return current is not None and current["born"] == record["born"] and (not command or current["digest"] == record["digest"])


def descendants(pid):
    if sys.platform.startswith("linux"):
        pairs = []
        for entry in Path("/proc").iterdir():
            if entry.name.isdigit():
                try:
                    fields = (entry / "stat").read_text().rsplit(") ", 1)[1].split()
                    pairs.append((int(entry.name), int(fields[1])))
                except (OSError, IndexError):
                    pass
    else:
        result = subprocess.run(["ps", "-axo", "pid=,ppid="], text=True, capture_output=True, check=True, timeout=5)
        pairs = [tuple(map(int, line.split())) for line in result.stdout.splitlines() if line.strip()]
    selected = {pid}
    while True:
        extra = {child for child, parent in pairs if parent in selected}
        if extra <= selected:
            break
        selected.update(extra)
    return [entry for item in sorted(selected) if (entry := identity(item))]


def process_cwd(pid):
    if sys.platform.startswith("linux"):
        return str(Path(f"/proc/{pid}/cwd").resolve(strict=True))
    result = subprocess.run(["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"],
                            text=True, capture_output=True, timeout=5)
    return next((line[1:] for line in result.stdout.splitlines() if line.startswith("n")), None)


def port_open(endpoint):
    try:
        with socket.create_connection((endpoint["host"], int(endpoint["port"])), timeout=0.5):
            return True
    except OSError:
        return False


def gesture_targets_ready(config, policy, snapshot, now):
    """复用手势规划前的设备状态检查。

    互动暂停或没有启用的绑定时，无须等待实时目标。只有设备清单或 HTTP
    可访问，不能证明启用规则的目标已就绪。
    """
    if not isinstance(config.get("enabled"), bool) or not isinstance(config.get("bindings"), list):
        return False
    if not config["enabled"]:
        return True
    targets = {binding.get("target") for binding in config["bindings"] if binding.get("enabled") is True}
    if not targets:
        return True
    flags = [policy.get(key) for key in ("enabled", "recognition", "interaction")]
    if not all(type(flag) is bool for flag in flags):
        return False
    if not all(flags):
        return True
    if snapshot.get("mode") != "ha-read-only" or not targets <= set(snapshot.get("action_targets", [])):
        return False
    def fresh(target):
        for state in snapshot.get("states", []):
            if not isinstance(target, str) or not state.get("id", "").startswith(target + ":") or state.get("quality") != "healthy":
                continue
            try:
                deadline = datetime.fromisoformat(state["valid_until"].replace("Z", "+00:00"))
                if deadline.tzinfo is not None and now < deadline:
                    return True
            except (KeyError, TypeError, AttributeError, ValueError):
                pass
        return False
    return all(fresh(target) for target in targets)


class Runner:
    def __init__(self, config):
        self.config = config
        self.state = Path(config["state_dir"]).expanduser().resolve()
        self.services = config["services"]
        self.booted_at = boot_time()
        ids = [s["id"] for s in self.services]
        if not ids or len(set(ids)) != len(ids) or any(not x.replace("-", "").isalnum() for x in ids):
            raise LifecycleError("invalid_service_ids")
        self.children = []

    def env(self, service):
        # 专用部署可以排除环境中继承的 API 或通道凭据。
        allowed = service.get("inherit_env")
        result = dict(os.environ) if allowed is None else {k: v for k, v in os.environ.items() if k in allowed}
        result.update(self.config.get("env", {}))
        result.update(service.get("env", {}))
        return result

    def command(self, service, argv, timeout=15):
        try:
            return subprocess.run(argv, cwd=service.get("cwd"), env=self.env(service),
                                  text=True, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            # 这里只取消命令行客户端，不向服务发送 SIGKILL。
            raise LifecycleError(service["id"] + ":command_timeout") from None

    def pending_file(self, service):
        return self.state / (service["id"] + "-pending.json")

    def owned(self, service):
        path = Path(service["pid_file"])
        if not path.exists():
            return None
        try:
            pid = int(path.read_text().strip())
        except ValueError:
            raise LifecycleError(service["id"] + ":invalid_pid_file") from None
        if pid <= 1:
            raise LifecycleError(service["id"] + ":invalid_pid_file")
        # 系统重启后旧进程已不存在，旧 PID 可能已被其他程序复用；
        # 保留该程序，继续使用正常的端口与启动检查。
        # 同次开机身份不符或开机时间未知时，后续仍拒绝执行。
        if self.booted_at is not None and path.stat().st_mtime < self.booted_at:
            return None
        entry = identity(pid)
        if entry is None:
            return None
        command = entry["command"]
        if service.get("command_equals"):
            matches = command == service["command_equals"]
        else:
            matches = bool(service.get("command_contains")) and all(x in command for x in service["command_contains"])
        expected_cwd = service.get("identity_cwd", service.get("cwd"))
        if not matches or (expected_cwd and process_cwd(entry["pid"]) != str(Path(expected_cwd).resolve())):
            raise LifecycleError(service["id"] + ":pid_identity_mismatch")
        return entry

    def running(self, service):
        if service["kind"] == "process":
            return self.owned(service) is not None
        probe = service["probe"]
        result = self.command(service, probe["argv"])
        if result.returncode:
            if result.returncode in probe.get("stopped_exit_codes", []):
                return False
            raise LifecycleError(service["id"] + ":status_unavailable")
        if probe.get("success_is_running"):
            return True
        try:
            value = json.loads(result.stdout)
            for key in probe.get("path", []):
                value = value[key]
        except (ValueError, KeyError, TypeError):
            raise LifecycleError(service["id"] + ":invalid_status_response") from None
        if type(value) is not bool:
            raise LifecycleError(service["id"] + ":status_is_not_boolean")
        return value

    def ready(self, service):
        spec = service.get("ready")
        if not spec:
            return True
        if "argv" in spec:
            return self.command(service, spec["argv"]).returncode == 0
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(spec["url"], timeout=2) as response:
                if response.status not in spec.get("codes", [200]):
                    return False
                if spec.get("json_equals"):
                    value = json.load(response)
                    if not all(value.get(k) == v for k, v in spec["json_equals"].items()):
                        return False
            if spec.get("verify_saved_gestures"):
                parsed = urlsplit(spec["url"])
                origin = parsed.scheme + "://" + parsed.netloc
                def get(path):
                    with opener.open(origin + path, timeout=3) as response:
                        return json.load(response)
                return gesture_targets_ready(get("/api/home/interactions")["config"],
                                             get("/api/embodied/infrastructure")["policy"],
                                             get("/api/snapshot"), datetime.now(timezone.utc))
            return True
        except urllib.error.HTTPError as error:
            return not spec.get("json_equals") and error.code in spec.get("codes", [200])
        except (OSError, ValueError, KeyError, TypeError):
            return False

    def wait(self, service, condition, timeout, error):
        deadline = time.monotonic() + timeout
        next_progress = time.monotonic() + 10
        while not condition():
            if time.monotonic() >= deadline:
                raise LifecycleError(service["id"] + ":" + error)
            if time.monotonic() >= next_progress:
                emit(service["id"], "waiting")
                next_progress = time.monotonic() + 10
            time.sleep(0.3)

    def wait_pending(self, service):
        path = self.pending_file(service)
        if path.exists():
            records = json.loads(path.read_text())
            self.wait(service, lambda: not any(same(item) for item in records),
                      service.get("stop_timeout", 180), "descendants_still_running")
            path.unlink()

    def stop_one(self, service):
        if service.get("keep_running"):
            emit(service["id"], "kept_running")
            return
        emit(service["id"], "stopping")
        if service["kind"] == "process":
            # 上次停止失败时保留子进程身份，包括在原父进程退出后仍运行的监护进程。
            root = self.owned(service)
            if root:
                pending = self.pending_file(service)
                records = json.loads(pending.read_text()) if pending.exists() else []
                records.extend(descendants(root["pid"]))
                save(pending, records)
                if same(root, command=True):
                    try:
                        os.kill(root["pid"], signal.SIGTERM)
                    except ProcessLookupError:
                        pass
            self.wait_pending(service)
            if service.get("listen") and port_open(service["listen"]):
                raise LifecycleError(service["id"] + ":port_still_in_use_no_process_killed")
        elif self.running(service):
            probe = service["probe"]
            if probe.get("pid_path"):
                response = self.command(service, probe["argv"])
                value = json.loads(response.stdout)
                for key in probe["pid_path"]:
                    value = value[key]
                entry = identity(value)
                if entry is None or not service.get("command_contains") or not all(x in entry["command"] for x in service["command_contains"]):
                    raise LifecycleError(service["id"] + ":service_pid_identity_mismatch")
                save(self.pending_file(service), descendants(entry["pid"]))
            result = self.command(service, service["stop"], service.get("stop_timeout", 180))
            if result.returncode:
                raise LifecycleError(service["id"] + ":stop_command_failed")
            self.wait(service, lambda: not self.running(service), service.get("stop_timeout", 180), "stop_unverified")
        self.wait_pending(service)
        if service.get("after_stop") and self.command(service, service["after_stop"], 60).returncode:
            raise LifecycleError(service["id"] + ":cleanup_pending_dependencies_kept")
        emit(service["id"], "stopped")

    def start_one(self, service):
        self.wait_pending(service)
        if self.running(service):
            self.wait(service, lambda: self.ready(service), service.get("start_timeout", 120), "not_ready")
            emit(service["id"], "already_running")
            return
        if service.get("listen") and port_open(service["listen"]):
            raise LifecycleError(service["id"] + ":port_in_use_no_process_killed")
        emit(service["id"], "starting")
        if service["kind"] == "process":
            log = Path(service["log_file"])
            log.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with log.open("ab") as stream:
                os.chmod(log, 0o600)
                child = subprocess.Popen(service["start"], cwd=service.get("cwd"), env=self.env(service),
                                         stdin=subprocess.DEVNULL, stdout=stream, stderr=stream, start_new_session=True)
            self.children.append(child)
            pid_file = Path(service["pid_file"])
            pid_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            pid_file.write_text(str(child.pid))
            os.chmod(pid_file, 0o600)
            # 某些启动器会先替换或重命名自身；等待期间只允许刚创建的那个 PID。
            def started():
                if child.poll() is not None:
                    raise LifecycleError(service["id"] + ":process_exited_check_private_log")
                try:
                    return self.running(service) and self.ready(service)
                except LifecycleError as error:
                    if str(error).endswith(":pid_identity_mismatch"):
                        return False
                    raise
            self.wait(service, started, service.get("start_timeout", 120), "start_not_ready")
        else:
            result = self.command(service, service["start"], service.get("start_timeout", 120))
            if result.returncode:
                # 启动客户端可能先超时，后台仍在初始化；只有配置了独立就绪检查
                # 才继续有限等待，进程状态与就绪检查同时通过后才能启动后续服务。
                if not service.get("ready"):
                    raise LifecycleError(service["id"] + ":start_command_failed")
                emit(service["id"], "checking_after_start_error")
            self.wait(service, lambda: self.running(service) and self.ready(service),
                      service.get("start_timeout", 120),
                      "start_command_failed" if result.returncode else "start_not_ready")
        emit(service["id"], "ready")

    def preflight(self):
        import shutil
        for service in self.services:
            if service["kind"] not in {"process", "service"}:
                raise LifecycleError("unsupported_service_kind")
            if not Path(service["cwd"]).is_dir():
                raise LifecycleError(service["id"] + ":cwd_missing")
            for argv in [service["start"], service.get("stop"), service.get("probe", {}).get("argv"),
                         service.get("ready", {}).get("argv"), service.get("after_stop")]:
                if argv and (not isinstance(argv, list) or not all(isinstance(x, str) for x in argv)
                             or not shutil.which(argv[0], path=self.env(service).get("PATH"))):
                    raise LifecycleError(service["id"] + ":executable_missing")
            if service["kind"] == "process" and not (service.get("command_equals") or service.get("command_contains")):
                raise LifecycleError(service["id"] + ":identity_missing")

    def run(self, action, dry_run=False):
        self.preflight()
        if dry_run:
            plan = list(reversed(self.services)) if action == "stop" else self.services
            if action == "restart":
                for service in self.services:
                    if service.get("keep_running"):
                        emit(service["id"], "would_prepare")
                for service in reversed(self.services):
                    emit(service["id"], "would_keep" if service.get("keep_running") else "would_stop")
            for service in plan:
                emit(service["id"], "would_keep" if action == "stop" and service.get("keep_running") else "would_" + ("start" if action == "restart" else action))
            return
        if action == "restart":
            # 冷启动时也要先准备已明确登记的容器主机，再查询或停止 HA；
            # 不把守护进程离线当作容器已停止，也不跳过失败的状态检查。
            for service in self.services:
                if service.get("keep_running"):
                    self.start_one(service)
        if action in {"stop", "restart"}:
            for service in reversed(self.services):
                self.stop_one(service)
        if action in {"start", "restart"}:
            for service in self.services:
                self.start_one(service)
        if action == "status":
            for service in self.services:
                running = self.running(service)
                emit(service["id"], "ready" if running and self.ready(service) else "not_ready" if running else "stopped")
        for child in self.children:
            child.poll()
        emit("deployment", action + "_complete")


def initialize(args):
    import shutil
    project = args.project.expanduser().resolve()
    config_path = args.config.expanduser().resolve()
    if config_path.exists():
        raise LifecycleError("config_already_exists_will_not_overwrite")
    python = project / ".venv/bin/python"
    if not python.is_file() or not (project / "homeplane/cli.py").is_file():
        raise LifecycleError("install_friday_first")
    state = project / "data/service-control"
    services = []
    if args.with_ha:
        docker = shutil.which("docker")
        if not docker:
            raise LifecycleError("docker_missing")
        prefix = (["sudo", "-n"] if args.docker_sudo else []) + [docker]
        compose = prefix + ["compose", "--project-name", "friday-home", "--file", str(project / "data/deployment/compose.yaml"),
                            "--env-file", str(project / "data/deployment/.env")]
        result = subprocess.run(compose + ["ps", "--all", "--quiet", "homeassistant"], capture_output=True, text=True, timeout=20)
        ids = result.stdout.split()
        if result.returncode or len(ids) != 1:
            raise LifecycleError("existing_ha_container_not_unique_start_it_first")
        container = ids[0]
        services.append({"id": "home-assistant", "kind": "service", "cwd": str(project),
                         "start": prefix + ["start", container], "stop": prefix + ["stop", "--timeout", "-1", container],
                         "probe": {"argv": prefix + ["inspect", "--format", "{{json .State.Running}}", container]},
                         "ready": {"url": "http://127.0.0.1:8123/api/", "codes": [200, 401]}, "stop_timeout": 180})
    services.append({"id": "friday", "kind": "process", "cwd": str(project), "identity_cwd": str(project),
                     "start": [str(python), "-B", "-m", "homeplane.cli", "serve", "--port", str(args.port)],
                     "command_contains": [str(python), "-m homeplane.cli serve --port " + str(args.port)],
                     "pid_file": str(state / "friday.pid"), "log_file": str(state / "friday.log"),
                     "listen": {"host": "127.0.0.1", "port": args.port},
                     "ready": {"url": f"http://127.0.0.1:{args.port}/api/doctor", "verify_saved_gestures": True}, "stop_timeout": 180})
    save(config_path, {"version": 1, "state_dir": str(state), "services": services})
    emit("configuration", "created_no_service_started")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "start", "stop", "restart", "status"])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--with-ha", action="store_true")
    parser.add_argument("--docker-sudo", action="store_true")
    parser.add_argument("--port", type=int, default=8740)
    args = parser.parse_args()
    os.umask(0o077)
    try:
        if args.action == "init":
            if args.dry_run:
                raise LifecycleError("init_does_not_support_dry_run")
            initialize(args)
        else:
            config = json.loads(args.config.expanduser().read_text())
            if config.get("version") != 1:
                raise LifecycleError("unsupported_config_version")
            runner = Runner(config)
            runner.state.mkdir(parents=True, exist_ok=True, mode=0o700)
            with (runner.state / "operation.lock").open("a") as lock:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    raise LifecycleError("another_lifecycle_command_is_running") from None
                runner.run(args.action, args.dry_run)
        return 0
    except (LifecycleError, OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        code = str(error) if isinstance(error, LifecycleError) else type(error).__name__
        emit("deployment", "failed:" + code)
        return 1
    except KeyboardInterrupt:
        emit("deployment", "interrupted_check_status_before_retry")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
