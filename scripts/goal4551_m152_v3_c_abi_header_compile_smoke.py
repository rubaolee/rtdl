from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_header_compile_smoke.goal4551.v1"
OUT_JSON = Path("docs/reports/goal4551_v3_0_m152_c_abi_header_compile_smoke_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4551_v3_0_m152_c_abi_header_compile_smoke_2026-06-17.md")
HEADER = Path("docs/history/v4_preparatory_embedding/staging/include/rtdl/rtdl.h")


def _existing_command(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _c_compiler() -> str | None:
    env = os.environ.get("CC")
    candidates = (env,) if env else ()
    if os.name == "nt":
        candidates += (r"C:\Program Files\LLVM\bin\clang.exe", "clang", "cc", "gcc")
    else:
        candidates += ("cc", "gcc", "clang")
    return _existing_command(tuple(candidate for candidate in candidates if candidate))


def _cxx_compiler() -> str | None:
    env = os.environ.get("CXX")
    candidates = (env,) if env else ()
    if os.name == "nt":
        candidates += (r"C:\Program Files\LLVM\bin\clang++.exe", "clang++", "c++", "g++")
    else:
        candidates += ("c++", "g++", "clang++")
    return _existing_command(tuple(candidate for candidate in candidates if candidate))


def _run_compile(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "ok": completed.returncode == 0,
        "stdout": completed.stdout,
        "stderr_tail": tuple(completed.stderr.splitlines()[-12:]),
    }


def compile_smoke(root: Path) -> dict[str, Any]:
    c_compiler = _c_compiler()
    cxx_compiler = _cxx_compiler()
    include_dir = root / "include"
    results: dict[str, Any] = {
        "c_compiler": c_compiler,
        "cxx_compiler": cxx_compiler,
        "c": None,
        "cxx": None,
    }
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        c_src = tmpdir / "rtdl_header_smoke.c"
        c_obj = tmpdir / "rtdl_header_smoke_c.o"
        c_src.write_text(
            "\n".join(
                [
                    '#include "rtdl/rtdl.h"',
                    "_Static_assert(RTDL_ABI_VERSION_MAJOR == 0, \"major\");",
                    "_Static_assert(RTDL_ABI_VERSION_MINOR == 1, \"minor\");",
                    "int main(void) { return (int)RTDL_STATUS_OK; }",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        cxx_src = tmpdir / "rtdl_header_smoke.cpp"
        cxx_obj = tmpdir / "rtdl_header_smoke_cxx.o"
        cxx_src.write_text(
            "\n".join(
                [
                    '#include "rtdl/rtdl.h"',
                    "static_assert(RTDL_ABI_VERSION_PATCH == 3, \"patch\");",
                    "int main() { return RTDL_STATUS_OK; }",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        if c_compiler:
            results["c"] = _run_compile(
                [c_compiler, "-std=c11", "-I", str(include_dir), "-c", str(c_src), "-o", str(c_obj)],
                root,
            )
        if cxx_compiler:
            results["cxx"] = _run_compile(
                [cxx_compiler, "-std=c++17", "-I", str(include_dir), "-c", str(cxx_src), "-o", str(cxx_obj)],
                root,
            )
    return results


def build_packet(root: Path = Path("."), *, run_compile: bool = False) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    compile_results = compile_smoke(root) if run_compile else None
    checks = {
        "header_exists": (root / HEADER).exists(),
        "header_uses_stdint_and_size_t": "#include <stdint.h>" in header and "#include <stddef.h>" in header,
        "header_has_extern_c": 'extern "C"' in header,
    }
    if compile_results is not None:
        checks.update(
            {
                "c_compiler_available": bool(compile_results["c_compiler"]),
                "cxx_compiler_available": bool(compile_results["cxx_compiler"]),
                "c_header_compile_ok": bool(compile_results["c"] and compile_results["c"]["ok"]),
                "cxx_header_compile_ok": bool(compile_results["cxx"] and compile_results["cxx"]["ok"]),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4551 / V3 M152",
        "status": "c_abi_header_compile_smoke_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "compile_results": compile_results,
        "claim_boundary": {
            "shared_library_symbols_implemented": False,
            "header_binary_compatibility_frozen": False,
            "non_python_client_validated": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4551 validates that the draft V3 `rtdl.h` header is usable from "
            "both C11 and C++17 translation units. This is a header hygiene gate "
            "only; it does not implement the ABI or freeze binary compatibility."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4551 / V3 M152 C ABI Header Compile Smoke",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
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
            "- This compiles header-only smoke translation units.",
            "- No shared-library ABI symbols are implemented or frozen.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_compile=True)
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
