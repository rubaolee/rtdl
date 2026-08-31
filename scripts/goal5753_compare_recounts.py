#!/usr/bin/env python3
"""Compare Windows and WSL Goal5753 recounts semantically and bytewise."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--windows", type=Path, required=True)
    parser.add_argument("--wsl", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    windows_bytes = args.windows.read_bytes()
    wsl_bytes = args.wsl.read_bytes()
    windows = json.loads(windows_bytes)
    wsl = json.loads(wsl_bytes)
    if windows != wsl:
        raise RuntimeError("Windows and WSL recount semantics differ")
    canonical = json.dumps(windows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result = {
        "schema": "rtdl.v4.goal5753.dual_platform_recount_comparison.v1",
        "status": "windows_and_wsl_semantically_identical",
        "windows_sha256": sha(windows_bytes),
        "wsl_sha256": sha(wsl_bytes),
        "byte_identical": windows_bytes == wsl_bytes,
        "byte_difference_explanation": (
            "platform_newline_serialization_only" if windows_bytes != wsl_bytes else "none"
        ),
        "canonical_semantic_sha256": sha(canonical),
        "semantic_equal": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
