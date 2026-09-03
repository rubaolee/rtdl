from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from scripts import goal5840_capture_gpu_evidence as capture
from scripts import goal5840_freeze_gpu_inputs as freeze
from scripts import goal5840_freeze_attempt02_repair_inputs as attempt02_freeze
from scripts import goal5840_freeze_attempt03_repair_inputs as attempt03_freeze
from scripts import goal5840_freeze_attempt04_repair_inputs as attempt04_freeze
from scripts import goal5840_freeze_repair_inputs as repair_freeze
from scripts import goal5840_independent_target_checker as checker
from scripts import goal5840_mutation_suite as mutation_suite
from scripts import goal5840_verify_gpu_evidence as verifier
from tests.goal5840_independent_target_checker_test import (
    _make_bundle,
    _reseal_bundle,
)


PREREGISTRATION = Path(
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "GOAL5840_PREREGISTRATION.json"
)


def _sealed_mutation_report(
    frozen: dict[str, dict[str, object]],
) -> dict[str, object]:
    applications = []
    for route_id, modes in verifier.EXPECTED_MODES.items():
        for mode in modes:
            for property_id in verifier.PROPERTIES:
                mutation_id = f"{route_id}::{property_id}"
                row = frozen[mutation_id]
                applications.append({
                    "route_id": route_id,
                    "mode": mode,
                    "property_id": property_id,
                    "mutation_id": mutation_id,
                    "target_selector": row["target_selector"],
                    "replacement": row["replacement"],
                    "preregistered_required_rejection": row[
                        "required_rejection"
                    ],
                    "checker_verdict": "REJECT",
                    "target_property_verdict": "REJECT",
                    "target_property_reason_id": (
                        "TC" + property_id[2:5] + "_TEST_REJECTION"
                    ),
                    "gpu_launch_required_for_rejection": False,
                })
    report: dict[str, object] = {
        "schema": "rtdl.goal5840.exact_bundle_mutation_suite.v1",
        "status": "PASS__ALL_FROZEN_MUTATIONS_REJECTED_BEFORE_GPU_LAUNCH",
        "preregistered_claim_unit_count": 15,
        "mode_replication_application_count": 20,
        "rejected_application_count": 20,
        "all_rejected_before_gpu_launch": True,
        "applications": applications,
        "claim_boundary": {
            "exact_captured_bundle_mutations_only": True,
            "general_soundness_theorem": False,
            "performance_or_speedup": False,
            "external_review_or_consensus": False,
        },
        "report_sha256": "",
    }
    report["report_sha256"] = hashlib.sha256(
        verifier.MUTATION_DOMAIN + verifier._canonical(report)
    ).hexdigest()
    return report


def _seal(document: dict[str, object], field: str, domain: bytes) -> None:
    document[field] = ""
    document[field] = hashlib.sha256(
        domain + verifier._canonical(document)
    ).hexdigest()


def _identity_seal(document: dict[str, object]) -> None:
    document["identity_sha256"] = verifier._digest({
        key: value
        for key, value in document.items()
        if key != "identity_sha256"
    })


