#!/usr/bin/env python3
"""Independently verify one downloaded Goal5844 engineering result directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from experiments.goal5842_causal_admission.contracts import digest
from experiments.goal5844_compact_execution.provenance import (
    Goal5844EvidenceError,
    sha256_file,
    validate_evidence_manifest,
    validate_file_record,
    validate_pyoptix_build_receipt,
)
from scripts import goal5844_run_gpu_engineering_comparison as comparison


def _load(path: Path, label: str) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise Goal5844EvidenceError(f"{label} is absent or symbolic")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise Goal5844EvidenceError(f"{label} is unreadable") from error
    if not isinstance(value, dict):
        raise Goal5844EvidenceError(f"{label} must be an object")
    return value


def _artifact(root: Path, provenance: dict[str, object], key: str) -> Path:
    path, _ = validate_file_record(root, provenance.get(key), f"Goal5844 {key}")
    return path


def verify_result_root(root: Path, *, expected_source_commit: str) -> dict[str, object]:
    result_root = root.expanduser().resolve(strict=True)
    manifest = validate_evidence_manifest(result_root)
    summary_path = result_root / "SUMMARY.json"
    summary = _load(summary_path, "Goal5844 summary")
    summary_body = dict(summary)
    summary_seal = summary_body.pop("result_sha256", None)
    if (
        summary.get("schema")
        != "rtdl.goal5844.compact_execution.engineering_comparison.v2"
        or summary.get("status")
        not in {
            "PASS__INTERNAL_ENGINEERING_TARGET_MET",
            "ADVERSE__CONTINUE_PERFORMANCE_ENGINEERING",
        }
        or summary.get("source_commit") != expected_source_commit
        or not isinstance(summary_seal, str)
        or summary_seal != digest(summary_body)
    ):
        raise Goal5844EvidenceError("Goal5844 summary header or seal differs")
    configuration = summary.get("configuration")
    provenance = summary.get("provenance")
    hardware = summary.get("hardware")
    if (
        not isinstance(configuration, dict)
        or set(configuration)
        != {
            "optix_sdk",
            "compute_capability",
            "pyoptix_distribution",
            "blocks",
            "warmups_per_worker",
            "repetitions_per_worker",
            "layer_warmups_per_worker",
            "layer_repetitions_per_worker",
        }
        or not isinstance(provenance, dict)
        or set(provenance)
        != {
            "native_library",
            "native_build_manifest",
            "native_build_log",
            "native_dynamic_defined_symbols",
            "required_v8_symbol",
            "required_v8_symbol_present",
            "device_source",
            "pyoptix_build_receipt",
        }
        or not isinstance(hardware, dict)
    ):
        raise Goal5844EvidenceError("Goal5844 summary configuration differs")
    blocks = configuration["blocks"]
    counts = (
        configuration["warmups_per_worker"],
        configuration["repetitions_per_worker"],
        configuration["layer_warmups_per_worker"],
        configuration["layer_repetitions_per_worker"],
    )
    if (
        type(blocks) is not int
        or blocks < 4
        or blocks % 2
        or any(type(value) is not int or value <= 0 for value in counts)
        or configuration["pyoptix_distribution"] != "pyoptix"
    ):
        raise Goal5844EvidenceError("Goal5844 summary run configuration is invalid")
    schedule = comparison.expected_schedule(blocks)
    if summary.get("schedule") != schedule:
        raise Goal5844EvidenceError("Goal5844 schedule differs from alternating design")

    native = _artifact(result_root, provenance, "native_library")
    native_manifest = _artifact(result_root, provenance, "native_build_manifest")
    native_build_log = _artifact(result_root, provenance, "native_build_log")
    symbols = _artifact(result_root, provenance, "native_dynamic_defined_symbols")
    device_source = _artifact(result_root, provenance, "device_source")
    pyoptix_receipt = _artifact(result_root, provenance, "pyoptix_build_receipt")
    if (
        provenance.get("required_v8_symbol") != comparison.V8_SYMBOL
        or provenance.get("required_v8_symbol_present") is not True
        or comparison.V8_SYMBOL
        not in {
            line.split()[-1]
            for line in symbols.read_text(encoding="utf-8").splitlines()
            if line.split()
        }
    ):
        raise Goal5844EvidenceError("Goal5844 v8 native symbol evidence differs")
    comparison._validate_native_build_manifest(
        native_manifest,
        native,
        source_commit=expected_source_commit,
        optix_sdk=str(configuration["optix_sdk"]),
        compute_capability=str(configuration["compute_capability"]),
        build_log_path=native_build_log,
    )
    receipt = validate_pyoptix_build_receipt(pyoptix_receipt)
    current_builder = (
        Path(__file__).resolve().with_name("goal5844_build_install_pyoptix.py")
    )
    if receipt["builder"]["sha256"] != sha256_file(
        current_builder.resolve(strict=True)
    ):
        raise Goal5844EvidenceError(
            "Goal5844 archived builder differs from the current source commit"
        )

    args = SimpleNamespace(
        native=native,
        native_build_manifest=native_manifest,
        device_source=device_source,
        pyoptix_build_receipt=pyoptix_receipt,
        optix_sdk=str(configuration["optix_sdk"]),
        compute_capability=str(configuration["compute_capability"]),
        pyoptix_distribution=str(configuration["pyoptix_distribution"]),
        blocks=blocks,
        warmups=int(configuration["warmups_per_worker"]),
        repetitions=int(configuration["repetitions_per_worker"]),
        layer_warmups=int(configuration["layer_warmups_per_worker"]),
        layer_repetitions=int(configuration["layer_repetitions_per_worker"]),
        source_commit=expected_source_commit,
    )
    worker_root = result_root / "workers"
    expected_names = {
        f"block_{int(item['block']):02d}_{int(item['position'])}_{item['arm']}.json"
        for item in schedule
    }
    actual_names = {path.name for path in worker_root.glob("*.json") if path.is_file()}
    if actual_names != expected_names:
        raise Goal5844EvidenceError("Goal5844 worker file set differs")
    rows: list[dict[str, object]] = []
    for item in schedule:
        name = (
            f"block_{int(item['block']):02d}_{int(item['position'])}_{item['arm']}.json"
        )
        row = _load(worker_root / name, f"Goal5844 worker {name}")
        comparison._validate_worker_result(
            row,
            args=args,
            arm=str(item["arm"]),
            block=int(item["block"]),
            source_commit=expected_source_commit,
            require_live_extension=False,
        )
        rows.append(row)
    if {json.dumps(row["hardware"], sort_keys=True) for row in rows} != {
        json.dumps(hardware, sort_keys=True)
    }:
        raise Goal5844EvidenceError("Goal5844 worker hardware identities differ")
    expected_summary = comparison.build_summary(
        args,
        rows,
        schedule=schedule,
        hardware=hardware,
        provenance=provenance,
    )
    if expected_summary != summary:
        raise Goal5844EvidenceError("Goal5844 summary does not recompute exactly")
    return {
        "schema": "rtdl.goal5844.downloaded_engineering_result_verification.v1",
        "status": "PASS__DOWNLOADED_RESULT_RECOMPUTED_FROM_HASHED_PAYLOADS",
        "source_commit": expected_source_commit,
        "summary_file_sha256": sha256_file(summary_path),
        "summary_result_sha256": summary["result_sha256"],
        "evidence_manifest_sha256": manifest["manifest_sha256"],
        "worker_count": len(rows),
        "engineering_target_met": summary["aggregate"]["engineering_target_met"],
        "median_within_block_ratio": summary["aggregate"]["median_within_block_ratio"],
        "claim_boundary": {
            "internal_engineering_evidence_only": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify_result_root(
        args.result_root, expected_source_commit=args.expected_source_commit
    )
    if args.output:
        if args.output.exists() or args.output.is_symlink():
            raise FileExistsError(args.output)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
