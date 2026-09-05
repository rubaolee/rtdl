import copy
import unittest
from pathlib import Path

from experiments.goal5847_aot_startup.contracts import (
    PYOPTIX_ARM,
    RTDL_ARM,
    expected_schedule,
)
from rtdsl import physical_execution_provenance as provenance
from scripts import goal5847_run_aot_startup_comparison as controller

ROOT = Path(__file__).resolve().parents[1]


class Goal5847AotStartupExperimentTest(unittest.TestCase):
    @staticmethod
    def _full_relation_receipt() -> dict[str, object]:
        bundle = "v4_custom_aabb_bounded_relation_composed"
        bundle_id = provenance.physical_program_bundle_id(bundle)
        mix = provenance._native_audit_mix_u64
        snapshot_items = (
            ("nonce_hi", 17),
            ("nonce_lo", 29),
            ("attempted_launch_count", 2),
            ("successful_launch_count", 2),
            ("failed_launch_count", 0),
            ("complete_context_launch_count", 2),
            ("incomplete_context_launch_count", 0),
            ("context_bind_count", 2),
            ("raygen_invocation_count", 8192),
            ("program_bundle_mix", mix(mix(0, bundle_id), bundle_id)),
            ("traversable_mix", mix(mix(0, 101), 103)),
            ("pipeline_mix", 1),
            ("sbt_mix", 1),
            ("stream_mix", 1),
            ("params_mix", 1),
            ("callsite_mix", 1),
            ("first_program_bundle_id", bundle_id),
            ("last_program_bundle_id", bundle_id),
            ("first_traversable", 101),
            ("last_traversable", 103),
            ("pending_context_at_finish", 0),
            ("session_error", 0),
            ("incomplete_callsite_record_count", 0),
            ("incomplete_callsite_lines", (0,) * 32),
        )
        return provenance.CapturedTraversalObservation(
            provider_library_path=Path("/evidence/librtdl_optix.so"),
            provider_library_sha256="a" * 64,
            nonce_hi=17,
            nonce_lo=29,
            physical_executor_classification="optix_traversal_observed",
            expected_program_bundles=(bundle,),
            expected_program_bundle_ids=(bundle_id,),
            expected_program_observed_at_receipt_edge=True,
            native_snapshot_items=snapshot_items,
        ).build_receipt(
            semantic_digest="b" * 64,
            output_digest="c" * 64,
            route_identity="v4_callback_ir:custom_aabb_bounded_relation_v1",
        )

    def test_schedule_is_balanced_and_alternating(self):
        schedule = expected_schedule(8)
        self.assertEqual(len(schedule), 16)
        for block in range(8):
            rows = schedule[2 * block:2 * block + 2]
            self.assertEqual({row[2] for row in rows}, {RTDL_ARM, PYOPTIX_ARM})
            self.assertEqual(
                rows[0][2], RTDL_ARM if block % 2 == 0 else PYOPTIX_ARM
            )

    def test_performance_gates_are_explicit_and_retain_every_sample(self):
        self.assertEqual(controller.BLOCKS, 8)
        self.assertEqual(controller.WARMUPS, 16)
        self.assertEqual(controller.REPETITIONS, 128)
        self.assertEqual(controller.PRIMARY_MEDIAN_RATIO_LIMIT, 0.50)
        self.assertEqual(controller.PRIMARY_WORST_RATIO_LIMIT, 0.75)
        self.assertEqual(controller.POST_IMPORT_MEDIAN_RATIO_LIMIT, 3.0)
        self.assertEqual(controller.POST_IMPORT_WORST_RATIO_LIMIT, 4.0)
        self.assertEqual(controller.STEADY_RATIO_LIMIT, 0.20)

    def test_worker_uses_precompiled_pyoptix_and_public_rtdlexe_surface(self):
        source = (
            ROOT / "experiments/goal5847_aot_startup/worker.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("compile_ptx(", source)
        self.assertIn("DEVICE_CONTEXT_VALIDATION_MODE_OFF", source)
        rtdl_body = source.split("def _run_rtdl(", 1)[1].split(
            "\ndef _run_pyoptix(", 1
        )[0]
        for private_escape in (
            "provider._binding_library",
            "prepared._owner",
            "prepared._handle",
        ):
            self.assertNotIn(private_escape, rtdl_body)
        self.assertIn("provider.runtime_compiler_attempt_count", rtdl_body)
        self.assertIn("deployment.begin_provider_initialization", rtdl_body)
        self.assertIn("runtime.load_rtdlexe", rtdl_body)

    def test_candidate_builder_uses_public_family_export(self):
        source = (
            ROOT / "scripts/goal5847_build_aot_candidates.py"
        ).read_text(encoding="utf-8")
        self.assertIn("build_family_rtdlexe(", source)
        self.assertNotIn("._handle", source)
        self.assertNotIn("._materialized", source)
        self.assertIn("TEST_ONLY_goal5847_", source)

    def test_controller_starts_parent_clock_before_worker_spawn(self):
        source = Path(controller.__file__).read_text(encoding="utf-8")
        start = source.index('environment["GOAL5847_CONTROLLER_START_NS"]')
        spawn = source.index("completed = subprocess.run(", start)
        self.assertLess(start, spawn)
        self.assertIn('"discarded_samples": 0', source)

    def test_worker_excludes_git_and_nvidia_smi_instrumentation_from_primary(self):
        source = (
            ROOT / "experiments/goal5847_aot_startup/worker.py"
        ).read_text(encoding="utf-8")
        main = source.split("def main() -> None:", 1)[1]
        execution = main.index("measurements = (")
        endpoint = main.index("process_to_correct =", execution)
        git_audit = main.index("source = _git_identity(root)", endpoint)
        hardware_audit = main.index("hardware = _hardware()", endpoint)
        self.assertLess(execution, endpoint)
        self.assertLess(endpoint, git_audit)
        self.assertLess(endpoint, hardware_audit)

    def test_rtdl_steady_has_no_private_oracle_or_extra_preconditioning_run(self):
        source = (
            ROOT / "experiments/goal5847_aot_startup/worker.py"
        ).read_text(encoding="utf-8")
        rtdl = source.split("def _run_rtdl(", 1)[1].split(
            "\ndef _run_pyoptix(", 1
        )[0]
        batch = rtdl.split("batch, phases", 1)[1].split(
            "provider, phases", 1
        )[0]
        self.assertNotIn("expected_rows=", batch)
        steady = rtdl.index("steady, latest = _sample(")
        diagnostic = rtdl.index("diagnostic = prepared.execute(")
        self.assertLess(steady, diagnostic)

    def test_rtdlexe_owner_reuses_preallocated_storage_and_canonical_rows(self):
        source = (ROOT / "src/rtdsl/v4_rtdlexe.py").read_text(
            encoding="utf-8"
        )
        owner = source.split("class _PreparedBoundedOwner:", 1)[1].split(
            "class _PreparedTriangleOwner:", 1
        )[0]
        self.assertIn("self._row_storage =", owner)
        self.assertIn("rows_native = self._row_storage", owner)
        self.assertIn("packed_rows == self._cached_output_packed", owner)
        self.assertIn("rows = self._cached_output_rows", owner)
        commit = owner.index(
            "self._commit_source_cache(batch._device_input_sha256)"
        )
        publish = owner.index("self._cached_output_packed,", commit)
        self.assertLess(commit, publish)

    def test_controller_enforces_every_preregistered_binary_binding(self):
        source = Path(controller.__file__).read_text(encoding="utf-8")
        for field in (
            "candidate_manifest_sha256",
            "candidate_manifest_seal",
            "native_library_sha256",
            "relation_artifact_sha256",
            "triangle_artifact_sha256",
            "precompiled_ptx_sha256",
            "pyoptix_build_receipt_sha256",
            "pyoptix_build_receipt_internal_seal",
            "pyoptix_commit",
            "pyoptix_tree",
        ):
            self.assertIn(f'bindings.get("{field}")', source)
        self.assertIn('evidence.get("raw_event_count") != 8192', source)

    def test_controller_revalidates_full_nested_traversal_receipt(self):
        receipt = self._full_relation_receipt()
        controller._validate_rtdl_traversal_receipt(
            receipt,
            provider_library_sha256="a" * 64,
            output_sha256="c" * 64,
        )

        forged = copy.deepcopy(receipt)
        forged["native_snapshot"]["successful_launch_count"] = 1
        body = dict(forged)
        body.pop("receipt_sha256")
        forged["receipt_sha256"] = provenance._stable_digest(body)
        with self.assertRaisesRegex(RuntimeError, "native snapshot differs"):
            controller._validate_rtdl_traversal_receipt(
                forged,
                provider_library_sha256="a" * 64,
                output_sha256="c" * 64,
            )


if __name__ == "__main__":
    unittest.main()
