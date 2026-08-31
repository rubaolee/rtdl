#!/usr/bin/env python3
"""Verify a returned exact-byte external gate before Goal5798 v12 worker zero."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    args = parser.parse_args()
    gate = json.loads(args.gate.read_text(encoding="utf-8"))
    required = {
        "schema": "rtdl.goal5798.v12_external_preexecution_gate.v1",
        "status": "APPROVED_FOR_EXACT_V12_FORMAL_EXECUTION",
        "external_review_received": True,
        "formal_execution_authorized": True,
        "owner_authority_alone_sufficient": False,
        "postreview_code_or_candidate_change": False,
    }
    for key, value in required.items():
        if gate.get(key) != value:
            raise RuntimeError(f"external gate field mismatch: {key}")
    if gate.get("candidate_manifest_file_sha256") != sha(args.candidate_manifest):
        raise RuntimeError("external gate candidate-manifest identity mismatch")
    if gate.get("runtime_manifest_file_sha256") != sha(args.runtime_manifest):
        raise RuntimeError("external gate runtime-manifest identity mismatch")
    review_path = Path(str(gate.get("external_review_path", "")))
    if not review_path.is_absolute():
        raise RuntimeError("external review path must be absolute on the execution host")
    if not review_path.is_file() or gate.get("external_review_file_sha256") != sha(review_path):
        raise RuntimeError("external review identity missing or mismatched")
    if gate.get("review_verdict") not in {
            "APPROVE", "APPROVE_WITH_CONDITIONS__V12_EXECUTION_CLEARED"}:
        raise RuntimeError("external verdict does not clear v12 execution")
    print(json.dumps({
        "status": "PASS",
        "gate_file_sha256": sha(args.gate),
        "external_review_file_sha256": sha(review_path),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
