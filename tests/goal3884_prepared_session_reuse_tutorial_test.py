from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "docs" / "learn" / "prepared_session_reuse.md"
TUTORIALS_README = ROOT / "docs" / "tutorials" / "README.md"
LEARN_README = ROOT / "docs" / "learn" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal3884_prepared_session_reuse_tutorial_2026-06-08.md"


class Goal3884PreparedSessionReuseTutorialTest(unittest.TestCase):
    def test_indexes_link_to_prepared_session_reuse_page(self) -> None:
        tutorials = TUTORIALS_README.read_text(encoding="utf-8")
        learn = LEARN_README.read_text(encoding="utf-8")

        self.assertIn("../learn/prepared_session_reuse.md", tutorials)
        self.assertIn("prepared_session_reuse.md", learn)
        self.assertIn("Prepared Session Reuse", tutorials)
        self.assertIn("Prepared Session Reuse", learn)

    def test_tutorial_teaches_live_api_and_metadata_surface(self) -> None:
        text = TUTORIAL.read_text(encoding="utf-8")
        for phrase in (
            "RTDL v2.10",
            "make_prepared_session_cache_key",
            "ExplicitPreparedSessionCache",
            "get_or_prepare_explicit_session",
            "prepared_session_residency",
            "prepared_session_reuse_idiom",
            "miss",
            "put",
            "hit",
            "input_fingerprints",
            "parameter fingerprints",
            "explicit_invalidate",
            "cold_hot_phase_split_required",
        ):
            self.assertIn(phrase, text)

    def test_tutorial_claim_boundary_is_non_authorizing(self) -> None:
        text = TUTORIAL.read_text(encoding="utf-8")
        for phrase in (
            "does not authorize",
            "public speedup wording",
            "broad RT-core speedup wording",
            "true-zero-copy wording",
            "automatic partner or backend selection",
            "app-specific native-engine logic",
            "The native engine stays app-agnostic",
        ):
            self.assertIn(phrase, text)

        for forbidden in (
            "guarantees speedup",
            "automatic backend selection",
            "true zero-copy is authorized",
            "app-specific native engine",
        ):
            self.assertNotIn(forbidden, text.lower())

    def test_minimal_cache_example_matches_live_contract(self) -> None:
        calls: list[str] = []
        cache = rt.ExplicitPreparedSessionCache(max_entries=4)
        key = rt.make_prepared_session_cache_key(
            primitive="fixed_radius_threshold_summary_3d",
            backend="optix",
            input_fingerprints={"points": {"rows": 65536, "source": "stable-fixture"}},
            parameters={"radius": 0.02, "k": 32},
            partner="numba",
            device="cuda:0",
        )

        def prepare_session():
            calls.append("prepare")
            return {"prepared_handle": "user-owned-handle"}

        first = rt.get_or_prepare_explicit_session(cache, key, prepare_session)
        second = rt.get_or_prepare_explicit_session(cache, key, prepare_session)

        self.assertFalse(first.cache_hit)
        self.assertTrue(second.cache_hit)
        self.assertEqual(calls, ["prepare"])
        self.assertIs(second.value, first.value)
        self.assertEqual(
            tuple(row["event"] for row in second.cache_event_log),
            ("miss", "put", "hit"),
        )
        metadata = second.to_metadata()
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])

    def test_report_documents_goal3884_scope(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3884",
            "prepared-session reuse",
            "current v2.10 learner guidance",
            "not a release action",
            "not a new performance claim",
            "generic primitive name",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