class Goal5840GpuEvidenceVerifierTest(unittest.TestCase):
    def test_verifier_imports_only_python_standard_library(self) -> None:
        path = Path(verifier.__file__)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported_roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(
                    alias.name.split(".", 1)[0] for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
        self.assertEqual(
            imported_roots,
            {
                "__future__",
                "argparse",
                "hashlib",
                "json",
                "os",
                "pathlib",
                "re",
                "struct",
                "subprocess",
                "sys",
                "tempfile",
                "typing",
            },
        )

    def test_safe_member_rejects_escape_and_accepts_plain_file(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            (root / "evidence.json").write_text("{}\n", encoding="ascii")
            self.assertEqual(
                verifier._safe_member(root, "evidence.json", "member"),
                root / "evidence.json",
            )
            for value in ("../evidence.json", "/tmp/evidence.json", "a/b.json"):
                with self.subTest(value=value):
                    with self.assertRaises(
                        verifier.Goal5840EvidenceVerificationError
                    ):
                        verifier._safe_member(root, value, "member")

    def test_elf_reader_returns_only_defined_dynamic_symbols(self) -> None:
        header_format = "<16sHHIQQQIHHHHHH"
        section_format = "<IIQQQQIIQQ"
        symbol_format = "<IBBHQQ"
        strings = b"\0defined_symbol\0undefined_symbol\0"
        header_size = struct.calcsize(header_format)
        string_offset = header_size
        symbol_offset = string_offset + len(strings)
        symbol_rows = b"".join((
            struct.pack(symbol_format, 0, 0, 0, 0, 0, 0),
            struct.pack(symbol_format, 1, 0x12, 0, 1, 0, 0),
            struct.pack(
                symbol_format,
                1 + len("defined_symbol") + 1,
                0x12,
                0,
                0,
                0,
                0,
            ),
        ))
        section_offset = symbol_offset + len(symbol_rows)
        ident = b"\x7fELF\x02\x01\x01" + b"\0" * 9
        header = struct.pack(
            header_format,
            ident,
            3,
            62,
            1,
            0,
            0,
            section_offset,
            0,
            header_size,
            0,
            0,
            struct.calcsize(section_format),
            3,
            0,
        )
        sections = b"".join((
            struct.pack(section_format, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            struct.pack(
                section_format,
                0,
                3,
                0,
                0,
                string_offset,
                len(strings),
                0,
                0,
                1,
                0,
            ),
            struct.pack(
                section_format,
                0,
                11,
                0,
                0,
                symbol_offset,
                len(symbol_rows),
                1,
                1,
                8,
                struct.calcsize(symbol_format),
            ),
        ))
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "minimal.so"
            path.write_bytes(header + strings + symbol_rows + sections)
            self.assertEqual(
                verifier._defined_elf64_dynamic_symbols(path),
                {"defined_symbol"},
            )

    def test_exact_twenty_application_mutation_report_validates(self) -> None:
        preregistration = json.loads(PREREGISTRATION.read_text(encoding="ascii"))
        frozen = verifier._verify_preregistration(preregistration)
        report = _sealed_mutation_report(frozen)
        verifier._verify_mutation_report(report, frozen)

    def test_missing_mutation_application_fails_even_after_reseal(self) -> None:
        preregistration = json.loads(PREREGISTRATION.read_text(encoding="ascii"))
        frozen = verifier._verify_preregistration(preregistration)
        report = copy.deepcopy(_sealed_mutation_report(frozen))
        report["applications"].pop()
        report["mode_replication_application_count"] = 19
        report["rejected_application_count"] = 19
        report["report_sha256"] = ""
        report["report_sha256"] = hashlib.sha256(
            verifier.MUTATION_DOMAIN + verifier._canonical(report)
        ).hexdigest()
        with self.assertRaises(verifier.Goal5840EvidenceVerificationError):
            verifier._verify_mutation_report(report, frozen)

    def test_capture_and_freeze_custody_include_verifier(self) -> None:
        path = "scripts/goal5840_verify_gpu_evidence.py"
        self.assertIn(path, capture.SOURCE_PATHS)
        self.assertIn(path, freeze.SOURCE_PATHS)
        self.assertLessEqual(
            verifier.RUNTIME_SOURCE_PATHS, set(capture.SOURCE_PATHS)
        )
        self.assertLessEqual(
            verifier.ORIGINAL_RUNTIME_SOURCE_PATHS, set(freeze.SOURCE_PATHS)
        )
        self.assertLessEqual(
            verifier.ATTEMPT_01_REPAIR_RUNTIME_SOURCE_PATHS,
            set(repair_freeze.SOURCE_PATHS),
        )
        self.assertLessEqual(
            verifier.ATTEMPT_02_REPAIR_RUNTIME_SOURCE_PATHS,
            set(attempt02_freeze.SOURCE_PATHS),
        )
        self.assertLessEqual(
            verifier.RUNTIME_SOURCE_PATHS, set(attempt04_freeze.SOURCE_PATHS)
        )
        self.assertEqual(
            capture.REPAIR_ALLOWED_CHANGED_PATHS,
            verifier.REPAIR_ALLOWED_CHANGED_PATHS,
        )
        self.assertEqual(
            tuple(repair_freeze.ALLOWED_CHANGED_PATHS),
            verifier.REPAIR_ALLOWED_CHANGED_PATHS,
        )
        self.assertEqual(
            capture.ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS,
            verifier.ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS,
        )
        self.assertEqual(
            tuple(attempt02_freeze.ALLOWED_CHANGED_PATHS),
            verifier.ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS,
        )
        self.assertEqual(
            tuple(attempt03_freeze.ALLOWED_CHANGED_PATHS),
            verifier.ATTEMPT_03_REPAIR_ALLOWED_CHANGED_PATHS,
        )
        self.assertEqual(
            tuple(attempt04_freeze.ALLOWED_CHANGED_PATHS),
            verifier.ATTEMPT_04_REPAIR_ALLOWED_CHANGED_PATHS,
        )
        self.assertEqual(
            capture.GOAL5840_REQUIRED_NATIVE_SYMBOLS,
            verifier.GOAL5840_REQUIRED_NATIVE_SYMBOLS,
        )
        self.assertEqual(
            capture.NATIVE_BUILD_SOURCE_PATHS,
            verifier.NATIVE_BUILD_SOURCE_PATHS,
        )

    def test_required_symbols_cover_all_three_prepared_routes(self) -> None:
        required = set(verifier.GOAL5840_REQUIRED_NATIVE_SYMBOLS)
        route_symbols = {
            "rtdl_optix_v4_prepare_bounded_relation_callback_v1",
            "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v3",
            "rtdl_optix_v4_destroy_prepared_bounded_relation_callback_v1",
            "rtdl_optix_v4_prepare_triangle_reduction_callback_v1",
            "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v2",
            "rtdl_optix_v4_destroy_prepared_triangle_reduction_callback_v1",
            "rtdl_optix_v4_checked_u64_product_sum_host_v1",
            "rtdl_optix_v4_prepare_builtin_sphere_callback_v1",
            "rtdl_optix_v4_execute_prepared_builtin_sphere_callback_v1",
            "rtdl_optix_v4_describe_prepared_builtin_sphere_callback_v1",
            "rtdl_optix_v4_destroy_prepared_builtin_sphere_callback_v1",
        }
        self.assertLessEqual(route_symbols, required)
        api = Path("src/native/optix/rtdl_optix_api.cpp").read_text(
            encoding="utf-8"
        )
        for symbol in route_symbols:
            with self.subTest(symbol=symbol):
                self.assertIn(f'extern "C" int {symbol}(', api)

    def test_capture_validates_native_build_source_and_manifest_seals(self) -> None:
        commit = "c" * 40
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            source_rows = []
            for index, relative in enumerate(
                sorted(capture.NATIVE_BUILD_SOURCE_PATHS), start=1
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                payload = f"source-{index}-{relative}\n".encode("ascii")
                path.write_bytes(payload)
                source_rows.append({
                    "path": relative,
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                })
            builder = root / (
                "scripts/goal5838_build_selected_sphere_optix_provider.py"
            )
            build_input = {
                "schema": "synthetic_build_input",
                "builder_path": str(builder.relative_to(root)),
                "builder_sha256": hashlib.sha256(
                    builder.read_bytes()
                ).hexdigest(),
            }
            native = root / "librtdl_optix.so"
            native.write_bytes(b"synthetic-native")
            document: dict[str, object] = {
                "schema": (
                    "rtdl.goal5838.selected_sphere_optix_provider_build.v2"
                ),
                "status": (
                    "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED"
                ),
                "repository": {
                    "expected_commit": commit,
                    "head_before": commit,
                    "head_after": commit,
                    "source_files": source_rows,
                },
                "build_input": build_input,
                "build_input_sha256": capture._digest(build_input),
                "native_output": {
                    "path": str(native),
                    "bytes": native.stat().st_size,
                    "sha256": hashlib.sha256(native.read_bytes()).hexdigest(),
                },
                "all_required_symbols_exported": True,
                "result_sha256": "",
            }
            _seal(document, "result_sha256", capture.NATIVE_BUILD_DOMAIN)
            manifest = root / "native_build.json"
            manifest.write_text(
                json.dumps(document, indent=2, sort_keys=True) + "\n",
                encoding="ascii",
            )
            with patch.object(capture, "ROOT", root):
                result = capture._verify_native_build(
                    manifest, native, commit
                )
            self.assertEqual(result["result_sha256"], document["result_sha256"])

    def test_complete_synthetic_capsule_replays(self) -> None:
        commit = "a" * 40
        preregistration_path = str(PREREGISTRATION)
        preregistration_bytes = PREREGISTRATION.read_bytes()
        preregistration = json.loads(preregistration_bytes)
        native_bytes = b"synthetic-goal5840-native-dso"
        native_sha = hashlib.sha256(native_bytes).hexdigest()
        frozen_paths = (
            "src/rtdsl/v4_family_schema.py",
            "src/rtdsl/v4_generic_family_lifecycle.py",
            "src/rtdsl/v4_family.py",
        )

        with tempfile.TemporaryDirectory() as name:
            directory = Path(name).resolve()
            native_path = directory / "librtdl_optix.so"
            native_path.write_bytes(native_bytes)
            bundles = []
            mode_rows = []
            frozen_mode_rows = []
            trust_roots = {}
            for index, (route_id, modes) in enumerate(
                verifier.EXPECTED_MODES.items(), start=1
            ):
                for mode in modes:
                    bundle, _declaration, _identity, control = _make_bundle(
                        route_id, mode=mode
                    )
                    output = {"synthetic_mode": mode, "ordinal": index}
                    output_sha = verifier._digest(output)
                    physical = bundle["physical_evidence"]
                    identity = physical["executable_identity"]
                    identity["provider_artifact_sha256"] = native_sha
                    _identity_seal(identity)
                    physical["target_binding"][
                        "native_library_sha256"
                    ] = native_sha
                    receipt = bundle["execution_receipt"]
                    receipt["executable_identity_sha256"] = identity[
                        "identity_sha256"
                    ]
                    receipt["native_library_sha256"] = native_sha
                    receipt["output_sha256"] = output_sha
                    receipt["traversal_receipt"][
                        "provider_library_sha256"
                    ] = native_sha
                    receipt["traversal_receipt"]["output_digest"] = output_sha
                    _reseal_bundle(bundle)

                    key = f"{route_id}::{mode}"
                    stem = f"mode_{len(mode_rows) + 1:02d}_{mode}"
                    bundle_path = directory / f"{stem}_bundle.json"
                    bundle_path.write_text(
                        json.dumps(bundle, indent=2, sort_keys=True) + "\n",
                        encoding="ascii",
                    )
                    roots = {
                        "declaration_sha256": bundle["declaration"][
                            "declaration_sha256"
                        ],
                        "executable_identity_sha256": identity[
                            "identity_sha256"
                        ],
                        "control_flow_manifest_sha256": control,
                    }
                    trust_roots[key] = roots
                    check = checker.check_target_evidence(
                        bundle,
                        trusted_declaration_sha256=roots[
                            "declaration_sha256"
                        ],
                        trusted_executable_identity_sha256=roots[
                            "executable_identity_sha256"
                        ],
                        trusted_control_flow_manifest_sha256=roots[
                            "control_flow_manifest_sha256"
                        ],
                    )
                    self.assertEqual(check["verdict"], "ACCEPT", check)
                    checker_path = directory / f"{stem}_independent_check.json"
                    checker_path.write_text(
                        json.dumps(check, indent=2, sort_keys=True) + "\n",
                        encoding="ascii",
                    )
                    fixture_sha = verifier._digest({"fixture": key})
                    mode_row = {
                        "key": key,
                        "route_id": route_id,
                        "mode": mode,
                        "fixture_sha256": fixture_sha,
                        "expected_output": output,
                        "expected_output_sha256": output_sha,
                        "observed_output": output,
                        "observed_output_sha256": output_sha,
                        "bundle_file": bundle_path.name,
                        "bundle_sha256": bundle["bundle_sha256"],
                        "independent_check_file": checker_path.name,
                        "independent_check_sha256": check["report_sha256"],
                        "independent_property_pass_count": 5,
                        "true_optix": True,
                    }
                    mode_rows.append(mode_row)
                    frozen_mode_rows.append({
                        "key": key,
                        "route_id": route_id,
                        "mode": mode,
                        "target_kind": (
                            "sphere"
                            if route_id.startswith("prospective::")
                            else "stable"
                        ),
                        "plan_sha256": bundle["declaration"]["plan_sha256"],
                        "declaration_sha256": roots["declaration_sha256"],
                        "control_flow_manifest_sha256": control,
                        "fixture_sha256": fixture_sha,
                        "expected_output": output,
                        "expected_output_sha256": output_sha,
                    })
                    bundles.append(bundle)

            trust: dict[str, object] = {
                "schema": "rtdl.goal5840.runtime_trust_roots.v1",
                "source": "synthetic_test",
                "trust_roots": trust_roots,
                "claim_boundary": {
                    "pre_pod_declaration_and_control_roots": True,
                    "post_materialization_executable_identity_root": True,
                    "independent_hardware_attestation": False,
                },
                "trust_roots_sha256": "",
            }
            _seal(
                trust,
                "trust_roots_sha256",
                verifier.TRUST_ROOT_DOMAIN,
            )
            trust_path = directory / "RUNTIME_TRUST_ROOTS.json"
            trust_path.write_text(
                json.dumps(trust, indent=2, sort_keys=True) + "\n",
                encoding="ascii",
            )

            mutation = mutation_suite.run_exact_bundle_mutations(
                bundles, trust_roots
            )
            mutation_path = directory / "EXACT_BUNDLE_MUTATION_RESULT.json"
            mutation_path.write_text(
                json.dumps(mutation, indent=2, sort_keys=True) + "\n",
                encoding="ascii",
            )

            source_blobs = {
                path: (Path(path).read_bytes() if Path(path).is_file() else b"")
                for path in (
                    set(attempt04_freeze.SOURCE_PATHS)
                    | verifier.NATIVE_BUILD_SOURCE_PATHS
                    | set(frozen_paths)
                )
            }
            source_rows = [
                {
                    "path": path,
                    "bytes": len(blob),
                    "sha256": hashlib.sha256(blob).hexdigest(),
                }
                for path, blob in sorted(source_blobs.items())
            ]
            frozen_core = {
                "seal_sha256": "b" * 64,
                "files": [
                    row for row in source_rows if row["path"] in frozen_paths
                ],
                "changed_file_count": 0,
            }
            pre_pod: dict[str, object] = {
                "schema": "rtdl.goal5840.pre_pod_input_authority.v1",
                "goal": 5840,
                "frozen_at_utc": "2026-09-03T00:00:00Z",
                "stage": "BEFORE_ANY_GOAL5840_GPU_EXECUTION",
                "status": "FROZEN_INPUTS_AND_TRUST_ROOTS__NO_GPU_RESULT",
                "preregistration": {
                    "path": preregistration_path,
                    "bytes": len(preregistration_bytes),
                    "file_sha256": hashlib.sha256(
                        preregistration_bytes
                    ).hexdigest(),
                    "authority_sha256": preregistration[
                        "authority_sha256"
                    ],
                    "mutation_count": 15,
                },
                "source_files": [
                    row
                    for row in source_rows
                    if row["path"] in verifier.ORIGINAL_RUNTIME_SOURCE_PATHS
                ],
                "goal5838_frozen_core": frozen_core,
                "route_bundle_group_count": 3,
                "required_mode_count": 4,
                "mode_cases": frozen_mode_rows,
                "execution_counts_at_freeze": {
                    "goal5840_gpu_launches": 0,
                    "goal5840_positive_target_bundles": 0,
                    "goal5840_exact_bundle_mutations": 0,
                },
                "claim_boundary": {
                    "input_and_declaration_freeze_only": True,
                    "lowering_preservation_established": False,
                    "gpu_result": False,
                    "performance_or_speedup": False,
                    "application_correctness": False,
                    "external_review_or_consensus": False,
                },
                "authority_sha256": "",
            }
            _seal(pre_pod, "authority_sha256", verifier.PRE_POD_DOMAIN)
            pre_pod_path = verifier.PRE_POD_AUTHORITY_PATH
            pre_pod_bytes = (
                json.dumps(pre_pod, indent=2, sort_keys=True) + "\n"
            ).encode("ascii")

            incident_path = verifier.ATTEMPT_01_INCIDENT_PATH
            incident_bytes = Path(incident_path).read_bytes()
            self.assertEqual(
                hashlib.sha256(incident_bytes).hexdigest(),
                verifier.ATTEMPT_01_INCIDENT_SHA256,
            )
            repair: dict[str, object] = {
                "schema": (
                    "rtdl.goal5840.post_attempt_01_repair_authority.v1"
                ),
                "goal": 5840,
                "frozen_at_utc": "2026-09-03T10:00:00Z",
                "stage": "AFTER_ATTEMPT_01_BEFORE_ATTEMPT_02_GPU_EXECUTION",
                "status": (
                    "FROZEN_BOUNDED_EVIDENCE_TRANSPORT_REPAIR__NO_ACCEPTED_RESULT"
                ),
                "base_attempt": {
                    "source_commit": verifier.ATTEMPT_01_SOURCE_COMMIT,
                    "pre_pod_input_authority": {
                        "path": pre_pod_path,
                        "bytes": len(pre_pod_bytes),
                        "file_sha256": hashlib.sha256(
                            pre_pod_bytes
                        ).hexdigest(),
                        "authority_sha256": pre_pod["authority_sha256"],
                    },
                    "attempt_01_incident": {
                        "path": incident_path,
                        "bytes": len(incident_bytes),
                        "file_sha256": hashlib.sha256(
                            incident_bytes
                        ).hexdigest(),
                        "classification": (
                            "EVIDENCE_TRANSPORT_ENGINEERING_FAILURE"
                        ),
                    },
                    "observed_counts": {
                        "runner_processes_started": 1,
                        "frozen_modes_entered": 1,
                        "public_route_expected_outputs_returned": 1,
                        "published_evidence_bundles": 0,
                        "published_independent_property_reports": 0,
                        "published_mutation_applications": 0,
                        "accepted_positive_evidence_rows": 0,
                    },
                },
                "repair_scope": {
                    "defect": (
                        "nested_read_only_mapping_not_recursively_json_"
                        "canonicalized"
                    ),
                    "repair": (
                        "recursive_mapping_sequence_to_canonical_json_tree"
                    ),
                    "nonsemantic_harness_hardening": (
                        "generate_pod_mutation_report_under_python_isolated_mode"
                    ),
                    "allowed_changed_paths": list(
                        verifier.REPAIR_ALLOWED_CHANGED_PATHS
                    ),
                    "exact_changed_paths_since_base": list(
                        verifier.REPAIR_ALLOWED_CHANGED_PATHS
                    ),
                    "route_change_allowed": False,
                    "fixture_or_oracle_change_allowed": False,
                    "declaration_or_control_root_change_allowed": False,
                    "property_or_mutation_change_allowed": False,
                    "native_engine_change_allowed": False,
                    "frozen_core_change_allowed": False,
                },
                "preregistration": pre_pod["preregistration"],
                "source_files": [
                    row
                    for row in source_rows
                    if row["path"]
                    in verifier.ATTEMPT_01_REPAIR_RUNTIME_SOURCE_PATHS
                ],
                "goal5838_frozen_core": frozen_core,
                "route_bundle_group_count": 3,
                "required_mode_count": 4,
                "mode_cases": frozen_mode_rows,
                "execution_counts_at_repair_freeze": {
                    "attempted_runner_processes": 1,
                    "entered_frozen_modes": 1,
                    "returned_expected_outputs": 1,
                    "published_evidence_bundles": 0,
                    "published_independent_property_reports": 0,
                    "published_mutation_applications": 0,
                    "accepted_goal5840_positive_evidence_rows": 0,
                },
                "claim_boundary": {
                    "append_only_engineering_repair_authority": True,
                    "scientific_inputs_unchanged": True,
                    "accepted_goal5840_result": False,
                    "lowering_preservation_established": False,
                    "performance_or_speedup": False,
                    "application_correctness": False,
                    "external_review_or_consensus": False,
                },
                "authority_sha256": "",
            }
            _seal(
                repair,
                "authority_sha256",
                verifier.REPAIR_AUTHORITY_DOMAIN,
            )
            repair_path = verifier.REPAIR_AUTHORITY_PATH
            repair_bytes = (
                json.dumps(repair, indent=2, sort_keys=True) + "\n"
            ).encode("ascii")

            attempt02_incident_path = verifier.ATTEMPT_02_INCIDENT_PATH
            attempt02_incident_bytes = Path(attempt02_incident_path).read_bytes()
            self.assertEqual(
                hashlib.sha256(attempt02_incident_bytes).hexdigest(),
                verifier.ATTEMPT_02_INCIDENT_SHA256,
            )
            attempt02_repair: dict[str, object] = {
                "schema": (
                    "rtdl.goal5840.post_attempt_02_repair_authority.v1"
                ),
                "goal": 5840,
                "frozen_at_utc": "2026-09-03T10:30:00Z",
                "stage": "AFTER_ATTEMPT_02_BEFORE_ATTEMPT_03_GPU_EXECUTION",
                "status": (
                    "FROZEN_BOUNDED_EXECUTABLE_IDENTITY_REPAIR__"
                    "NO_ACCEPTED_RESULT"
                ),
                "base_chain": {
                    "attempt_01_source_commit": verifier.ATTEMPT_01_SOURCE_COMMIT,
                    "attempt_01_repair_commit": verifier.ATTEMPT_01_REPAIR_COMMIT,
                    "post_attempt_01_repair_authority": {
                        "path": repair_path,
                        "bytes": len(repair_bytes),
                        "file_sha256": hashlib.sha256(repair_bytes).hexdigest(),
                        "authority_sha256": repair["authority_sha256"],
                    },
                    "attempt_02_incident": {
                        "path": attempt02_incident_path,
                        "bytes": len(attempt02_incident_bytes),
                        "file_sha256": hashlib.sha256(
                            attempt02_incident_bytes
                        ).hexdigest(),
                        "classification": (
                            "EVIDENCE_EXECUTABLE_IDENTITY_CANONICALIZATION_"
                            "ENGINEERING_FAILURE"
                        ),
                    },
                    "formal_observed_counts_through_attempt_02": {
                        "runner_processes_started": 2,
                        "frozen_modes_entered": 2,
                        "public_route_expected_outputs_returned": 2,
                        "published_evidence_bundles": 0,
                        "published_independent_property_reports": 0,
                        "published_mutation_applications": 0,
                        "accepted_positive_evidence_rows": 0,
                    },
                    "post_failure_diagnostics": {
                        "diagnostic_processes": 2,
                        "diagnostic_mode_executions": 2,
                        "diagnostic_expected_outputs_returned": 2,
                        "diagnostic_evidence_files_published": 0,
                        "accepted_positive_evidence_rows": 0,
                    },
                },
                "repair_scope": {
                    "defect": (
                        "str_derived_enum_role_stringified_to_enum_qualname"
                    ),
                    "repair": (
                        "preserve_and_validate_underlying_string_enum_value"
                    ),
                    "allowed_changed_paths": list(
                        verifier.ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS
                    ),
                    "exact_changed_paths_since_base": list(
                        verifier.ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS
                    ),
                    "route_change_allowed": False,
                    "fixture_or_oracle_change_allowed": False,
                    "declaration_or_control_root_change_allowed": False,
                    "property_or_mutation_change_allowed": False,
                    "native_engine_change_allowed": False,
                    "frozen_core_change_allowed": False,
                },
                "preregistration": pre_pod["preregistration"],
                "source_files": [
                    row
                    for row in source_rows
                    if row["path"]
                    in verifier.ATTEMPT_02_REPAIR_RUNTIME_SOURCE_PATHS
                ],
                "goal5838_frozen_core": frozen_core,
                "route_bundle_group_count": 3,
                "required_mode_count": 4,
                "mode_cases": frozen_mode_rows,
                "execution_counts_at_repair_freeze": {
                    "formal_runner_processes": 2,
                    "formal_entered_modes": 2,
                    "formal_returned_expected_outputs": 2,
                    "diagnostic_processes": 2,
                    "diagnostic_mode_executions": 2,
                    "published_evidence_bundles": 0,
                    "published_independent_property_reports": 0,
                    "published_mutation_applications": 0,
                    "accepted_goal5840_positive_evidence_rows": 0,
                },
                "claim_boundary": {
                    "append_only_engineering_repair_authority": True,
                    "two_prior_formal_failures_preserved": True,
                    "diagnostic_launches_not_accepted_as_evidence": True,
                    "scientific_inputs_unchanged": True,
                    "accepted_goal5840_result": False,
                    "lowering_preservation_established": False,
                    "performance_or_speedup": False,
                    "application_correctness": False,
                    "external_review_or_consensus": False,
                },
                "authority_sha256": "",
            }
            _seal(
                attempt02_repair,
                "authority_sha256",
                verifier.ATTEMPT_02_REPAIR_AUTHORITY_DOMAIN,
            )
            attempt02_repair_path = verifier.ATTEMPT_02_REPAIR_AUTHORITY_PATH
            attempt02_repair_bytes = (
                json.dumps(attempt02_repair, indent=2, sort_keys=True) + "\n"
            ).encode("ascii")

            attempt03_incident_path = verifier.ATTEMPT_03_INCIDENT_PATH
            attempt03_incident_bytes = Path(attempt03_incident_path).read_bytes()
            self.assertEqual(
                hashlib.sha256(attempt03_incident_bytes).hexdigest(),
                verifier.ATTEMPT_03_INCIDENT_SHA256,
            )
            attempt03_authority_source_paths = (
                verifier.ATTEMPT_03_REPAIR_RUNTIME_SOURCE_PATHS
                | {"tests/goal5760_v4_bounded_relation_test.py"}
            )
            attempt04_authority_source_paths = (
                attempt03_authority_source_paths
                | {"scripts/goal5840_freeze_attempt04_repair_inputs.py"}
            )
            attempt03_repair: dict[str, object] = {
                "schema": (
                    "rtdl.goal5840.post_attempt_03_repair_authority.v1"
                ),
                "goal": 5840,
                "frozen_at_utc": "2026-09-03T11:00:00Z",
                "stage": "AFTER_ATTEMPT_03_BEFORE_ATTEMPT_04_GPU_EXECUTION",
                "status": (
                    "FROZEN_INLINE_SPECIALIZATION_CHECKER_REPAIR__"
                    "NO_ACCEPTED_RESULT"
                ),
                "base_chain": {
                    "attempt_03_source_commit": verifier.ATTEMPT_03_SOURCE_COMMIT,
                    "post_attempt_02_repair_authority": {
                        "path": attempt02_repair_path,
                        "bytes": len(attempt02_repair_bytes),
                        "file_sha256": hashlib.sha256(
                            attempt02_repair_bytes
                        ).hexdigest(),
                        "authority_sha256": attempt02_repair[
                            "authority_sha256"
                        ],
                    },
                    "attempt_03_incident": {
                        "path": attempt03_incident_path,
                        "bytes": len(attempt03_incident_bytes),
                        "file_sha256": hashlib.sha256(
                            attempt03_incident_bytes
                        ).hexdigest(),
                        "classification": (
                            "INDEPENDENT_CHECKER_INLINE_SPECIALIZATION_RULE_"
                            "ENGINEERING_FAILURE"
                        ),
                        "published_failure_artifacts": [
                            {
                                "name": (
                                    "mode_01_capacity_fail_closed_collection_"
                                    "bundle.json"
                                ),
                                "bytes": 1364074,
                                "file_sha256": (
                                    "398e366efe3c7c156ef5c334ded4a258e360f55e"
                                    "ded254eb5c7f491726296635"
                                ),
                            },
                            {
                                "name": (
                                    "mode_01_capacity_fail_closed_collection_"
                                    "independent_check.json"
                                ),
                                "bytes": 3396,
                                "file_sha256": (
                                    "7aa16896c14e63664b486514b35713657b950a7e"
                                    "8e8a74709aa9816a0760c51a"
                                ),
                            },
                        ],
                    },
                    "formal_observed_counts_through_attempt_03": {
                        "runner_processes_started": 3,
                        "frozen_modes_entered": 3,
                        "public_route_expected_outputs_returned": 3,
                        "published_evidence_bundles": 1,
                        "published_independent_property_reports": 1,
                        "independently_accepted_reports": 0,
                        "published_mutation_applications": 0,
                        "accepted_positive_evidence_rows": 0,
                    },
                    "prior_post_failure_diagnostics": {
                        "diagnostic_processes": 2,
                        "diagnostic_mode_executions": 2,
                        "accepted_positive_evidence_rows": 0,
                    },
                    "attempt_03_post_failure_gpu_diagnostics": {
                        "diagnostic_processes": 0,
                        "diagnostic_mode_executions": 0,
                        "accepted_positive_evidence_rows": 0,
                    },
                },
                "repair_scope": {
                    "defect": (
                        "linked_ptx_symbol_rule_applied_to_closed_inline_"
                        "partial_evaluation"
                    ),
                    "repair": (
                        "independently_hash_inline_definitions_and_extract_"
                        "partial_evaluation_role_effects"
                    ),
                    "allowed_changed_paths": list(
                        verifier.ATTEMPT_03_REPAIR_ALLOWED_CHANGED_PATHS
                    ),
                    "exact_changed_paths_since_base": list(
                        verifier.ATTEMPT_03_REPAIR_ALLOWED_CHANGED_PATHS
                    ),
                    "linked_routes_keep_final_ptx_symbol_rule": True,
                    "bounded_wrapper_declares_partial_evaluation": True,
                    "route_change_allowed": False,
                    "fixture_or_oracle_change_allowed": False,
                    "declaration_or_control_root_change_allowed": False,
                    "property_or_mutation_change_allowed": False,
                    "native_engine_change_allowed": False,
                    "frozen_core_change_allowed": False,
                },
                "preregistration": pre_pod["preregistration"],
                "source_files": [
                    row
                    for row in source_rows
                    if row["path"] in attempt03_authority_source_paths
                ],
                "goal5838_frozen_core": frozen_core,
                "route_bundle_group_count": 3,
                "required_mode_count": 4,
                "mode_cases": frozen_mode_rows,
                "execution_counts_at_repair_freeze": {
                    "formal_runner_processes": 3,
                    "formal_entered_modes": 3,
                    "formal_returned_expected_outputs": 3,
                    "prior_diagnostic_processes": 2,
                    "prior_diagnostic_mode_executions": 2,
                    "published_evidence_bundles": 1,
                    "published_independent_property_reports": 1,
                    "independently_accepted_reports": 0,
                    "published_mutation_applications": 0,
                    "accepted_goal5840_positive_evidence_rows": 0,
                },
                "claim_boundary": {
                    "append_only_engineering_repair_authority": True,
                    "three_prior_formal_failures_preserved": True,
                    "failure_bundle_and_reject_report_not_accepted": True,
                    "diagnostic_launches_not_accepted_as_evidence": True,
                    "scientific_inputs_unchanged": True,
                    "accepted_goal5840_result": False,
                    "lowering_preservation_established": False,
                    "performance_or_speedup": False,
                    "application_correctness": False,
                    "external_review_or_consensus": False,
                },
                "authority_sha256": "",
            }
            _seal(
                attempt03_repair,
                "authority_sha256",
                verifier.ATTEMPT_03_REPAIR_AUTHORITY_DOMAIN,
            )
            attempt03_repair_path = verifier.ATTEMPT_03_REPAIR_AUTHORITY_PATH
            attempt03_repair_bytes = (
                json.dumps(attempt03_repair, indent=2, sort_keys=True) + "\n"
            ).encode("ascii")

            attempt04_incident_path = verifier.ATTEMPT_04_INCIDENT_PATH
            attempt04_incident_bytes = Path(attempt04_incident_path).read_bytes()
            self.assertEqual(
                hashlib.sha256(attempt04_incident_bytes).hexdigest(),
                verifier.ATTEMPT_04_INCIDENT_SHA256,
            )
            attempt04_repair: dict[str, object] = {
                "schema": (
                    "rtdl.goal5840.post_attempt_04_repair_authority.v1"
                ),
                "goal": 5840,
                "frozen_at_utc": "2026-09-03T12:00:00Z",
                "stage": "AFTER_ATTEMPT_04_BEFORE_ATTEMPT_05_GPU_EXECUTION",
                "status": (
                    "FROZEN_TRIANGLE_STATUS_FLOW_CHECKER_REPAIR__"
                    "NO_COMPLETE_ACCEPTED_RESULT"
                ),
                "base_chain": {
                    "attempt_04_source_commit": verifier.ATTEMPT_04_SOURCE_COMMIT,
                    "post_attempt_03_repair_authority": {
                        "path": attempt03_repair_path,
                        "bytes": len(attempt03_repair_bytes),
                        "file_sha256": hashlib.sha256(
                            attempt03_repair_bytes
                        ).hexdigest(),
                        "authority_sha256": attempt03_repair[
                            "authority_sha256"
                        ],
                    },
                    "attempt_04_incident": {
                        "path": attempt04_incident_path,
                        "bytes": len(attempt04_incident_bytes),
                        "file_sha256": hashlib.sha256(
                            attempt04_incident_bytes
                        ).hexdigest(),
                        "classification": (
                            "INDEPENDENT_CHECKER_TRIANGLE_STATUS_FLOW_RULE_"
                            "ENGINEERING_FAILURE"
                        ),
                        "published_failure_artifacts": [
                            {
                                "name": (
                                    "mode_01_capacity_fail_closed_collection_"
                                    "bundle.json"
                                ),
                                "bytes": 1364069,
                                "file_sha256": (
                                    "785b0b9906368eabfecb190b0f6afc0d0768c2b"
                                    "cad00144cd018e5636c0f1d76"
                                ),
                            },
                            {
                                "name": (
                                    "mode_01_capacity_fail_closed_collection_"
                                    "independent_check.json"
                                ),
                                "bytes": 3967,
                                "file_sha256": (
                                    "0c007fea0a8ab28e1ba3fe2f04752126aef28cd"
                                    "6bd181a9213d31de5c3f69876"
                                ),
                                "verdict": "ACCEPT",
                                "property_pass_count": 5,
                            },
                            {
                                "name": "mode_02_all_hit_count_bundle.json",
                                "bytes": 806032,
                                "file_sha256": (
                                    "03e869e83164e3c8dac830111d7dbf17ae97ad0"
                                    "f69e00d3c5cb2f6bca7084739"
                                ),
                            },
                            {
                                "name": (
                                    "mode_02_all_hit_count_"
                                    "independent_check.json"
                                ),
                                "bytes": 3616,
                                "file_sha256": (
                                    "02fbbf9a788b2d8589a6911ce20f07fec0e8e71"
                                    "fec5871e456c898d9888a6b90"
                                ),
                                "verdict": "REJECT",
                                "property_pass_count": 4,
                                "property_reject_count": 1,
                                "reason_id": (
                                    "TC004_STATUS_SOURCE_ANCHOR_MISSING"
                                ),
                            },
                        ],
                    },
                    "formal_observed_counts_through_attempt_04": {
                        "runner_processes_started": 4,
                        "frozen_modes_entered": 5,
                        "public_route_expected_outputs_returned": 5,
                        "published_evidence_bundles": 3,
                        "published_independent_property_reports": 3,
                        "independently_accepted_per_mode_reports": 1,
                        "published_mutation_applications": 0,
                        "accepted_complete_goal5840_results": 0,
                    },
                    "prior_post_failure_gpu_diagnostics": {
                        "diagnostic_processes": 2,
                        "diagnostic_mode_executions": 2,
                        "accepted_as_evidence": 0,
                    },
                    "attempt_04_post_failure_gpu_diagnostics": {
                        "diagnostic_processes": 0,
                        "diagnostic_mode_executions": 0,
                        "accepted_as_evidence": 0,
                    },
                    "attempt_04_post_failure_offline_checker_diagnostics": {
                        "processes": 2,
                        "bundle_checks": 3,
                        "accepted_bundle_checks": 2,
                        "accepted_as_formal_evidence": 0,
                    },
                },
                "repair_scope": {
                    "defect": (
                        "stale_synthetic_triangle_status_flow_text_anchors"
                    ),
                    "repair": (
                        "route_specific_lexically_masked_entry_function_"
                        "status_flow_and_cardinality_checks"
                    ),
                    "allowed_changed_paths": list(
                        verifier.ATTEMPT_04_REPAIR_ALLOWED_CHANGED_PATHS
                    ),
                    "exact_changed_paths_since_base": list(
                        verifier.ATTEMPT_04_REPAIR_ALLOWED_CHANGED_PATHS
                    ),
                    "triangle_fast_and_diagnostic_paths_checked": True,
                    "comment_and_string_spoofing_rejected": True,
                    "route_change_allowed": False,
                    "fixture_or_oracle_change_allowed": False,
                    "declaration_or_control_root_change_allowed": False,
                    "property_or_mutation_change_allowed": False,
                    "native_engine_or_runtime_change_allowed": False,
                    "frozen_core_change_allowed": False,
                },
                "preregistration": pre_pod["preregistration"],
                "source_files": [
                    row
                    for row in source_rows
                    if row["path"] in attempt04_authority_source_paths
                ],
                "goal5838_frozen_core": frozen_core,
                "route_bundle_group_count": 3,
                "required_mode_count": 4,
                "mode_cases": frozen_mode_rows,
                "execution_counts_at_repair_freeze": {
                    "formal_runner_processes": 4,
                    "formal_entered_modes": 5,
                    "formal_returned_expected_outputs": 5,
                    "prior_gpu_diagnostic_processes": 2,
                    "prior_gpu_diagnostic_mode_executions": 2,
                    "published_evidence_bundles": 3,
                    "published_independent_property_reports": 3,
                    "independently_accepted_per_mode_reports": 1,
                    "published_mutation_applications": 0,
                    "accepted_goal5840_complete_results": 0,
                },
                "claim_boundary": {
                    "append_only_engineering_repair_authority": True,
                    "four_prior_formal_failures_preserved": True,
                    "attempt_04_mode_01_acceptance_preserved": True,
                    "attempt_04_incomplete_run_not_accepted_as_goal_result": (
                        True
                    ),
                    "diagnostic_processes_not_accepted_as_evidence": True,
                    "scientific_inputs_unchanged": True,
                    "accepted_goal5840_result": False,
                    "lowering_preservation_established": False,
                    "performance_or_speedup": False,
                    "application_correctness": False,
                    "external_review_or_consensus": False,
                },
                "authority_sha256": "",
            }
            _seal(
                attempt04_repair,
                "authority_sha256",
                verifier.ATTEMPT_04_REPAIR_AUTHORITY_DOMAIN,
            )
            attempt04_repair_path = verifier.ATTEMPT_04_REPAIR_AUTHORITY_PATH
            attempt04_repair_bytes = (
                json.dumps(attempt04_repair, indent=2, sort_keys=True) + "\n"
            ).encode("ascii")

            build_sources = [
                row
                for row in source_rows
                if row["path"] in verifier.NATIVE_BUILD_SOURCE_PATHS
            ]
            build_input = {
                "schema": "synthetic_goal5840_build_input",
                "builder_path": (
                    "scripts/goal5838_build_selected_sphere_optix_provider.py"
                ),
                "builder_sha256": hashlib.sha256(
                    source_blobs[
                        "scripts/goal5838_build_selected_sphere_optix_provider.py"
                    ]
                ).hexdigest(),
            }
            build: dict[str, object] = {
                "schema": (
                    "rtdl.goal5838.selected_sphere_optix_provider_build.v2"
                ),
                "status": (
                    "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED"
                ),
                "repository": {
                    "expected_commit": commit,
                    "head_before": commit,
                    "head_after": commit,
                    "source_files": build_sources,
                },
                "build_input": build_input,
                "build_input_sha256": verifier._digest(build_input),
                "native_output": {
                    "path": str(native_path),
                    "bytes": len(native_bytes),
                    "sha256": native_sha,
                },
                "all_required_symbols_exported": True,
                "result_sha256": "",
            }
            _seal(build, "result_sha256", verifier.NATIVE_BUILD_DOMAIN)
            build_path = directory / "native_build.json"
            build_path.write_text(
                json.dumps(build, indent=2, sort_keys=True) + "\n",
                encoding="ascii",
            )

            source_blobs[preregistration_path] = preregistration_bytes
            source_blobs[pre_pod_path] = pre_pod_bytes
            source_blobs[incident_path] = incident_bytes
            source_blobs[repair_path] = repair_bytes
            source_blobs[attempt02_incident_path] = attempt02_incident_bytes
            source_blobs[attempt02_repair_path] = attempt02_repair_bytes
            source_blobs[attempt03_incident_path] = attempt03_incident_bytes
            source_blobs[attempt03_repair_path] = attempt03_repair_bytes
            source_blobs[attempt04_incident_path] = attempt04_incident_bytes
            source_blobs[attempt04_repair_path] = attempt04_repair_bytes
            repository_rows = [
                {
                    "path": path,
                    "bytes": len(source_blobs[path]),
                    "sha256": hashlib.sha256(source_blobs[path]).hexdigest(),
                }
                for path in sorted(verifier.RESULT_SOURCE_PATHS)
            ]
            dynamic_symbols = set(verifier.GOAL5840_REQUIRED_NATIVE_SYMBOLS)
            dynamic_symbols.add("synthetic_extra_symbol")
            summary: dict[str, object] = {
                "schema": "rtdl.goal5840.true_optix_target_evidence.v5",
                "status": (
                    "PASS__FOUR_MODES_TRUE_OPTIX_AND_15_UNIQUE_MUTATIONS_REJECTED"
                ),
                "formal_attempt_number": 5,
                "repository": {
                    "expected_commit": commit,
                    "head_before": commit,
                    "head_after": commit,
                    "branch": "synthetic",
                    "origin": "synthetic",
                    "clean_before": True,
                    "clean_after": True,
                    "source_files": repository_rows,
                },
                "machine": {"name": "synthetic"},
                "runtime": {"python": "synthetic"},
                "native": {
                    "path": str(native_path),
                    "bytes": len(native_bytes),
                    "sha256": native_sha,
                    "build_manifest": {
                        "path": str(build_path),
                        "bytes": build_path.stat().st_size,
                        "sha256": hashlib.sha256(
                            build_path.read_bytes()
                        ).hexdigest(),
                        "schema": build["schema"],
                        "status": build["status"],
                        "result_sha256": build["result_sha256"],
                    },
                    "goal5840_required_symbol_check": {
                        "schema": "rtdl.goal5840.required_native_symbols.v1",
                        "method": (
                            "gnu_nm_dynamic_external_defined_exact_name"
                        ),
                        "required_symbols": list(
                            verifier.GOAL5840_REQUIRED_NATIVE_SYMBOLS
                        ),
                        "all_required_symbols_exported": True,
                        "exported_symbol_count": len(dynamic_symbols),
                        "exported_symbol_names_sha256": verifier._digest(
                            sorted(dynamic_symbols)
                        ),
                        "nm_path": "/usr/bin/nm",
                    },
                },
                "preregistration": {
                    "path": preregistration_path,
                    "file_sha256": hashlib.sha256(
                        preregistration_bytes
                    ).hexdigest(),
                    "authority_sha256": preregistration[
                        "authority_sha256"
                    ],
                },
                "pre_pod_input_authority": {
                    "path": pre_pod_path,
                    "file_sha256": hashlib.sha256(
                        pre_pod_bytes
                    ).hexdigest(),
                    "authority_sha256": pre_pod["authority_sha256"],
                    "source_commit": verifier.ATTEMPT_01_SOURCE_COMMIT,
                },
                "attempt_01_engineering_failure": {
                    "path": incident_path,
                    "bytes": len(incident_bytes),
                    "file_sha256": hashlib.sha256(
                        incident_bytes
                    ).hexdigest(),
                    "accepted_positive_evidence_rows": 0,
                },
                "post_attempt_01_repair_authority": {
                    "path": repair_path,
                    "file_sha256": hashlib.sha256(
                        repair_bytes
                    ).hexdigest(),
                    "authority_sha256": repair["authority_sha256"],
                },
                "attempt_02_engineering_failure": {
                    "path": attempt02_incident_path,
                    "bytes": len(attempt02_incident_bytes),
                    "file_sha256": hashlib.sha256(
                        attempt02_incident_bytes
                    ).hexdigest(),
                    "accepted_positive_evidence_rows": 0,
                    "diagnostic_launches_accepted_as_evidence": 0,
                },
                "post_attempt_02_repair_authority": {
                    "path": attempt02_repair_path,
                    "file_sha256": hashlib.sha256(
                        attempt02_repair_bytes
                    ).hexdigest(),
                    "authority_sha256": attempt02_repair["authority_sha256"],
                },
                "attempt_03_engineering_failure": {
                    "path": attempt03_incident_path,
                    "bytes": len(attempt03_incident_bytes),
                    "file_sha256": hashlib.sha256(
                        attempt03_incident_bytes
                    ).hexdigest(),
                    "published_failure_bundle_count": 1,
                    "published_reject_report_count": 1,
                    "accepted_positive_evidence_rows": 0,
                    "post_failure_gpu_diagnostic_launches": 0,
                },
                "post_attempt_03_repair_authority": {
                    "path": attempt03_repair_path,
                    "file_sha256": hashlib.sha256(
                        attempt03_repair_bytes
                    ).hexdigest(),
                    "authority_sha256": attempt03_repair["authority_sha256"],
                },
                "attempt_04_engineering_failure": {
                    "path": attempt04_incident_path,
                    "bytes": len(attempt04_incident_bytes),
                    "file_sha256": hashlib.sha256(
                        attempt04_incident_bytes
                    ).hexdigest(),
                    "published_failure_bundle_count": 2,
                    "published_independent_report_count": 2,
                    "independently_accepted_per_mode_report_count": 1,
                    "accepted_complete_goal5840_result_count": 0,
                    "post_failure_gpu_diagnostic_launches": 0,
                },
                "post_attempt_04_repair_authority": {
                    "path": attempt04_repair_path,
                    "file_sha256": hashlib.sha256(
                        attempt04_repair_bytes
                    ).hexdigest(),
                    "authority_sha256": attempt04_repair["authority_sha256"],
                },
                "frozen_core": frozen_core,
                "route_bundle_group_count": 3,
                "required_mode_bundle_count": 4,
                "true_optix_mode_count": 4,
                "independent_property_pass_count": 20,
                "preregistered_unique_mutation_count": 15,
                "mode_replication_mutation_count": 20,
                "mode_cases": mode_rows,
                "runtime_trust_roots_file": trust_path.name,
                "runtime_trust_roots_sha256": trust[
                    "trust_roots_sha256"
                ],
                "mutation_result_file": mutation_path.name,
                "mutation_result_sha256": mutation["report_sha256"],
                "claim_boundary": {
                    "three_bounded_routes_only": True,
                    "four_required_modes": True,
                    "target_side_structural_refinement_evidence": True,
                    "attempt_01_preserved_as_unaccepted_engineering_failure": (
                        True
                    ),
                    "attempt_02_preserved_as_unaccepted_engineering_failure": (
                        True
                    ),
                    "attempt_03_preserved_as_unaccepted_engineering_failure": (
                        True
                    ),
                    "attempt_04_preserved_as_incomplete_engineering_failure": (
                        True
                    ),
                    "attempt_04_mode_01_acceptance_preserved_without_goal_promotion": (
                        True
                    ),
                    "diagnostic_launches_preserved_as_unaccepted_engineering_work": (
                        True
                    ),
                    "append_only_repair_authority_chain_verified": True,
                    "general_compiler_soundness": False,
                    "application_correctness": False,
                    "performance_or_speedup": False,
                    "external_review_or_consensus": False,
                },
                "summary_sha256": "",
            }
            _seal(summary, "summary_sha256", verifier.SUMMARY_DOMAIN)
            result_path = directory / "RESULT.json"
            result_path.write_text(
                json.dumps(summary, indent=2, sort_keys=True) + "\n",
                encoding="ascii",
            )

            def git_blob(_root: Path, observed_commit: str, path: str) -> bytes:
                self.assertIn(
                    observed_commit,
                    {
                        commit,
                        verifier.ATTEMPT_01_SOURCE_COMMIT,
                        verifier.ATTEMPT_01_REPAIR_COMMIT,
                        verifier.ATTEMPT_03_SOURCE_COMMIT,
                        verifier.ATTEMPT_04_SOURCE_COMMIT,
                    },
                )
                return source_blobs[path]

            def changed_paths(
                _root: Path, base: str, observed_commit: str
            ) -> tuple[str, ...]:
                if (
                    base == verifier.ATTEMPT_01_SOURCE_COMMIT
                    and observed_commit == verifier.ATTEMPT_01_REPAIR_COMMIT
                ):
                    return verifier.REPAIR_ALLOWED_CHANGED_PATHS
                if (
                    base == verifier.ATTEMPT_01_REPAIR_COMMIT
                    and observed_commit == verifier.ATTEMPT_03_SOURCE_COMMIT
                ):
                    return verifier.ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS
                if (
                    base == verifier.ATTEMPT_03_SOURCE_COMMIT
                    and observed_commit == verifier.ATTEMPT_04_SOURCE_COMMIT
                ):
                    return verifier.ATTEMPT_03_REPAIR_ALLOWED_CHANGED_PATHS
                if (
                    base == verifier.ATTEMPT_04_SOURCE_COMMIT
                    and observed_commit == commit
                ):
                    return verifier.ATTEMPT_04_REPAIR_ALLOWED_CHANGED_PATHS
                self.fail(
                    f"unexpected synthetic Git diff: {base}..{observed_commit}"
                )

            with patch.object(
                verifier, "_git_blob", side_effect=git_blob
            ), patch.object(
                verifier,
                "_git_changed_paths",
                side_effect=changed_paths,
            ), patch.object(
                verifier,
                "_defined_elf64_dynamic_symbols",
                return_value=dynamic_symbols,
            ):
                report = verifier.verify(
                    result_path,
                    native_path=native_path,
                    native_build_manifest_path=build_path,
                    expected_commit=commit,
                    repository_root=Path.cwd(),
                )
            self.assertEqual(
                report["status"],
                "PASS__DOWNLOADED_GOAL5840_EVIDENCE_REPLAYED_AND_BOUND",
            )
            self.assertEqual(report["verified_mode_count"], 4)
            self.assertEqual(report["replayed_property_pass_count"], 20)
            self.assertEqual(report["verified_unique_mutation_count"], 15)


if __name__ == "__main__":
    unittest.main()
