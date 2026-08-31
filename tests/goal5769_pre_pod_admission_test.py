from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from rtdsl import canonical_physical_resolution as canonical_resolution
from rtdsl import default_compiler_frontdoor as compiler_frontdoor
from rtdsl import default_physical_selection as physical_selection

from scripts.goal5769_pre_pod_admission import (
    FORMAL_REVIEW_ABSORPTION_SCHEMA,
    OWNER_DIRECT_FORMAL_AUTHORITY_SCHEMA,
    OWNER_DIRECT_FORMAL_REVIEW_SCHEMA,
    OWNER_DIRECT_PREPARE_AUTHORITY_SCHEMA,
    OWNER_DIRECT_PREPARE_REVIEW_SCHEMA,
    REVIEW_ABSORPTION_SCHEMA,
    canonical_digest,
    validate_formal_authority_files,
    validate_prepare_authority_files,
)
from scripts.goal5768_target_prepare import _digest as prepare_digest
from scripts.goal5768_target_prepare import _validate_receipt
from scripts import goal5768_three_way_frontdoors as three_way


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Goal5769PrePodAdmissionTest(unittest.TestCase):
    def _fixture(self, root: Path):
        review = root / "review.md"
        review.write_text("approve exact successor\n", encoding="utf-8")
        bundle = "1" * 64
        source = "2" * 64
        toolchain = "3" * 64
        tests = "4" * 64
        absorption = {
            "schema": REVIEW_ABSORPTION_SCHEMA,
            "review_kind": "owner_returned_external_review",
            "self_review": False,
            "exact_byte_external_review": True,
            "normalized_review_sha256": _sha(review.read_bytes()),
            "p0": 0,
            "p1": 0,
            "stage_a_create_only_prepare_recommended": True,
            "stage_b_formal_execution_authorized": False,
            "reviewed_bundle_sha256": bundle,
            "reviewed_source_archive_sha256": source,
            "reviewed_toolchain_policy_sha256": toolchain,
            "reviewed_test_manifest_sha256": tests,
        }
        absorption_path = root / "absorption.json"
        absorption_path.write_text(
            json.dumps(absorption, sort_keys=True) + "\n", encoding="utf-8")
        authority = {
            "bundle_sha256": bundle,
            "source_archive_sha256": source,
            "toolchain_policy_sha256": toolchain,
            "test_manifest_sha256": tests,
            "owner_authorized_create_only_prepare": True,
            "required_compute_capability": "89",
            "required_optix_sdk": "9.0.0",
            "required_cuda_toolkit": "12.8",
            "required_gpu_name": "NVIDIA RTX 4000 Ada Generation",
            "required_gpu_uuid": "GPU-fixture",
            "required_driver_version": "580.126.09",
            "required_python_executable_sha256": "5" * 64,
            "formal_worker_allowed": False,
            "registered_formal_timing_allowed": False,
            "stage_b_formal_execution_authorized": False,
            "owner_returned_external_review_sha256": _sha(review.read_bytes()),
            "owner_returned_review_absorption_sha256": _sha(
                absorption_path.read_bytes()),
        }
        authority["authority_sha256"] = canonical_digest(authority)
        args = dict(
            owner_review_path=review,
            review_absorption_path=absorption_path,
            bundle_sha256=bundle, source_sha256=source,
            toolchain_policy_sha256=toolchain,
            test_manifest_sha256=tests, cc="89", optix_sdk="9.0.0",
            cuda_toolkit="12.8")
        return authority, absorption, absorption_path, args

    def test_real_review_and_absorption_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authority, _, _, args = self._fixture(root)
            validate_prepare_authority_files(authority, **args)
            fake = root / "fake.md"
            fake.write_text("self review\n", encoding="utf-8")
            with self.assertRaises(PermissionError):
                validate_prepare_authority_files(
                    authority, **{**args, "owner_review_path": fake})

    def test_wrong_bundle_self_review_p1_and_stage_b_fail_closed(self):
        for mutation in (
            {"reviewed_bundle_sha256": "9" * 64},
            {"self_review": True},
            {"p1": 1},
            {"stage_b_formal_execution_authorized": True},
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                authority, absorption, absorption_path, args = self._fixture(root)
                absorption.update(mutation)
                absorption_path.write_text(
                    json.dumps(absorption, sort_keys=True) + "\n", encoding="utf-8")
                authority["owner_returned_review_absorption_sha256"] = _sha(
                    absorption_path.read_bytes())
                authority.pop("authority_sha256")
                authority["authority_sha256"] = canonical_digest(authority)
                with self.assertRaises(PermissionError):
                    validate_prepare_authority_files(authority, **args)

    def test_well_formed_but_unbacked_digest_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authority, _, _, args = self._fixture(root)
            authority["owner_returned_external_review_sha256"] = "a" * 64
            authority.pop("authority_sha256")
            authority["authority_sha256"] = canonical_digest(authority)
            with self.assertRaises(PermissionError):
                validate_prepare_authority_files(authority, **args)

    def test_owner_direct_successor_requires_exact_delta_and_no_external_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directive = root / "owner_directive.md"
            directive.write_text("continue, preserve failures, final review\n", encoding="utf-8")
            bundle, source, toolchain, tests = (
                "1" * 64, "2" * 64, "3" * 64, "4" * 64)
            review = {
                "schema": OWNER_DIRECT_PREPARE_REVIEW_SCHEMA,
                "review_kind": "strict_internal_self_review",
                "self_review": True,
                "external_review_claimed": False,
                "p0": 0, "p1": 0,
                "stage_a_create_only_prepare_recommended": True,
                "stage_b_formal_execution_authorized": False,
                "successor_bundle_sha256": bundle,
                "successor_source_archive_sha256": source,
                "toolchain_policy_sha256": toolchain,
                "test_manifest_sha256": tests,
                "owner_continuous_directive_sha256": _sha(directive.read_bytes()),
                "baseline_v24_terminal_failure_preserved": True,
                "v4_product_or_native_changed": False,
                "formal_worker_or_timing_reused": False,
                "changed_source_paths": [
                    "scripts/goal5768_formal_controller.py",
                    "scripts/goal5768_target_prepare.py",
                    "scripts/goal5768_three_way_worker.py",
                    "scripts/goal5769_pre_pod_admission.py",
                    "tests/goal5768_formal_harness_test.py",
                    "tests/goal5769_pre_pod_admission_test.py",
                ],
            }
            review_path = root / "internal_review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            authority = {
                "schema": OWNER_DIRECT_PREPARE_AUTHORITY_SCHEMA,
                "owner_continuous_directive_sha256": _sha(directive.read_bytes()),
                "strict_internal_review_sha256": _sha(review_path.read_bytes()),
                "bundle_sha256": bundle,
                "source_archive_sha256": source,
                "toolchain_policy_sha256": toolchain,
                "test_manifest_sha256": tests,
                "owner_authorized_create_only_prepare": True,
                "required_compute_capability": "89",
                "required_optix_sdk": "9.0.0",
                "required_cuda_toolkit": "12.8",
                "required_gpu_name": "NVIDIA RTX 4000 Ada Generation",
                "required_gpu_uuid": "GPU-f2ade1f1-fa77-adbd-7cc2-d92c24a3efef",
                "required_driver_version": "580.173.02",
                "required_python_executable_sha256": "5" * 64,
                "formal_worker_allowed": False,
                "registered_formal_timing_allowed": False,
                "stage_b_formal_execution_authorized": False,
                "external_preexecution_review_claimed": False,
            }
            authority["authority_sha256"] = canonical_digest(authority)
            args = dict(
                owner_review_path=directive,
                review_absorption_path=review_path,
                bundle_sha256=bundle, source_sha256=source,
                toolchain_policy_sha256=toolchain,
                test_manifest_sha256=tests, cc="89", optix_sdk="9.0.0",
                cuda_toolkit="12.8")
            validate_prepare_authority_files(authority, **args)
            authority["external_preexecution_review_claimed"] = True
            authority.pop("authority_sha256")
            authority["authority_sha256"] = canonical_digest(authority)
            with self.assertRaises(PermissionError):
                validate_prepare_authority_files(authority, **args)

    def test_owner_direct_formal_requires_exact_prepared_internal_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directive = root / "owner_directive.md"
            directive.write_text("run exact 312 after strict review\n", encoding="utf-8")
            plan = {
                "plan_sha256": "1" * 64,
                "formal_identity_sha256": "2" * 64,
                "bundle_sha256": "3" * 64,
                "prepared_identity_sha256": "4" * 64,
                "target_identity_sha256": "5" * 64,
            }
            review = {
                "schema": OWNER_DIRECT_FORMAL_REVIEW_SCHEMA,
                "review_kind": "strict_internal_self_review",
                "self_review": True,
                "external_review_claimed": False,
                "p0": 0, "p1": 0,
                "stage_b_formal_execution_recommended": True,
                **{f"reviewed_{key}": value for key, value in plan.items()},
                "reviewed_expected_worker_count": 312,
                "owner_continuous_directive_sha256": _sha(directive.read_bytes()),
                "stage_a_functional_worker_count": 39,
                "stage_a_all_correct_and_behavioral_true_optix": True,
                "formal_observation_reuse_allowed": False,
            }
            review_path = root / "internal_review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            authority = {
                "schema": OWNER_DIRECT_FORMAL_AUTHORITY_SCHEMA,
                "owner_continuous_directive_sha256": _sha(directive.read_bytes()),
                "strict_internal_review_sha256": _sha(review_path.read_bytes()),
                "external_preexecution_review_claimed": False,
            }
            validate_formal_authority_files(
                plan, authority, owner_review_path=directive,
                review_absorption_path=review_path)
            review["reviewed_prepared_identity_sha256"] = "9" * 64
            review_path.write_text(json.dumps(review), encoding="utf-8")
            authority["strict_internal_review_sha256"] = _sha(review_path.read_bytes())
            with self.assertRaises(PermissionError):
                validate_formal_authority_files(
                    plan, authority, owner_review_path=directive,
                    review_absorption_path=review_path)

    def test_formal_review_must_bind_exact_prepared_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            review = root / "prepared_review.md"
            review.write_text("approve exact prepared Stage B\n", encoding="utf-8")
            plan = {
                "plan_sha256": "1" * 64,
                "formal_identity_sha256": "2" * 64,
                "bundle_sha256": "3" * 64,
                "prepared_identity_sha256": "4" * 64,
                "target_identity_sha256": "5" * 64,
            }
            absorption = {
                "schema": FORMAL_REVIEW_ABSORPTION_SCHEMA,
                "review_kind": "owner_returned_external_review",
                "self_review": False,
                "exact_byte_external_review": True,
                "normalized_review_sha256": _sha(review.read_bytes()),
                "p0": 0, "p1": 0,
                "stage_b_formal_execution_recommended": True,
                **{f"reviewed_{key}": value for key, value in plan.items()},
                "reviewed_expected_worker_count": 312,
            }
            absorption_path = root / "prepared_absorption.json"
            absorption_path.write_text(
                json.dumps(absorption, sort_keys=True) + "\n", encoding="utf-8")
            authority = {
                "owner_returned_external_review_sha256": _sha(review.read_bytes()),
                "owner_returned_review_absorption_sha256": _sha(
                    absorption_path.read_bytes()),
            }
            validate_formal_authority_files(
                plan, authority, owner_review_path=review,
                review_absorption_path=absorption_path)
            absorption["reviewed_plan_sha256"] = "9" * 64
            absorption_path.write_text(
                json.dumps(absorption, sort_keys=True) + "\n", encoding="utf-8")
            authority["owner_returned_review_absorption_sha256"] = _sha(
                absorption_path.read_bytes())
            with self.assertRaises(PermissionError):
                validate_formal_authority_files(
                    plan, authority, owner_review_path=review,
                    review_absorption_path=absorption_path)

    def test_canonical_standalone_provider_sources_are_exactly_pinned(self):
        canonical_resolution.current_canonical_provider_registry.cache_clear()
        registry = canonical_resolution.current_canonical_provider_registry()
        root = Path(canonical_resolution.__file__).resolve().parents[2]
        self.assertGreaterEqual(len(registry.standalone_providers), 1)
        for provider in registry.standalone_providers:
            with self.subTest(provider=provider.stable_id):
                self.assertEqual(
                    provider.source_sha256,
                    _sha((root / provider.source_path).read_bytes()),
                )

        original_read_bytes = Path.read_bytes

        def drift_one_source(path: Path) -> bytes:
            payload = original_read_bytes(path)
            if path.as_posix().endswith("src/native/optix/rtdl_optix_workloads.cpp"):
                return payload + b"\n"
            return payload

        canonical_resolution.current_canonical_provider_registry.cache_clear()
        with mock.patch.object(Path, "read_bytes", drift_one_source):
            with self.assertRaisesRegex(
                canonical_resolution.CanonicalPhysicalResolutionError,
                "STANDALONE_PROVIDER_SOURCE_DRIFT",
            ):
                canonical_resolution.current_canonical_provider_registry()
        canonical_resolution.current_canonical_provider_registry.cache_clear()

    def test_direct_grouped_i64_optix_launch_binds_audit_context(self):
        root = Path(canonical_resolution.__file__).resolve().parents[2]
        source = (
            root / "src/native/optix/rtdl_optix_workloads.cpp"
        ).read_text(encoding="utf-8")
        start = source.index(
            "static void "
            "run_prepared_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction_optix("
        )
        end = source.index(
            "static void "
            "run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_optix(",
            start,
        )
        body = source[start:end]
        binding = (
            'rtdl_optix_bind_traversal_audit_context(\n'
            '        "ray_triangle_primitive_grouped_i64_reduction_3d",\n'
            '        prepared->accel.handle);'
        )
        self.assertEqual(body.count(binding), 1)
        self.assertLess(body.index(binding), body.index("OPTIX_CHECK(optixLaunch"))

    def test_prepared_closest_hit_launches_bind_audit_context(self):
        root = Path(canonical_resolution.__file__).resolve().parents[2]
        source = (root / "src/native/optix/rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8")
        binding = (
            'rtdl_optix_bind_traversal_audit_context(\n'
            '        "ray_closest_hit_3d",\n'
            '        prepared->accel.handle);'
        )
        for start_name, end_name in (
            ("launch_prepared_static_triangle_scene_3d_ray_closest_hit_records_optix(",
             "launch_prepared_static_triangle_scene_3d_device_ray_closest_hit_records_optix("),
            ("launch_prepared_static_triangle_scene_3d_device_ray_closest_hit_records_optix(",
             "run_prepared_static_triangle_scene_3d_ray_closest_hit_records_optix("),
        ):
            start = source.index(start_name)
            end = source.index(end_name, start + len(start_name))
            body = source[start:end]
            self.assertEqual(body.count(binding), 1)
            self.assertLess(body.index(binding), body.index("OPTIX_CHECK(optixLaunch"))
        direct_start = source.index("run_ray_closest_hit_3d_optix(")
        direct_end = source.index("static std::string ray_anyhit_kernel_source_3d()", direct_start)
        direct = source[direct_start:direct_end]
        direct_binding = (
            'rtdl_optix_bind_traversal_audit_context(\n'
            '        "ray_closest_hit_3d",\n'
            '        accel.handle);'
        )
        self.assertEqual(direct.count(direct_binding), 1)
        self.assertLess(
            direct.index(direct_binding), direct.index("OPTIX_CHECK(optixLaunch"))

    def test_all_default_source_authority_pins_match_current_bytes(self):
        root = Path(canonical_resolution.__file__).resolve().parents[2]
        for relative, expected in sorted(physical_selection._SOURCE_PINS.items()):
            with self.subTest(relative=relative):
                self.assertEqual(expected, _sha((root / relative).read_bytes()))
        self.assertEqual(
            compiler_frontdoor._WORKLOADS_SHA,
            _sha((root / compiler_frontdoor._WORKLOADS).read_bytes()),
        )
        self.assertEqual(
            compiler_frontdoor._CORE_SHA,
            _sha((root / compiler_frontdoor._CORE).read_bytes()),
        )

    def test_all_predecessor_python_entrypoints_are_import_complete(self):
        for lane in three_way.LANES:
            if lane.app in {"triangle_counting", "particle_tracking"}:
                continue
            with self.subTest(lane=lane.lane_id):
                self.assertIsNotNone(
                    three_way._module(lane, "rtdl3_whole_app.py", "import_gate")
                )
        xhd = three_way.LANE_BY_ID["xhd__global_witness"]
        xhd_v2 = three_way._module(
            xhd, "v2_true_optix_direct.py", "v2_import_gate")
        self.assertIsNotNone(xhd_v2._historical_cell_mbr_module())

    def test_target_prepare_bootstraps_fresh_source_src_before_frontdoor_import(self):
        root = Path(canonical_resolution.__file__).resolve().parents[2]
        source = (root / "scripts/goal5768_target_prepare.py").read_text(
            encoding="utf-8")
        bootstrap = 'sys.path.insert(0, str(source / "src"))'
        frontdoor_import = (
            "from scripts.goal5768_three_way_frontdoors import LANES")
        self.assertEqual(source.count(bootstrap), 1)
        self.assertLess(source.index(bootstrap), source.index(frontdoor_import))

    def test_target_prepare_binds_exact_gpu_uuid_not_only_model_driver_and_cc(self):
        root = Path(canonical_resolution.__file__).resolve().parents[2]
        source = (root / "scripts/goal5768_target_prepare.py").read_text(
            encoding="utf-8")
        self.assertIn(
            'authority["required_gpu_uuid"] != gpu_columns[1]', source)

    def test_target_prepare_never_relabels_owner_direct_review_as_external(self):
        root = Path(canonical_resolution.__file__).resolve().parents[2]
        source = (root / "scripts/goal5768_target_prepare.py").read_text(
            encoding="utf-8")
        self.assertIn(
            '"owner_direct_after_strict_internal_review__not_external_review"',
            source)
        self.assertNotIn(
            '"owner_returned_external_review_sha256": _sha(', source)
        self.assertIn('"external_preexecution_review_claimed": (', source)

    def test_target_prepare_receipt_gate_matches_strict_recount_invariants(self):
        native = "a" * 64
        snapshot = {
            "attempted_launch_count": 2,
            "successful_launch_count": 2,
            "complete_context_launch_count": 2,
            "context_bind_count": 2,
            "failed_launch_count": 0,
            "incomplete_context_launch_count": 0,
            "incomplete_callsite_record_count": 0,
            "pending_context_at_finish": 0,
            "session_error": 0,
            "first_traversable": 1,
            "last_traversable": 1,
            "first_program_bundle_id": 2,
            "last_program_bundle_id": 2,
            "raygen_invocation_count": 17,
        }

        def endpoint(current: dict[str, int]) -> dict[str, object]:
            body = {
                "physical_executor_classification":
                    "optix_traversal_observed",
                "native_snapshot": current,
            }
            return {
                "matched": True,
                "native_library_sha256": native,
                "traversal_receipt": {
                    **body, "receipt_sha256": prepare_digest(body),
                },
            }

        _validate_receipt(endpoint(snapshot), native)
        for name, value in (
            ("attempted_launch_count", 3),
            ("context_bind_count", 1),
            ("incomplete_callsite_record_count", 1),
            ("raygen_invocation_count", 0),
        ):
            with self.subTest(name=name):
                malformed = {**snapshot, name: value}
                with self.assertRaises(RuntimeError):
                    _validate_receipt(endpoint(malformed), native)


if __name__ == "__main__":
    unittest.main()
