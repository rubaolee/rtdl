from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import v3_phoenix_component_union_m38_pod_ab as runner


class V3PhoenixM39ComponentUnionHarnessTest(unittest.TestCase):
    def test_dry_run_builds_three_variant_harness_without_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            args = runner.parse_args(
                [
                    "--output-dir",
                    tmpdir,
                    "--dry-run",
                ]
            )
            payload = runner.run_packet(args)

        self.assertEqual(payload["summary"]["status"], runner.STATUS_DRY_RUN_NOT_RELEASE)
        self.assertEqual(set(payload["variants"]), set(runner.ALL_VARIANTS))
        self.assertEqual(payload["comparisons"]["status"], "dry_run_no_performance_interpretation")
        self.assertFalse(payload["summary"]["release_authorized"])
        self.assertFalse(payload["summary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["summary"]["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["summary"]["focused_pod_spend_authorized_now"])
        self.assertFalse(payload["summary"]["all_app_pod_spend_authorized"])
        self.assertTrue(payload["summary"]["same_generated_point_set_enforced"])
        for row in payload["variants"].values():
            self.assertTrue(row["component_labels_contract"])
            self.assertFalse(row["component_signature_substituted_for_labels"])

    def test_serious_scale_and_repeat_gates_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            args = runner.parse_args(
                [
                    "--output-dir",
                    tmpdir,
                    "--point-count",
                    "128",
                    "--dry-run",
                ]
            )
            with self.assertRaises(SystemExit):
                runner.run_packet(args)

            args = runner.parse_args(
                [
                    "--output-dir",
                    tmpdir,
                    "--repeat",
                    "1",
                    "--dry-run",
                ]
            )
            with self.assertRaises(SystemExit):
                runner.run_packet(args)

    def test_runner_command_and_source_use_m37_helper_and_label_routes(self) -> None:
        args = runner.parse_args(["--dry-run", "--require-rt-hardware"])
        command = runner.build_command(args, variant=runner.RUNNER)
        self.assertIn("scripts/v3_phoenix_component_union_m38_pod_ab.py", command)
        self.assertIn("--require-rt-hardware", command)

        source = Path(runner.__file__).read_text(encoding="utf-8")
        self.assertIn("run_radius_graph_component_union_3d_prepared_session", source)
        self.assertIn("fixed_radius_graph_component_labels_3d_v2_8", source)
        self.assertIn("prepare_embree_fixed_radius_count_threshold_3d", source)
        self.assertIn("radius_graph_components_3d_numba_prepared_grid_partner_columns", source)
        self.assertIn("signature_from_numba_label_columns", source)
        self.assertIn("hard_cap_watchdog", source)
        self.assertIn("os._exit(124)", source)
        self.assertNotIn("run_radius_graph_component_signature_3d_prepared_session(", source)

    def test_canonical_signature_ignores_label_ids_but_preserves_counts(self) -> None:
        left = {"cluster_sizes": {"99": 4, "2": 3}, "core_count": 7, "noise_count": 1}
        right = {"cluster_sizes": {"1": 3, "8": 4}, "core_count": 7, "noise_count": 1}
        self.assertEqual(
            runner.canonical_component_signature(left),
            runner.canonical_component_signature(right),
        )

    def test_failure_checks_fail_closed_on_signature_shortcut_or_missing_runner_metadata(self) -> None:
        variants = {
            runner.EMBREE: {
                "status": "ok",
                "component_labels_contract": True,
                "component_signature_substituted_for_labels": False,
                "canonical_component_signature": {"cluster_sizes": (3,), "core_count": 3, "noise_count": 0},
                "hot_query_median_sec": 3.0,
                "runner_inclusive_wall_median_sec": 3.0,
            },
            runner.LEGACY: {
                "status": "ok",
                "component_labels_contract": True,
                "component_signature_substituted_for_labels": False,
                "canonical_component_signature": {"cluster_sizes": (3,), "core_count": 3, "noise_count": 0},
                "hot_query_median_sec": 1.0,
                "runner_inclusive_wall_median_sec": 1.0,
            },
            runner.RUNNER: {
                "status": "ok",
                "component_labels_contract": True,
                "component_signature_substituted_for_labels": True,
                "canonical_component_signature": {"cluster_sizes": (3,), "core_count": 3, "noise_count": 0},
                "hot_query_median_sec": 1.0,
                "runner_inclusive_wall_median_sec": 1.0,
                "runtime_trunk_executes_end_to_end": False,
                "component_union_phase_accounting_visible": False,
                "component_label_columns_present": False,
                "component_signature_pass_executed": True,
            },
        }
        comparisons = runner.comparison_payload(variants)
        self.assertEqual(comparisons["runner_vs_legacy_hot_speedup"], 1.0)
        failed = runner.failure_checks(
            variants,
            comparisons,
            {},
            selected_variants=runner.ALL_VARIANTS,
            dry_run=False,
        )

        self.assertIn(f"{runner.RUNNER}_signature_substituted_for_labels", failed)
        self.assertIn("runner_runtime_trunk_not_end_to_end", failed)
        self.assertIn("runner_component_label_columns_missing", failed)
        self.assertIn("runner_component_signature_pass_executed", failed)

    def test_real_run_payload_status_is_not_dry_run_label(self) -> None:
        args = runner.parse_args(["--allow-non-serious-local-smoke", "--point-count", "128"])
        variants = {
            runner.EMBREE: {
                "status": "ok",
                "component_labels_contract": True,
                "component_signature_substituted_for_labels": False,
                "canonical_component_signature": {"cluster_sizes": (3,), "core_count": 3, "noise_count": 0},
                "hot_query_median_sec": 3.0,
                "runner_inclusive_wall_median_sec": 3.0,
            },
            runner.LEGACY: {
                "status": "ok",
                "component_labels_contract": True,
                "component_signature_substituted_for_labels": False,
                "canonical_component_signature": {"cluster_sizes": (3,), "core_count": 3, "noise_count": 0},
                "hot_query_median_sec": 1.0,
                "runner_inclusive_wall_median_sec": 1.0,
            },
            runner.RUNNER: {
                "status": "ok",
                "component_labels_contract": True,
                "component_signature_substituted_for_labels": False,
                "canonical_component_signature": {"cluster_sizes": (3,), "core_count": 3, "noise_count": 0},
                "hot_query_median_sec": 1.0,
                "runner_inclusive_wall_median_sec": 1.0,
                "runtime_trunk_executes_end_to_end": True,
                "component_union_phase_accounting_visible": True,
                "component_label_columns_present": True,
                "component_signature_pass_executed": False,
            },
        }

        payload = runner.build_payload(
            args=args,
            environment={"hardware_gate": {"status": "not_required"}},
            point_set={"generated_once_in_process": True},
            variant_payloads=variants,
            run_errors={},
            selected_variants=runner.ALL_VARIANTS,
        )

        self.assertEqual(payload["status"], runner.STATUS_RUN_COMPLETE_NOT_RELEASE)
        self.assertEqual(payload["summary"]["status"], runner.STATUS_RUN_COMPLETE_NOT_RELEASE)
        self.assertNotEqual(payload["summary"]["status"], runner.STATUS_DRY_RUN_NOT_RELEASE)


if __name__ == "__main__":
    unittest.main()
