from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_exported_symbol_audit.goal4556.v1"
OUT_JSON = Path("docs/reports/goal4556_v3_0_m157_c_abi_exported_symbol_audit_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4556_v3_0_m157_c_abi_exported_symbol_audit_2026-06-17.md")
MAKEFILE = Path("Makefile")
HEADER = Path("include/rtdl/rtdl.h")

EXPECTED_SYMBOLS = (
    "rtdl_abi_version_major",
    "rtdl_abi_version_minor",
    "rtdl_abi_version_patch",
    "rtdl_abi_is_compatible",
    "rtdl_status_string",
    "rtdl_context_last_error",
    "rtdl_context_create",
    "rtdl_context_destroy",
    "rtdl_context_set_external_runtime",
    "rtdl_buffer_import",
    "rtdl_buffer_export",
    "rtdl_buffer_destroy",
    "rtdl_index_build",
    "rtdl_query_execute",
    "rtdl_index_destroy",
    "rtdl_query_destroy",
)


def _shared_suffix() -> str:
    if os.name == "nt":
        return ".dll"
    return ".dylib" if os.uname().sysname == "Darwin" else ".so"


def _artifact_path(root: Path) -> Path:
    return root / "build" / ("librtdl_c_api" + _shared_suffix())


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _parse_nm_symbols(output: str) -> tuple[str, ...]:
    symbols: list[str] = []
    for line in output.splitlines():
        parts = line.split()
        if not parts:
            continue
        symbol = parts[-1]
        if symbol.startswith("rtdl_"):
            symbols.append(symbol)
    return tuple(sorted(set(symbols)))


def run_symbol_audit(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    nm = shutil.which("nm")
    artifact = _artifact_path(root)
    result: dict[str, Any] = {
        "make": make,
        "nm": nm,
        "artifact": artifact.as_posix(),
        "make_result": None,
        "nm_result": None,
        "exported_symbols": (),
        "missing_symbols": EXPECTED_SYMBOLS,
        "ok": False,
    }
    if make is None or nm is None:
        return result
    make_completed = subprocess.run(
        [make, "build-c-api"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["make_result"] = {
        "command": [make, "build-c-api"],
        "returncode": make_completed.returncode,
        "ok": make_completed.returncode == 0 and artifact.exists(),
        "stdout_tail": _tail(make_completed.stdout),
        "stderr_tail": _tail(make_completed.stderr),
    }
    if make_completed.returncode != 0 or not artifact.exists():
        return result
    if os.name == "nt":
        nm_command = [nm, "-g", str(artifact)]
    elif os.uname().sysname == "Darwin":
        nm_command = [nm, "-gU", str(artifact)]
    else:
        nm_command = [nm, "-D", "--defined-only", str(artifact)]
    nm_completed = subprocess.run(
        nm_command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    exported = _parse_nm_symbols(nm_completed.stdout)
    missing = tuple(symbol for symbol in EXPECTED_SYMBOLS if symbol not in exported)
    result.update(
        {
            "nm_result": {
                "command": nm_command,
                "returncode": nm_completed.returncode,
                "ok": nm_completed.returncode == 0,
                "stdout_tail": _tail(nm_completed.stdout),
                "stderr_tail": _tail(nm_completed.stderr),
            },
            "exported_symbols": exported,
            "missing_symbols": missing,
            "ok": nm_completed.returncode == 0 and not missing,
        }
    )
    return result


def build_packet(root: Path = Path("."), *, run_audit: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    header = (root / HEADER).read_text(encoding="utf-8")
    audit = run_symbol_audit(root) if run_audit else None
    checks = {
        "makefile_has_build_c_api_target": "build-c-api:" in makefile,
        "header_declares_expected_symbols": all(symbol in header for symbol in EXPECTED_SYMBOLS),
        "expected_symbol_count_is_16": len(EXPECTED_SYMBOLS) == 16,
    }
    if audit is not None:
        checks.update(
            {
                "make_available": bool(audit["make"]),
                "nm_available": bool(audit["nm"]),
                "make_build_ok": bool(audit["make_result"] and audit["make_result"]["ok"]),
                "nm_audit_ok": bool(audit["nm_result"] and audit["nm_result"]["ok"]),
                "all_expected_symbols_exported": bool(audit["ok"]),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4556 / V3 M157",
        "status": "c_abi_exported_symbol_audit_checked",
        "date": "2026-06-17",
        "expected_symbols": EXPECTED_SYMBOLS,
        "checks": checks,
        "failed_checks": failed,
        "audit": audit,
        "claim_boundary": {
            "backend_query_implemented": False,
            "binary_compatibility_frozen": False,
            "semantic_compatibility_validated": False,
            "dlpack_support_implemented": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4556 audits the `make build-c-api` artifact and verifies that the "
            "current lifecycle and version-negotiation C ABI symbols are actually exported from the shared "
            "library. This checks the build product's symbol surface only; it does "
            "not freeze binary compatibility or validate backend query semantics."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    audit = packet["audit"] or {}
    lines = [
        "# Goal4556 / V3 M157 C ABI Exported Symbol Audit",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Symbols",
        "",
        f"- Expected: `{len(packet['expected_symbols'])}`",
        f"- Missing: `{audit.get('missing_symbols')}`",
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
            "- This audits exported lifecycle symbols from the Makefile-built shared library.",
            "- No backend query, semantic compatibility, DLPack bridge, frozen ABI, or release claim is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-audit", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_audit=not args.no_audit)
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
