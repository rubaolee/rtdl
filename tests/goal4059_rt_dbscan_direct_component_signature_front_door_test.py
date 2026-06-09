from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
FRONT_DOOR = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4059_rt_dbscan_direct_component_signature_front_door_2026-06-08.md"
POD_PROBE = ROOT / "docs" / "reports" / "goal4059_direct_numba_component_signature_front_door_pod_probe.json"


class Goal4059RtDbscanDirectComponentSignatureFrontDoorTest(unittest.TestCase):
    def test_public_front_door_and_lower_adapter_are_exported(self) -> None:
        self.assertTrue(hasattr(rt, "fixed_radius_graph_component_size_signature_3d_v2_8"))
        self.assertTrue(
            hasattr(
                rt,
                "radius_graph_component_signature_3d_optix_numba_prepared_grouped_stream_partner_columns",
            )
        )
        self.assertIn("fixed_radius_graph_component_size_signature_3d_v2_8", rt.__all__)
        self.assertIn(
            "radius_graph_component_signature_3d_optix_numba_prepared_grouped_stream_partner_columns",
            rt.__all__,
        )

    def test_lower_adapter_counts_parent_workspace_without_app_vocab(self) -> None:
        source = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("def _numba_radius_graph_component_signature_kernel", source)
        self.assertIn("def run_component_signature", source)
        self.assertIn("direct_root_count_from_parent_workspace_and_border_candidates", source)
        self.assertIn("materializes_component_labels", source)
        self.assertIn("label_counts", source)
        signature_section = source[source.index("def _numba_radius_graph_component_signature_kernel") :]
        signature_section = signature_section[: signature_section.index("_CUPY_RADIUS_GRAPH_COMPONENTS_3D_ADJACENCY_KERNELS")]
        self.assertNotIn("dbscan", signature_section.lower())
        self.assertNotIn("cluster", signature_section.lower())

    def test_front_door_exposes_signature_contract_without_hidden_dispatch(self) -> None:
        source = FRONT_DOOR.read_text(encoding="utf-8")

        self.assertIn("fixed_radius_graph_component_size_signature_3d_v2_8", source)
        self.assertIn("grouped_stream_component_size_signature_3d", source)
        self.assertIn("component-size signature front door currently requires partner='numba'", source)
        self.assertIn('"operation": "fixed_radius_graph_component_size_signature_3d"', source)
        self.assertIn('"automatic_partner_selection_allowed": False', source)
        self.assertIn('"app_specific_engine_logic_allowed": False', source)

    def test_rt_dbscan_numba_column_signature_uses_direct_front_door(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("rt.fixed_radius_graph_component_size_signature_3d_v2_8", source)
        self.assertIn("_cluster_signature_from_numba_signature_count_columns", source)
        self.assertIn("numba_direct_component_signature_counts", source)
        self.assertIn("column_signature_uses_numba_direct_component_signature", source)
        self.assertNotIn('"native_dbscan_abi_added": True', source)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal4059",
            "signature-only continuation",
            "fixed_radius_graph_component_size_signature_3d_v2_8",
            "does not add a DBSCAN native ABI",
            "does not choose a partner automatically",
            "materializes_component_labels: false",
        ):
            self.assertIn(phrase, text)

    def test_pod_probe_records_direct_signature_evidence_without_release_claims(self) -> None:
        data = json.loads(POD_PROBE.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], "Goal4059")
        self.assertEqual(data["commit"], "16be56b7")
        self.assertTrue(data["validation"]["matches_reference"])
        self.assertEqual(
            data["validation"]["strategy"],
            "numba_direct_component_signature_counts",
        )
        self.assertFalse(data["validation"]["materializes_component_labels"])
        self.assertGreater(
            data["prior_comparison"]["speedup_vs_prior_baseline"],
            1.0,
        )
        self.assertIn("not a release or paper speedup claim", data["prior_comparison"]["boundary"])
        for value in data["claim_boundary"].values():
            self.assertFalse(value)
        for row in data["timing_rows"]:
            self.assertEqual(row["strategy"], "numba_direct_component_signature_counts")
            self.assertFalse(row["materializes_component_labels"])
            self.assertFalse(row["materializes_point_ids"])
            self.assertFalse(row["materializes_core_flags"])


if __name__ == "__main__":
    unittest.main()
