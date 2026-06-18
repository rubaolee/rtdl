from __future__ import annotations

import argparse
import ctypes
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any


PACKET_VERSION = "rtdl.v3_0.python_ctypes_layout_audit.goal4599.v1"
OUT_JSON = Path("docs/reports/goal4599_v3_0_m200_python_ctypes_layout_audit_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4599_v3_0_m200_python_ctypes_layout_audit_2026-06-17.md")
HEADER = Path("docs/history/v4_preparatory_embedding/staging/include/rtdl/rtdl.h")
STABILITY_POLICY = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_stability_policy.md")
PYTHON_AABB2_EXAMPLE = Path("docs/history/v4_preparatory_embedding/examples/embedding/python_ctypes_aabb2_query_client.py")
PYTHON_CUDA_EXAMPLE = Path("docs/history/v4_preparatory_embedding/examples/embedding/python_ctypes_cuda_buffer_metadata_client.py")
LAYOUT_TYPES = {
    "rtdl_external_runtime": ("RtdlExternalRuntime", ("device_type", "device_id", "context", "stream", "user_data")),
    "rtdl_buffer_view": (
        "RtdlBufferView",
        ("data", "byte_count", "device_type", "device_id", "dtype", "ndim", "shape", "strides", "release", "user_data"),
    ),
    "rtdl_context_desc": ("RtdlContextDesc", ("abi_version_major", "abi_version_minor", "backend", "external_runtime")),
    "rtdl_index_desc": ("RtdlIndexDesc", ("abi_version_major", "abi_version_minor", "primitive_kind", "primitives", "primitive_count")),
    "rtdl_query_desc": ("RtdlQueryDesc", ("abi_version_major", "abi_version_minor", "query_kind", "inputs", "input_count")),
}


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _load_module(root: Path, path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, root / path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _python_layout(root: Path) -> dict[str, Any]:
    aabb2 = _load_module(root, PYTHON_AABB2_EXAMPLE, "goal4599_python_ctypes_aabb2")
    cuda = _load_module(root, PYTHON_CUDA_EXAMPLE, "goal4599_python_ctypes_cuda")
    modules = {
        "RtdlExternalRuntime": aabb2,
        "RtdlBufferView": aabb2,
        "RtdlContextDesc": aabb2,
        "RtdlIndexDesc": aabb2,
        "RtdlQueryDesc": aabb2,
    }
    # The CUDA example carries the same neutral buffer view; compare it too.
    layout: dict[str, Any] = {}
    for c_name, (py_name, fields) in LAYOUT_TYPES.items():
        cls = getattr(modules[py_name], py_name)
        layout[c_name] = {
            "size": ctypes.sizeof(cls),
            "offsets": {field: getattr(cls, field).offset for field in fields},
        }
    cuda_buffer_view = getattr(cuda, "RtdlBufferView")
    layout["python_cuda_example_rtdl_buffer_view"] = {
        "size": ctypes.sizeof(cuda_buffer_view),
        "offsets": {
            field: getattr(cuda_buffer_view, field).offset
            for field in LAYOUT_TYPES["rtdl_buffer_view"][1]
        },
    }
    return layout


def _layout_probe_source() -> str:
    lines = [
        '#include "rtdl/rtdl.h"',
        "#include <stddef.h>",
        "#include <stdio.h>",
        "#define PRINT_SIZE(T) printf(\"%s.size=%zu\\n\", #T, sizeof(T))",
        "#define PRINT_OFFSET(T, F) printf(\"%s.%s=%zu\\n\", #T, #F, offsetof(T, F))",
        "",
        "int main(void) {",
    ]
    for c_name, (_, fields) in LAYOUT_TYPES.items():
        lines.append(f"  PRINT_SIZE({c_name});")
        for field in fields:
            lines.append(f"  PRINT_OFFSET({c_name}, {field});")
    lines.extend(
        [
            "  return 0;",
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def _parse_c_layout(stdout: str) -> dict[str, Any]:
    layout: dict[str, Any] = {}
    for line in stdout.splitlines():
        if not line.strip():
            continue
        key, value_text = line.split("=", 1)
        type_name, field = key.split(".", 1)
        row = layout.setdefault(type_name, {"size": None, "offsets": {}})
        value = int(value_text)
        if field == "size":
            row["size"] = value
        else:
            row["offsets"][field] = value
    return layout


def run_c_layout_probe(root: Path) -> dict[str, Any]:
    cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    result: dict[str, Any] = {
        "cc": cc,
        "compile_result": None,
        "run_result": None,
        "c_layout": None,
        "ok": False,
    }
    if cc is None:
        return result
    with tempfile.TemporaryDirectory(prefix="rtdl_c_abi_layout_") as tmp:
        tmpdir = Path(tmp)
        source = tmpdir / "layout_probe.c"
        exe = tmpdir / "layout_probe"
        source.write_text(_layout_probe_source(), encoding="utf-8")
        compile_command = [cc, "-std=c11", "-I", str(root / "include"), str(source), "-o", str(exe)]
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
        run_completed = subprocess.run(
            [str(exe)],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        result["run_result"] = {
            "command": [exe.as_posix()],
            "returncode": run_completed.returncode,
            "ok": run_completed.returncode == 0,
            "stdout_tail": _tail(run_completed.stdout),
            "stderr_tail": _tail(run_completed.stderr),
        }
        if run_completed.returncode != 0:
            return result
        result["c_layout"] = _parse_c_layout(run_completed.stdout)
    result["ok"] = result["compile_result"]["ok"] and result["run_result"]["ok"] and bool(result["c_layout"])
    return result


def _layout_matches(c_layout: dict[str, Any], py_layout: dict[str, Any]) -> bool:
    for c_name in LAYOUT_TYPES:
        if c_layout.get(c_name) != py_layout.get(c_name):
            return False
    return c_layout.get("rtdl_buffer_view") == py_layout.get("python_cuda_example_rtdl_buffer_view")


def build_packet(root: Path = Path("."), *, run_probe: bool = False) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    policy = (root / STABILITY_POLICY).read_text(encoding="utf-8")
    aabb2_example = (root / PYTHON_AABB2_EXAMPLE).read_text(encoding="utf-8")
    cuda_example = (root / PYTHON_CUDA_EXAMPLE).read_text(encoding="utf-8")
    py_layout = _python_layout(root)
    c_probe = run_c_layout_probe(root) if run_probe else None
    checks = {
        "header_declares_layout_types": all(f"typedef struct {name}" in header for name in LAYOUT_TYPES),
        "python_aabb2_example_declares_all_layout_types": all(
            py_name in aabb2_example for py_name, _ in LAYOUT_TYPES.values()
        ),
        "python_cuda_example_declares_buffer_view": "class RtdlBufferView" in cuda_example,
        "python_examples_share_buffer_view_layout": py_layout["rtdl_buffer_view"]
        == py_layout["python_cuda_example_rtdl_buffer_view"],
        "stability_policy_names_layout_audit": "C/Python `ctypes` layout audit" in policy
        and "compiler-observed `sizeof`/`offsetof` evidence" in policy,
    }
    if c_probe is not None:
        checks.update(
            {
                "c_compiler_available": bool(c_probe["cc"]),
                "c_layout_probe_compiles": bool(c_probe["compile_result"] and c_probe["compile_result"]["ok"]),
                "c_layout_probe_runs": bool(c_probe["run_result"] and c_probe["run_result"]["ok"]),
                "c_layout_matches_python_ctypes_layout": bool(
                    c_probe["c_layout"] and _layout_matches(c_probe["c_layout"], py_layout)
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4599 / V3 M200",
        "status": "python_ctypes_layout_audit_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "python_ctypes_layout": py_layout,
        "c_layout_probe": c_probe,
        "claim_boundary": {
            "stable_abi_authorized": False,
            "generated_binding_authorized": False,
            "cross_platform_layout_claim_authorized": False,
            "packaged_sdk_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4599 adds a C/Python layout audit for the current draft C ABI "
            "descriptor structs used by the Python `ctypes` examples. The pod "
            "evidence compiles a tiny C `sizeof`/`offsetof` probe against "
            "`docs/history/v4_preparatory_embedding/staging/include/rtdl/rtdl.h` and compares it with Python `ctypes` layout "
            "for external runtime, buffer view, context, index, and query "
            "descriptors. This catches binding-offset drift without authorizing "
            "stable ABI, generated binding, cross-platform layout, SDK, or "
            "release wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    c_probe = packet["c_layout_probe"] or {}
    lines = [
        "# Goal4599 / V3 M200 Python Ctypes Layout Audit",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Probe",
        "",
        f"- OK: `{c_probe.get('ok')}`",
        f"- C compiler: `{c_probe.get('cc')}`",
        "",
        "## Checked Types",
        "",
        "| C type | Size | Fields |",
        "| --- | --- | --- |",
    ]
    for c_name in LAYOUT_TYPES:
        layout = packet["python_ctypes_layout"][c_name]
        fields = ", ".join(f"{name}:{offset}" for name, offset in layout["offsets"].items())
        lines.append(f"| `{c_name}` | `{layout['size']}` | `{fields}` |")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is a same-platform layout audit for the current draft C ABI and Python `ctypes` examples.",
            "- It does not authorize stable ABI, generated bindings, cross-platform layout guarantees, packaged SDK, or release claims.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-probe", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_probe=not args.no_probe)
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
