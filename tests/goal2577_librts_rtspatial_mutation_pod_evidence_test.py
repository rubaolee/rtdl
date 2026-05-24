from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs/reports/goal2577_librts_rtspatial_mutation_pod_evidence_2026-05-24.json"
REPORT = ROOT / "docs/reports/goal2577_librts_rtspatial_mutation_pod_evidence_2026-05-24.md"


class LibRTSRTSpatialMutationPodEvidenceTest(unittest.TestCase):
    def test_artifact_records_authors_mutation_tests(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["source"]["rtspatial_head"], "52509e8022abeab722f5a9a89d1917e8b481defe")
        self.assertEqual(artifact["results"]["tests"], 3)
        self.assertEqual(artifact["results"]["failures"], 0)
        self.assertEqual(artifact["results"]["errors"], 0)
        self.assertIn("fp32_intersects_envelope_batch_update", artifact["results"]["cases"])
        self.assertIn("fp32_test_delete", artifact["results"]["cases"])
        self.assertIn("fp32_test_delete_compact", artifact["results"]["cases"])

    def test_raw_gtest_json_matches_summary(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        raw = json.loads((ROOT / artifact["raw_outputs"]["gtest_json"]).read_text(encoding="utf-8"))
        self.assertEqual(raw["tests"], artifact["results"]["tests"])
        self.assertEqual(raw["failures"], artifact["results"]["failures"])
        self.assertEqual(raw["errors"], artifact["results"]["errors"])
        names = {case["name"] for suite in raw["testsuites"] for case in suite["testsuite"]}
        self.assertEqual(names, set(artifact["results"]["cases"]))

    def test_report_keeps_rtdl_claim_boundary_closed(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not add an RTDL native mutation primitive", text)
        self.assertIn("Not an RTDL performance claim", text)
        self.assertIn("Not full LibRTS paper reproduction", text)


if __name__ == "__main__":
    unittest.main()
