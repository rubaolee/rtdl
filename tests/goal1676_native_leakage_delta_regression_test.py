from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native"
REPORT = ROOT / "docs" / "reports" / "goal1676_native_leakage_delta_regression_2026-05-10.md"
GATE = ROOT / "docs" / "release_reports" / "v1_7_app_agnostic_native_gate.md"

LEAKAGE_RE = re.compile(
    r"\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b",
    re.IGNORECASE,
)

REMOVED_SYMBOLS = {
    "rtdl_optix_count_poses_prepared_ray_anyhit_2d_prepared_indices",
    "rtdl_optix_destroy_prepared_pose_indices_2d",
    "rtdl_optix_pose_flags_prepared_ray_anyhit_2d_packed",
    "rtdl_optix_pose_flags_prepared_ray_anyhit_2d_prepared_indices",
    "rtdl_optix_prepare_pose_indices_2d",
    "rtdl_oracle_polygon",
}

REPLACEMENT_SYMBOLS = {
    "rtdl_optix_group_flags_prepared_ray_anyhit_2d_packed",
    "rtdl_optix_prepare_group_indices_2d",
    "rtdl_optix_group_flags_prepared_ray_anyhit_2d_prepared_indices",
    "rtdl_optix_count_groups_prepared_ray_anyhit_2d_prepared_indices",
    "rtdl_optix_destroy_prepared_group_indices_2d",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _native_text() -> str:
    chunks: list[str] = []
    for path in NATIVE.rglob("*"):
        if path.suffix.lower() in {".cpp", ".h", ".cu", ".mm"}:
            chunks.append(_text(path))
    return "\n".join(chunks)


class Goal1676NativeLeakageDeltaRegressionTest(unittest.TestCase):
    def test_removed_goal1673_and_goal1674_symbols_stay_absent(self) -> None:
        text = _native_text()
        for symbol in REMOVED_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, text)

    def test_group_replacements_stay_present(self) -> None:
        text = _native_text()
        for symbol in REPLACEMENT_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, text)

    def test_strict_gate_still_has_remaining_app_shaped_work(self) -> None:
        text = _native_text()
        symbols = {match.group(0) for match in LEAKAGE_RE.finditer(text)}
        self.assertTrue(symbols)
        for representative in (
            "RTDL_DB_KIND_INT64",
            "rtdl_embree_run_shape_pair_relation_flags",
            "RTDL_DB_OP_BETWEEN",
        ):
            with self.subTest(representative=representative):
                self.assertIn(representative, text)

    def test_report_and_gate_record_delta_guard(self) -> None:
        report_text = REPORT.read_text(encoding="utf-8")
        gate_text = GATE.read_text(encoding="utf-8")
        for phrase in (
            "the five OptiX pose-shaped prepared any-hit native symbols removed by",
            "the old `rtdl_oracle_polygon` root wrapper removed by Goal1674",
            "This does not pass the app-agnostic native-engine gate",
            "Blocked wording remains",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("goal1676_native_leakage_delta_regression_2026-05-10.md", gate_text)


if __name__ == "__main__":
    unittest.main()
