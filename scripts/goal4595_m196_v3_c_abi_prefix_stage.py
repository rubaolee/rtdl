from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_prefix_stage.goal4595.v1"
OUT_JSON = Path("docs/reports/goal4595_v3_0_m196_c_abi_prefix_stage_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4595_v3_0_m196_c_abi_prefix_stage_2026-06-17.md")
MAKEFILE = Path("Makefile")
PKG_CONFIG_TEMPLATE = Path("docs/history/v4_preparatory_embedding/staging/packaging/rtdl-c-api.pc")
STAGING_CONTRACT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("docs/history/v4_preparatory_embedding/examples/embedding/README.md")
DEFAULT_TEST_PREFIX = "/opt/rtdl"


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _existing_command(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def run_prefix_stage_smoke(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    pkg_config = shutil.which("pkg-config")
    cc = _existing_command(("cc", "gcc", "clang"))
    result: dict[str, Any] = {
        "make": make,
        "pkg_config": pkg_config,
        "cc": cc,
        "stage_root": None,
        "prefix": DEFAULT_TEST_PREFIX,
        "prefix_dir": None,
        "make_result": None,
        "cflags_result": None,
        "libs_result": None,
        "compile_result": None,
        "run_result": None,
        "ok": False,
    }
    if make is None or pkg_config is None or cc is None:
        return result
    with tempfile.TemporaryDirectory(prefix="rtdl_c_api_prefix_stage_") as tmp:
        stage_root = Path(tmp)
        prefix_dir = stage_root / DEFAULT_TEST_PREFIX.strip("/")
        result["stage_root"] = stage_root.as_posix()
        result["prefix_dir"] = prefix_dir.as_posix()
        make_completed = subprocess.run(
            [
                make,
                "stage-c-api-prefix",
                f"C_API_PREFIX_STAGE_ROOT={stage_root.as_posix()}",
                f"C_API_PREFIX={DEFAULT_TEST_PREFIX}",
            ],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        result["make_result"] = {
            "command": [
                make,
                "stage-c-api-prefix",
                f"C_API_PREFIX_STAGE_ROOT={stage_root.as_posix()}",
                f"C_API_PREFIX={DEFAULT_TEST_PREFIX}",
            ],
            "returncode": make_completed.returncode,
            "ok": make_completed.returncode == 0,
            "stdout_tail": _tail(make_completed.stdout),
            "stderr_tail": _tail(make_completed.stderr),
        }
        if make_completed.returncode != 0:
            return result
        pc_dir = prefix_dir / "lib" / "pkgconfig"
        env = os.environ.copy()
        env["PKG_CONFIG_PATH"] = str(pc_dir)
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
        result["cflags_result"] = {
            "command": [pkg_config, "--cflags", "rtdl-c-api"],
            "returncode": cflags_completed.returncode,
            "ok": cflags_completed.returncode == 0,
            "stdout": cflags_completed.stdout.strip(),
            "stderr_tail": _tail(cflags_completed.stderr),
        }
        result["libs_result"] = {
            "command": [pkg_config, "--libs", "rtdl-c-api"],
            "returncode": libs_completed.returncode,
            "ok": libs_completed.returncode == 0,
            "stdout": libs_completed.stdout.strip(),
            "stderr_tail": _tail(libs_completed.stderr),
        }
        if cflags_completed.returncode != 0 or libs_completed.returncode != 0:
            return result
        source = prefix_dir / "share" / "rtdl" / "examples" / "c_api_direct_link_client.c"
        exe = prefix_dir / "share" / "rtdl" / "examples" / "rtdl_c_api_direct_link_client"
        compile_command = [
            cc,
            "-std=c11",
            *shlex.split(cflags_completed.stdout),
            str(source),
            "-o",
            str(exe),
            *shlex.split(libs_completed.stdout),
        ]
        compile_completed = subprocess.run(
            compile_command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        result["compile_result"] = {
            "command": compile_command,
            "returncode": compile_completed.returncode,
            "ok": compile_completed.returncode == 0,
            "stdout_tail": _tail(compile_completed.stdout),
            "stderr_tail": _tail(compile_completed.stderr),
        }
        if compile_completed.returncode != 0:
            return result
        run_env = os.environ.copy()
        run_env["LD_LIBRARY_PATH"] = str(prefix_dir / "lib") + os.pathsep + run_env.get("LD_LIBRARY_PATH", "")
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
        result["make_result"]["ok"]
        and result["cflags_result"]["ok"]
        and result["libs_result"]["ok"]
        and result["compile_result"]["ok"]
        and result["run_result"]["ok"]
        and result["run_result"]["stdout"] == "direct_link_ok 0.1.3 ok"
        and result["prefix_dir"] in result["cflags_result"]["stdout"]
        and result["prefix_dir"] in result["libs_result"]["stdout"]
    )
    return result


def build_packet(root: Path = Path("."), *, run_smoke: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    pc_template = (root / PKG_CONFIG_TEMPLATE).read_text(encoding="utf-8")
    staging_contract = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    smoke = run_prefix_stage_smoke(root) if run_smoke else None
    checks = {
        "makefile_declares_prefix_stage_target": "\nstage-c-api-prefix:" in makefile,
        "makefile_declares_prefix_stage_controls": "C_API_PREFIX_STAGE_ROOT ?=" in makefile
        and "C_API_PREFIX ?=" in makefile,
        "makefile_prefix_stage_uses_install_like_layout": "/include/rtdl" in makefile
        and "/lib/pkgconfig" in makefile
        and "/share/rtdl/examples" in makefile,
        "pkg_config_template_remains_pcfiledir_relocatable": "prefix=${pcfiledir}/../.." in pc_template,
        "staging_contract_documents_prefix_stage": "make stage-c-api-prefix" in staging_contract
        and "DESTDIR/prefix-style" in staging_contract,
        "embedding_readme_documents_prefix_stage": "make stage-c-api-prefix" in embedding
        and "build/c_api_prefix_stage/usr/local" in embedding,
        "docs_preserve_not_installed_sdk_boundary": "privileged system install" in staging_contract
        and "privileged system install" in embedding,
    }
    if smoke is not None:
        checks.update(
            {
                "prefix_stage_make_ok": bool(smoke["make_result"] and smoke["make_result"]["ok"]),
                "pkg_config_available": bool(smoke["pkg_config"]),
                "cc_available": bool(smoke["cc"]),
                "prefix_pkg_config_cflags_ok": bool(smoke["cflags_result"] and smoke["cflags_result"]["ok"]),
                "prefix_pkg_config_libs_ok": bool(smoke["libs_result"] and smoke["libs_result"]["ok"]),
                "prefix_direct_link_client_compiles": bool(
                    smoke["compile_result"] and smoke["compile_result"]["ok"]
                ),
                "prefix_direct_link_client_runs": bool(
                    smoke["run_result"]
                    and smoke["run_result"]["ok"]
                    and smoke["run_result"]["stdout"] == "direct_link_ok 0.1.3 ok"
                ),
                "prefix_flags_point_at_staged_prefix": bool(
                    smoke["prefix_dir"]
                    and smoke["prefix_dir"] in (smoke["cflags_result"] or {}).get("stdout", "")
                    and smoke["prefix_dir"] in (smoke["libs_result"] or {}).get("stdout", "")
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4595 / V3 M196",
        "status": "c_abi_prefix_stage_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "prefix_stage_smoke": smoke,
        "claim_boundary": {
            "prefix_layout_stage_authorized": not failed,
            "system_install_authorized": False,
            "package_manager_artifact_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "generated_binding_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4595 adds and validates `make stage-c-api-prefix`, a "
            "DESTDIR/prefix-style C ABI staging layout. The pod evidence stages "
            "the bundle under a temporary root with prefix `/opt/rtdl`, uses only "
            "that staged prefix's `lib/pkgconfig/rtdl-c-api.pc` metadata to "
            "compile the staged direct-link C client, and runs it against the "
            "staged library. This authorizes a prefix-layout staging proof only; "
            "it is not a privileged system install, package-manager artifact, "
            "packaged SDK, stable ABI, generated binding, or release claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["prefix_stage_smoke"] or {}
    lines = [
        "# Goal4595 / V3 M196 C ABI Prefix Stage",
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
        f"- Prefix: `{smoke.get('prefix')}`",
        f"- Prefix dir: `{smoke.get('prefix_dir')}`",
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
            "- This validates a DESTDIR/prefix-style C ABI staging layout only.",
            "- It does not authorize a privileged system install, package-manager artifact, packaged SDK, stable ABI, generated binding, or release claim.",
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
