from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "rt-dbscan-paper"
SUMMARY = APP_DIR / "results" / "uci_3droad_1k_optix_cupy_author_directional_gate_summary.json"


class Goal5109RtDbscanOptixCupyAuthorContractGapTest(unittest.TestCase):
    def test_optix_cupy_runs_but_matches_conventional_not_author_directional_contract(self) -> None:
        self.assertTrue(SUMMARY.exists(), SUMMARY)
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertFalse(summary["matched"])
        self.assertFalse(summary["signature_matched"])
        self.assertFalse(summary["component_partition_matched"])
        self.assertTrue(summary["core_flags_matched"])

        self.assertEqual(
            summary["rtdl"]["signature"],
            {
                "core_count": 329,
                "component_count": 3,
                "component_sizes": [102, 168, 181],
                "noise_count": 549,
            },
        )
        self.assertEqual(
            summary["author_signature"],
            {
                "core_count": 329,
                "component_count": 3,
                "component_sizes": [90, 168, 181],
                "noise_count": 561,
            },
        )

        metadata = summary["rtdl"]["metadata"]
        self.assertEqual(summary["rtdl"]["backend"], "optix_cupy_component_signature")
        self.assertEqual(metadata["partner"], "cupy")
        self.assertEqual(
            metadata["partner_reference_contract"],
            "generic_prepared_optix_cupy_grouped_stream_component_labels_3d",
        )
        self.assertEqual(
            metadata["grouped_stream_policy"],
            "optix_applies_predicated_union_and_border_candidate_during_traversal",
        )
        self.assertFalse(metadata["materializes_neighbor_rows"])
        self.assertFalse(metadata["materializes_directed_adjacency_stream"])

        self.assertFalse(summary["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["performance_claim_authorized"])
        self.assertFalse(summary["whole_program_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
