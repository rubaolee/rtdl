from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3873_prepared_session_residency_contract_2026-06-08.md"


class _ClosableHandle:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class Goal3873PreparedSessionResidencyContractTest(unittest.TestCase):
    def test_contract_requires_explicit_keys_and_blocks_claims(self) -> None:
        contract = rt.describe_prepared_session_residency_contract()
        validation = rt.validate_prepared_session_residency_contract(contract)

        self.assertEqual(contract["contract_version"], rt.PREPARED_SESSION_RESIDENCY_VERSION)
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        self.assertTrue(contract["requires_explicit_cache_key"])
        self.assertTrue(contract["requires_visible_invalidation"])
        self.assertTrue(contract["requires_cold_hot_phase_split"])
        self.assertTrue(contract["no_hidden_automatic_partner_backend_selection"])

        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            self.assertFalse(contract[flag], flag)

    def test_cache_key_is_stable_and_rejects_app_shaped_primitives(self) -> None:
        first = rt.make_prepared_session_cache_key(
            primitive="fixed_radius_threshold_summary_3d",
            backend="optix",
            input_fingerprints={"query_points": (1, 2, 3), "search_points": {"rows": 128}},
            parameters={"radius": 0.02, "k": 32},
            partner="numba",
            device="cuda:0",
        )
        second = rt.make_prepared_session_cache_key(
            primitive="fixed_radius_threshold_summary_3d",
            backend="optix",
            input_fingerprints={"search_points": {"rows": 128}, "query_points": (1, 2, 3)},
            parameters={"k": 32, "radius": 0.02},
            partner="numba",
            device="cuda:0",
        )
        self.assertEqual(first.stable_id, second.stable_id)
        self.assertEqual(first.to_metadata()["automatic_partner_selection_authorized"], False)

        with self.assertRaises(ValueError):
            rt.make_prepared_session_cache_key(
                primitive="hausdorff_threshold_path",
                backend="optix",
                input_fingerprints={"points": 3},
            )

        for app_handle in V2_8_PROMOTED_BENCHMARK_APPS:
            with self.subTest(app_handle=app_handle):
                with self.assertRaises(ValueError):
                    rt.make_prepared_session_cache_key(
                        primitive=f"{app_handle}_prepared_path",
                        backend="optix",
                        input_fingerprints={"payload": "fixture"},
                    )

    def test_policy_and_explicit_cache_record_hits_misses_and_invalidation(self) -> None:
        key = rt.make_prepared_session_cache_key(
            primitive="aabb_index_query_2d",
            backend="optix",
            input_fingerprints={"boxes": {"rows": 1024}},
            parameters={"operation": "all"},
        )
        policy = rt.RtdlPreparedSessionResidencyPolicy(cache_key=key, cache_enabled=True)
        metadata = policy.to_metadata()
        self.assertTrue(metadata["cache_enabled"])
        self.assertIn("explicit_invalidate", metadata["invalidation_events"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

        cache = rt.ExplicitPreparedSessionCache(max_entries=1)
        handle = _ClosableHandle()
        cache.put(key, handle)
        self.assertIs(cache.get(key), handle)
        self.assertTrue(cache.invalidate(key))
        self.assertTrue(handle.closed)
        self.assertIsNone(cache.get(key))

        events = tuple(row["event"] for row in cache.event_log)
        self.assertEqual(events, ("put", "hit", "explicit_invalidate", "miss"))
        self.assertFalse(cache.to_metadata()["public_speedup_claim_authorized"])

    def test_timing_summary_keeps_goal3872_cold_hot_lesson_non_authorizing(self) -> None:
        key = rt.make_prepared_session_cache_key(
            primitive="ray_triangle_weighted_sum_3d",
            backend="optix",
            input_fingerprints={"scene": "goal3872-triangle-counting"},
            parameters={"copies": 2048},
        )
        policy = rt.RtdlPreparedSessionResidencyPolicy(cache_key=key, cache_enabled=False)
        rows = (
            rt.RtdlPreparedSessionTimingRecord(
                row_id="triangle_counting_generic_summary",
                prepare_sec=0.39183870516717434,
                hot_query_sec=0.00015036482363939285,
                repeat=50,
                warmup=5,
                prepared_session_policy=policy,
            ),
            rt.RtdlPreparedSessionTimingRecord(
                row_id="ranked_neighbor_summary",
                prepare_sec=1.7026465376839042,
                hot_query_sec=0.00013345852494239807,
                repeat=50,
                warmup=5,
                prepared_session_policy=policy,
            ),
        )
        summary = rt.summarize_prepared_session_timing_records(rows)
        self.assertEqual(summary["row_count"], 2)
        self.assertGreater(summary["geomean_prepare_to_hot_query_ratio"], 5000.0)
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["true_zero_copy_claim_authorized"])

    def test_report_documents_the_goal3872_to_goal3873_design_step(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3873",
            "prepared-session cache key",
            "cold prepare vs hot query",
            "explicit lifetime and invalidation",
            "no hidden automatic partner/backend selection",
            "not a true-zero-copy or public speedup claim",
            "app-specific native-engine logic remains forbidden",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
