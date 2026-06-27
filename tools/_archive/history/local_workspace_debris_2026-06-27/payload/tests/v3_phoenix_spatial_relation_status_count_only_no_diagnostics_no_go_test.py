from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts"
    / "v3_phoenix_spatial_relation_status_count_only_no_diagnostics_no_go.py"
)
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_relation_status_count_only_no_diagnostics_no_go_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
SOURCE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class V3PhoenixSpatialRelationStatusCountOnlyNoDiagnosticsNoGoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_packet_rejects_candidate_without_release_claims(self) -> None:
        packet = self.packet
        self.assertEqual(
            packet["status"],
            "spatial_relation_status_count_only_no_diagnostics_no_go_not_m7",
        )
        self.assertEqual(packet["generic_capability"], "point_location_topology_stream")
        self.assertEqual(
            packet["candidate"]["tested_flag"],
            "RTDL_OPTIX_RELATION_STATUS_CORRECTED_COUNT_ONLY_NO_DIAGNOSTICS",
        )
        self.assertFalse(packet["candidate"]["source_retained"])
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertFalse(packet["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(packet["m7_promotion_authorized"])
        self.assertEqual(packet["m7_qualified_release_rows_added"], 0)
        self.assertEqual(packet["failed_checks"], [])
        self.assertTrue(all(packet["checks"].values()))

    def test_count_only_preserves_count_but_is_slower(self) -> None:
        diagnostic = self.packet["diagnostic_prefilter_zero"]
        count_only = self.packet["count_only_no_diagnostics"]
        comparison = self.packet["comparison"]
        self.assertEqual(diagnostic["row_count"], 47262)
        self.assertEqual(count_only["row_count"], 47262)
        self.assertTrue(diagnostic["row_count_consistent"])
        self.assertTrue(count_only["row_count_consistent"])
        self.assertAlmostEqual(diagnostic["prepared_query_ms_median"], 1.8975920975208282)
        self.assertAlmostEqual(count_only["prepared_query_ms_median"], 1.903872936964035)
        self.assertGreater(
            comparison["prepared_query_delta_ms_count_only_minus_diagnostic"],
            0.0,
        )
        self.assertGreater(comparison["count_only_gap_to_author_ms"], 0.0)

    def test_diagnostics_were_suppressed_but_not_useful(self) -> None:
        diagnostic = self.packet["diagnostic_prefilter_zero"]
        count_only = self.packet["count_only_no_diagnostics"]
        self.assertEqual(set(diagnostic["raw_candidate_counts"]), {47570})
        self.assertEqual(set(count_only["raw_candidate_counts"]), {0})
        self.assertEqual(set(count_only["emitted_counts"]), {47262})
        self.assertFalse(self.packet["summary"]["count_only_was_faster"])

    def test_failed_flag_is_not_retained_in_native_source(self) -> None:
        self.assertNotIn(
            "RTDL_OPTIX_RELATION_STATUS_CORRECTED_COUNT_ONLY_NO_DIAGNOSTICS",
            self.source,
        )
        self.assertIn("RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO", self.source)

    def test_provenance_limitation_is_explicit(self) -> None:
        provenance = self.packet["provenance_limitations"]
        self.assertIsNone(provenance["pod_evidence_git_commit"])
        self.assertIn("was not a git checkout", provenance["reason"])
        self.assertIn("live current-source absence of the failed flag", provenance["mitigation"])
        self.assertIn("source_manifest.sha256", provenance["future_requirement"])

    def test_markdown_records_no_go(self) -> None:
        for phrase in (
            "Status: `spatial_relation_status_count_only_no_diagnostics_no_go_not_m7`.",
            "Count-only/no-diagnostics median: `1.903873 ms`",
            "Delta count-only minus diagnostic: `0.006281 ms`",
            "Count-only faster: `false`",
            "Count-only source retained: `false`",
            "POD evidence git commit: `None`",
            "source_manifest.sha256",
            "Was I foolish?",
        ):
            self.assertIn(phrase, self.markdown)

    def test_script_rebuilds_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            md_out = Path(tmp) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                    "--pretty",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.packet)
            self.assertIn("Count-Only/No-Diagnostics No-Go", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
