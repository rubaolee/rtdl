from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUN_CASE_SCRIPT = ROOT / "scripts" / "goal2642_barnes_hut_embree_vs_optix_lowering_perf.py"
HARNESS_SCRIPT = ROOT / "scripts" / "goal2803_barnes_hut_v25_consolidated_harness.py"
REPORT = ROOT / "docs" / "reports" / "goal2851_barnes_hut_harness_progress_logging_2026-05-31.md"


class Goal2851BarnesHutHarnessProgressLoggingTest(unittest.TestCase):
    def test_underlying_run_case_accepts_progress_callback(self) -> None:
        source = RUN_CASE_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("Callable[[str], None] | None", source)
        self.assertIn("progress_callback: Callable[[str], None] | None = None", source)
        self.assertIn("backend={backend} repeat={repeat_index + 1}/{repeats} start", source)
        self.assertIn("backend={backend} repeat={repeat_index + 1}/{repeats} ", source)
        self.assertIn("done sec=", source)

    def test_goal2803_routes_progress_around_suppressed_json(self) -> None:
        source = HARNESS_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("def _case_progress(message: str) -> None:", source)
        self.assertIn("file=sys.stderr", source)
        self.assertIn("membership case {index + 1}/{len(cases)} progress", source)
        self.assertIn("progress_callback=_case_progress", source)
        self.assertIn("contextlib.redirect_stdout", source)

    def test_report_records_boundary_and_pod_smoke(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2851",
            "progress_callback",
            "suppressed per-case JSON",
            "not a performance change",
            "not a public speedup claim",
            "pod smoke",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
