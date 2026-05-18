from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2344_v2_1_internal_closure_2026-05-18.md"
POD_JSON = ROOT / "docs" / "reports" / "goal2344_v2_1_internal_closure_pod_example_readiness_2026-05-18.json"
DOCS_INDEX = ROOT / "docs" / "README.md"
EXAMPLES_INDEX = ROOT / "examples" / "README.md"
ROOT_README = ROOT / "README.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2345_gemini_review_goal2344_v2_1_internal_closure_2026-05-18.md"


class Goal2344V21InternalClosureTest(unittest.TestCase):
    def test_closure_report_marks_v2_1_internal_not_release(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("internal checkpoint closed; not released", text)
        self.assertIn("Do not call it a release", text)
        self.assertIn("v2.0 remains the current release", text)
        self.assertIn("51/51 Embree and OptiX", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("Goal2345 Gemini review", text)

    def test_pod_artifact_records_full_pass(self) -> None:
        payload = json.loads(POD_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["summary"]["total"], 51)
        self.assertEqual(payload["summary"]["pass"], 51)
        self.assertEqual(payload["summary"]["failed_count"], 0)
        groups = {row["group"] for row in payload["results"]}
        self.assertEqual(groups, {"embree", "optix"})

    def test_public_docs_link_internal_checkpoint_without_replacing_v2_0(self) -> None:
        docs = DOCS_INDEX.read_text(encoding="utf-8")
        examples = EXAMPLES_INDEX.read_text(encoding="utf-8")
        readme = ROOT_README.read_text(encoding="utf-8")
        for text in (docs, examples, readme):
            self.assertIn("v2.1", text)
            self.assertIn("internal", text.lower())
        self.assertIn("RTDL v2.0 is the released", docs)
        self.assertIn("This directory is organized for RTDL v2.0 users first", examples)
        self.assertIn("RTDL v2.0 is the Python+partner+RTDL source-tree release", readme)

    def test_gemini_review_accepts_internal_boundary(self) -> None:
        review = GEMINI_REVIEW.read_text(encoding="utf-8")
        self.assertIn("accept-with-boundary", review)
        self.assertIn("51/51", review)
        self.assertIn("Internal checkpoint only", review)
        self.assertNotIn("[Insert", review)


if __name__ == "__main__":
    unittest.main()
