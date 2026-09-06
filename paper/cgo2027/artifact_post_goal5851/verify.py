#!/usr/bin/env python3
"""Offline verifier for the anonymous CGO 2027 evidence projection."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath

PROJECTION_SCHEMA = "rtdl.cgo2027.submission_evidence.performance_projection.v1"
SUMMARY_SCHEMA = "rtdl.cgo2027.submission_evidence.recount_summary.v1"
MANIFEST_SCHEMA = "rtdl.cgo2027.submission_evidence.artifact_manifest.v1"
EXPECTED_PROJECTION_SHA256 = (
    "fa30b906b0d5a6edfdcc3267f24cea8274c9c9450a79edeef0058e89f6d252ca"
)

GENERATIONS = ("G0_ADA", "G1_AMPERE")
TASKS = (
    "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1",
    "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1",
)
ARMS = (
    "A_RTDL_AOT_PUBLIC",
    "B_IDIOMATIC_PINNED_PYOPTIX",
    "C_STRONG_DEVICE_CONTINUATION_PYOPTIX",
    "D_DIRECT_CUDA_OPTIX",
    "E_FROZEN_RTDL_CONTROL",
)
BLOCKS = 8
STEADY_REPETITIONS = 128
INSTRUMENTATION_REPLICATES = 16
SOURCE_LABEL_M = "M_MEASURED_SUCCESSOR"
SOURCE_LABEL_E = "E_FROZEN_PREDECESSOR"

OUTPUT_SHA256 = {
    "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1": (
        "2df49102543561c678ce39e05cc6c79ce92c0ea919ad45134d53d19bb67174ef"
    ),
    "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1": (
        "2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77"
    ),
}

PARTITION_KEYS = (
    "canonical_input_construction",
    "signed_deployment_install",
    "parallel_artifact_and_provider_admission",
    "provider_artifact_bind_wait",
    "static_input_deployment",
    "dynamic_input_deployment",
    "native_prepare",
    "first_complete_execution",
    "public_output_validation",
    "unattributed_control_plane",
)

COMPONENT_KEYS = (
    "trust_root_and_package_discovery",
    "artifact_metadata_decode",
    "artifact_bytes_read_and_hash",
    "authority_bytes_read_and_hash",
    "rsa_verification",
    "native_image_read_and_hash",
    "native_dso_load_and_symbol_binding",
    "cuda_primary_context",
    "optix_module_program_pipeline_sbt",
    "provider_unexplained_wait",
    "static_input_validation_and_allocation",
    "dynamic_input_validation_and_allocation",
    "host_to_device_transfer",
    "gas_build_or_reuse",
)

EXPECTED_CONTRACT = {
    "arm_order": list(ARMS),
    "block_count": BLOCKS,
    "generation_order": list(GENERATIONS),
    "instrumentation": {
        "arm": "A_RTDL_AOT_PUBLIC",
        "blocks": 8,
        "gate_type": "registered_qualification",
        "limit_ppm": 50000,
        "modes": ["off", "on"],
        "replicates_per_mode_per_block": INSTRUMENTATION_REPLICATES,
    },
    "ratio_orientation": "NUMERATOR_OVER_DENOMINATOR__LOWER_FAVORS_NUMERATOR",
    "registered_gates": {
        "a_over_c_implementation_entry": {
            "gate_type": "registered_primary",
            "max_block_ppm": 1350000,
            "median_ppm": 1200000,
        },
        "a_over_d_prepared_steady": {
            "gate_type": "registered_primary",
            "max_block_ppm": None,
            "median_ppm": 1200000,
        },
        "a_over_e_prepared_steady": {
            "gate_type": "registered_regression_control",
            "max_block_ppm": None,
            "median_ppm": 1050000,
        },
        "c_over_b_prepared_steady": {
            "gate_type": "registered_baseline_competence",
            "max_block_ppm": None,
            "median_ppm": 1050000,
        },
    },
    "samples_per_formal_cell": STEADY_REPETITIONS,
    "source_policy": {
        "A_RTDL_AOT_PUBLIC": SOURCE_LABEL_M,
        "B_IDIOMATIC_PINNED_PYOPTIX": SOURCE_LABEL_M,
        "C_STRONG_DEVICE_CONTINUATION_PYOPTIX": SOURCE_LABEL_M,
        "D_DIRECT_CUDA_OPTIX": SOURCE_LABEL_M,
        "E_FROZEN_RTDL_CONTROL": SOURCE_LABEL_E,
    },
    "task_order": list(TASKS),
    "ungated_diagnostics": [
        "a_over_c_post_import",
        "a_over_e_post_import",
        "a_over_e_implementation_entry",
        "lifecycle_component_medians",
    ],
}

EXPECTED_METRICS = {
    ("G0_ADA", TASKS[1]): {
        "ad_median_ppm": 1175066,
        "ad_max_ppm": 1211025,
        "ac_entry_median_ppm": 642180,
        "ac_post_median_ppm": 1559788,
        "ac_post_min_ppm": 1527058,
        "ac_post_max_ppm": 1639385,
        "ae_steady_median_ppm": 903016,
        "ae_post_median_ppm": 1169262,
        "ae_entry_median_ppm": 1079554,
        "cb_steady_median_ppm": 602851,
    },
    ("G0_ADA", TASKS[0]): {
        "ad_median_ppm": 1076852,
        "ad_max_ppm": 1092253,
        "ac_entry_median_ppm": 653826,
        "ac_post_median_ppm": 1749327,
        "ac_post_min_ppm": 1724948,
        "ac_post_max_ppm": 1865823,
        "ae_steady_median_ppm": 584438,
        "ae_post_median_ppm": 1305383,
        "ae_entry_median_ppm": 1192358,
        "cb_steady_median_ppm": 220775,
    },
    ("G1_AMPERE", TASKS[1]): {
        "ad_median_ppm": 1133636,
        "ad_max_ppm": 1142675,
        "ac_entry_median_ppm": 618362,
        "ac_post_median_ppm": 1637468,
        "ac_post_min_ppm": 1608213,
        "ac_post_max_ppm": 1652853,
        "ae_steady_median_ppm": 922388,
        "ae_post_median_ppm": 1162775,
        "ae_entry_median_ppm": 1137637,
        "cb_steady_median_ppm": 654279,
    },
    ("G1_AMPERE", TASKS[0]): {
        "ad_median_ppm": 1094795,
        "ad_max_ppm": 1118811,
        "ac_entry_median_ppm": 681393,
        "ac_post_median_ppm": 1837415,
        "ac_post_min_ppm": 1815733,
        "ac_post_max_ppm": 2377129,
        "ae_steady_median_ppm": 608228,
        "ae_post_median_ppm": 1261676,
        "ae_entry_median_ppm": 1216714,
        "cb_steady_median_ppm": 226921,
    },
}

EXPECTED_LIFECYCLE_MEDIANS = {
    ("G0_ADA", TASKS[1], "A_RTDL_AOT_PUBLIC"): (76945387, 449360871, 526017079),
    ("G0_ADA", TASKS[1], "C_STRONG_DEVICE_CONTINUATION_PYOPTIX"): (529643869, 287443064, 817456190),
    ("G0_ADA", TASKS[0], "A_RTDL_AOT_PUBLIC"): (77533247, 455176354, 532028248),
    ("G0_ADA", TASKS[0], "C_STRONG_DEVICE_CONTINUATION_PYOPTIX"): (577765364, 261400088, 841974925),
    ("G1_AMPERE", TASKS[1], "A_RTDL_AOT_PUBLIC"): (80106317, 370675186, 451894144),
    ("G1_AMPERE", TASKS[1], "C_STRONG_DEVICE_CONTINUATION_PYOPTIX"): (502762916, 226534499, 729125644),
    ("G1_AMPERE", TASKS[0], "A_RTDL_AOT_PUBLIC"): (81205542, 379391600, 460452378),
    ("G1_AMPERE", TASKS[0], "C_STRONG_DEVICE_CONTINUATION_PYOPTIX"): (467040680, 206312319, 673359247),
}

EXPECTED_INSTRUMENTATION_OVERHEAD_PPM = {
    ("G0_ADA", TASKS[1]): 2349,
    ("G0_ADA", TASKS[0]): 2781,
    ("G1_AMPERE", TASKS[1]): 0,
    ("G1_AMPERE", TASKS[0]): 2431,
}

EXPECTED_AOT = {
    ("G0_ADA", TASKS[1]): (76826501, 20166),
    ("G0_ADA", TASKS[0]): (78176935, 11171),
    ("G1_AMPERE", TASKS[1]): (58513283, 19626),
    ("G1_AMPERE", TASKS[0]): (58279761, 10431),
}

REQUIRED_PUBLIC_FILES = {
    "CLAIM_SCOPE.md",
    "DEPENDENCIES.md",
    "EXPECTED_RESULTS.md",
    "README.md",
    "REPLAY_MATRIX.md",
    "data/performance_projection.json",
    "data/recount_summary.json",
    "verify.py",
}

FORBIDDEN_PUBLIC_BYTES = (
    b"/" + b"Users/",
    b"/" + b"workspace/",
    b"\\" + b"Users\\",
    b"root" + b"@",
    b"rl" + b"2025",
    b"history/" + b"internal_docs",
    b"GPU" + b"-",
    b"ssh." + b"runpod.io",
)
FORBIDDEN_PUBLIC_PATTERNS = (re.compile(rb"(?i)goal[0-9]+"),)


class VerificationError(ValueError):
    """The artifact is malformed, incomplete, or outside the frozen scope."""


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def digest(value: object) -> str:
    return digest_bytes(canonical_bytes(value))


def strict_json_bytes(payload: bytes, *, label: str) -> object:
    def object_from_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise VerificationError(f"{label}: duplicate JSON key {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> object:
        raise VerificationError(f"{label}: non-finite JSON value {value}")

    try:
        return json.loads(
            payload,
            object_pairs_hook=object_from_pairs,
            parse_constant=reject_constant,
        )
    except VerificationError:
        raise
    except (UnicodeError, json.JSONDecodeError) as error:
        raise VerificationError(f"{label}: not strict JSON") from error


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def integer_median(values: Sequence[int]) -> int:
    require(bool(values), "median requires at least one value")
    require(
        all(type(value) is int for value in values),
        "median values must be exact integers",
    )
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) // 2


def ratio_ppm(numerator: int, denominator: int) -> int:
    require(type(numerator) is int and numerator >= 0, "invalid ratio numerator")
    require(type(denominator) is int and denominator > 0, "invalid ratio denominator")
    return (numerator * 1_000_000 + denominator // 2) // denominator


def _validate_sha256(value: object, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value),
        f"{label}: invalid SHA-256",
    )
    return value


def _validate_row_seal(row: Mapping[str, object], label: str) -> None:
    body = dict(row)
    seal = body.pop("row_sha256", None)
    _validate_sha256(seal, f"{label}.row_sha256")
    require(seal == digest(body), f"{label}: row seal differs")


def _expected_cell_id(generation: str, block: int, task: str, arm: str) -> str:
    return (
        f"{generation}-B{block:02d}-T{TASKS.index(task)}-A{ARMS.index(arm)}"
    )


def _validate_lifecycle(value: object, *, direct: bool, label: str) -> None:
    if direct:
        require(value is None, f"{label}: Direct must not invent Python lifecycle")
        return
    require(isinstance(value, Mapping), f"{label}: lifecycle is absent")
    expected = {
        "component_diagnostics_ns",
        "endpoint_partition_ns",
        "implementation_entry_to_first_correct_result_ns",
        "implementation_import_ns",
        "implementation_import_to_endpoint_gap_ns",
        "post_import_to_first_correct_result_ns",
    }
    require(set(value) == expected, f"{label}: lifecycle fields differ")
    import_ns = value["implementation_import_ns"]
    gap_ns = value["implementation_import_to_endpoint_gap_ns"]
    post_ns = value["post_import_to_first_correct_result_ns"]
    entry_ns = value["implementation_entry_to_first_correct_result_ns"]
    require(type(import_ns) is int and import_ns > 0, f"{label}: invalid import")
    require(type(gap_ns) is int and gap_ns >= 0, f"{label}: invalid gap")
    require(type(post_ns) is int and post_ns > 0, f"{label}: invalid post-import")
    require(type(entry_ns) is int and entry_ns > 0, f"{label}: invalid entry")
    require(entry_ns == import_ns + gap_ns + post_ns, f"{label}: lifecycle does not reconcile")
    partition = value["endpoint_partition_ns"]
    require(isinstance(partition, Mapping), f"{label}: partition is absent")
    require(set(partition) == set(PARTITION_KEYS), f"{label}: partition fields differ")
    require(
        all(type(partition[key]) is int and partition[key] >= 0 for key in PARTITION_KEYS),
        f"{label}: invalid partition duration",
    )
    require(sum(partition.values()) == post_ns, f"{label}: partition total differs")
    components = value["component_diagnostics_ns"]
    require(isinstance(components, Mapping), f"{label}: component diagnostics absent")
    require(set(components) == set(COMPONENT_KEYS), f"{label}: component fields differ")
    require(
        all(
            components[key] is None
            or (type(components[key]) is int and components[key] >= 0)
            for key in COMPONENT_KEYS
        ),
        f"{label}: invalid component duration",
    )


def _validate_formal_rows(projection: Mapping[str, object]) -> dict[tuple[str, int, str, str], Mapping[str, object]]:
    rows = projection.get("formal_workers")
    require(isinstance(rows, list), "formal_workers must be a list")
    require(len(rows) == 160, "formal worker count differs")
    index: dict[tuple[str, int, str, str], Mapping[str, object]] = {}
    required = {
        "arm",
        "block",
        "cell_id",
        "generation",
        "lifecycle",
        "oracle_exact",
        "output_sha256",
        "phase_instrumentation",
        "row_sha256",
        "source_label",
        "steady_median_ns",
        "steady_samples_ns",
        "steady_samples_sha256",
        "task",
    }
    for position, row in enumerate(rows):
        label = f"formal_workers[{position}]"
        require(isinstance(row, Mapping), f"{label}: row must be an object")
        require(set(row) == required, f"{label}: fields differ")
        _validate_row_seal(row, label)
        generation = row["generation"]
        task = row["task"]
        arm = row["arm"]
        block = row["block"]
        require(generation in GENERATIONS, f"{label}: generation differs")
        require(task in TASKS, f"{label}: task differs")
        require(arm in ARMS, f"{label}: arm differs")
        require(type(block) is int and 0 <= block < BLOCKS, f"{label}: block differs")
        key = (generation, block, task, arm)
        require(key not in index, f"{label}: duplicate schedule cell")
        require(row["cell_id"] == _expected_cell_id(*key), f"{label}: cell ID differs")
        expected_source = SOURCE_LABEL_E if arm == ARMS[4] else SOURCE_LABEL_M
        require(row["source_label"] == expected_source, f"{label}: source identity differs")
        samples = row["steady_samples_ns"]
        require(isinstance(samples, list), f"{label}: samples must be a list")
        require(len(samples) == STEADY_REPETITIONS, f"{label}: sample count differs")
        require(
            all(type(value) is int and value > 0 for value in samples),
            f"{label}: invalid sample",
        )
        require(
            row["steady_samples_sha256"] == digest(samples),
            f"{label}: sample digest differs",
        )
        require(
            row["steady_median_ns"] == integer_median(samples),
            f"{label}: worker median differs",
        )
        require(row["oracle_exact"] is True, f"{label}: output oracle not exact")
        require(row["output_sha256"] == OUTPUT_SHA256[task], f"{label}: output digest differs")
        expected_instrumentation = None if arm == ARMS[3] else True
        require(
            row["phase_instrumentation"] is expected_instrumentation,
            f"{label}: phase instrumentation differs",
        )
        _validate_lifecycle(row["lifecycle"], direct=arm == ARMS[3], label=label)
        index[key] = row
    expected_keys = {
        (generation, block, task, arm)
        for generation in GENERATIONS
        for block in range(BLOCKS)
        for task in TASKS
        for arm in ARMS
    }
    require(set(index) == expected_keys, "formal schedule is incomplete")
    return index


def _validate_instrumentation_rows(projection: Mapping[str, object]) -> dict[tuple[str, str, int, str, int], int]:
    rows = projection.get("instrumentation_workers")
    require(isinstance(rows, list), "instrumentation_workers must be a list")
    require(len(rows) == 1024, "instrumentation worker count differs")
    index: dict[tuple[str, str, int, str, int], int] = {}
    required = {
        "block", "endpoint_ns", "generation", "mode", "replicate",
        "row_sha256", "source_label", "task",
    }
    for position, row in enumerate(rows):
        label = f"instrumentation_workers[{position}]"
        require(isinstance(row, Mapping), f"{label}: row must be an object")
        require(set(row) == required, f"{label}: fields differ")
        _validate_row_seal(row, label)
        key = (row["generation"], row["task"], row["block"], row["mode"], row["replicate"])
        require(key[0] in GENERATIONS and key[1] in TASKS, f"{label}: identity differs")
        require(type(key[2]) is int and 0 <= key[2] < BLOCKS, f"{label}: block differs")
        require(key[3] in ("off", "on"), f"{label}: mode differs")
        require(type(key[4]) is int and 0 <= key[4] < INSTRUMENTATION_REPLICATES, f"{label}: replicate differs")
        require(key not in index, f"{label}: duplicate instrumentation cell")
        require(row["source_label"] == SOURCE_LABEL_M, f"{label}: source differs")
        endpoint = row["endpoint_ns"]
        require(type(endpoint) is int and endpoint > 0, f"{label}: endpoint differs")
        index[key] = endpoint
    expected = {
        (generation, task, block, mode, replicate)
        for generation in GENERATIONS
        for task in TASKS
        for block in range(BLOCKS)
        for mode in ("off", "on")
        for replicate in range(INSTRUMENTATION_REPLICATES)
    }
    require(set(index) == expected, "instrumentation schedule is incomplete")
    return index


def _validate_aot_rows(projection: Mapping[str, object]) -> dict[tuple[str, str], Mapping[str, object]]:
    rows = projection.get("aot_qualification")
    require(isinstance(rows, list) and len(rows) == 4, "AOT row count differs")
    index: dict[tuple[str, str], Mapping[str, object]] = {}
    required = {
        "cold_first_resolution_ns", "durations_ns", "generation",
        "row_sha256", "source_label", "task",
    }
    for position, row in enumerate(rows):
        label = f"aot_qualification[{position}]"
        require(isinstance(row, Mapping) and set(row) == required, f"{label}: fields differ")
        _validate_row_seal(row, label)
        key = (row["generation"], row["task"])
        require(key[0] in GENERATIONS and key[1] in TASKS, f"{label}: identity differs")
        require(key not in index, f"{label}: duplicate row")
        require(row["source_label"] == SOURCE_LABEL_M, f"{label}: source differs")
        durations = row["durations_ns"]
        require(
            isinstance(durations, list)
            and len(durations) == 5
            and all(type(value) is int and value > 0 for value in durations),
            f"{label}: durations differ",
        )
        require(
            type(row["cold_first_resolution_ns"]) is int
            and row["cold_first_resolution_ns"] > 0,
            f"{label}: cold denominator differs",
        )
        index[key] = row
    require(set(index) == set(EXPECTED_AOT), "AOT schedule is incomplete")
    return index


def _validate_competence_rows(projection: Mapping[str, object]) -> dict[tuple[str, str, str], Mapping[str, object]]:
    rows = projection.get("nonformal_competence_workers")
    require(isinstance(rows, list) and len(rows) == 8, "competence worker count differs")
    index: dict[tuple[str, str, str], Mapping[str, object]] = {}
    required = {
        "arm", "generation", "row_sha256", "source_label",
        "steady_median_ns", "steady_samples_ns", "steady_samples_sha256", "task",
    }
    for position, row in enumerate(rows):
        label = f"nonformal_competence_workers[{position}]"
        require(isinstance(row, Mapping) and set(row) == required, f"{label}: fields differ")
        _validate_row_seal(row, label)
        key = (row["generation"], row["task"], row["arm"])
        require(key[0] in GENERATIONS and key[1] in TASKS, f"{label}: identity differs")
        require(key[2] in (ARMS[1], ARMS[2]), f"{label}: arm differs")
        require(key not in index, f"{label}: duplicate row")
        require(row["source_label"] == SOURCE_LABEL_M, f"{label}: source differs")
        samples = row["steady_samples_ns"]
        require(
            isinstance(samples, list)
            and len(samples) == STEADY_REPETITIONS
            and all(type(value) is int and value > 0 for value in samples),
            f"{label}: samples differ",
        )
        require(row["steady_samples_sha256"] == digest(samples), f"{label}: sample digest differs")
        require(row["steady_median_ns"] == integer_median(samples), f"{label}: median differs")
        index[key] = row
    expected = {
        (generation, task, arm)
        for generation in GENERATIONS
        for task in TASKS
        for arm in (ARMS[1], ARMS[2])
    }
    require(set(index) == expected, "competence schedule is incomplete")
    return index


def validate_projection(
    projection: object,
    *,
    expected_projection_sha256: str | None = EXPECTED_PROJECTION_SHA256,
) -> dict[str, object]:
    require(isinstance(projection, Mapping), "projection must be an object")
    expected_fields = {
        "aot_qualification",
        "claim_boundary",
        "contract",
        "formal_workers",
        "instrumentation_workers",
        "nonformal_competence_workers",
        "projection_sha256",
        "schema",
    }
    require(set(projection) == expected_fields, "projection fields differ")
    body = dict(projection)
    seal = body.pop("projection_sha256", None)
    _validate_sha256(seal, "projection_sha256")
    require(seal == digest(body), "projection self-seal differs")
    if expected_projection_sha256 is not None:
        _validate_sha256(expected_projection_sha256, "frozen expected projection")
        require(seal == expected_projection_sha256, "projection identity differs from frozen verifier")
    require(projection["schema"] == PROJECTION_SCHEMA, "projection schema differs")
    require(projection["contract"] == EXPECTED_CONTRACT, "projection contract or gate type differs")
    require(
        projection["claim_boundary"] == {
            "cross_machine_raw_time_ratio_computed": False,
            "external_review_complete": False,
            "offline_recount_is_gpu_execution": False,
            "original_per_execution_receipt_requirement_fulfilled": False,
            "public_or_manuscript_claim_authorized": False,
        },
        "projection claim boundary differs",
    )
    formal = _validate_formal_rows(projection)
    instrumentation = _validate_instrumentation_rows(projection)
    aot = _validate_aot_rows(projection)
    competence = _validate_competence_rows(projection)
    return {
        "formal": formal,
        "instrumentation": instrumentation,
        "aot": aot,
        "competence": competence,
        "projection_sha256": seal,
    }


def _formal_metric(row: Mapping[str, object], metric: str) -> int:
    if metric == "steady":
        return int(row["steady_median_ns"])
    lifecycle = row["lifecycle"]
    require(isinstance(lifecycle, Mapping), "requested lifecycle metric is absent")
    if metric == "entry":
        return int(lifecycle["implementation_entry_to_first_correct_result_ns"])
    if metric == "post_import":
        return int(lifecycle["post_import_to_first_correct_result_ns"])
    raise VerificationError(f"unknown metric: {metric}")


def build_summary(projection: object, *, expected_projection_sha256: str | None = EXPECTED_PROJECTION_SHA256) -> dict[str, object]:
    validated = validate_projection(
        projection, expected_projection_sha256=expected_projection_sha256
    )
    formal = validated["formal"]
    rows = []
    lifecycle_rows = []

    def block_ratios(
        generation: str,
        task: str,
        numerator: str,
        denominator: str,
        metric: str,
    ) -> list[int]:
        return [
            ratio_ppm(
                _formal_metric(
                    formal[(generation, block, task, numerator)], metric
                ),
                _formal_metric(
                    formal[(generation, block, task, denominator)], metric
                ),
            )
            for block in range(BLOCKS)
        ]

    for generation in GENERATIONS:
        for task in TASKS:
            ad = block_ratios(generation, task, ARMS[0], ARMS[3], "steady")
            ac_entry = block_ratios(generation, task, ARMS[0], ARMS[2], "entry")
            ac_post = block_ratios(
                generation, task, ARMS[0], ARMS[2], "post_import"
            )
            ae_steady = block_ratios(generation, task, ARMS[0], ARMS[4], "steady")
            ae_entry = block_ratios(generation, task, ARMS[0], ARMS[4], "entry")
            ae_post = block_ratios(
                generation, task, ARMS[0], ARMS[4], "post_import"
            )
            cb = block_ratios(generation, task, ARMS[2], ARMS[1], "steady")
            row = {
                "generation": generation,
                "task": task,
                "a_over_d_steady_ppm_by_block": ad,
                "a_over_d_steady_median_ppm": integer_median(ad),
                "a_over_d_steady_max_ppm": max(ad),
                "a_over_c_entry_ppm_by_block": ac_entry,
                "a_over_c_entry_median_ppm": integer_median(ac_entry),
                "a_over_c_entry_max_ppm": max(ac_entry),
                "a_over_c_post_import_ppm_by_block": ac_post,
                "a_over_c_post_import_median_ppm": integer_median(ac_post),
                "a_over_c_post_import_min_ppm": min(ac_post),
                "a_over_c_post_import_max_ppm": max(ac_post),
                "a_over_e_steady_ppm_by_block": ae_steady,
                "a_over_e_steady_median_ppm": integer_median(ae_steady),
                "a_over_e_entry_ppm_by_block": ae_entry,
                "a_over_e_entry_median_ppm": integer_median(ae_entry),
                "a_over_e_post_import_ppm_by_block": ae_post,
                "a_over_e_post_import_median_ppm": integer_median(ae_post),
                "c_over_b_steady_ppm_by_block": cb,
                "c_over_b_steady_median_ppm": integer_median(cb),
            }
            expected = EXPECTED_METRICS[(generation, task)]
            observed = {
                "ad_median_ppm": row["a_over_d_steady_median_ppm"],
                "ad_max_ppm": row["a_over_d_steady_max_ppm"],
                "ac_entry_median_ppm": row["a_over_c_entry_median_ppm"],
                "ac_post_median_ppm": row["a_over_c_post_import_median_ppm"],
                "ac_post_min_ppm": row["a_over_c_post_import_min_ppm"],
                "ac_post_max_ppm": row["a_over_c_post_import_max_ppm"],
                "ae_steady_median_ppm": row["a_over_e_steady_median_ppm"],
                "ae_post_median_ppm": row["a_over_e_post_import_median_ppm"],
                "ae_entry_median_ppm": row["a_over_e_entry_median_ppm"],
                "cb_steady_median_ppm": row["c_over_b_steady_median_ppm"],
            }
            require(
                observed == expected,
                f"frozen numerical oracle differs: {generation}/{task}: "
                f"observed={observed!r} expected={expected!r}",
            )
            rows.append(row)
            for arm in (ARMS[0], ARMS[2]):
                values = [formal[(generation, block, task, arm)]["lifecycle"] for block in range(BLOCKS)]
                require(all(isinstance(value, Mapping) for value in values), "lifecycle row absent")
                import_ns = integer_median([value["implementation_import_ns"] for value in values])
                gap_ns = integer_median([value["implementation_import_to_endpoint_gap_ns"] for value in values])
                post_ns = integer_median([value["post_import_to_first_correct_result_ns"] for value in values])
                entry_ns = integer_median([value["implementation_entry_to_first_correct_result_ns"] for value in values])
                expected_lifecycle = EXPECTED_LIFECYCLE_MEDIANS[(generation, task, arm)]
                require((import_ns, post_ns, entry_ns) == expected_lifecycle, f"lifecycle median oracle differs: {generation}/{task}/{arm}")
                lifecycle_rows.append({
                    "generation": generation,
                    "task": task,
                    "arm": arm,
                    "implementation_import_median_ns": import_ns,
                    "implementation_gap_median_ns": gap_ns,
                    "post_import_median_ns": post_ns,
                    "implementation_entry_median_ns": entry_ns,
                    "import_over_entry_ppm": ratio_ppm(import_ns, entry_ns),
                    "median_components_are_not_additive": True,
                })

    instrumentation_rows = []
    inst = validated["instrumentation"]
    for generation in GENERATIONS:
        for task in TASKS:
            ratios = []
            blocks = []
            for block in range(BLOCKS):
                off = [inst[(generation, task, block, "off", replicate)] for replicate in range(INSTRUMENTATION_REPLICATES)]
                on = [inst[(generation, task, block, "on", replicate)] for replicate in range(INSTRUMENTATION_REPLICATES)]
                off_median = integer_median(off)
                on_median = integer_median(on)
                value = ratio_ppm(on_median, off_median)
                ratios.append(value)
                blocks.append({
                    "block": block,
                    "off_endpoint_ns_by_replicate": off,
                    "on_endpoint_ns_by_replicate": on,
                    "off_endpoint_median_ns": off_median,
                    "on_endpoint_median_ns": on_median,
                    "on_over_off_ppm": value,
                })
            paired_median = integer_median(ratios)
            overhead = max(0, paired_median - 1_000_000)
            require(overhead == EXPECTED_INSTRUMENTATION_OVERHEAD_PPM[(generation, task)], f"instrumentation oracle differs: {generation}/{task}")
            instrumentation_rows.append({
                "generation": generation,
                "task": task,
                "arm": ARMS[0],
                "worker_count": 256,
                "blocks": blocks,
                "paired_on_over_off_median_ppm": paired_median,
                "instrumentation_overhead_ppm": overhead,
                "limit_ppm": 50000,
                "pass": overhead <= 50000,
            })

    aot_rows = []
    for generation in GENERATIONS:
        for task in TASKS:
            row = validated["aot"][(generation, task)]
            median_ns = integer_median(row["durations_ns"])
            ratio = ratio_ppm(median_ns, row["cold_first_resolution_ns"])
            require((median_ns, ratio) == EXPECTED_AOT[(generation, task)], f"AOT oracle differs: {generation}/{task}")
            aot_rows.append({
                "generation": generation,
                "task": task,
                "fresh_process_hit_durations_ns": row["durations_ns"],
                "fresh_process_hit_median_ns": median_ns,
                "cold_first_resolution_ns": row["cold_first_resolution_ns"],
                "fresh_process_hit_over_cold_ppm": ratio,
                "absolute_limit_ns": 1000000000,
                "relative_limit_ppm": 100000,
                "pass": median_ns <= 1000000000 and ratio <= 100000,
            })

    competence_rows = []
    competence = validated["competence"]
    for generation in GENERATIONS:
        for task in TASKS:
            weak = competence[(generation, task, ARMS[1])]["steady_median_ns"]
            strong = competence[(generation, task, ARMS[2])]["steady_median_ns"]
            competence_rows.append({
                "generation": generation,
                "task": task,
                "strong_median_ns": strong,
                "idiomatic_median_ns": weak,
                "strong_over_idiomatic_ppm": ratio_ppm(strong, weak),
                "limit_ppm": 1050000,
                "pass": ratio_ppm(strong, weak) <= 1050000,
                "scope": "nonformal_preflight_competence_only",
            })

    body: dict[str, object] = {
        "schema": SUMMARY_SCHEMA,
        "projection_sha256": validated["projection_sha256"],
        "formal_worker_count": 160,
        "formal_steady_sample_count": 20480,
        "formal_worker_median_recount_count": 160,
        "performance_rows": rows,
        "lifecycle_decomposition_rows": lifecycle_rows,
        "instrumentation_rows": instrumentation_rows,
        "aot_rows": aot_rows,
        "nonformal_competence_rows": competence_rows,
        "claim_boundary": {
            "a_over_d_worst_block_is_descriptive_not_gated": True,
            "a_over_e_first_result_is_post_hoc_non_gating": True,
            "cross_machine_raw_time_ratio_computed": False,
            "implementation_entry_positive_performance_claim_allowed": False,
            "post_import_is_adverse_diagnostic": True,
            "public_or_manuscript_claim_authorized": False,
        },
    }
    return {**body, "summary_sha256": digest(body)}


def verify_artifact(root: Path, *, expected_projection_sha256: str | None = EXPECTED_PROJECTION_SHA256) -> dict[str, object]:
    root = root.resolve()
    manifest_path = root / "manifest.json"
    require(manifest_path.is_file() and not manifest_path.is_symlink(), "manifest is absent or symlinked")
    manifest_raw = manifest_path.read_bytes()
    manifest = strict_json_bytes(manifest_raw, label="manifest.json")
    require(isinstance(manifest, Mapping), "manifest must be an object")
    require(set(manifest) == {"file_count", "files", "manifest_sha256", "payload_bytes", "schema"}, "manifest fields differ")
    body = dict(manifest)
    seal = body.pop("manifest_sha256", None)
    _validate_sha256(seal, "manifest_sha256")
    require(seal == digest(body), "manifest self-seal differs")
    require(manifest["schema"] == MANIFEST_SCHEMA, "manifest schema differs")
    files = manifest["files"]
    require(isinstance(files, list), "manifest files must be a list")
    require(len(files) == manifest["file_count"], "manifest file count differs")
    require(sum(row.get("bytes", -1) for row in files if isinstance(row, Mapping)) == manifest["payload_bytes"], "manifest payload bytes differ")
    listed: dict[str, Mapping[str, object]] = {}
    for position, row in enumerate(files):
        require(isinstance(row, Mapping) and set(row) == {"bytes", "path", "sha256"}, f"manifest row {position} differs")
        relative = PurePosixPath(row["path"])
        require(not relative.is_absolute() and ".." not in relative.parts and relative.as_posix() != "manifest.json", f"manifest row {position} path differs")
        name = relative.as_posix()
        require(name not in listed, f"duplicate manifest path: {name}")
        require(type(row["bytes"]) is int and row["bytes"] >= 0, f"manifest row {position} byte count differs")
        _validate_sha256(row["sha256"], f"manifest row {position}")
        listed[name] = row
    require(set(listed) == REQUIRED_PUBLIC_FILES, "public artifact member set differs")
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    require(actual == set(listed) | {"manifest.json"}, "unexpected, missing, or symlinked artifact member")
    for name, row in listed.items():
        path = root.joinpath(*PurePosixPath(name).parts)
        require(path.is_file() and not path.is_symlink(), f"invalid artifact member: {name}")
        payload = path.read_bytes()
        require(len(payload) == row["bytes"], f"artifact byte count differs: {name}")
        require(digest_bytes(payload) == row["sha256"], f"artifact hash differs: {name}")
        for forbidden in FORBIDDEN_PUBLIC_BYTES:
            require(forbidden not in payload, f"identity leakage in {name}")
        for forbidden in FORBIDDEN_PUBLIC_PATTERNS:
            require(forbidden.search(payload) is None, f"identity pattern leakage in {name}")
    projection_raw = (root / "data" / "performance_projection.json").read_bytes()
    projection = strict_json_bytes(projection_raw, label="performance_projection.json")
    summary = build_summary(projection, expected_projection_sha256=expected_projection_sha256)
    stored_summary = strict_json_bytes((root / "data" / "recount_summary.json").read_bytes(), label="recount_summary.json")
    require(stored_summary == summary, "stored recount summary differs from independent replay")
    return {
        "status": "PASS__OFFLINE_PROJECTION_RECOUNT",
        "manifest_sha256": seal,
        "projection_sha256": summary["projection_sha256"],
        "summary_sha256": summary["summary_sha256"],
        "formal_worker_count": summary["formal_worker_count"],
        "formal_steady_sample_count": summary["formal_steady_sample_count"],
        "instrumentation_worker_count": 1024,
        "aot_qualification_count": 20,
        "nonformal_competence_worker_count": 8,
        "gpu_execution_performed": False,
        "project_import_performed": False,
        "public_or_manuscript_claim_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    try:
        receipt = verify_artifact(args.artifact_root)
    except (OSError, VerificationError, TypeError, ValueError) as error:
        print(json.dumps({"status": "REJECT", "error": str(error)}, sort_keys=True))
        return 1
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
