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


PACKET_VERSION = "rtdl.v3_0.c_abi_pkg_config_stage.goal4577.v1"
OUT_JSON = Path("docs/reports/goal4577_v3_0_m178_c_abi_pkg_config_stage_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4577_v3_0_m178_c_abi_pkg_config_stage_2026-06-17.md")
MAKEFILE = Path("Makefile")
PKG_CONFIG_TEMPLATE = Path("docs/history/v4_preparatory_embedding/staging/packaging/rtdl-c-api.pc")
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


def _direct_client_source() -> str:
    return "\n".join(
        [
            '#include "rtdl/rtdl.h"',
            "#include <stdio.h>",
            "",
            "int main(void) {",
            "  if (!rtdl_abi_is_compatible(",
            "          RTDL_ABI_VERSION_MAJOR,",
            "          RTDL_ABI_VERSION_MINOR,",
            "          RTDL_ABI_VERSION_PATCH)) {",
            "    return 2;",
            "  }",
            "  rtdl_context_desc desc = {0};",
            "  desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;",
            "  desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;",
            "  desc.backend = RTDL_BACKEND_CPU;",
            "  rtdl_context* context = 0;",
            "  rtdl_status status = rtdl_context_create(&desc, &context);",
            "  if (status != RTDL_STATUS_OK || context == 0) {",
            "    return 3;",
            "  }",
            "  printf(\"direct_link_ok %u.%u.%u %s\\n\",",
            "         rtdl_abi_version_major(),",
            "         rtdl_abi_version_minor(),",
            "         rtdl_abi_version_patch(),",
            "         rtdl_status_string(status));",
            "  rtdl_context_destroy(context);",
            "  return 0;",
            "}",
            "",
        ]
    )


def run_pkg_config_smoke(root: Path) -> dict[str, Any]:
    stage_result = staging.run_stage(root)
    pkg_config = shutil.which("pkg-config")
    cc = _existing_command(("cc", "gcc", "clang"))
    stage_dir = root / "build" / "c_api_stage"
    pc_dir = stage_dir / "lib" / "pkgconfig"
    env = os.environ.copy()
    env["PKG_CONFIG_PATH"] = str(pc_dir)
    result: dict[str, Any] = {
        "stage_result": stage_result,
        "pkg_config": pkg_config,
        "cc": cc,
        "pc_dir": pc_dir.as_posix(),
        "pc_file": (pc_dir / "rtdl-c-api.pc").as_posix(),
        "cflags_result": None,
        "libs_result": None,
        "compile_result": None,
        "run_result": None,
        "ok": False,
    }
    if not stage_result["ok"] or pkg_config is None or cc is None:
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
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        source = tmpdir / "direct_link_client.c"
        exe = tmpdir / "direct_link_client"
        source.write_text(_direct_client_source(), encoding="utf-8")
        cflags = shlex.split(cflags_completed.stdout)
        libs = shlex.split(libs_completed.stdout)
        compile_command = [cc, "-std=c11", *cflags, str(source), "-o", str(exe), *libs]
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
            "command": [str(exe)],
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
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    pc_template = (root / PKG_CONFIG_TEMPLATE).read_text(encoding="utf-8")
    staging_contract = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    smoke = run_pkg_config_smoke(root) if run_smoke else None
    checks = {
        "pkg_config_template_exists": (root / PKG_CONFIG_TEMPLATE).exists(),
        "pkg_config_template_is_relocatable_to_pcfiledir": "prefix=${pcfiledir}/../.." in pc_template,
        "pkg_config_template_names_0_1_3": "Version: 0.1.3" in pc_template,
        "pkg_config_template_exports_cflags_and_libs": "Cflags: -I${includedir}" in pc_template
        and "Libs: -L${libdir} -lrtdl_c_api" in pc_template,
        "makefile_stages_pkg_config_file": "lib/pkgconfig/rtdl-c-api.pc" in makefile
        and "$(C_API_PKG_CONFIG)" in makefile,
        "staging_contract_documents_pkg_config": "PKG_CONFIG_PATH" in staging_contract
        and "pkg-config --cflags --libs rtdl-c-api" in staging_contract,
        "embedding_readme_documents_pkg_config": "PKG_CONFIG_PATH" in embedding
        and "pkg-config --cflags --libs rtdl-c-api" in embedding,
    }
    if smoke is not None:
        checks.update(
            {
                "stage_bundle_smoke_ok": bool(smoke["stage_result"]["ok"]),
                "pkg_config_available": bool(smoke["pkg_config"]),
                "cc_available": bool(smoke["cc"]),
                "pkg_config_cflags_ok": bool(smoke["cflags_result"] and smoke["cflags_result"]["ok"]),
                "pkg_config_libs_ok": bool(smoke["libs_result"] and smoke["libs_result"]["ok"]),
                "direct_link_client_compiles": bool(smoke["compile_result"] and smoke["compile_result"]["ok"]),
                "direct_link_client_runs": bool(
                    smoke["run_result"]
                    and smoke["run_result"]["ok"]
                    and smoke["run_result"]["stdout"] == "direct_link_ok 0.1.3 ok"
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4577 / V3 M178",
        "status": "c_abi_pkg_config_stage_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "pkg_config_smoke": smoke,
        "claim_boundary": {
            "system_install_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "language_binding_generated": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4577 adds staged `pkg-config` metadata for the draft C ABI and "
            "validates a direct-link C client built from `pkg-config --cflags` "
            "and `--libs` against the staged library. This improves source-tree "
            "embeddability but is still not a system install, packaged SDK, "
            "stable ABI, language binding, or release claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["pkg_config_smoke"] or {}
    lines = [
        "# Goal4577 / V3 M178 C ABI Pkg-Config Stage",
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
        f"- Cflags: `{(smoke.get('cflags_result') or {}).get('stdout')}`",
        f"- Libs: `{(smoke.get('libs_result') or {}).get('stdout')}`",
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
            "- This validates source-tree staged pkg-config metadata only.",
            "- It does not authorize a system install, packaged SDK, stable ABI, generated language binding, or release claim.",
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
