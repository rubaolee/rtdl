from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
GOAL3438_SCRIPT = ROOT / "scripts" / "goal3438_spatial_rayjoin_prepared_subroute_reuse_probe.py"
SCRIPT = ROOT / "scripts" / "goal3441_shape_pair_active_count_phase_timing_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3441_shape_pair_active_count_phase_timings_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3441_shape_pair_active_count_phase_timings_pod_2026-06-05.json"


class Goal3441ShapePairActiveCountPhaseTimingsTest(unittest.TestCase):
    def test_native_surface_exports_generic_shape_pair_timing_accessor(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")

        for phrase in (
            "g_optix_last_shape_pair_left_prepare_s",
            "g_optix_last_shape_pair_left_upload_s",
            "g_optix_last_shape_pair_traversal_s",
            "g_optix_last_shape_pair_flag_download_s",
            "g_optix_last_shape_pair_containment_s",
            "g_optix_last_shape_pair_pair_count",
            "g_optix_last_shape_pair_active_count",
            "rtdl_optix_shape_pair_relation_get_last_phase_timings",
            "reset_shape_pair_relation_phase_timings",
        ):
            self.assertIn(phrase, workloads)
        self.assertIn("rtdl_optix_shape_pair_relation_get_last_phase_timings", prelude)
        self.assertIn("double* containment_out", prelude)
        self.assertIn("size_t* active_count_out", prelude)

    def test_native_count_path_records_phase_breakdown_without_app_terms(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        start = text.index("static ShapePairRelationFlagComputation compute_shape_pair_relation_flags_with_prepared_right_optix")
        end = text.index("static void run_shape_pair_relation_flags_optix", start)
        body = text[start:end]

        for phrase in (
            "left_prepare_start",
            "left_upload_start",
            "traversal_start",
            "download_start",
            "containment_start",
            "g_optix_last_shape_pair_active_count = active_count",
        ):
            self.assertIn(phrase, body)
        for app_term in ("rayjoin", "cdb", "county", "soil"):
            self.assertNotIn(app_term, body.lower())

    def test_python_runtime_exposes_last_phase_timings(self) -> None:
        text = RUNTIME.read_text(encoding="utf-8")

        for phrase in (
            "def last_phase_timings(self) -> dict[str, float | int | str] | None:",
            "def get_last_shape_pair_relation_phase_timings()",
            "def _get_last_shape_pair_relation_phase_timings_from_library",
            "rtdl_optix_shape_pair_relation_get_last_phase_timings",
            '"containment": float(containment.value)',
            '"active_count": int(active_count.value)',
        ):
            self.assertIn(phrase, text)

    def test_app_and_probes_carry_native_phase_timings(self) -> None:
        app = APP.read_text(encoding="utf-8")
        goal3438 = GOAL3438_SCRIPT.read_text(encoding="utf-8")
        goal3441 = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('"native_phase_timings": native_phase_timings', app)
        self.assertIn('"native_phase_timings": payload["native_phase_timings"]', goal3438)
        for phrase in (
            "rtdl.goal3441.shape_pair_active_count_phase_timings.v1",
            "native_phase_timings",
            "containment_sec",
            "traversal_sec",
            "flag_download_sec",
            "[goal3441]",
            "rayjoin_paper_reproduction_claim_authorized",
        ):
            self.assertIn(phrase, goal3441)

    def test_report_records_diagnostic_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3441",
            "diagnostic infrastructure",
            "not a speedup claim",
            "generic shape-pair relation flags",
            "CPU containment supplement",
            "`public_speedup_claim_authorized: False`",
        ):
            self.assertIn(phrase, text)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3441 pod artifact pending")
    def test_pod_artifact_records_phase_breakdown(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3441.shape_pair_active_count_phase_timings.v1")
        self.assertEqual(payload["goal"], 3441)
        self.assertEqual(payload["iterations"], 4)
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))
        self.assertTrue(all(count == payload["active_counts"][0] for count in payload["active_counts"]))
        last = payload["last_native_phase_timings"]
        self.assertEqual(last["mode"], "active_count")
        self.assertGreater(last["pair_count"], 0)
        self.assertEqual(last["active_count"], payload["active_counts"][-1])
        for key in ("left_prepare", "left_upload", "traversal", "flag_download", "containment"):
            self.assertIn(key, last)


if __name__ == "__main__":
    unittest.main()
