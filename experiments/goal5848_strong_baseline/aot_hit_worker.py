"""Fresh-process exact AOT cache-hit probe for Goal5848 AC8."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from rtdsl.v4_aot_cache import ExactAOTBuildRequest, resolve_exact_aot

from .contracts import TASKS, digest, strict_json_loads
from .worker import _compiler_modules, _nvrtc_mappings, _write_create


def _request_from_mapping(value: object) -> ExactAOTBuildRequest:
    if not isinstance(value, dict):
        raise TypeError("Goal5848 AOT request row is absent")
    request = dict(value)
    if request.pop("schema", None) != "rtdl.v4.exact_aot_build_request.v1":
        raise RuntimeError("Goal5848 AOT request schema differs")
    try:
        return ExactAOTBuildRequest(**request)
    except TypeError as error:
        raise RuntimeError("Goal5848 AOT request fields differ") from error


def _candidate(path: Path, task: str) -> tuple[dict[str, object], Path]:
    value = strict_json_loads(
        path.resolve(strict=True).read_text(encoding="utf-8"),
        label="Goal5848 AOT candidate manifest",
    )
    label = "relation" if task == TASKS[0] else "triangle"
    rows = value.get("rows") if isinstance(value, dict) else None
    if (
        not isinstance(value, dict)
        or value.get("schema") != "rtdl.goal5848.aot_candidates.v1"
        or value.get("status")
        != "PASS__EXACT_AOT_CACHE_AND_CANDIDATES_VERIFIED"
        or not isinstance(rows, dict)
        or not isinstance(rows.get(label), dict)
    ):
        raise RuntimeError("Goal5848 AOT candidate manifest differs")
    return dict(rows[label]), Path(str(value["aot_cache_root"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--worker-id", required=True)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidate, cache_root = _candidate(args.candidate_manifest, args.task)
    request = _request_from_mapping(candidate.get("aot_request"))
    if (
        request.source_commit != args.expected_source_commit
        or request.identity_sha256
        != candidate.get("aot_request_identity_sha256")
    ):
        raise RuntimeError("Goal5848 AOT request identity differs")
    producer_calls = 0

    def forbidden_producer(_root: Path):
        nonlocal producer_calls
        producer_calls += 1
        raise RuntimeError("Goal5848 fresh cache hit invoked producer")

    from scripts.goal5848_build_aot_candidates import _verifier

    compiler_before = _compiler_modules()
    mappings_before = _nvrtc_mappings()
    started = time.perf_counter_ns()
    entry = resolve_exact_aot(
        request,
        cache_root=cache_root,
        producer=forbidden_producer,
        verifier=lambda paths: _verifier(paths, request=request),
    )
    duration_ns = time.perf_counter_ns() - started
    compiler_after = _compiler_modules()
    mappings_after = _nvrtc_mappings()
    if (
        not entry.cache_hit
        or entry.producer_invoked
        or producer_calls != 0
        or compiler_before
        or compiler_after
        or mappings_before
        or mappings_after
    ):
        raise RuntimeError("Goal5848 fresh cache hit touched compiler lifecycle")
    value = {
        "schema": "rtdl.goal5848.aot_fresh_process_hit.v1",
        "status": "PASS__EXACT_VERIFIED_HIT__NO_PRODUCER_NO_COMPILER",
        "worker_id": args.worker_id,
        "task": args.task,
        "pid": os.getpid(),
        "python": sys.version.split()[0],
        "source_commit": args.expected_source_commit,
        "request_identity_sha256": request.identity_sha256,
        "entry_path": str(entry.entry_path),
        "duration_ns": duration_ns,
        "cache_hit": entry.cache_hit,
        "producer_invoked": entry.producer_invoked,
        "producer_call_count": producer_calls,
        "compiler_modules_before": list(compiler_before),
        "compiler_modules_after": list(compiler_after),
        "nvrtc_mappings_before": list(mappings_before),
        "nvrtc_mappings_after": list(mappings_after),
        "verification": entry.verification,
        "public_or_manuscript_claim_authorized": False,
    }
    value["receipt_sha256"] = digest(value)
    _write_create(args.output, value)
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
