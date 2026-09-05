#!/usr/bin/env python3
"""Recount the two Goal5844 GPU transactions from retained JSON evidence."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from experiments.goal5842_causal_admission.contracts import digest, sha256_file


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT
    / "history/internal_docs/goal5844_public_execution_parity_20260904/evidence"
)
AUTHORITY_PATH = EVIDENCE_ROOT.parent / "GOAL5844_INTERNAL_AUTHORITY.json"
RTDL_ARM = "RTDL_PUBLIC_V8_COMPACT_STAMP"
PYOPTIX_ARM = "PINNED_PYOPTIX_COMPATIBLE_API"
EXPECTED_GPU_UUID = "GPU-4b436f5f-bf8f-1d8c-0202-98e6e7b387e9"
SUMMARY_CLAIM = {
    "external_review_complete": False,
    "formal_baseline": False,
    "goal5843_rows_reused_or_pooled": False,
    "internal_engineering_evidence_only": True,
    "public_or_manuscript_claim_authorized": False,
}
WORKER_CLAIM = {
    "engineering_evidence_only": True,
    "external_review_complete": False,
    "public_or_manuscript_claim_authorized": False,
}
VERIFICATION_CLAIM = {
    "external_review_complete": False,
    "internal_engineering_evidence_only": True,
    "public_or_manuscript_claim_authorized": False,
}
PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
ATTEMPTS = {
    "attempt1_adverse": {
        "source_commit": "5e1518afe24230be677484f8e437e0a0da6bb30d",
        "status": "ADVERSE__CONTINUE_PERFORMANCE_ENGINEERING",
        "summary_result_sha256": (
            "4d6548238849c49e7aa89dcb663f08febb2815d83da924dd3a083db5549a94d3"
        ),
        "archive_sha256": (
            "d4d57100f77c74b1f43187d7c82e290fa6071524aa8478b8369f0925a6e93814"
        ),
        "attribution_keys": (
            "provider_owner_v8_compact",
            "direct_native_abi_v8_integrated_audit",
            "explicit_full_forensic_expansion",
        ),
    },
    "attempt2_target_met": {
        "source_commit": "ee0237963bcd838d652a059f15ecc0d3f56dfd09",
        "status": "PASS__INTERNAL_ENGINEERING_TARGET_MET",
        "summary_result_sha256": (
            "6229aeba61fa681cbcda37e0ca253f725269fe08c2dd5e85f91502e5ad0a3b03"
        ),
        "archive_sha256": (
            "4336526eb6084d18353812187b2bd6c57515a642d804313abbaa79b52b1b678d"
        ),
        "attribution_keys": (
            "provider_owner_v8_compact",
            "protocol_validated_compact",
            "family_bridge_validated_compact",
            "direct_native_abi_v8_integrated_audit",
            "explicit_full_forensic_expansion",
        ),
    },
}


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON object required: {path}")
    return value


def _verify_seal(value: dict[str, object], field: str) -> None:
    observed = value.get(field)
    body = dict(value)
    body.pop(field, None)
    if observed != digest(body):
        raise RuntimeError(f"{field} differs")


def _timing(value: object, expected_count: int) -> list[int]:
    if not isinstance(value, dict):
        raise TypeError("timing summary required")
    samples = value.get("samples_ns")
    if (
        not isinstance(samples, list)
        or len(samples) != expected_count
        or any(type(item) is not int or item <= 0 for item in samples)
    ):
        raise RuntimeError("timing samples differ")
    if value != {
        "sample_count": expected_count,
        "samples_ns": samples,
        "minimum_ns": min(samples),
        "median_ns": int(statistics.median(samples)),
        "maximum_ns": max(samples),
    }:
        raise RuntimeError("timing summary does not reproduce")
    return samples


def _archive_digest(path: Path) -> str:
    fields = path.read_text(encoding="ascii").strip().split()
    if len(fields) != 2 or len(fields[0]) != 64:
        raise RuntimeError("archive digest record differs")
    return fields[0]


def _recount_attempt(name: str, contract: dict[str, object]) -> dict[str, object]:
    root = EVIDENCE_ROOT / name
    summary = _load(root / "SUMMARY.json")
    _verify_seal(summary, "result_sha256")
    if (
        summary.get("source_commit") != contract["source_commit"]
        or summary.get("status") != contract["status"]
        or summary.get("result_sha256") != contract["summary_result_sha256"]
        or summary.get("all_samples_retained") is not True
    ):
        raise RuntimeError(f"{name} frozen result identity differs")
    if summary.get("claim_boundary") != SUMMARY_CLAIM:
        raise RuntimeError(f"{name} claim ceiling differs")
    hardware = summary.get("hardware")
    if (
        not isinstance(hardware, dict)
        or hardware.get("gpu_uuid") != EXPECTED_GPU_UUID
        or hardware.get("compute_capability") != "8.9"
    ):
        raise RuntimeError(f"{name} hardware identity differs")

    workers = [_load(path) for path in sorted((root / "workers").glob("*.json"))]
    if len(workers) != 16:
        raise RuntimeError(f"{name} worker count differs")
    by_key: dict[tuple[int, str], dict[str, object]] = {}
    worker_hashes: list[str] = []
    public_samples = {RTDL_ARM: [], PYOPTIX_ARM: []}
    attribution_samples: dict[str, list[int]] = {}
    for worker in workers:
        _verify_seal(worker, "result_sha256")
        if (
            worker.get("source_commit") != contract["source_commit"]
            or worker.get("status") != "PASS__INTERNAL_ENGINEERING_WORKER"
            or worker.get("hardware") != hardware
            or worker.get("task") != summary.get("task")
            or worker.get("repetitions") != 128
            or worker.get("claim_boundary") != WORKER_CLAIM
        ):
            raise RuntimeError(f"{name} worker identity differs")
        arm = worker.get("arm")
        block = worker.get("block")
        if arm not in (RTDL_ARM, PYOPTIX_ARM) or type(block) is not int:
            raise RuntimeError(f"{name} worker arm or block differs")
        key = (block, arm)
        if key in by_key:
            raise RuntimeError(f"{name} duplicate worker")
        by_key[key] = worker
        worker_hashes.append(str(worker["result_sha256"]))
        measurements = worker.get("measurements")
        if not isinstance(measurements, dict):
            raise RuntimeError(f"{name} worker measurements missing")
        public_samples[arm].extend(_timing(measurements.get("steady_public"), 128))
        attribution = measurements.get("attribution")
        if arm == PYOPTIX_ARM:
            if attribution is not None:
                raise RuntimeError(f"{name} PyOptiX attribution must be absent")
            identity = measurements.get("identity")
            if (
                not isinstance(identity, dict)
                or identity.get("pyoptix_repository_commit") != PYOPTIX_COMMIT
            ):
                raise RuntimeError(f"{name} PyOptiX source identity differs")
        else:
            if not isinstance(attribution, dict) or set(attribution) != set(
                contract["attribution_keys"]
            ):
                raise RuntimeError(f"{name} RTDL attribution fields differ")
            for layer, timing in attribution.items():
                attribution_samples.setdefault(layer, []).extend(_timing(timing, 64))

    schedule = summary.get("schedule")
    expected_schedule = []
    for block in range(8):
        order = (RTDL_ARM, PYOPTIX_ARM) if block % 2 == 0 else (PYOPTIX_ARM, RTDL_ARM)
        for position, arm in enumerate(order):
            expected_schedule.append(
                {"block": block, "position": position, "arm": arm}
            )
    if schedule != expected_schedule or set(by_key) != {
        (block, arm) for block in range(8) for arm in (RTDL_ARM, PYOPTIX_ARM)
    }:
        raise RuntimeError(f"{name} balanced schedule differs")

    within_block = []
    for block in range(8):
        rtdl_ns = by_key[(block, RTDL_ARM)]["measurements"]["steady_public"][
            "median_ns"
        ]
        pyoptix_ns = by_key[(block, PYOPTIX_ARM)]["measurements"]["steady_public"][
            "median_ns"
        ]
        within_block.append(
            {
                "block": block,
                "rtdl_median_ns": rtdl_ns,
                "pyoptix_median_ns": pyoptix_ns,
                "rtdl_over_pyoptix": rtdl_ns / pyoptix_ns,
            }
        )
    if summary.get("within_block") != within_block:
        raise RuntimeError(f"{name} within-block ratios do not reproduce")
    ratios = [row["rtdl_over_pyoptix"] for row in within_block]
    aggregate = summary.get("aggregate")
    if not isinstance(aggregate, dict) or aggregate != {
        "rtdl_sample_count": 1024,
        "pyoptix_sample_count": 1024,
        "rtdl_median_ns": int(statistics.median(public_samples[RTDL_ARM])),
        "pyoptix_median_ns": int(statistics.median(public_samples[PYOPTIX_ARM])),
        "median_within_block_ratio": float(statistics.median(ratios)),
        "engineering_target_ratio": 1.25,
        "engineering_target_met": statistics.median(ratios) <= 1.25,
    }:
        raise RuntimeError(f"{name} aggregate does not reproduce")
    if summary.get("worker_result_sha256") != worker_hashes:
        raise RuntimeError(f"{name} worker hash order differs")

    for verification_name in (
        "DOWNLOADED_STYLE_VERIFICATION.json",
        "LOCAL_INDEPENDENT_VERIFICATION.json",
    ):
        verification = _load(root / verification_name)
        if (
            verification.get("source_commit") != contract["source_commit"]
            or verification.get("status")
                != "PASS__DOWNLOADED_RESULT_RECOMPUTED_FROM_HASHED_PAYLOADS"
            or verification.get("claim_boundary") != VERIFICATION_CLAIM
            or verification.get("summary_result_sha256")
                != contract["summary_result_sha256"]
            or verification.get("median_within_block_ratio")
                != aggregate["median_within_block_ratio"]
            or verification.get("worker_count") != 16
        ):
            raise RuntimeError(f"{name} downloaded verification differs")
    transaction = _load(root / "POD_TRANSACTION.json")
    _verify_seal(transaction, "transaction_sha256")
    if (
        transaction.get("source_commit") != contract["source_commit"]
        or transaction.get("claim_boundary") != VERIFICATION_CLAIM
        or transaction.get("comparison_summary_sha256")
            != sha256_file(root / "SUMMARY.json")
    ):
        raise RuntimeError(f"{name} pod transaction differs")
    manifest = _load(root / "EVIDENCE_MANIFEST.json")
    _verify_seal(manifest, "manifest_sha256")
    if manifest.get("claim_boundary") != {
        "internal_engineering_evidence_only": True,
        "public_or_manuscript_claim_authorized": False,
    }:
        raise RuntimeError(f"{name} evidence manifest claim differs")
    if _archive_digest(root / "FULL_ARCHIVE.sha256") != contract["archive_sha256"]:
        raise RuntimeError(f"{name} archive digest differs")

    layer_medians = {
        layer: int(statistics.median(samples))
        for layer, samples in sorted(attribution_samples.items())
    }
    return {
        "source_commit": contract["source_commit"],
        "status": summary["status"],
        "summary_result_sha256": summary["result_sha256"],
        "archive_sha256": contract["archive_sha256"],
        "hardware": hardware,
        "rtdl_public_median_ns": aggregate["rtdl_median_ns"],
        "pyoptix_public_median_ns": aggregate["pyoptix_median_ns"],
        "median_within_block_ratio": aggregate["median_within_block_ratio"],
        "minimum_block_ratio": min(ratios),
        "maximum_block_ratio": max(ratios),
        "rtdl_first_median_ratio": statistics.median(ratios[0::2]),
        "pyoptix_first_median_ratio": statistics.median(ratios[1::2]),
        "attribution_median_ns": layer_medians,
        "worker_count": 16,
        "public_sample_count_per_arm": 1024,
        "all_samples_retained": True,
    }


def build() -> dict[str, object]:
    attempts = {
        name: _recount_attempt(name, contract)
        for name, contract in ATTEMPTS.items()
    }
    before = attempts["attempt1_adverse"]
    after = attempts["attempt2_target_met"]
    if (
        before["median_within_block_ratio"] <= 1.25
        or after["median_within_block_ratio"] > 1.25
        or before["hardware"] != after["hardware"]
    ):
        raise RuntimeError("Goal5844 before/after decision differs")
    files = []
    for path in sorted(EVIDENCE_ROOT.rglob("*")):
        if path.is_file():
            files.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    authority: dict[str, object] = {
        "schema": "rtdl.goal5844.public_execution_parity.internal_authority.v1",
        "status": (
            "PASS__GOAL5844_INTERNAL_ENGINEERING_TARGET_MET__"
            "EXTERNAL_REVIEW_PENDING"
        ),
        "attempts": attempts,
        "comparison": {
            "same_gpu_uuid": EXPECTED_GPU_UUID,
            "first_adverse_transaction_retained": True,
            "transactions_pooled": False,
            "rtdl_public_median_speedup_after_over_before": (
                before["rtdl_public_median_ns"] / after["rtdl_public_median_ns"]
            ),
            "pyoptix_median_after_over_before": (
                after["pyoptix_public_median_ns"]
                / before["pyoptix_public_median_ns"]
            ),
            "direct_native_median_after_over_before": (
                after["attribution_median_ns"][
                    "direct_native_abi_v8_integrated_audit"
                ]
                / before["attribution_median_ns"][
                    "direct_native_abi_v8_integrated_audit"
                ]
            ),
            "target_ratio": 1.25,
            "target_met_by_successor": True,
        },
        "historical_boundary": {
            "goal5838_exact_commit_authority_preserved": True,
            "current_tree_byte_identity_to_goal5838_claimed": False,
            "successor_modifies_generic_lifecycle_after_prospective_exam": True,
            "goal5843_rows_reused_or_pooled": False,
        },
        "claim_boundary": {
            "internal_engineering_evidence_only": True,
            "formal_baseline": False,
            "public_or_manuscript_claim_authorized": False,
            "hardware_independent_claim_authorized": False,
            "external_review_complete": False,
            "consensus_claimed": False,
        },
        "stored_evidence_files": files,
        "producer": {
            "path": str(Path(__file__).resolve().relative_to(ROOT)),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
    }
    authority["authority_sha256"] = digest(authority)
    return authority


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        if AUTHORITY_PATH.exists() or AUTHORITY_PATH.is_symlink():
            raise FileExistsError(AUTHORITY_PATH)
        AUTHORITY_PATH.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    else:
        stored = _load(AUTHORITY_PATH)
        if stored != value:
            raise RuntimeError("stored Goal5844 authority differs")
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
