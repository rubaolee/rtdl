#!/usr/bin/env python3
"""Independent stdlib-only recount of the Goal5801-G A3 Home evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
from typing import Any


SOURCE_COMMIT = "60904636748e649e874b6a2f7ca1afbea5298455"
SOURCE_TREE = "c3f1bc9c5426d9c3abf55fd091e84bc7394e0f8c"
SOURCE_ARCHIVE_SHA256 = (
    "a21a484319ff7e53da4daeb297d6ec8e12a613aee76406e26bd615c91f253a00"
)
SOURCE_ARCHIVE_BYTES = 15_523_840
SOURCE_ARCHIVE_MEMBERS = 346
NATIVE_SHA256 = "3a5efb26069d0da55f373ce7f9f4338be35e378a7086ccc64ad239bf98cee905"
NATIVE_BYTES = 6_317_384
RESULT_SHA256 = "679ab482374103a5524ab1e8019a731891c0ebf1e77e67ec26726671c1b30baa"
RUNTIME_RAW_SHA256 = (
    "31e1dac7e48b5e2c413cab4717975fb07b9b77559ab8894b7d9dc35750fc7e76"
)
RUNTIME_TEXT_SHA256 = (
    "fec6a74f3a9645fc8f6457eacd286d4e6f6143d11283612029460f78363fd81f"
)
BUNDLE = "v4_builtin_triangle_callback_ir_four_role_composed"
EXPECTED_PTX = {
    "baseline_primitive_identity": (
        "result_baseline.ptx",
        64_121,
        "e855b6a6cd3cce1afd64943533bff93c802da42a211d724fcd81c8e8c4f742e1",
    ),
    "fresh_leaf_reads_argument_2_bound_to_front_values": (
        "result_normal_metadata.ptx",
        64_621,
        "1149f5cdf18f0766672baf9aa085aa3c8a68125dc82d7147f7931a095893d9f1",
    ),
    "same_leaf_argument_2_rebound_to_back_values": (
        "result_swapped_metadata.ptx",
        64_625,
        "8ee5437c272be91c3a94d08f73378bd635af2e937a3057ab5e2aaad429b73ae5",
    ),
}
EXPECTED_OUTPUTS = {
    "baseline_primitive_identity": [
        [0, 1, 0xA11CE001],
        [1, 1, 0xA11CE001],
        [0xFFFFFFFF, 0, 0xA11CE000],
    ],
    "fresh_leaf_reads_argument_2_bound_to_front_values": [
        [17, 1, 0xA11CE001],
        [29, 1, 0xA11CE001],
        [0xFFFFFFFF, 0, 0xA11CE000],
    ],
    "same_leaf_argument_2_rebound_to_back_values": [
        [31, 1, 0xA11CE001],
        [43, 1, 0xA11CE001],
        [0xFFFFFFFF, 0, 0xA11CE000],
    ],
}


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=True,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path: Path) -> tuple[int, str]:
    body = path.read_bytes()
    return len(body), hashlib.sha256(body).hexdigest()


def fnv1a64(text: str) -> int:
    value = 1469598103934665603
    for byte in text.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & ((1 << 64) - 1)
    return value


def native_mix(state: int, value: int) -> int:
    mask = (1 << 64) - 1
    state &= mask
    value = (value + 0x9E3779B97F4A7C15) & mask
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & mask
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & mask
    value = (value ^ (value >> 31)) & mask
    return (
        state
        ^ (
            value
            + 0x9E3779B97F4A7C15
            + ((state << 6) & mask)
            + (state >> 2)
        )
    ) & mask


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.evidence_root.resolve()
    output = args.output.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)

    checks: list[str] = []

    def require(name: str, condition: bool) -> None:
        if not condition:
            raise RuntimeError(f"independent check failed: {name}")
        checks.append(name)

    evidence_dir = root / "evidence"
    result_path = evidence_dir / "result.json"
    source_path = root / "source.tar"
    native_path = root / "librtdl_optix.so"
    require("result_exact_file", file_digest(result_path) == (25_088, RESULT_SHA256))
    require(
        "source_archive_exact_file",
        file_digest(source_path) == (SOURCE_ARCHIVE_BYTES, SOURCE_ARCHIVE_SHA256),
    )
    require(
        "native_exact_file", file_digest(native_path) == (NATIVE_BYTES, NATIVE_SHA256))
    require("exit_code_zero", (evidence_dir / "exit_code.txt").read_bytes() == b"0\n")

    result = json.loads(result_path.read_text(encoding="utf-8"))
    outer_body = dict(result)
    outer_seal = outer_body.pop("receipt_sha256")
    require("outer_evidence_seal", digest(outer_body) == outer_seal)
    require("schema", result["schema"] == "rtdl.goal5801_g.public_triangle_home_kat.v2")
    require(
        "status",
        result["status"] == "PASS__ORACLE_ISOLATED_REHASHABLE_HOME_EXECUTION",
    )
    require(
        "oracle_output_absent_from_execute",
        result["oracle_output_or_expected_value_passed_into_execute"] is False
        and result["oracle_compared_only_after_public_execute_returned"] is True,
    )
    require(
        "zero_measurement_scope",
        result["registered_performance_timing_count"] == 0
        and result["formal_worker_count"] == 0
        and result["pod"] is False
        and result["wsl"] is False,
    )

    stdout_lines = (evidence_dir / "stdout.txt").read_text(encoding="utf-8").splitlines()
    printed = [
        line.removeprefix("GOAL5801_G_HOME_EVIDENCE=")
        for line in stdout_lines
        if line.startswith("GOAL5801_G_HOME_EVIDENCE=")
    ]
    require("one_stdout_evidence_record", len(printed) == 1)
    require("stdout_record_equals_file", json.loads(printed[0]) == result)
    stderr = (evidence_dir / "stderr.txt").read_text(encoding="utf-8")
    require("nine_tests_passed", "Ran 9 tests" in stderr and "\nOK\n" in stderr)

    archive_members: dict[str, bytes] = {}
    with tarfile.open(source_path, mode="r:") as archive:
        members = archive.getmembers()
        require("source_archive_member_count", len(members) == SOURCE_ARCHIVE_MEMBERS)
        names = [member.name for member in members]
        require("source_archive_unique_names", len(names) == len(set(names)))
        for member in members:
            pure = PurePosixPath(member.name)
            require(
                f"safe_member:{member.name}",
                not pure.is_absolute() and ".." not in pure.parts,
            )
            require(
                f"regular_or_directory:{member.name}", member.isfile() or member.isdir())
            if member.isfile():
                stream = archive.extractfile(member)
                if stream is None:
                    raise RuntimeError(f"missing tar payload: {member.name}")
                archive_members[member.name] = stream.read()

    source_rows = result["source_files"]
    require("source_manifest_unique", len(source_rows) == len({row["path"] for row in source_rows}))
    required_source_paths = {
        "src/native/optix/rtdl_optix_core.cpp",
        "src/native/optix/rtdl_optix_prelude.h",
        "src/rtdsl/v4.py",
        "src/rtdsl/physical_execution_provenance.py",
        "src/rtdsl/v4_public_builtin_triangle.py",
        "src/rtdsl/v4_triangle_prepared_runtime.py",
        "src/rtdsl/v4_triangle_optix_compiler.py",
        "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
        "tests/goal5801_g_public_generic_triangle_authoring_test.py",
    }
    require("source_manifest_exact_paths", {row["path"] for row in source_rows} == required_source_paths)
    for row in source_rows:
        payload = archive_members[row["path"]]
        require(f"source_bytes:{row['path']}", len(payload) == row["bytes"])
        require(
            f"source_sha256:{row['path']}",
            hashlib.sha256(payload).hexdigest() == row["sha256"],
        )

    runtime = archive_members["src/rtdsl/v4_triangle_prepared_runtime.py"]
    runtime_identity = result["prepared_runtime_source_identity"]
    require(
        "runtime_raw_identity",
        len(runtime) == runtime_identity["raw_bytes"] == 19_055
        and hashlib.sha256(runtime).hexdigest()
        == runtime_identity["raw_sha256"]
        == RUNTIME_RAW_SHA256,
    )
    runtime_text = runtime.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    require(
        "runtime_canonical_text_identity",
        hashlib.sha256(runtime_text.encode("utf-8")).hexdigest()
        == runtime_identity["canonical_text_sha256"]
        == RUNTIME_TEXT_SHA256,
    )
    require(
        "runtime_identity_domains_distinct",
        runtime_identity["canonical_identity_is_not_raw_byte_identity"] is True
        and runtime_identity["raw_sha256"] != runtime_identity["canonical_text_sha256"],
    )

    oracle = result["independent_cpu_oracle_output"]
    require("baseline_equals_cpu_oracle", oracle == EXPECTED_OUTPUTS["baseline_primitive_identity"])
    runs = result["runs"]
    require("three_exact_run_labels", [run["label"] for run in runs] == list(EXPECTED_PTX))
    bundle_id = fnv1a64(BUNDLE)
    require("bundle_id_known_vector", bundle_id == 0xD0EACA28180FDB05)
    for run in runs:
        label = run["label"]
        require(f"output_exact:{label}", run["output"] == EXPECTED_OUTPUTS[label])
        require(f"output_digest:{label}", digest(run["output"]) == run["output_sha256"])
        ptx_name, ptx_bytes, ptx_sha = EXPECTED_PTX[label]
        require(
            f"ptx_payload:{label}",
            file_digest(evidence_dir / ptx_name) == (ptx_bytes, ptx_sha)
            and run["composed_ptx_bytes"] == ptx_bytes
            and run["composed_ptx_sha256"] == ptx_sha,
        )

        decision = run["protocol_contract_decision"]
        decision_body = dict(decision)
        decision_seal = decision_body.pop("decision_sha256")
        require(
            f"contract_accept:{label}",
            decision["verdict"] == "ACCEPT"
            and decision["findings"] == []
            and decision["executable_capability_issued"] is False
            and digest(decision_body) == decision_seal,
        )

        identity = run["executable_identity"]
        identity_body = dict(identity)
        identity_seal = identity_body.pop("identity_sha256")
        require(f"executable_identity:{label}", digest(identity_body) == identity_seal)
        require(
            f"executable_payload_bindings:{label}",
            identity["composed_ptx_sha256"] == ptx_sha
            and identity["native_library_sha256"] == NATIVE_SHA256,
        )

        receipt = run["traversal_receipt"]
        receipt_body = dict(receipt)
        receipt_seal = receipt_body.pop("receipt_sha256")
        snapshot = receipt["native_snapshot"]
        require(f"traversal_receipt_seal:{label}", digest(receipt_body) == receipt_seal)
        require(
            f"traversal_envelope:{label}",
            receipt["schema"] == "rtdl.physical_execution.traversal_receipt.v1"
            and receipt["provider_library"] == "librtdl_optix"
            and receipt["provider_library_sha256"] == NATIVE_SHA256
            and receipt["route_identity"]
            == "v4_builtin_triangle_callback_ir:four_role_composed_v1"
            and receipt["output_digest"] == run["output_sha256"]
            and receipt["physical_executor_classification"] == "optix_traversal_observed"
            and receipt["expected_program_bundles"] == [BUNDLE]
            and receipt["expected_program_bundle_ids"] == [bundle_id]
            and receipt["expected_program_observed_at_receipt_edge"] is True,
        )
        require(
            f"traversal_native_counts:{label}",
            snapshot["nonce_hi"] == receipt["nonce"]["hi"]
            and snapshot["nonce_lo"] == receipt["nonce"]["lo"]
            and (receipt["nonce"]["hi"], receipt["nonce"]["lo"]) != (0, 0)
            and snapshot["attempted_launch_count"] == 1
            and snapshot["successful_launch_count"] == 1
            and snapshot["failed_launch_count"] == 0
            and snapshot["complete_context_launch_count"] == 1
            and snapshot["incomplete_context_launch_count"] == 0
            and snapshot["context_bind_count"] == 1
            and snapshot["raygen_invocation_count"] == 3
            and snapshot["pending_context_at_finish"] == 0
            and snapshot["session_error"] == 0
            and snapshot["incomplete_callsite_record_count"] == 0
            and snapshot["incomplete_callsite_lines"] == [0] * 32,
        )
        traversable = snapshot["first_traversable"]
        require(
            f"traversal_native_identity:{label}",
            traversable != 0
            and snapshot["last_traversable"] == traversable
            and snapshot["first_program_bundle_id"] == bundle_id
            and snapshot["last_program_bundle_id"] == bundle_id
            and snapshot["program_bundle_mix"] == native_mix(0, bundle_id)
            and snapshot["traversable_mix"] == native_mix(0, traversable),
        )
        u32_fields = {
            "pending_context_at_finish",
            "session_error",
            "incomplete_callsite_record_count",
        }
        for key, value in snapshot.items():
            if key == "incomplete_callsite_lines":
                continue
            width = 32 if key in u32_fields else 64
            require(
                f"snapshot_scalar_domain:{label}:{key}",
                type(value) is int and 0 <= value < 1 << width,
            )

        lifecycle = run["lifecycle_receipt"]
        require(
            f"lifecycle_binding:{label}",
            lifecycle["schema"] == "rtdl.v4.public_builtin_triangle_callback_lifecycle.v1"
            and lifecycle["execution_count"] == 1
            and lifecycle["native_library_sha256"] == NATIVE_SHA256
            and lifecycle["composed_ptx_sha256"] == ptx_sha
            and lifecycle["executable_identity_sha256"] == identity_seal
            and lifecycle["protocol_contract_verdict"] == "ACCEPT"
            and lifecycle["cold_result_replaced"] is False,
        )

    require(
        "metadata_rebinding_changes_artifacts",
        runs[1]["executable_identity"]["wrapper_source_sha256"]
        != runs[2]["executable_identity"]["wrapper_source_sha256"]
        and runs[1]["composed_ptx_sha256"] != runs[2]["composed_ptx_sha256"]
        and runs[1]["output"] != runs[2]["output"],
    )
    require(
        "declared_mechanism_boundaries",
        result["stale_plan_semantic_leaf_rejected_before_materialize"] is True
        and result["fresh_semantic_leaf_materialized_and_executed"] is True
        and result["metadata_argument_rebinding_changed_wrapper_and_output"] is True,
    )

    verification = {
        "schema": "rtdl.goal5801_g.a3_independent_verification.v1",
        "status": "PASS",
        "source_commit": SOURCE_COMMIT,
        "source_tree": SOURCE_TREE,
        "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
        "native_sha256": NATIVE_SHA256,
        "result_sha256": RESULT_SHA256,
        "checks_passed": len(checks),
        "checks": checks,
        "claim_boundary": {
            "canonical_runtime_identity_is_raw_byte_identity": False,
            "native_source_manifest_proves_native_build_provenance": False,
            "evidence_harness_uses_private_ptx_inspection": True,
            "generalization_exam_count": 0,
            "third_party_user_count": 0,
            "registered_performance_timing_count": 0,
        },
    }
    verification["verification_sha256"] = digest(verification)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(verification, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps(verification, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
