#!/usr/bin/env python3
"""Drive v2.10 pod validation over SSH with explicit progress output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import threading
import textwrap
from typing import Any


REPO_URL = "https://github.com/rubaolee/rtdl.git"


def _shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def build_remote_script(
    *,
    repo_url: str,
    ref: str,
    build_optix: bool,
    optix_prefix: str,
    run_hardware: bool,
    run_partner_comparison: bool,
    timeout_scale: float,
) -> str:
    bundle_flags = []
    if run_hardware:
        bundle_flags.extend(["--run-front-door", "--run-scale-profile"])
    if run_partner_comparison:
        bundle_flags.append("--run-partner-comparison")
    flags = " ".join(bundle_flags)
    build_step = ""
    if build_optix:
        build_step = textwrap.dedent(
            f"""
            echo "[rtdl-remote-pod] build OptiX library"
            make build-optix OPTIX_PREFIX={_shell_quote(optix_prefix)} CUDA_PREFIX="${{CUDA_HOME:-/usr/local/cuda}}"
            export RTDL_OPTIX_LIBRARY="$PWD/build/librtdl_optix.so"
            """
        ).strip()
    else:
        build_step = textwrap.dedent(
            """
            echo "[rtdl-remote-pod] skip build; use existing RTDL_OPTIX_LIBRARY or build/librtdl_optix.so"
            if [ -z "${RTDL_OPTIX_LIBRARY:-}" ] && [ -f "$PWD/build/librtdl_optix.so" ]; then
              export RTDL_OPTIX_LIBRARY="$PWD/build/librtdl_optix.so"
            fi
            """
        ).strip()

    return textwrap.dedent(
        f"""
        set -euo pipefail
        echo "[rtdl-remote-pod] start $(date -Iseconds)"
        WORKDIR="$(mktemp -d /root/rtdl_v2_10_validation.XXXXXX)"
        echo "[rtdl-remote-pod] workdir $WORKDIR"
        git clone --depth 1 {_shell_quote(repo_url)} "$WORKDIR/repo"
        cd "$WORKDIR/repo"
        if [ {_shell_quote(ref)} != "main" ]; then
          echo "[rtdl-remote-pod] checkout requested ref"
          git fetch --depth 1 origin {_shell_quote(ref)}
          git checkout --detach FETCH_HEAD
        fi
        export PYTHONPATH=src:.
        echo "[rtdl-remote-pod] head $(git rev-parse --short HEAD)"
        echo "[rtdl-remote-pod] bootstrap probe before build"
        python3 scripts/rtdl_pod_bootstrap_probe.py --json | tee "$WORKDIR/bootstrap_probe_before_build.json"
        {build_step}
        echo "[rtdl-remote-pod] bootstrap probe after setup"
        python3 scripts/rtdl_pod_bootstrap_probe.py --json | tee "$WORKDIR/bootstrap_probe_after_setup.json"
        echo "[rtdl-remote-pod] run validation bundle flags={flags or 'preflight-only'}"
        python3 scripts/rtdl_v2_10_pod_validation_bundle.py {flags} --timeout-scale {timeout_scale} --output-dir "$WORKDIR/v2_10_pod_validation_bundle"
        echo "[rtdl-remote-pod] artifacts $WORKDIR"
        echo "[rtdl-remote-pod] done $(date -Iseconds)"
        """
    ).strip() + "\n"


def build_ssh_command(target: str, *, port: str | None, identity_file: str | None) -> list[str]:
    command = ["ssh", "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=4"]
    if port:
        command.extend(["-p", port])
    if identity_file:
        command.extend(["-i", identity_file])
    command.extend([target, "bash", "-s"])
    return command


def plan(args: argparse.Namespace) -> dict[str, Any]:
    remote_script = build_remote_script(
        repo_url=args.repo_url,
        ref=args.ref,
        build_optix=args.build_optix,
        optix_prefix=args.optix_prefix,
        run_hardware=args.run_hardware,
        run_partner_comparison=args.run_partner_comparison,
        timeout_scale=args.timeout_scale,
    )
    command = build_ssh_command(args.target, port=args.port, identity_file=args.identity_file)
    return {
        "tool": "rtdl_remote_pod_validation_driver",
        "mode": "execute" if args.execute else "dry_run",
        "repo_url": args.repo_url,
        "ref": args.ref,
        "command": command,
        "remote_script": remote_script,
        "destructive_checkout": False,
        "uses_fresh_mktemp_workdir": True,
        "timeout_sec": args.timeout_sec,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
    }


def _execute_ssh(payload: dict[str, Any], *, timeout_sec: int, json_mode: bool) -> dict[str, Any]:
    stream = sys.stderr if json_mode else sys.stdout
    timed_out = {"value": False}

    process = subprocess.Popen(
        payload["command"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    def _kill_on_timeout() -> None:
        timed_out["value"] = True
        process.kill()

    timer = threading.Timer(timeout_sec, _kill_on_timeout)
    timer.start()
    captured: list[str] = []
    try:
        assert process.stdin is not None
        process.stdin.write(payload["remote_script"])
        process.stdin.close()
        assert process.stdout is not None
        for line in process.stdout:
            captured.append(line)
            stream.write(line)
            stream.flush()
        returncode = process.wait()
    finally:
        timer.cancel()

    stdout = "".join(captured)
    return {
        **payload,
        "returncode": returncode,
        "stdout_tail": stdout[-8000:],
        "stderr_tail": "",
        "timed_out": timed_out["value"],
        "status": "pass" if returncode == 0 and not timed_out["value"] else "fail",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="SSH target, for example root@1.2.3.4")
    parser.add_argument("--port", help="SSH port")
    parser.add_argument("--identity-file", help="SSH private key path")
    parser.add_argument("--execute", action="store_true", help="actually run the remote script")
    parser.add_argument("--repo-url", default=REPO_URL, help="Git repository URL to clone on the pod")
    parser.add_argument("--ref", default="main", help="branch or tag to run; non-main refs are fetched and checked out")
    parser.add_argument("--build-optix", action="store_true", help="run make build-optix on the pod")
    parser.add_argument("--optix-prefix", default="/root/vendor/optix-sdk")
    parser.add_argument("--run-hardware", action="store_true", help="run front-door and scale-profile hardware packets")
    parser.add_argument("--run-partner-comparison", action="store_true", help="also run the large CuPy/Numba comparison")
    parser.add_argument("--timeout-scale", type=float, default=1.0)
    parser.add_argument("--timeout-sec", type=int, default=7200)
    parser.add_argument("--json", action="store_true", help="print the dry-run or execution summary as JSON")
    args = parser.parse_args(argv)

    payload = plan(args)
    if not args.execute:
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print("RTDL Remote Pod Validation Driver")
            print("mode: dry_run")
            print("ssh:")
            print(" ".join(payload["command"]))
            print("remote script:")
            print(payload["remote_script"])
        return 0

    print("[rtdl-remote-driver] launching ssh validation", file=sys.stderr if args.json else sys.stdout, flush=True)
    summary = _execute_ssh(payload, timeout_sec=args.timeout_sec, json_mode=args.json)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"[rtdl-remote-driver] status={summary['status']} returncode={summary['returncode']}", flush=True)
    return int(summary["returncode"])


if __name__ == "__main__":
    raise SystemExit(main())
