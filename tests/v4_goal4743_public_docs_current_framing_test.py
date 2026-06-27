from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "current_v4_status.md",
    ROOT / "docs" / "app_level_benchmark_summary.md",
    ROOT / "docs" / "learn" / "performance_wording.md",
)


class V4Goal4743PublicDocsCurrentFramingTest(unittest.TestCase):
    def test_public_docs_use_user_facing_current_matrix_framing(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in PUBLIC_DOCS)
        self.assertNotIn("complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim", combined)
        self.assertIn("two material hot-path rows over V2.14", combined)
        self.assertIn("similar-speed or modest-gain rows elsewhere", combined)
        self.assertIn("It does not say every benchmark app is", combined)

    def test_current_app_table_has_repaired_rows(self) -> None:
        summary = (ROOT / "docs" / "app_level_benchmark_summary.md").read_text(encoding="utf-8")
        self.assertIn("RayDB-style | `1.113x` | `1.111x`", summary)
        self.assertIn("Triangle counting | `4.360x` | `1.021x`", summary)
        self.assertIn("Barnes-Hut aggregate frontier | `286.142x` | `0.993x`", summary)
        self.assertIn("Robot collision | `1.020x` | `1.000x`", summary)
        self.assertNotIn("Robot collision | n/a | n/a", summary)
        self.assertIn("Spatial RayJoin shape-pair | `1.000x` | `1.004x`", summary)

    def test_docs_keep_custom_predicate_separate_from_legacy_apps(self) -> None:
        summary = (ROOT / "docs" / "app_level_benchmark_summary.md").read_text(encoding="utf-8")
        self.assertIn("V4-Specific Workflow", summary)
        self.assertIn("Custom predicate early-exit | `4.633x` | `4.633x`", summary)
        self.assertIn("constrained custom predicate early-exit", (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_docs_do_not_show_negative_marketing_copy_as_user_guidance(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in PUBLIC_DOCS)
        self.assertNotIn("All benchmark apps are faster in V4", combined)
        self.assertNotIn("broad V4-over-V2.14", combined)
        self.assertNotIn("app-specific native", combined)


if __name__ == "__main__":
    unittest.main()
