import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "phoenix_v3_m4_grouped_continuation_20260620"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m4_grouped_continuation_pod_evidence_2026-06-20.md"
INDEX = ART / "phoenix_v3_m4_evidence_index_2026-06-20.json"


def load(name: str) -> dict[str, object]:
    return json.loads((ART / name).read_text(encoding="utf-8"))


class V3PhoenixM4GroupedContinuationEvidenceTest(unittest.TestCase):
    def test_preflight_records_binding_environment_and_claim_gates(self):
        self.assertEqual(load("system_python3_gpu_env_gate.json")["status"], "fail")
        self.assertEqual(load("gpu_env_gate.json")["status"], "pass")
        self.assertIn("source_version_match=pass", (ART / "source_identity_check.txt").read_text())
        self.assertIn("packet claim-boundary gate ok", (ART / "pre_run_packet_gate.txt").read_text())
        self.assertTrue((ART / "source_manifest.sha256").stat().st_size > 1000)

    def test_m4_artifacts_are_serious_scale_and_claim_gated(self):
        m9 = load("m9_grouped_stream_partner_65536.json")
        self.assertEqual(m9["parameters"]["point_count"], 65536)
        self.assertTrue(m9["comparison"]["signature_match"])

        m10 = load("m10_same_stream_65536.json")
        self.assertEqual(m10["parameters"]["point_count"], 65536)
        self.assertTrue(m10["comparison"]["same_stream_ready"])
        self.assertFalse(m10["comparison"]["true_zero_copy_ready"])
        self.assertEqual(
            m10["comparison"]["event_accounting_status"],
            "succeeded_with_independent_median_accounting_warning",
        )
        self.assertEqual(m10["comparison"]["event_accounting_warning_count"], 1)

        m11 = load("m11_no_hidden_copy_65536.json")
        self.assertEqual(m11["parameters"]["point_count"], 65536)
        self.assertTrue(m11["comparison"]["transfer_counter_observed"])
        self.assertTrue(m11["comparison"]["no_hidden_column_copy_ready"])

        m18 = load("m18_device_grouped_65536.json")
        self.assertEqual(m18["parameters"]["ray_count"], 65536)
        self.assertEqual(m18["parameters"]["group_count"], 1024)
        self.assertFalse(m18["comparison"]["public_claim_authorized"])

        m23 = load("m23_dbscan_component_signature_524288.json")
        self.assertEqual(m23["parameters"]["copies"], 65536)
        self.assertEqual(m23["parameters"]["point_count"], 524288)
        self.assertTrue(m23["comparison"]["native_continuation_active"])
        self.assertFalse(m23["comparison"]["public_claim_authorized"])

    def test_m28_records_four_independent_backend_mode_rows(self):
        m28 = load("m28_raydb_grouped_reduction_262144.json")
        self.assertEqual(m28["status"], "ok")
        self.assertEqual(m28["parameters"]["generated_rows"], 262144)
        self.assertEqual(m28["parameters"]["generated_groups"], 1024)
        rows = {(row["backend"], row["mode"]) for row in m28["rows"]}
        self.assertEqual(rows, {("embree", "count"), ("embree", "sum"), ("optix", "count"), ("optix", "sum")})
        for row in m28["rows"]:
            self.assertTrue(row["matches_cpu_reference"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(m28["comparison"]["public_speedup_claim_authorized"])

    def test_evidence_index_carries_per_row_boundaries_and_provenance(self):
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        self.assertFalse(index["release_authorized"])
        self.assertFalse(index["public_speedup_claim_authorized"])
        self.assertEqual(index["phoenix_m7_qualified_release_rows"], 0)
        self.assertEqual(index["source_identity"]["current_commit"], "no_git_worktree")
        gap = index["binding_environment"]["open_packaging_gap"]
        self.assertEqual(gap["status"], "open")
        self.assertEqual(gap["target_fix_milestone"], "before Phoenix M7 release qualification")
        rows = {row["gate"]: row for row in index["rows"]}
        self.assertEqual(set(rows), {"M9", "M10", "M11", "M18", "M23", "M28"})
        for row in rows.values():
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["public_claim_authorized"])
            self.assertFalse(row["public_zero_copy_wording_authorized"])
            self.assertFalse(row["phoenix_m7_qualified"])
            self.assertEqual(row["source_manifest"], "source_manifest.sha256")
            self.assertIn("no_git_worktree", row["source_identity"])
        self.assertFalse(rows["M10"]["clean_pass"])
        self.assertEqual(rows["M10"]["accounting_warning_count"], 1)
        self.assertEqual(rows["M10"]["result_classification"], "pass_internal_with_accounting_warning")
        self.assertEqual(
            rows["M28"]["ratio_citation_policy"],
            "internal CPU-reference comparisons only; must not be cited as cross-backend speedup until M7 qualification",
        )

    def test_report_keeps_release_boundary_visible(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "not release evidence",
            "release_authorized: false",
            "public_speedup_claim_authorized: false",
            "Phoenix M7-qualified release rows: 0",
            "pass with accounting warning",
            "non-clean pass",
            "not a clean pass",
            "does not authorize public speedup wording",
            "phoenix_m4_system_python_missing_cupy_numba",
            "must not be cited as cross-backend speedup until M7 qualification",
            "pass_internal_with_accounting_warning",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
