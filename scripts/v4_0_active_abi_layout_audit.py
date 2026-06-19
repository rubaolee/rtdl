#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "src" / "v4" / "include" / "rtdl" / "rtdl.h"
CTYPES_SMOKE = ROOT / "src" / "v4" / "examples" / "python_ctypes_aabb2_smoke.py"


def _load_ctypes_smoke() -> Any:
    spec = importlib.util.spec_from_file_location("rtdl_v4_ctypes_smoke", CTYPES_SMOKE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {CTYPES_SMOKE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cpp_probe_source(layout: dict[str, Any]) -> str:
    lines = [
        '#include "rtdl/rtdl.h"',
        "#include <cstddef>",
        "#include <iostream>",
        "",
        "int main() {",
        '  std::cout << "pointer_size " << sizeof(void*) << "\\n";',
        '  std::cout << "max_rank " << RTDL_MAX_RANK << "\\n";',
    ]
    descriptors = layout["descriptors"]
    for type_name, type_layout in descriptors.items():
        lines.append(
            f'  std::cout << "type {type_name} sizeof " << sizeof({type_name}) << "\\n";'
        )
        for field_name in type_layout["fields"]:
            lines.append(
                f'  std::cout << "field {type_name} {field_name} "'
                f"<< offsetof({type_name}, {field_name}) << \" \" "
                f"<< sizeof((({type_name}*)0)->{field_name}) << \"\\n\";"
            )
    lines.extend(["  return 0;", "}"])
    return "\n".join(lines)


def _parse_cpp_probe(stdout: str) -> dict[str, Any]:
    layout: dict[str, Any] = {"descriptors": {}}
    for raw_line in stdout.splitlines():
        parts = raw_line.split()
        if not parts:
            continue
        if parts[0] == "pointer_size":
            layout["pointer_size"] = int(parts[1])
        elif parts[0] == "max_rank":
            layout["max_rank"] = int(parts[1])
        elif parts[0] == "type" and len(parts) == 4 and parts[2] == "sizeof":
            layout["descriptors"][parts[1]] = {"sizeof": int(parts[3]), "fields": {}}
        elif parts[0] == "field" and len(parts) == 5:
            layout["descriptors"][parts[1]]["fields"][parts[2]] = {
                "offset": int(parts[3]),
                "size": int(parts[4]),
            }
        else:
            raise RuntimeError(f"unexpected layout probe line: {raw_line!r}")
    return layout


def _run_cpp_probe(cxx: str, layout: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    compiler_path = shutil.which(cxx) or cxx
    with tempfile.TemporaryDirectory(prefix="rtdl_v4_layout_") as tmp:
        tmpdir = Path(tmp)
        source = tmpdir / "layout_probe.cpp"
        exe = tmpdir / ("layout_probe.exe" if os.name == "nt" else "layout_probe")
        source.write_text(_cpp_probe_source(layout), encoding="utf-8")
        compile_cmd = [
            cxx,
            "-std=c++17",
            "-I",
            str(HEADER.parent.parent),
            str(source),
            "-o",
            str(exe),
        ]
        compile_result = subprocess.run(
            compile_cmd,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        if compile_result.returncode != 0:
            raise RuntimeError(
                "layout probe compile failed\n"
                f"command: {' '.join(compile_cmd)}\n"
                f"stdout:\n{compile_result.stdout}\n"
                f"stderr:\n{compile_result.stderr}"
            )
        run_result = subprocess.run(
            [str(exe)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        if run_result.returncode != 0:
            raise RuntimeError(
                "layout probe execution failed\n"
                f"stdout:\n{run_result.stdout}\n"
                f"stderr:\n{run_result.stderr}"
            )
        metadata = {
            "compiler": cxx,
            "compiler_path": compiler_path,
            "compile_command": compile_cmd,
        }
        return _parse_cpp_probe(run_result.stdout), metadata


def build_audit(cxx: str = "c++") -> dict[str, Any]:
    smoke = _load_ctypes_smoke()
    ctypes_layout = smoke.layout_snapshot()
    c_layout, metadata = _run_cpp_probe(cxx, ctypes_layout)
    matches = c_layout == ctypes_layout
    return {
        "manifest_kind": "rtdl_v4_active_abi_layout_audit_v1",
        "date": "2026-06-19",
        "status": "active_experimental_substrate_layout_audit",
        "abi_version": "0.2.0",
        "stable": False,
        "header": "src/v4/include/rtdl/rtdl.h",
        "ctypes_mirror": "src/v4/examples/python_ctypes_aabb2_smoke.py",
        "platform": {
            "python": sys.version.split()[0],
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "compiler": metadata,
        "matches": matches,
        "c_header_layout": c_layout,
        "ctypes_layout": ctypes_layout,
        "claim_boundaries": {
            "stable_sdk": False,
            "public_c_abi_release": False,
            "package_install": False,
            "non_python_host_release": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit active V4 C ABI descriptor layouts.")
    parser.add_argument("--cxx", default=os.environ.get("CXX", "c++"))
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    payload = build_audit(cxx=args.cxx)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["matches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
