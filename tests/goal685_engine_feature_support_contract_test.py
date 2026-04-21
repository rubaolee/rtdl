from __future__ import annotations

from pathlib import Path
import re
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "features" / "engine_support_matrix.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal685_consensus_2026-04-21.md"


class Goal685EngineFeatureSupportContractTest(unittest.TestCase):
    def test_every_public_feature_has_status_for_every_engine(self) -> None:
        matrix = rt.engine_feature_support_matrix()
        self.assertGreaterEqual(len(matrix), 20)

        for feature, entries in matrix.items():
            with self.subTest(feature=feature):
                self.assertEqual(set(entries), set(rt.RTDL_ENGINES))
                for engine in rt.RTDL_ENGINES:
                    support = entries[engine]
                    self.assertEqual(support.feature, feature)
                    self.assertEqual(support.engine, engine)
                    self.assertIn(support.status, rt.ENGINE_SUPPORT_STATUSES)
                    self.assertTrue(support.note.strip())

    def test_public_api_exports_query_helpers(self) -> None:
        support = rt.engine_feature_support("ray_triangle_any_hit_2d", "optix")

        self.assertEqual(support.status, "native")
        self.assertIs(rt.assert_engine_feature_supported("ray_triangle_any_hit_2d", "optix"), support)

        with self.assertRaisesRegex(ValueError, "unknown RTDL feature/engine pair"):
            rt.engine_feature_support("not_a_feature", "optix")

    def test_doc_records_no_blank_or_silent_cpu_fallback_policy(self) -> None:
        text = DOC.read_text(encoding="utf-8")

        for phrase in (
            "native",
            "native_assisted",
            "compatibility_fallback",
            "unsupported_explicit",
            "Silent CPU fallback is not allowed",
            "rtdsl.engine_feature_support_matrix()",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_doc_table_matches_machine_readable_matrix_statuses(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        rows = {}
        for line in text.splitlines():
            if not line.startswith("| `"):
                continue
            cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
            rows[cells[0]] = dict(zip(rt.RTDL_ENGINES, cells[1:], strict=True))

        matrix = rt.engine_feature_support_matrix()
        self.assertEqual(set(rows), set(matrix))
        for feature, entries in matrix.items():
            for engine, support in entries.items():
                with self.subTest(feature=feature, engine=engine):
                    self.assertEqual(rows[feature][engine], support.status)

    def test_public_docs_link_engine_support_contract(self) -> None:
        for path in (
            REPO_ROOT / "README.md",
            REPO_ROOT / "docs" / "features" / "README.md",
            REPO_ROOT / "docs" / "current_main_support_matrix.md",
            REPO_ROOT / "docs" / "backend_maturity.md",
            REPO_ROOT / "docs" / "release_reports" / "v0_9_6" / "support_matrix.md",
        ):
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertRegex(text, re.compile(r"Engine Feature Support Contract|engine feature support contract"))

    def test_consensus_records_external_acceptance(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("The 3-AI consensus is ACCEPT", text)
        self.assertIn("Claude | ACCEPT", text)
        self.assertIn("Gemini Flash | ACCEPT", text)


if __name__ == "__main__":
    unittest.main()
