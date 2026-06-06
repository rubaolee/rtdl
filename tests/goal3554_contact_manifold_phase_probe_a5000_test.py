from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "reports" / "goal3554_contact_manifold_probe_repeat_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3554_contact_manifold_phase_probe_a5000_2026-06-06.md"


class Goal3554ContactManifoldPhaseProbeA5000Test(unittest.TestCase):
    def test_probe_identifies_collect_k_not_broadphase_as_stable_gap(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        v23 = payload["v23"]
        v28 = payload["v28"]

        broadphase_speedup = v23["broadphase_median_of_trials"] / v28["broadphase_median_of_trials"]
        collect_speedup = v23["collect_median"] / v28["collect_median"]
        prepare_speedup = v23["prepare_median"] / v28["prepare_median"]

        self.assertGreater(broadphase_speedup, 0.98)
        self.assertLess(broadphase_speedup, 1.03)
        self.assertLess(collect_speedup, 0.55)
        self.assertGreater(prepare_speedup, 1.1)
        self.assertEqual(len(v23["broadphase_median_trials"]), 3)
        self.assertEqual(len(v28["broadphase_median_trials"]), 3)
        self.assertEqual(len(v23["collect_trials"]), 3)
        self.assertEqual(len(v28["collect_trials"]), 3)

    def test_report_keeps_boundary_and_next_target_generic(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("should not be treated as a stable AABB traversal regression", text)
        self.assertIn("generic bounded witness collection", text)
        self.assertIn("app-agnostic bounded row contract", text)
        self.assertIn("diagnostic evidence only", text)
        self.assertNotIn("public speedup claim authorized", text.lower())


if __name__ == "__main__":
    unittest.main()
