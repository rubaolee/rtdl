#!/usr/bin/env python3
"""Extract and compare embedded RTDL PTX with a matched baseline PTX."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import re


def _find_ptx(value: object) -> bytes:
    if isinstance(value, dict):
        encoded = value.get("composed_ptx_base64", value.get("ptx_base64"))
        if isinstance(encoded, str):
            return base64.b64decode(encoded, validate=True)
        for child in value.values():
            try:
                return _find_ptx(child)
            except LookupError:
                pass
    elif isinstance(value, list):
        for child in value:
            try:
                return _find_ptx(child)
            except LookupError:
                pass
    elif isinstance(value, str) and value.startswith(("{", "[")):
        try:
            return _find_ptx(json.loads(value))
        except (json.JSONDecodeError, LookupError):
            pass
    raise LookupError("artifact has no ptx_base64 leaf")


def _stats(raw: bytes) -> dict[str, object]:
    text = raw.decode("utf-8")
    lines = tuple(text.splitlines())
    instructions = tuple(
        line.strip() for line in lines
        if re.match(r"^[a-zA-Z@].*;\s*(?://.*)?$", line.strip())
    )
    return {
        "bytes": len(raw),
        "lines": len(lines),
        "instruction_lines": len(instructions),
        "atomic_lines": sum("atom." in line or "red." in line for line in instructions),
        "global_load_lines": sum("ld.global" in line for line in instructions),
        "global_store_lines": sum("st.global" in line for line in instructions),
        "branch_lines": sum(re.search(r"\b(?:bra|brx)\b", line) is not None
                            for line in instructions),
        "call_lines": sum(re.search(r"\bcall\b", line) is not None
                          for line in instructions),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--baseline-ptx", type=Path, required=True)
    parser.add_argument("--extracted-ptx", type=Path)
    args = parser.parse_args()
    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    rtdl = _find_ptx(artifact)
    baseline = args.baseline_ptx.read_bytes()
    if args.extracted_ptx is not None:
        args.extracted_ptx.write_bytes(rtdl)
    result = {
        "schema": "rtdl.goal5805.informal_ptx_comparison.v1",
        "scientific_claim_authorized": False,
        "rtdl": _stats(rtdl),
        "matched_pyoptix": _stats(baseline),
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
