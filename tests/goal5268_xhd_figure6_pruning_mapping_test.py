from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_DIR / "results"
MAPPING = RESULTS / "xhd_goal5268_figure6_pruning_phase_counter_mapping_2026-07-09.json"


class Goal5268XhdFigure6PruningMappingTest(unittest.TestCase):
    def _load(self, path: Path) -> dict[str, object]:
        if not path.exists():
            self.skipTest(f"missing artifact: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_mapping_keeps_figure6_unreproduced(self) -> None:
        payload = self._load(MAPPING)

        self.assertEqual(payload["schema"], "rtdl.paper_reproduction.xhd.figure6_pruning_phase_counter_mapping.v1")
        self.assertEqual(payload["status"], "figure6_mapping_ready__figure6_not_reproduced")
        claim = payload["claim_boundary"]
        self.assertFalse(claim["figure6_reproduced"])
        self.assertFalse(claim["full_paper_reproduction_claimed"])
        self.assertFalse(claim["exact_paper_dataset_identity_claimed"])
        self.assertFalse(claim["performance_ratio_claimed"])

    def test_author_source_mapping_identifies_required_flags_and_fields(self) -> None:
        payload = self._load(MAPPING)
        mapping = payload["author_source_mapping"]

        self.assertIn("--eb", mapping["flags"]["relevant_flags"])
        self.assertIn("--prune", mapping["flags"]["relevant_flags"])
        self.assertIn("--lb", mapping["flags"]["relevant_flags"])
        self.assertIn("--profiling", mapping["flags"]["relevant_flags"])
        fields = set(mapping["json_fields"]["per_iteration_fields"])
        self.assertIn("Hits", fields)
        self.assertIn("ComparedPoints", fields)
        self.assertIn("RTTime", fields)
        self.assertIn("CUDATime", fields)
        self.assertIn("OffloadingSize", fields)

    def test_profile_runs_have_counters_and_expose_lb256_correctness_caveat(self) -> None:
        payload = self._load(MAPPING)
        runs = {item["label"]: item for item in payload["profile_runs"]}

        self.assertEqual(set(runs), {"noopt", "eb", "eb_prune", "xhd_lb256"})
        for label in ["noopt", "eb", "eb_prune"]:
            self.assertTrue(runs[label]["matches_author_reference"])
            self.assertGreater(runs[label]["sum_Hits"], 0)
            self.assertGreater(runs[label]["sum_ComparedPoints"], 0)
            self.assertEqual(runs[label]["sum_OffloadingSize"], 0)

        xhd = runs["xhd_lb256"]
        self.assertFalse(xhd["matches_author_reference"])
        self.assertGreater(xhd["sum_OffloadingSize"], 0)
        self.assertIn("aborts", xhd["check_true_status"])
        self.assertIn("Wrong HausdorffDistance", xhd["check_true_error"])

    def test_downloaded_profile_jsons_contain_expected_counter_fields(self) -> None:
        payload = self._load(MAPPING)

        for run in payload["profile_runs"]:
            artifact = ROOT / run["artifact"]
            profile = self._load(artifact)
            iterations = profile["Running"]["Repeats"][0]["Iterations"]
            self.assertGreater(len(iterations), 0)
            for key in ["RTTime", "CUDATime", "NumInputPoints", "NumOutputPoints", "Hits", "ComparedPoints"]:
                self.assertIn(key, iterations[0])


if __name__ == "__main__":
    unittest.main()
