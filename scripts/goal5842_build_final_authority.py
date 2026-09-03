#!/usr/bin/env python3
"""Build or verify Goal5842's two-generation internal final authority."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path

from experiments.goal5842_causal_admission.contracts import digest
from scripts import goal5842_build_cross_generation_authority as cross_builder
from scripts import goal5842_build_first_generation_authority as ada_builder
from scripts import goal5842_build_second_generation_authority as ampere_builder


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "history/internal_docs/goal5842_causal_admission_cost_20260903"
ADA_RECOUNT_PATH = EVIDENCE_ROOT / "V12_ADA_INDEPENDENT_RECOUNT.json"
AMPERE_RECOUNT_PATH = EVIDENCE_ROOT / "V12_AMPERE_INDEPENDENT_RECOUNT.json"
CROSS_AUTHORITY_PATH = EVIDENCE_ROOT / "V12_CROSS_GENERATION_AUTHORITY.json"
REPORT_PATH = (
    EVIDENCE_ROOT
    / "FORMAL_V12_AMPERE_SECOND_GENERATION_AND_CROSS_GENERATION_REPORT.md"
)
REVIEW_PATH = EVIDENCE_ROOT / "FINAL_INTERNAL_HOSTILE_REVIEW_V12_TWO_GENERATION.md"
AUTHORITY_PATH = EVIDENCE_ROOT / "GOAL5842_FINAL_INTERNAL_AUTHORITY.json"
AUTHORITY_DOMAIN = b"rtdl.goal5842.final_internal_authority.v1\0"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def file_sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def authority_seal(value: Mapping[str, object]) -> str:
    body = dict(value)
    body["authority_sha256"] = ""
    return hashlib.sha256(AUTHORITY_DOMAIN + canonical_bytes(body)).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="ascii"))
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def verify_cross_authority() -> dict[str, object]:
    observed = read_json(CROSS_AUTHORITY_PATH)
    seal = observed.get("authority_sha256")
    unsealed = dict(observed)
    unsealed.pop("authority_sha256", None)
    require(isinstance(seal, str) and digest(unsealed) == seal, "cross authority seal mismatch")
    rebuilt = cross_builder.build([ADA_RECOUNT_PATH, AMPERE_RECOUNT_PATH])

    # The frozen V12 cross builder records resolved local paths. Paths are not
    # evidence identity; normalize only that field while requiring every hash,
    # generation, UUID, status, and claim boundary to remain exact.
    def portable(value: Mapping[str, object]) -> dict[str, object]:
        row = deepcopy(dict(value))
        row.pop("authority_sha256", None)
        hardware = row.get("hardware_rows")
        require(isinstance(hardware, list), "cross hardware rows missing")
        for item in hardware:
            require(isinstance(item, dict), "cross hardware row malformed")
            item["path"] = Path(str(item.get("path"))).name
        return row

    require(portable(observed) == portable(rebuilt), "cross authority differs from rebuild")
    require(
        observed.get("status") == "PASS__GOAL5842_TWO_GENERATION_INTERNAL_EVIDENCE_GATE"
        and observed.get("generation_count") == 2
        and observed.get("architecture_generations") == ["ADA", "AMPERE"]
        and observed.get("same_exact_harness_and_workloads") is True
        and observed.get("cross_machine_raw_time_ratios_computed") is False
        and observed.get("public_performance_claim_authorized") is False
        and observed.get("external_review_or_consensus") is False,
        "cross authority status or claim boundary differs",
    )
    return observed


def build() -> dict[str, object]:
    ada = ada_builder.verify_stored()
    ampere = ampere_builder.verify_stored()
    require(ADA_RECOUNT_PATH.is_file(), "exported Ada recount missing")
    require(
        file_sha256(ADA_RECOUNT_PATH) == ada["execution"]["recount_file_sha256"],
        "exported Ada recount differs from verified archive",
    )
    cross = verify_cross_authority()
    require(REPORT_PATH.is_file(), "formal two-generation report missing")
    require(REVIEW_PATH.is_file(), "final internal hostile review missing")
    require(
        ada["source_commit"] == ampere["source_commit"] == cross["source_commit"],
        "generation source commits differ",
    )
    require(
        ada["preregistration"]["preregistration_sha256"]
        == ampere["preregistration"]["preregistration_sha256"]
        == cross["preregistration_sha256"],
        "generation preregistration seals differ",
    )
    require(
        ada["hardware"]["architecture_generation"] == "ADA"
        and ampere["hardware"]["architecture_generation"] == "AMPERE"
        and ada["hardware"]["gpu_uuid"] != ampere["hardware"]["gpu_uuid"],
        "two distinct generation identities are not proven",
    )
    result: dict[str, object] = {
        "schema": "rtdl.goal5842.final_internal_authority.v1",
        "status": (
            "PASS__GOAL5842_INTERNAL_TECHNICAL_COMPLETE__"
            "EXTERNAL_REVIEW_PENDING"
        ),
        "source_commit": ada["source_commit"],
        "preregistration_sha256": cross["preregistration_sha256"],
        "generation_authorities": [
            {
                "architecture_generation": "ADA",
                "path": str(ada_builder.AUTHORITY_PATH.relative_to(ROOT)),
                "file_sha256": file_sha256(ada_builder.AUTHORITY_PATH),
                "authority_sha256": ada["authority_sha256"],
                "archive_sha256": ada["archive"]["sha256"],
                "recount_sha256": ada["execution"]["recount_sha256"],
            },
            {
                "architecture_generation": "AMPERE",
                "path": str(ampere_builder.AUTHORITY_PATH.relative_to(ROOT)),
                "file_sha256": file_sha256(ampere_builder.AUTHORITY_PATH),
                "authority_sha256": ampere["authority_sha256"],
                "archive_sha256": ampere["archive"]["sha256"],
                "recount_sha256": ampere["execution"]["recount_sha256"],
            },
        ],
        "cross_generation_authority": {
            "path": str(CROSS_AUTHORITY_PATH.relative_to(ROOT)),
            "file_sha256": file_sha256(CROSS_AUTHORITY_PATH),
            "authority_sha256": cross["authority_sha256"],
            "architecture_generations": cross["architecture_generations"],
            "generation_count": cross["generation_count"],
        },
        "reports": [
            {
                "path": str(REPORT_PATH.relative_to(ROOT)),
                "sha256": file_sha256(REPORT_PATH),
            },
            {
                "path": str(REVIEW_PATH.relative_to(ROOT)),
                "sha256": file_sha256(REVIEW_PATH),
            },
        ],
        "completion_basis": {
            "same_exact_harness_and_workloads": True,
            "complete_archive_count": 2,
            "pod_recount_count": 2,
            "local_byte_identical_recount_count": 2,
            "distinct_gpu_architecture_generation_count": 2,
            "distinct_gpu_uuid_count": 2,
            "all_adverse_results_retained": True,
            "post_result_internal_hostile_review_complete": True,
            "v11_rows_pooled": False,
            "cross_machine_raw_time_ratios_computed": False,
        },
        "scientific_result": {
            "admission_cost_direction_replicated_across_generations": True,
            "all_six_primary_bootstrap_intervals_exclude_zero": True,
            "admission_is_not_dominant_setup_gap_diagnosis_replicated": True,
            "materialization_and_native_prepare_dominate_setup_on_both_generations": True,
            "current_provider_baselines_are_adverse": True,
            "checker_removal_recommended": False,
        },
        "claim_boundary": {
            "goal5842_internal_technical_complete": True,
            "goal5842_external_review_complete": False,
            "external_review_or_consensus": False,
            "public_performance_claim_authorized": False,
            "manuscript_performance_wording_authorized": False,
            "hardware_independent_timing_magnitude_claimed": False,
            "intrinsic_language_overhead_claimed": False,
            "checker_off_is_supported_api": False,
            "optimization_result_included": False,
        },
        "authority_sha256": "",
    }
    result["authority_sha256"] = authority_seal(result)
    return result


def verify_stored() -> dict[str, object]:
    observed = read_json(AUTHORITY_PATH)
    require(
        observed.get("authority_sha256") == authority_seal(observed),
        "stored final seal mismatch",
    )
    rebuilt = build()
    require(observed == rebuilt, "stored final authority differs from rebuild")
    return observed


def write_output(path: Path) -> dict[str, object]:
    result = build()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="ascii") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
        stream.write("\n")
    return result


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args(argv)
    result = verify_stored() if args.verify_stored else write_output(args.output.resolve())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
