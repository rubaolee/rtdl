#!/usr/bin/env python3
"""Fail-closed final gate over independently recounted Goal5842 generations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from experiments.goal5842_causal_admission.contracts import (
    CROSS_GENERATION_AUTHORITY_SCHEMA,
    INDEPENDENT_RECOUNT_SCHEMA,
    digest,
    sha256_file,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_recount(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "recount must be an object")
    seal = value.get("recount_sha256")
    unsealed = dict(value)
    unsealed.pop("recount_sha256", None)
    require(isinstance(seal, str) and digest(unsealed) == seal, "recount seal mismatch")
    require(
        value.get("schema") == INDEPENDENT_RECOUNT_SCHEMA, "recount schema mismatch"
    )
    require(
        value.get("status") == "PASS__ONE_GPU_GENERATION_RECOUNT_COMPLETE",
        "recount status mismatch",
    )
    require(
        value.get("cross_generation_gate_passed") is False,
        "single-generation recount overclaims gate",
    )
    require(
        value.get("public_performance_claim_authorized") is False,
        "single-generation recount overclaims performance",
    )
    return value


def build(paths: list[Path]) -> dict[str, object]:
    require(
        len(paths) >= 2, "at least two independently recounted generations required"
    )
    rows = []
    recounts = []
    for path in paths:
        resolved = path.resolve(strict=True)
        recount = load_recount(resolved)
        recounts.append(recount)
        rows.append(
            {
                "path": str(resolved),
                "file_sha256": sha256_file(resolved),
                "recount_sha256": recount["recount_sha256"],
                "gpu_uuid": recount["hardware"]["gpu_uuid"],
                "gpu_model": recount["hardware"]["gpu_model"],
                "architecture_generation": recount["architecture_generation"],
                "causal_result_sha256": recount["causal_result_sha256"],
                "baseline_result_sha256": recount["baseline_result_sha256"],
            }
        )
    commits = {row["source_commit"] for row in recounts}
    preregs = {row["preregistration_sha256"] for row in recounts}
    generations = {row["architecture_generation"] for row in recounts}
    uuids = {row["hardware"]["gpu_uuid"] for row in recounts}
    require(len(commits) == 1, "recounts use different source commits")
    require(len(preregs) == 1, "recounts use different preregistrations")
    require(len(generations) >= 2, "recounts do not cover two GPU generations")
    require(len(uuids) == len(recounts), "one physical GPU was reused as multiple rows")
    result: dict[str, object] = {
        "schema": CROSS_GENERATION_AUTHORITY_SCHEMA,
        "status": "PASS__GOAL5842_TWO_GENERATION_INTERNAL_EVIDENCE_GATE",
        "source_commit": next(iter(commits)),
        "preregistration_sha256": next(iter(preregs)),
        "generation_count": len(generations),
        "architecture_generations": sorted(generations),
        "hardware_rows": rows,
        "same_exact_harness_and_workloads": True,
        "cross_machine_raw_time_ratios_computed": False,
        "no_post_result_success_threshold": True,
        "external_review_or_consensus": False,
        "public_performance_claim_authorized": False,
    }
    result["authority_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recount", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.recount)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="ascii") as stream:
        json.dump(
            result, stream, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False
        )
        stream.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
