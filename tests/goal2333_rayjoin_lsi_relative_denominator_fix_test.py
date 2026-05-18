from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2333_rayjoin_lsi_relative_denominator_fix_2026-05-18.md"
ARTIFACTS = ROOT / "docs" / "reports" / "goal2333_rayjoin_lsi_mismatch_probe"
DEBUG_PATCH = ROOT / "docs" / "research" / "rayjoin_lsi_result_export_debug_patch.diff"
PROBE_SCRIPT = ROOT / "scripts" / "goal2333_rayjoin_lsi_mismatch_probe.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> object:
    return json.loads(_read(path))


class Goal2333RayJoinLsiRelativeDenominatorFixTest(unittest.TestCase):
    def test_report_records_fix_without_perf_claim(self) -> None:
        text = _read(REPORT)
        self.assertIn("lsi-same-contract-mismatch-fixed-performance-still-behind", text)
        self.assertIn("scale-aware denominator", text)
        self.assertIn("query segment id | 2148", text)
        self.assertIn("base segment id | 226827", text)
        self.assertIn("does not authorize", text)
        self.assertIn("RTDL-beats-RayJoin claim", text)
        self.assertIn("v2.0 release decision", text)

    def test_debug_patch_exports_rayjoin_lsi_result_ids(self) -> None:
        text = _read(DEBUG_PATCH)
        self.assertIn("RAYJOIN_EXPORT_LSI_XSECTS", text)
        self.assertIn("rtdl.rayjoin.lsi_xsects.v1", text)
        self.assertIn("query_eid1", text)
        self.assertIn("base_eid1", text)

    def test_native_refiners_use_relative_denominator_policy(self) -> None:
        paths = [
            ROOT / "src" / "native" / "embree" / "rtdl_embree_geometry.cpp",
            ROOT / "src" / "native" / "oracle" / "rtdl_oracle_geometry.cpp",
            ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp",
            ROOT / "src" / "native" / "vulkan" / "rtdl_vulkan_core.cpp",
        ]
        for path in paths:
            text = _read(path)
            self.assertIn("segment_intersection_denominator_is_degenerate", text, path)
            self.assertIn("std::hypot", text, path)
            self.assertNotIn(
                "const double denom = rx * sy - ry * sx;\n    if (std::abs(denom) < 1.0e-7)",
                text,
                path,
            )
            self.assertNotIn(
                "double denom = cross(r, s);\n  if (std::fabs(denom) < kSegmentIntersectionEps)",
                text,
                path,
            )
        self.assertIn(
            "std::numeric_limits<double>::epsilon()",
            _read(ROOT / "src" / "native" / "oracle" / "rtdl_oracle_internal.h"),
        )
        for path in [
            ROOT / "src" / "native" / "embree" / "rtdl_embree_geometry.cpp",
            ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp",
            ROOT / "src" / "native" / "vulkan" / "rtdl_vulkan_core.cpp",
        ]:
            self.assertIn("std::numeric_limits<double>::epsilon()", _read(path), path)

    def test_probe_script_compares_identity_sets(self) -> None:
        text = _read(PROBE_SCRIPT)
        self.assertIn("missing_from_rtdl", text)
        self.assertIn("extra_in_rtdl", text)
        self.assertIn("same_contract_with_rayjoin_query_exec", text)

    def test_prefix_artifact_identifies_single_missing_pair(self) -> None:
        payload = _json(ARTIFACTS / "rtdl_vs_rayjoin_lsi_pairs_4096.json")
        self.assertEqual(payload["alignment"], "one_based")
        self.assertEqual(payload["rayjoin_count"], 342)
        self.assertEqual(payload["rtdl_count"], 341)
        self.assertEqual(payload["missing_from_rtdl_count"], 1)
        self.assertEqual(payload["extra_in_rtdl_count"], 0)
        self.assertEqual(payload["missing_from_rtdl"], [{"base_id": 226827, "query_id": 2148}])
        self.assertFalse(payload["claim_boundary"]["same_contract_with_rayjoin_query_exec"])

    def test_after_fix_artifacts_match_rayjoin_identity_sets(self) -> None:
        small = _json(ARTIFACTS / "rtdl_vs_rayjoin_lsi_pairs_4096_after_relative_denom.json")
        large = _json(ARTIFACTS / "rtdl_vs_rayjoin_lsi_pairs_65536_after_relative_denom.json")
        self.assertEqual(small["rayjoin_count"], 342)
        self.assertEqual(small["rtdl_count"], 342)
        self.assertEqual(small["missing_from_rtdl_count"], 0)
        self.assertEqual(small["extra_in_rtdl_count"], 0)
        self.assertTrue(small["claim_boundary"]["same_contract_with_rayjoin_query_exec"])
        self.assertEqual(large["rayjoin_count"], 5809)
        self.assertEqual(large["rtdl_count"], 5809)
        self.assertEqual(large["missing_from_rtdl_count"], 0)
        self.assertEqual(large["extra_in_rtdl_count"], 0)
        self.assertTrue(large["claim_boundary"]["same_contract_with_rayjoin_query_exec"])

    def test_after_fix_replay_keeps_perf_claims_locked(self) -> None:
        replay = _json(ARTIFACTS / "rtdl_replay_after_relative_denom" / "same_query_prepared_comparison.json")
        self.assertEqual(set(replay["lsi"]["scalar_count"]["values"]), {5809})
        self.assertEqual(set(replay["lsi"]["raw_rows"]["values"]), {5809})
        self.assertEqual(set(replay["pip"]["scalar_count"]["values"]), {5783})
        self.assertEqual(set(replay["pip"]["positive_rows"]["values"]), {5783})
        self.assertGreater(replay["lsi"]["scalar_count"]["median_sec"], 0.004)
        self.assertGreater(replay["pip"]["scalar_count"]["median_sec"], 0.005)
        self.assertFalse(replay["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(replay["claim_boundary"]["paper_scale_perf_claim_authorized"])
        self.assertFalse(replay["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(replay["claim_boundary"]["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
