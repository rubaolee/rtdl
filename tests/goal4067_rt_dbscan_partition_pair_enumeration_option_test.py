from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from examples.current.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    run_rt_dbscan_benchmark,
)


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal4067_rt_dbscan_partition_pair_enumeration_option_2026-06-09.md"
POD_SMOKE = ROOT / "docs" / "reports" / "goal4067_rt_dbscan_partition_pair_enumeration_option_pod_smoke.json"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


class Goal4067RtDbscanPartitionPairEnumerationSourceTest(unittest.TestCase):
    def test_app_docs_and_report_expose_explicit_count_then_emit_option(self) -> None:
        text = APP.read_text(encoding="utf-8") + "\n" + README.read_text(encoding="utf-8") + "\n" + REPORT.read_text(encoding="utf-8")
        for fragment in (
            "--partition-pair-enumeration",
            "device_count_then_emit",
            "mode_default",
            "partition_pair_enumeration_user_selection",
            "partition_pair_enumeration_effective",
            "partition_pair_enumeration_explicit_override",
            "partition_pair_enumeration_default_route_changed",
            "opt-in preview",
            "not a default-route promotion",
            "goal4067_rt_dbscan_partition_pair_enumeration_option_pod_smoke.json",
        ):
            self.assertIn(fragment, text)

    def test_invalid_partition_pair_enumeration_fails_before_cupy_is_needed(self) -> None:
        with self.assertRaisesRegex(ValueError, "partition_pair_enumeration must be"):
            run_rt_dbscan_benchmark(
                mode="partner_cupy_prepared_partition_convergence_component_signature_3d",
                dataset="tiny",
                point_count=None,
                radius=None,
                min_neighbors=None,
                seed=20260519,
                partner="cupy",
                include_rows=False,
                validate=False,
                partition_pair_enumeration="not_a_mode",
            )

    def test_signature_mode_still_rejects_python_rows_with_explicit_pair_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "signature mode does not materialize Python rows"):
            run_rt_dbscan_benchmark(
                mode="partner_cupy_prepared_partition_convergence_component_signature_3d",
                dataset="tiny",
                point_count=None,
                radius=None,
                min_neighbors=None,
                seed=20260519,
                partner="cupy",
                include_rows=True,
                validate=False,
                partition_pair_enumeration="device_count_then_emit",
            )


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4067RtDbscanPartitionPairEnumerationRuntimeTest(unittest.TestCase):
    def test_prepared_signature_mode_can_request_count_then_emit(self) -> None:
        payload = run_rt_dbscan_benchmark(
            mode="partner_cupy_prepared_partition_convergence_component_signature_3d",
            dataset="tiny",
            point_count=None,
            radius=None,
            min_neighbors=None,
            seed=20260519,
            partner="cupy",
            include_rows=False,
            validate=True,
            partition_pair_enumeration="device_count_then_emit",
        )

        self.assertTrue(payload["matches_reference"])
        self.assertFalse(payload["claim_boundary"]["full_dbscan"])
        self.assertFalse(payload["claim_boundary"]["rt_core_accelerated"])
        metadata = payload["metadata"]
        self.assertEqual(metadata["partition_pair_enumeration_user_selection"], "device_count_then_emit")
        self.assertEqual(metadata["partition_pair_enumeration_effective"], "device_count_then_emit")
        self.assertTrue(metadata["partition_pair_enumeration_explicit_override"])
        self.assertFalse(metadata["partition_pair_enumeration_default_route_changed"])
        self.assertTrue(metadata["prepared_partition_summary_app_mode"])
        self.assertTrue(metadata["prepared_partition_summary_reused"])
        self.assertFalse(metadata["partition_convergence_hybrid_promoted"])
        self.assertFalse(metadata["current_default_route"])
        self.assertFalse(metadata["full_dbscan_semantics"])
        self.assertTrue(metadata["graph_component_contract_only"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])


class Goal4067RtDbscanPartitionPairEnumerationPodArtifactTest(unittest.TestCase):
    def test_pod_smoke_records_count_then_emit_selection_and_closed_claims(self) -> None:
        payload = json.loads(POD_SMOKE.read_text(encoding="utf-8"))

        self.assertEqual(payload["mode"], "partner_cupy_prepared_partition_convergence_component_signature_3d")
        self.assertEqual(payload["dataset"], "tiny")
        self.assertTrue(payload["matches_reference"])
        self.assertFalse(payload["claim_boundary"]["full_dbscan"])
        self.assertFalse(payload["claim_boundary"]["rt_core_accelerated"])
        self.assertFalse(payload["claim_boundary"]["paper_speedup_claim_authorized"])
        metadata = payload["metadata"]
        self.assertEqual(metadata["partition_pair_enumeration_user_selection"], "device_count_then_emit")
        self.assertEqual(metadata["partition_pair_enumeration_effective"], "device_count_then_emit")
        self.assertEqual(metadata["partition_summary_pair_enumeration"], "device_count_then_emit")
        self.assertEqual(metadata["partition_summary_pair_capacity_source"], "device_exact_count")
        self.assertTrue(metadata["partition_pair_enumeration_explicit_override"])
        self.assertFalse(metadata["partition_pair_enumeration_default_route_changed"])
        self.assertFalse(metadata["partition_convergence_hybrid_promoted"])
        self.assertFalse(metadata["current_default_route"])
        digest = metadata["prepared_partition_summary_digest"]
        self.assertEqual(digest["pair_enumeration"], "device_count_then_emit")
        self.assertEqual(digest["pair_capacity_source"], "device_exact_count")
        self.assertEqual(digest["pair_capacity"], max(1, digest["pair_count"]))


if __name__ == "__main__":
    unittest.main()
