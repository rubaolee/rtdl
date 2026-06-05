from __future__ import annotations

from pathlib import Path
import json
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "README.md"
SCRIPT = ROOT / "scripts" / "goal3438_spatial_rayjoin_prepared_subroute_reuse_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3438_spatial_rayjoin_prepared_subroute_reuse_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3438_spatial_rayjoin_prepared_subroute_reuse_pod_2026-06-05.json"


class Goal3438SpatialRayJoinPreparedSubrouteReuseTest(unittest.TestCase):
    def test_app_exposes_overlay_seed_prepared_active_count_handle(self) -> None:
        text = APP.read_text(encoding="utf-8")

        for phrase in (
            "class PreparedRayJoinOptixShapePairActiveCount",
            "def prepare_rayjoin_optix_shape_pair_active_count",
            "def pack_rayjoin_optix_shape_pair_active_count_left_shapes",
            "def run_rayjoin_prepared_optix_shape_pair_active_count_workload",
            '"prepared_optix_shape_pair_active_count"',
            "prepared_optix_shape_pair_active_count_reuse",
            "shape_pair_active_count_complete",
            '"v2_8_release_authorized": False',
            '"rt_core_speedup_claim_authorized": False',
        ):
            self.assertIn(phrase, text)

        self.assertIn("prepare_shape_pair_relation_flags_optix", text)
        self.assertIn("self._prepared.count_active(packed_left.packed_polygons)", text)
        self.assertIn("full overlay row continuation remains a separate route", text)

    def test_readme_documents_overlay_reuse_without_full_overlay_claim(self) -> None:
        text = README.read_text(encoding="utf-8")

        for phrase in (
            "prepare_rayjoin_optix_shape_pair_active_count",
            "pack_rayjoin_optix_shape_pair_active_count_left_shapes",
            "prepared shape-pair active-count handle",
            "generic prepared shape-pair relation flags",
            "full overlay",
            "row continuation remains a separate app-layer concern",
        ):
            self.assertIn(phrase, text)

    def test_v2_8_gap_matrix_records_reusable_subroute_family(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("reusable prepared handles", spatial["current_best_path"])
        self.assertIn("overlay-seed active-count summaries", spatial["current_best_path"])
        self.assertIn("prepared/reusable route shape now covers PIP, LSI, and overlay-seed", spatial["current_bottleneck"])
        self.assertIn("full overlay rows", spatial["current_bottleneck"])
        for goal in ("Goal3435", "Goal3438"):
            self.assertIn(goal, spatial["evidence_refs"])
        self.assertFalse(spatial["release_authorized"])
        self.assertFalse(spatial["public_speedup_claim_authorized"])
        self.assertFalse(spatial["rt_core_speedup_claim_authorized"])
        self.assertFalse(spatial["true_zero_copy_claim_authorized"])

    def test_probe_script_covers_all_three_prepared_subroutes(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3438.spatial_rayjoin_prepared_subroute_reuse.v1",
            "prepare_rayjoin_optix_cupy_refined_pip",
            "prepare_rayjoin_optix_compact_grouped_count_segments",
            "prepare_rayjoin_optix_shape_pair_active_count",
            "prepared_optix_cupy_refined_pip_reuse_handle",
            "prepared_optix_left_id_dense_count_reuse",
            "prepared_optix_shape_pair_active_count_reuse",
            "[goal3438:pip]",
            "[goal3438:lsi]",
            "[goal3438:overlay]",
            "rayjoin_paper_reproduction_claim_authorized",
        ):
            self.assertIn(phrase, text)

    def test_report_records_scope_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3438",
            "PreparedRayJoinOptixShapePairActiveCount",
            "prepared/repeated shape",
            "PIP, LSI, and overlay-seed",
            "generic shape-pair active-count",
            "Full overlay row continuation remains unsolved",
            "`release_authorized: False`",
            "`rt_core_speedup_claim_authorized: False`",
        ):
            self.assertIn(phrase, text)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3438 pod artifact pending")
    def test_pod_artifact_records_three_subroutes(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3438.spatial_rayjoin_prepared_subroute_reuse.v1")
        self.assertEqual(payload["goal"], 3438)
        self.assertEqual(payload["iterations"], 4)
        self.assertEqual(
            sorted(payload["routes"]),
            ["lsi_dense_count", "overlay_active_count", "pip"],
        )
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))
        self.assertTrue(all(run["prepared_reuse"]["enabled"] for run in payload["routes"]["pip"]["runs"]))
        self.assertTrue(all(run["prepared_reuse"]["enabled"] for run in payload["routes"]["lsi_dense_count"]["runs"]))
        self.assertTrue(all(run["prepared_reuse"]["enabled"] for run in payload["routes"]["overlay_active_count"]["runs"]))


if __name__ == "__main__":
    unittest.main()
