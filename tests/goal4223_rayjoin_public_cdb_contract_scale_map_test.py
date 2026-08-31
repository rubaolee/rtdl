from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4223_rayjoin_public_cdb_contract_scale_map_rtx4000ada"
SUMMARY = ARTIFACT_DIR / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal4223_rayjoin_public_cdb_contract_scale_map_2026-06-09.md"

FORBIDDEN_TRUE_FLAGS = {
    "release_authorized",
    "public_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rt_core_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
    "paper_reproduction_claim_authorized",
    "rayjoin_paper_reproduction_claim_authorized",
    "rtdl_beats_rayjoin_claim_authorized",
    "true_zero_copy_claim_authorized",
    "automatic_partner_selection_authorized",
    "app_specific_native_engine_logic_allowed",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _forbidden_true_paths(value, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_FLAGS and child is True:
                hits.append(child_path)
            hits.extend(_forbidden_true_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(_forbidden_true_paths(child, f"{path}[{index}]"))
    return hits


class Goal4223RayjoinPublicCdbContractScaleMapTest(unittest.TestCase):
    def test_summary_and_report_exist(self) -> None:
        self.assertTrue(SUMMARY.is_file())
        self.assertTrue(REPORT.is_file())

    def test_scale_map_passes_with_closed_claim_boundaries(self) -> None:
        payload = _load(SUMMARY)
        self.assertEqual(payload["schema"], "rtdl.goal4223.rayjoin_public_cdb_contract_scale_map.v1")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["source_commit"], "63289bbc")
        self.assertEqual(payload["source_dirty"], [])
        self.assertEqual(len(payload["rows"]), 7)
        self.assertEqual(_forbidden_true_paths(payload), [])
        self.assertIn("not a RayJoin paper reproduction", payload["boundary"])

    def test_route_split_is_contract_visible_not_automatic_dispatch(self) -> None:
        payload = _load(SUMMARY)
        self.assertEqual(
            payload["recommended_route_counts"],
            {
                "numba_cuda_jit_scalar_count": 1,
                "rtdl_optix_prepared_segment_pair_count": 3,
                "rtdl_optix_prepared_shape_pair_active_count": 3,
            },
        )
        by_case = {row["case_id"]: row for row in payload["rows"]}
        pip = by_case["pip_county512"]
        self.assertEqual(pip["recommended_route"], "numba_cuda_jit_scalar_count")
        self.assertLess(pip["rtdl_optix_speedup_vs_numba"], 1.0)
        self.assertFalse(pip["numba_rawkernel_required"])

        for case_id in (
            "lsi_county256_soil256_count128",
            "lsi_county256_soil256_count256",
            "lsi_county256_soil256_count512",
        ):
            row = by_case[case_id]
            self.assertEqual(row["workload"], "lsi")
            self.assertEqual(row["recommended_route"], "rtdl_optix_prepared_segment_pair_count")
            self.assertGreater(row["rtdl_optix_speedup_vs_numba"], 20.0)

        for case_id in (
            "overlay_county128_soil128",
            "overlay_county256_soil256",
            "overlay_county512_soil512",
        ):
            row = by_case[case_id]
            self.assertEqual(row["workload"], "overlay_seed")
            self.assertEqual(row["recommended_route"], "rtdl_optix_prepared_shape_pair_active_count")
            self.assertGreater(row["rtdl_optix_speedup_vs_numba"], 60.0)

    def test_every_row_preserves_same_contract_count_parity(self) -> None:
        payload = _load(SUMMARY)
        for row in payload["rows"]:
            self.assertTrue(row["counts_match"], row["case_id"])
            self.assertEqual(row["numba_row_count"], row["rtdl_optix_row_count"], row["case_id"])
            self.assertGreater(row["numba_candidate_pair_count"], 0)


if __name__ == "__main__":
    unittest.main()
