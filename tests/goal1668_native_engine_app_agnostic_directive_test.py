from __future__ import annotations

from pathlib import Path
import json
import os
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1668_native_engine_app_agnostic_directive_response_2026-05-10.md"
DIRECTIVE = ROOT / "docs" / "directives" / "goal1668_antigravity_directive_app_agnostic_engine_2026-05-10.md"
MANIFEST = ROOT / "docs" / "reports" / "goal1668_native_leakage_manifest_baseline_2026-05-10.json"
GATE = ROOT / "docs" / "release_reports" / "v1_7_app_agnostic_native_gate.md"
NATIVE = ROOT / "src" / "native"

LEAKAGE_RE = re.compile(
    r"\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b",
    re.IGNORECASE,
)


CURRENT_DIRTY_BASELINE_SYMBOLS = 96
CURRENT_DIRTY_BASELINE_REQUIRED_SYMBOLS = (
    "rtdl_optix_db_dataset_compact_summary_batch",
    "rtdl_optix_prepare_pose_indices_2d",
    "rtdl_embree_run_directed_hausdorff_2d",
    "rtdl_optix_run_bfs_expand",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _native_leakage_symbols() -> set[str]:
    hits: set[str] = set()
    for path in NATIVE.rglob("*"):
        if path.suffix.lower() not in {".cpp", ".h", ".cu", ".mm"}:
            continue
        for match in LEAKAGE_RE.finditer(_text(path)):
            hits.add(match.group(0))
    return hits


class Goal1668NativeEngineAppAgnosticDirectiveTest(unittest.TestCase):
    def test_directive_snapshot_is_repo_tracked(self) -> None:
        text = _text(DIRECTIVE)
        self.assertIn("MANDATORY ARCHITECTURAL DIRECTIVE", text)
        self.assertIn("The RTDL native engine (C++/CUDA) must become 100% app-agnostic", text)

    def test_current_dirty_baseline_manifest_matches_phase1_audit(self) -> None:
        manifest = json.loads(_text(MANIFEST))
        self.assertEqual(manifest["unique_symbol_count"], CURRENT_DIRTY_BASELINE_SYMBOLS)
        self.assertIn("not an allowlist", manifest["note"])
        self.assertEqual(set(manifest["terms"]), {
            "db",
            "pip",
            "bfs",
            "robot",
            "pose",
            "polygon",
            "knn",
            "hausdorff",
            "jaccard",
        })

    def test_current_native_tree_still_has_known_leakage_until_superseded(self) -> None:
        hits = _native_leakage_symbols()

        # This records representative current dirty-state symbols accepted by
        # Goal1668. When the v1.7/v2.0 migration removes or quarantines them,
        # update this baseline and enable the forward release gate below.
        for required in CURRENT_DIRTY_BASELINE_REQUIRED_SYMBOLS:
            with self.subTest(required=required):
                self.assertIn(required, hits)

    def test_goal1668_report_blocks_full_native_app_agnostic_claim(self) -> None:
        text = _text(REPORT)
        for phrase in (
            "current status: `NOT ZERO`",
            "native internals are not app-agnostic today",
            "RTDL native internals are fully app-agnostic.",
            "must not claim",
            "partner tensor handoff",
            "true zero-copy",
            "docs/reports/goal1668_native_leakage_manifest_baseline_2026-05-10.json",
            "deletion/sunset plan",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_v1_7_gate_requires_zero_or_quarantine(self) -> None:
        text = _text(GATE)
        for phrase in (
            "Wrapper-backed Python APIs do not satisfy this gate",
            "strict leakage audit returns zero",
            "mechanically quarantined outside the\n  release surface",
            "Do not solve regressions by reintroducing app-specific C++/CUDA entry points",
            "non-release legacy\nbuild path",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

        for expanded_term in ("table", "column", "edge", "vertex", "agent", "trajectory"):
            with self.subTest(expanded_term=expanded_term):
                self.assertIn(f"`{expanded_term}`", text)

    def test_forward_release_gate_can_be_enabled_for_v1_7_or_v2_0(self) -> None:
        if os.environ.get("RTDL_ENFORCE_APP_AGNOSTIC_NATIVE_GATE") != "1":
            self.skipTest("forward app-agnostic native gate is not enabled for this dirty baseline")

        hits = _native_leakage_symbols()
        self.assertEqual(hits, set(), "release-surface native engine still has app-shaped symbols")


if __name__ == "__main__":
    unittest.main()
