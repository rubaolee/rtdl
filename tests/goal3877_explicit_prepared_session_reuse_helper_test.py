from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3877_explicit_prepared_session_reuse_helper_2026-06-08.md"


class Goal3877ExplicitPreparedSessionReuseHelperTest(unittest.TestCase):
    def _key(self, *, parameter: int = 1):
        return rt.make_prepared_session_cache_key(
            primitive="fixed_radius_threshold_summary_3d",
            backend="optix",
            input_fingerprints={"points": "stable-fixture"},
            parameters={"parameter": parameter},
            partner="numba",
            device="cuda:0",
        )

    def test_get_or_prepare_calls_prepare_once_then_reuses(self) -> None:
        key = self._key()
        cache = rt.ExplicitPreparedSessionCache(max_entries=2)
        calls: list[str] = []

        def prepare():
            calls.append("prepare")
            return {"prepared": True, "id": len(calls)}

        first = rt.get_or_prepare_explicit_session(cache, key, prepare)
        second = rt.get_or_prepare_explicit_session(cache, key, prepare)

        self.assertFalse(first.cache_hit)
        self.assertTrue(second.cache_hit)
        self.assertEqual(calls, ["prepare"])
        self.assertIs(second.value, first.value)

        events = tuple(row["event"] for row in second.cache_event_log)
        self.assertEqual(events, ("miss", "put", "hit"))

    def test_reuse_result_metadata_is_non_authorizing(self) -> None:
        key = self._key()
        cache = rt.ExplicitPreparedSessionCache(max_entries=2)
        result = rt.get_or_prepare_explicit_session(cache, key, lambda: object())
        metadata = result.to_metadata()

        self.assertTrue(metadata["explicit_cache_lookup"])
        self.assertEqual(metadata["stable_id"], key.stable_id)
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["policy"]["automatic_partner_selection_authorized"])

    def test_policy_key_mismatch_fails_closed(self) -> None:
        key = self._key(parameter=1)
        other = self._key(parameter=2)
        policy = rt.RtdlPreparedSessionResidencyPolicy(cache_key=other, cache_enabled=True)
        cache = rt.ExplicitPreparedSessionCache(max_entries=2)

        with self.assertRaises(ValueError):
            rt.get_or_prepare_explicit_session(cache, key, lambda: object(), policy=policy)

    def test_prepare_must_be_callable_on_miss(self) -> None:
        key = self._key()
        cache = rt.ExplicitPreparedSessionCache(max_entries=2)
        with self.assertRaises(TypeError):
            rt.get_or_prepare_explicit_session(cache, key, None)

    def test_report_documents_explicit_non_hidden_reuse(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3877",
            "get_or_prepare_explicit_session",
            "caller-owned cache",
            "caller-provided key",
            "caller-provided prepare function",
            "no hidden automatic partner/backend selection",
            "not a true-zero-copy or public speedup claim",
            "app-specific native-engine logic remains forbidden",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
