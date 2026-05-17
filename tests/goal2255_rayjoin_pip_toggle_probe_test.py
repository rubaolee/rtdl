import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2255_rayjoin_pip_toggle_probe_2026-05-17.md"
DEFAULT = ROOT / "docs" / "reports" / "goal2255_rayjoin_pip_toggle_default_pod_2026-05-17.json"
NO_PREFILTER = ROOT / "docs" / "reports" / "goal2255_rayjoin_pip_toggle_no_prefilter_pod_2026-05-17.json"
NO_ONE_PASS = ROOT / "docs" / "reports" / "goal2255_rayjoin_pip_toggle_no_one_pass_pod_2026-05-17.json"


class Goal2255RayjoinPipToggleProbeTest(unittest.TestCase):
    def _median(self, path: Path) -> float:
        data = json.loads(path.read_text(encoding="utf-8"))
        optix = data["backends"]["optix"]
        self.assertTrue(optix["all_parity_vs_reference"])
        self.assertEqual(set(optix["row_counts"]), {8686})
        return float(optix["elapsed_sec_median"])

    def test_toggles_show_default_fastest(self) -> None:
        default = self._median(DEFAULT)
        no_prefilter = self._median(NO_PREFILTER)
        no_one_pass = self._median(NO_ONE_PASS)

        self.assertLess(default, no_one_pass)
        self.assertLess(default, no_prefilter)
        self.assertGreater(no_prefilter / default, 7.0)
        self.assertGreater(no_one_pass / default, 1.3)

    def test_report_records_design_lesson_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("device-side predicate filtering", text)
        self.assertIn("one-pass compact output", text)
        self.assertIn("device-resident output stream", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
