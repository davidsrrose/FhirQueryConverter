#!/usr/bin/env python3
"""
Python entrypoint for running the development server inside the Docker wrapper.
It optionally installs dependencies and forwards signals to the Node process.
"""

import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
TRUTHY = {"1", "true", "yes", "on"}


def log(message: str) -> None:
    """Uniform, flush-after-print logging."""
    print(f"[wrapper] {message}", flush=True)


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.lower() in TRUTHY


def ensure_dependencies(force: bool = False, skip: bool = False) -> None:
    """Install node dependencies if needed."""
    if skip:
        log("SKIP_INSTALL set; skipping npm install.")
        return

    node_modules = REPO_ROOT / "node_modules"
    package_lock = REPO_ROOT / "package-lock.json"
    install_cmd = ["npm", "ci"] if package_lock.exists() else ["npm", "install"]

    if node_modules.exists():
        if force:
            log("FORCE_INSTALL set; removing existing node_modules for a clean install.")
            shutil.rmtree(node_modules)
        else:
            log("node_modules present; skipping install (set FORCE_INSTALL=1 to reinstall).")
            return

    log(f"Installing dependencies with: {' '.join(install_cmd)}")
    subprocess.run(install_cmd, cwd=REPO_ROOT, check=True)


def run_dev(env: dict[str, str]) -> int:
    """Spawn the dev server and forward termination signals."""
    cmd = ["npm", "run", "dev"]
    log(f"Starting dev server via: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=REPO_ROOT, env=env)

    def forward(signum, _frame):
        log(f"Forwarding signal {signum} to dev server.")
        proc.send_signal(signum)

    signal.signal(signal.SIGTERM, forward)
    signal.signal(signal.SIGINT, forward)

    return proc.wait()


def main() -> None:
    env = os.environ.copy()
    defaults = {
        "NODE_ENV": "development",
        "HOST": "0.0.0.0",
        "PORT": "5000",
        "CHOKIDAR_USEPOLLING": "true",
        "WATCHPACK_POLLING": "true",
        "BROWSER": "none",
    }
    for key, value in defaults.items():
        env.setdefault(key, value)

    skip_install = env_bool("SKIP_INSTALL", default=False)
    force_install = env_bool("FORCE_INSTALL", default=False)

    try:
        ensure_dependencies(force=force_install, skip=skip_install)
    except subprocess.CalledProcessError as exc:
        log(f"npm install failed with exit code {exc.returncode}")
        sys.exit(exc.returncode)

    try:
        code = run_dev(env)
        log(f"Dev server exited with code {code}")
        sys.exit(code)
    except KeyboardInterrupt:
        log("Interrupted; shutting down.")
        sys.exit(130)


if __name__ == "__main__":
    main()
