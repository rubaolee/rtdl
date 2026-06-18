from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
from typing import Any

from scripts import goal4576_m177_v3_c_abi_staging_bundle as staging


PACKET_VERSION = "rtdl.v3_0.c_abi_direct_link_example.goal4579.v1"
OUT_JSON = Path("docs/reports/goal4579_v3_0_m180_c_abi_direct_link_example_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4579_v3_0_m180_c_abi_direct_link_example_2026-06-17.md")
MAKEFILE = Path("Makefile")
EXAMPLE = Path("examples/current/embedding/c_api_direct_link_client.c")
STAGING_CONTRACT = Path("docs/learn/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("examples/current/embedding/README.md")


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def run_direct_link_example(root: Path) -> dict[str, Any]:
    stage_result = staging.run_stage(root)
    pkg_config = shutil.which("pkg-config")
    cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    stage_dir = root / "build" / "c_api_stage"
    staged_example = stage_dir / "examples" / "c_api_direct_link_client.c"
    exe = stage_dir / "examples" / "rtdl_c_api_direct_link_client"
    env = os.environ.copy()
    env["PKG_CONFIG_PATH"] = str(stage_dir / "lib" / "pkgconfig")
    result: dict[str, Any] = {
        "stage_result": stage_result,
        "pkg_config": pkg_config,
        "cc": cc,
        "staged_example": staged_example.as_posix(),
        "compile_result": None,
        "run_result": None,
        "ok": False,
    }
    if not stage_result["ok"] or pkg_config is None or cc is None or not staged_example.exists():
        return result
    cflags_completed = subprocess.run(
        [pkg_config, "--cflags", "rtdl-c-api"],
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    libs_completed = subprocess.run(
        [pkg_config, "--libs", "rtdl-c-api"],
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if cflags_completed.returncode != 0 or libs_completed.returncode != 0:
        result["compile_result"] = {
            "ok": False,
            "cflags_stderr_tail": _tail(cflags_completed.stderr),
            "libs_stderr_tail": _tail(libs_completed.stderr),
        }
        return result
    command = [
        cc,
        "-std=c11",
        *shlex.split(cflags_completed.stdout),
        str(staged_example),
        "-o",
        str(exe),
        *shlex.split(libs_completed.stdout),
    ]
    compile_completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["compile_result"] = {
        "command": command,
        "returncode": compile_completed.returncode,
        "ok": compile_completed.returncode == 0,
        "stdout_tail": _tail(compile_completed.stdout),
        "stderr_tail": _tail(compile_completed.stderr),
    }
    if compile_completed.returncode != 0:
        return result
    run_env = os.environ.copy()
    run_env["LD_LIBRARY_PATH"] = str(stage_dir / "lib") + os.pathsep + run_env.get("LD_LIBRARY_PATH", "")
    run_completed = subprocess.run(
        [str(exe)],
        cwd=root,
        env=run_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["run_result"] = {
        "command": [exe.as_posix()],
        "returncode": run_completed.returncode,
        "ok": run_completed.returncode == 0,
        "stdout": run_completed.stdout.strip(),
        "stderr_tail": _tail(run_completed.stderr),
    }
    result["ok"] = (
        result["compile_result"]["ok"]
        and result["run_result"]["ok"]
        and result["run_result"]["stdout"] == "direct_link_ok 0.1.3 ok"
    )
    return result


def build_packet(root: Path = Path("."), *, run_smoke: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    example = (root / EXAMPLE).read_text(encoding="utf-8")
    staging_contract = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    smoke = run_direct_link_example(root) if run_smoke else None
    checks = {
        "direct_link_example_exists": (root / EXAMPLE).exists(),
        "example_uses_public_header_and_capability_queries": '#include "rtdl/rtdl.h"' in example
        and "rtdl_backend_is_supported" in example
        and "rtdl_route_is_supported" in example,
        "example_creates_and_destroys_context": "rtdl_context_create" in example
        and "rtdl_context_destroy" in example,
        "makefile_stages_direct_link_example": "c_api_direct_link_client.c" in makefile,
        "staging_contract_documents_direct_link_example": "c_api_direct_link_client.c" in staging_contract
        and "rtdl_c_api_direct_link_client" in staging_contract,
        "embedding_readme_documents_direct_link_example": "c_api_direct_link_client.c" in embedding
        and "rtdl_c_api_direct_link_client" in embedding,
    }
    if smoke is not None:
        checks.update(
            {
                "stage_bundle_smoke_ok": bool(smoke["stage_result"]["ok"]),
                "pkg_config_available": bool(smoke["pkg_config"]),
                "cc_available": bool(smoke["cc"]),
                "staged_direct_link_example_compiles": bool(
                    smoke["compile_result"] and smoke["compile_result"]["ok"]
                ),
                "staged_direct_link_example_runs": bool(
                    smoke["run_result"]
                    and smoke["run_result"]["ok"]
                    and smoke["run_result"]["stdout"] == "direct_link_ok 0.1.3 ok"
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4579 / V3 M180",
        "status": "c_abi_direct_link_example_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "direct_link_smoke": smoke,
        "claim_boundary": {
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "general_backend_query_authorized": False,
            "language_binding_generated": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4579 promotes the direct-link C ABI smoke into a real source-tree "
            "example and stages it with `make stage-c-api`. The pod evidence "
            "compiles the staged example with the staged pkg-config metadata and "
            "runs it against the staged library. This remains a draft source-tree "
            "embedding example, not a packaged SDK or stable ABI claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["direct_link_smoke"] or {}
    lines = [
        "# Goal4579 / V3 M180 C ABI Direct-Link Example",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Smoke",
        "",
        f"- OK: `{smoke.get('ok')}`",
        f"- Output: `{(smoke.get('run_result') or {}).get('stdout')}`",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This validates a staged direct-link C example only.",
            "- No packaged SDK, stable ABI, general backend query, generated language binding, or release claim is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-smoke", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_smoke=not args.no_smoke)
    if not args.no_write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_report(packet, OUT_REPORT)
    print(
        json.dumps(
            {
                "failed_checks": packet["failed_checks"],
                "status": "accept" if not packet["failed_checks"] else "reject",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
