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

from scripts import goal4576_m177_v3_c_abi_staging_bundle as staging


PACKET_VERSION = "rtdl.v3_0.c_abi_pkg_config_relocatable_stage.goal4586.v1"
OUT_JSON = Path("docs/reports/goal4586_v3_0_m187_c_abi_pkg_config_relocatable_stage_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4586_v3_0_m187_c_abi_pkg_config_relocatable_stage_2026-06-17.md")
PKG_CONFIG_TEMPLATE = Path("packaging/rtdl-c-api.pc")
STAGING_CONTRACT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("docs/history/v4_preparatory_embedding/examples/embedding/README.md")


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _existing_command(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _shared_suffix() -> str:
    if os.name == "nt":
        return ".dll"
    return ".dylib" if os.uname().sysname == "Darwin" else ".so"


def run_relocatable_stage_smoke(root: Path) -> dict[str, Any]:
    stage_result = staging.run_stage(root)
    pkg_config = shutil.which("pkg-config")
    cc = _existing_command(("cc", "gcc", "clang"))
    source_stage = root / "build" / "c_api_stage"
    result: dict[str, Any] = {
        "stage_result": stage_result,
        "pkg_config": pkg_config,
        "cc": cc,
        "copied_stage_dir": None,
        "cflags_result": None,
        "libs_result": None,
        "compile_result": None,
        "run_result": None,
        "ok": False,
    }
    if not stage_result["ok"] or pkg_config is None or cc is None or not source_stage.exists():
        return result
    with tempfile.TemporaryDirectory(prefix="rtdl_c_api_stage_reloc_") as tmp:
        copied_stage = Path(tmp) / "c_api_stage"
        shutil.copytree(source_stage, copied_stage)
        result["copied_stage_dir"] = copied_stage.as_posix()
        pc_dir = copied_stage / "lib" / "pkgconfig"
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
        exe = copied_stage / "examples" / "rtdl_c_api_direct_link_client_relocated"
        source = copied_stage / "examples" / "c_api_direct_link_client.c"
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
        run_env["LD_LIBRARY_PATH"] = str(copied_stage / "lib") + os.pathsep + run_env.get("LD_LIBRARY_PATH", "")
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
        result["cflags_result"]["ok"]
        and result["libs_result"]["ok"]
        and result["compile_result"]["ok"]
        and result["run_result"]["ok"]
        and result["run_result"]["stdout"] == "direct_link_ok 0.1.3 ok"
    )
    return result


def build_packet(root: Path = Path("."), *, run_smoke: bool = False) -> dict[str, Any]:
    pc_template = (root / PKG_CONFIG_TEMPLATE).read_text(encoding="utf-8")
    staging_contract = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    smoke = run_relocatable_stage_smoke(root) if run_smoke else None
    checks = {
        "pkg_config_template_uses_pcfiledir_relative_prefix": "prefix=${pcfiledir}/../.." in pc_template,
        "pkg_config_template_does_not_embed_repo_path": "C:" not in pc_template
        and "/workspace/" not in pc_template
        and "/Users/" not in pc_template,
        "docs_describe_source_tree_staging_not_install": "source-tree staging" in staging_contract
        and "not an installed SDK" in embedding,
    }
    if smoke is not None:
        checks.update(
            {
                "stage_bundle_smoke_ok": bool(smoke["stage_result"]["ok"]),
                "pkg_config_available": bool(smoke["pkg_config"]),
                "cc_available": bool(smoke["cc"]),
                "relocated_pkg_config_cflags_ok": bool(smoke["cflags_result"] and smoke["cflags_result"]["ok"]),
                "relocated_pkg_config_libs_ok": bool(smoke["libs_result"] and smoke["libs_result"]["ok"]),
                "relocated_direct_link_client_compiles": bool(
                    smoke["compile_result"] and smoke["compile_result"]["ok"]
                ),
                "relocated_direct_link_client_runs": bool(
                    smoke["run_result"]
                    and smoke["run_result"]["ok"]
                    and smoke["run_result"]["stdout"] == "direct_link_ok 0.1.3 ok"
                ),
                "relocated_flags_point_at_copied_stage": bool(
                    smoke["copied_stage_dir"]
                    and smoke["copied_stage_dir"] in (smoke["cflags_result"] or {}).get("stdout", "")
                    and smoke["copied_stage_dir"] in (smoke["libs_result"] or {}).get("stdout", "")
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4586 / V3 M187",
        "status": "c_abi_pkg_config_relocatable_stage_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "relocatable_stage_smoke": smoke,
        "claim_boundary": {
            "system_install_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "generated_language_binding_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4586 proves the staged pkg-config metadata is relocatable within "
            "the source-tree staging contract. The pod evidence builds "
            "`build/c_api_stage`, copies that stage to a temporary directory, "
            "uses the copied `lib/pkgconfig/rtdl-c-api.pc` to compile the staged "
            "direct-link C client, and runs it against the copied library. This "
            "is still not a system install, packaged SDK, stable ABI, generated "
            "binding, or release claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["relocatable_stage_smoke"] or {}
    lines = [
        "# Goal4586 / V3 M187 C ABI pkg-config Relocatable Stage",
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
        f"- Copied stage: `{smoke.get('copied_stage_dir')}`",
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
            "- This validates relocatability of the source-tree staging bundle only.",
            "- It does not authorize a system install, packaged SDK, stable ABI, generated binding, or release claim.",
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
