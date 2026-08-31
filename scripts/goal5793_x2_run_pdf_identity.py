#!/usr/bin/env python3
"""Run the frozen X2 PDF identity parser in a fresh isolated process."""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = Path(__file__).resolve()
MAX_CHILD_INPUT_BYTES = 70_000_000
DEFAULT_TIMEOUT_SECONDS = 60


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _load_scientific_modules(vendor_root: Path | None = None):
    if vendor_root is not None:
        vendor_root = vendor_root.resolve()
        if not vendor_root.is_dir() or not (vendor_root / "pypdf" / "__init__.py").is_file():
            raise RuntimeError("PDF_VENDOR_ROOT_INVALID")
        sys.path.insert(0, str(vendor_root))
    sys.path.insert(0, str(ROOT))
    try:
        from scripts.goal5793_x1_canonical import seal_document
        from scripts.goal5793_x2_pdf_identity import extract_pdf_identity
    except ModuleNotFoundError:
        tools = RUNNER_PATH.parent
        sys.path.insert(0, str(tools))
        from goal5793_x1_canonical import seal_document  # type: ignore
        from goal5793_x2_pdf_identity import extract_pdf_identity  # type: ignore
    return seal_document, extract_pdf_identity


def _child(payload: Mapping[str, Any], vendor_root: Path | None) -> dict[str, Any]:
    if set(payload) != {"schema", "pdf_base64", "component"} or payload.get("schema") != "rtdl.goal5793.x2.pdf_identity_child_input.v1":
        raise RuntimeError("PDF_CHILD_INPUT_SCHEMA_INVALID")
    try:
        pdf_bytes = base64.b64decode(payload["pdf_base64"], validate=True)
    except Exception as exc:
        raise RuntimeError("PDF_CHILD_INPUT_BASE64_INVALID") from exc
    if not isinstance(payload["component"], Mapping):
        raise RuntimeError("PDF_CHILD_COMPONENT_INVALID")
    seal_document, extract_pdf_identity = _load_scientific_modules(vendor_root)
    receipt = extract_pdf_identity(pdf_bytes, payload["component"])
    result: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.isolated_pdf_identity_result.v1",
        "status": "ISOLATED_PDF_IDENTITY_COMPLETE",
        "runner": {"path_name": RUNNER_PATH.name, "bytes": RUNNER_PATH.stat().st_size, "sha256": hashlib.sha256(RUNNER_PATH.read_bytes()).hexdigest()},
        "process": {"isolated_flag": True, "bytecode_disabled": True, "python_executable": str(Path(sys.executable).resolve()), "pid": os.getpid()},
        "pdf_identity_receipt": receipt,
        "network_calls": 0,
        "result_sha256": "",
    }
    result["result_sha256"] = seal_document(
        result, seal_field="result_sha256", domain="rtdl.goal5793.x2.isolated_pdf_identity_result", version=1
    )
    return result


def run_isolated_pdf_identity(
    pdf_bytes: bytes,
    component: Mapping[str, Any],
    *,
    vendor_root: Path | None = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 300:
        raise RuntimeError("PDF_CHILD_TIMEOUT_INVALID")
    payload = _canonical(
        {
            "schema": "rtdl.goal5793.x2.pdf_identity_child_input.v1",
            "pdf_base64": base64.b64encode(pdf_bytes).decode("ascii"),
            "component": component,
        }
    )
    if len(payload) > MAX_CHILD_INPUT_BYTES:
        raise RuntimeError("PDF_CHILD_INPUT_LIMIT_EXCEEDED")
    override = os.environ.get("RTDL_X2_ISOLATED_PYTHON")
    child_python = Path(override).resolve() if override else Path(sys.executable).resolve()
    if not child_python.is_file():
        raise RuntimeError("PDF_CHILD_INTERPRETER_MISSING")
    command = [str(child_python), "-I", "-B", str(RUNNER_PATH), "--child"]
    if vendor_root is None:
        spec = importlib.util.find_spec("pypdf")
        if spec is None or spec.origin is None:
            raise RuntimeError("PDF_VENDOR_ROOT_INVALID")
        vendor_root = Path(spec.origin).resolve().parent.parent
    command += ["--vendor-root", str(vendor_root.resolve())]
    environment = {
        key: value
        for key, value in os.environ.items()
        if key.upper() in {"SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "TEMP", "TMP", "COMSPEC"}
    }
    environment["PYTHONNOUSERSITE"] = "1"
    try:
        completed = subprocess.run(
            command,
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout_seconds,
            env=environment,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("PDF_CHILD_TIMEOUT") from exc
    if completed.returncode != 0:
        raise RuntimeError("PDF_CHILD_FAILED__NO_IN_PROCESS_FALLBACK")
    try:
        result = json.loads(completed.stdout.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("PDF_CHILD_OUTPUT_INVALID") from exc
    if not isinstance(result, dict) or result.get("schema") != "rtdl.goal5793.x2.isolated_pdf_identity_result.v1":
        raise RuntimeError("PDF_CHILD_OUTPUT_INVALID")
    runner = result.get("runner")
    if runner != {"path_name": RUNNER_PATH.name, "bytes": RUNNER_PATH.stat().st_size, "sha256": hashlib.sha256(RUNNER_PATH.read_bytes()).hexdigest()}:
        raise RuntimeError("PDF_CHILD_RUNNER_IDENTITY_MISMATCH")
    if result.get("process", {}).get("isolated_flag") is not True or result.get("network_calls") != 0 or Path(result.get("process", {}).get("python_executable", "")).resolve() != child_python:
        raise RuntimeError("PDF_CHILD_PROCESS_BOUNDARY_MISMATCH")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--vendor-root", type=Path)
    args = parser.parse_args()
    if not args.child:
        parser.error("this command is an isolated child entrypoint")
    data = sys.stdin.buffer.read(MAX_CHILD_INPUT_BYTES + 1)
    if len(data) > MAX_CHILD_INPUT_BYTES:
        raise SystemExit("PDF_CHILD_INPUT_LIMIT_EXCEEDED")
    try:
        payload = json.loads(data.decode("utf-8", errors="strict"))
        result = _child(payload, args.vendor_root)
    except Exception as exc:
        sys.stderr.write(f"{type(exc).__name__}:{exc}\n")
        return 2
    sys.stdout.buffer.write(_canonical(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
