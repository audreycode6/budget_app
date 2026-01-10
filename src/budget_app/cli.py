import os
import sys
import subprocess
import argparse
from typing import List

SRC_DIR = os.path.join(os.getcwd(), "src")


def _ensure_src_on_pythonpath(env):
    env = env.copy()
    path = env.get("PYTHONPATH", "")
    parts = [p for p in path.split(os.pathsep) if p]
    if SRC_DIR not in parts:
        parts.insert(0, SRC_DIR)
    env["PYTHONPATH"] = os.pathsep.join(parts)
    return env


def _start(cmd: List[str]) -> int:
    env = _ensure_src_on_pythonpath(os.environ)
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, env=env)
    return proc.returncode


def do_test(args):
    base = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "src",
        "-p",
        "*_test.py",
    ]
    if args.verbose:
        base.append("-v")
    return _start(base)


def do_test_module(args):
    return _start([sys.executable, "-m", args.module])


def do_start(args):
    return _start([sys.executable, "-m", "budget_app.app"])


def do_db_migrate(args):
    msg = args.message or "migration"
    return _start(
        [
            sys.executable,
            "-m",
            "flask",
            "--app",
            "budget_app.app",
            "db",
            "migrate",
            "-m",
            msg,
        ]
    )


def do_db_upgrade(args):
    return _start(
        [sys.executable, "-m", "flask", "--app", "budget_app.app", "db", "upgrade"]
    )


def do_db_downgrade(args):
    return _start(
        [sys.executable, "-m", "flask", "--app", "budget_app.app", "db", "downgrade"]
    )


def main(argv=None):
    parser = argparse.ArgumentParser(prog="app", description="Budget app helper CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_test = sub.add_parser("test", help="run all tests")
    p_test.add_argument("-v", "--verbose", dest="verbose", action="store_true")
    p_test.set_defaults(func=do_test)

    p_test_mod = sub.add_parser("test-module", help="run a specific test module")
    p_test_mod.add_argument(
        "module",
        help="python module path, e.g. budget_app.routes.handlers.http.auth_test",
    )
    p_test_mod.set_defaults(func=do_test_module)

    p_start = sub.add_parser("start", help="start the app")
    p_start.set_defaults(func=do_start)

    p_migrate = sub.add_parser("db-migrate", help="generate a migration")
    p_migrate.add_argument("-m", "--message", help="migration message", default=None)
    p_migrate.set_defaults(func=do_db_migrate)

    p_upgrade = sub.add_parser("db-upgrade", help="apply migrations")
    p_upgrade.set_defaults(func=do_db_upgrade)

    p_downgrade = sub.add_parser("db-downgrade", help="rollback migrations")
    p_downgrade.set_defaults(func=do_db_downgrade)

    args = parser.parse_args(argv)
    rc = args.func(args)
    sys.exit(rc)


if __name__ == "__main__":
    main()
