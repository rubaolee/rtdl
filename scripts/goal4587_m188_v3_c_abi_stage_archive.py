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


PACKET_VERSION = "rtdl.v3_0.c_abi_stage_archive.goal4587.v1"
OUT_JSON = Path("docs/reports/goal4587_v3_0_m188_c_abi_stage_archive_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4587_v3_0_m188_c_abi_stage_archive_2026-06-17.md")
MAKEFILE = Path("Makefile")
STAGING_CONTRACT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("docs/history/v4_preparatory_embedding/examples/embedding/README.md")
ARCHIVE = Path("build/rtdl-c-api-stage-0.1.3.tar.gz")
ARCHIVE_ROOT = "rtdl-c-api-stage-0.1.3"


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _existing_command(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def run_stage_archive_smoke(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    pkg_config = shutil.which("pkg-config")
    cc = _existing_command(("cc", "gcc", "clang"))
    archive = root / ARCHIVE
    result: dict[str, Any] = {
        "make": make,
        "pkg_config": pkg_config,
        "cc": cc,
        "archive": archive.as_posix(),
        "make_result": None,
        "archive_exists": False,
        "archive_size_bytes": 0,
        "extract_dir": None,
        "cflags_result": None,
        "libs_result": None,
        "compile_result": None,
        "run_result": None,
        "ok": False,
    }
    if make is None or pkg_config is None or cc is None:
        return result
    make_completed = subprocess.run(
        [make, "package-c-api-stage"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["make_result"] = {
        "command": [make, "package-c-api-stage"],
        "returncode": make_completed.returncode,
        "ok": make_completed.returncode == 0,
        "stdout_tail": _tail(make_completed.stdout),
        "stderr_tail": _tail(make_completed.stderr),
    }
    result["archive_exists"] = archive.exists()
    result["archive_size_bytes"] = archive.stat().st_size if archive.exists() else 0
    if make_completed.returncode != 0 or not archive.exists():
        return result
    with tempfile.TemporaryDirectory(prefix="rtdl_c_api_stage_archive_") as tmp:
        tmpdir = Path(tmp)
        shutil.unpack_archive(str(archive), str(tmpdir))
        extracted = tmpdir / ARCHIVE_ROOT
        result["extract_dir"] = extracted.as_posix()
        pc_dir = extracted / "lib" / "pkgconfig"
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
        exe = extracted / "examples" / "rtdl_c_api_direct_link_client_from_archive"
        source = extracted / "examples" / "c_api_direct_link_client.c"
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
        run_env["LD_LIBRARY_PATH"] = str(extracted / "lib") + os.pathsep + run_env.get("LD_LIBRARY_PATH", "")
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
        and result["archive_exists"]
        and result["archive_size_bytes"] > 0
        and result["cflags_result"]["ok"]
        and result["libs_result"]["ok"]
        and result["compile_result"]["ok"]
        and result["run_result"]["ok"]
        and result["run_result"]["stdout"] == "direct_link_ok 0.1.3 ok"
    )
    return result


def build_packet(root: Path = Path("."), *, run_smoke: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    staging_contract = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    smoke = run_stage_archive_smoke(root) if run_smoke else None
    checks = {
        "makefile_declares_package_stage_target": "\npackage-c-api-stage:" in makefile,
        "package_stage_target_depends_on_stage": "package-c-api-stage: stage-c-api" in makefile,
        "package_stage_archive_name_is_versioned": "rtdl-c-api-stage-0.1.3" in makefile
        and "$(C_API_STAGE_ARCHIVE_ROOT).tar.gz" in makefile,
        "staging_contract_documents_archive_target": "make package-c-api-stage" in staging_contract
        and "rtdl-c-api-stage-0.1.3.tar.gz" in staging_contract,
        "embedding_readme_documents_archive_target": "make package-c-api-stage" in embedding
        and "rtdl-c-api-stage-0.1.3.tar.gz" in embedding,
    }
    if smoke is not None:
        checks.update(
            {
                "make_package_stage_ok": bool(smoke["make_result"] and smoke["make_result"]["ok"]),
                "archive_exists_and_nonempty": bool(smoke["archive_exists"] and smoke["archive_size_bytes"] > 0),
                "extracted_archive_pkg_config_cflags_ok": bool(
                    smoke["cflags_result"] and smoke["cflags_result"]["ok"]
                ),
                "extracted_archive_pkg_config_libs_ok": bool(smoke["libs_result"] and smoke["libs_result"]["ok"]),
                "extracted_archive_direct_link_compiles": bool(
                    smoke["compile_result"] and smoke["compile_result"]["ok"]
                ),
                "extracted_archive_direct_link_runs": bool(
                    smoke["run_result"]
                    and smoke["run_result"]["ok"]
                    and smoke["run_result"]["stdout"] == "direct_link_ok 0.1.3 ok"
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4587 / V3 M188",
        "status": "c_abi_stage_archive_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "stage_archive_smoke": smoke,
        "claim_boundary": {
            "packaged_sdk_authorized": False,
            "system_install_authorized": False,
            "stable_abi_authorized": False,
            "generated_binding_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4587 adds and validates `make package-c-api-stage`, a versioned "
            "archive of the source-tree C ABI staging bundle. The pod evidence "
            "builds the archive, extracts it elsewhere, compiles the staged "
            "direct-link C client via the extracted pkg-config metadata, and runs "
            "it against the extracted library. This is a movable source-tree "
            "stage archive, not a packaged SDK, system install, stable ABI, "
            "generated binding, or release claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smoke = packet["stage_archive_smoke"] or {}
    lines = [
        "# Goal4587 / V3 M188 C ABI Stage Archive",
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
        f"- Archive: `{smoke.get('archive')}`",
        f"- Archive size bytes: `{smoke.get('archive_size_bytes')}`",
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
            "- This validates a movable source-tree stage archive only.",
            "- It does not authorize a packaged SDK, system install, stable ABI, generated binding, or release claim.",
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
