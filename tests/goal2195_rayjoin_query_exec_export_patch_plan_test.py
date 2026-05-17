from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2195_rayjoin_query_exec_export_patch_plan_2026-05-17.md"
PATCH = ROOT / "docs" / "reports" / "goal2195_rayjoin_query_exec_export_patch_2026-05-17.diff"


class Goal2195RayjoinQueryExecExportPatchPlanTest(unittest.TestCase):
    def test_patch_adds_query_stream_output_flag_and_schema(self) -> None:
        patch = PATCH.read_text(encoding="utf-8")

        self.assertIn("DEFINE_string(query_stream_output", patch)
        self.assertIn("DECLARE_string(query_stream_output", patch)
        self.assertIn("config.query_stream_output = FLAGS_query_stream_output", patch)
        self.assertIn("rtdl.rayjoin.same_query_stream.v1", patch)
        self.assertIn("rayjoin_query_exec_export_patch", patch)

    def test_patch_exports_lsi_and_pip_queries(self) -> None:
        patch = PATCH.read_text(encoding="utf-8")

        self.assertIn("MaybeExportLSIQueryStream(config, points, edges)", patch)
        self.assertIn("MaybeExportPIPQueryStream(config, unscaled_points)", patch)
        self.assertIn('\\"x0\\"', patch)
        self.assertIn('\\"x1\\"', patch)
        self.assertIn('\\"x\\"', patch)
        self.assertIn("edge.eid", patch)

    def test_report_preserves_boundaries_and_next_pod_step(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("external RayJoin comparison checkout only", text)
        self.assertIn("git apply --check", text)
        self.assertIn("no RTDL native engine change", text)
        self.assertIn("not yet been compiled or run on the RTX pod", text)
        self.assertIn("ready for pod validation", text)
        self.assertIn("scripts/goal2192_rayjoin_same_query_stream_runner.py run-stream", text)


if __name__ == "__main__":
    unittest.main()
