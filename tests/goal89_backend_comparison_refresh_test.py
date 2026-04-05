from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def _load(path: str) -> dict:
    return json.loads((REPO / path).read_text(encoding="utf-8"))


class Goal89BackendComparisonRefreshTest(unittest.TestCase):
    def test_long_exact_source_backend_matrix_invariants(self) -> None:
        optix_prepared = _load(
            "docs/reports/goal82_optix_pre_embree_audit_artifacts_2026-04-04/prepared/summary.json"
        )
        optix_raw = _load(
            "docs/reports/goal81_optix_long_exact_raw_input_win_artifacts_2026-04-04/optix/summary.json"
        )
        embree_prepared = _load(
            "docs/reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/prepared/summary.json"
        )
        embree_raw = _load(
            "docs/reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/raw/summary.json"
        )
        vulkan_prepared = _load(
            "docs/reports/goal87_vulkan_long_exact_source_artifacts_2026-04-05/summary.json"
        )
        vulkan_raw = _load(
            "docs/reports/goal88_vulkan_long_exact_raw_input_artifacts_2026-04-05/summary.json"
        )

        expected_digest = "0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec"
        expected_row_count = 39073

        for summary in (
            optix_prepared,
            optix_raw,
            embree_prepared,
            embree_raw,
            vulkan_prepared,
            vulkan_raw,
        ):
            self.assertEqual(summary["postgis"]["row_count"], expected_row_count)
            self.assertEqual(summary["postgis"]["sha256"], expected_digest)
            self.assertTrue(summary["postgis"]["plan"]["uses_index"])
            self.assertTrue(summary["result"]["parity_preserved_all_reruns"])

        self.assertTrue(embree_prepared["result"]["beats_postgis_all_reruns"])
        self.assertFalse(vulkan_prepared["result"]["beats_postgis_all_reruns"])
        self.assertFalse(optix_prepared["result"]["beats_postgis_all_reruns"])
        self.assertLess(
            min(run["backend_sec"] for run in optix_prepared["runs"]),
            min(run["postgis_sec"] for run in optix_prepared["runs"]),
        )

        self.assertTrue(optix_raw["result"]["repeated_run_improved"])
        self.assertTrue(embree_raw["result"]["repeated_run_improved"])
        self.assertTrue(vulkan_raw["result"]["repeated_run_improved"])

        self.assertLess(
            optix_raw["result"]["best_repeated_run_sec"],
            min(run["postgis_sec"] for run in optix_raw["runs"]),
        )
        self.assertLess(
            embree_raw["result"]["best_repeated_run_sec"],
            min(run["postgis_sec"] for run in embree_raw["runs"]),
        )
        self.assertGreater(
            vulkan_raw["result"]["best_repeated_run_sec"],
            max(run["postgis_sec"] for run in vulkan_raw["runs"]),
        )


if __name__ == "__main__":
    unittest.main()
