from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2153_rayjoin_external_cdb_public_sample_pod_evidence_2026-05-16.md"
WARM = ROOT / "docs" / "reports" / "goal2152_rayjoin_external_cdb_public_sample_warm_pod_2026-05-16.json"
COLD = ROOT / "docs" / "reports" / "goal2152_rayjoin_external_cdb_public_sample_pod_2026-05-16.json"


class Goal2153RayjoinExternalCdbPublicSamplePodEvidenceTest(unittest.TestCase):
    def test_report_records_public_sample_boundary_and_diagnostic(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "id_ed25519_rtdl_codex",
            "Rejected copied key: `~/.ssh/id_ed25519`",
            "derived inputs, not exact RayJoin paper inputs",
            "cold one-shot app run",
            "lsi_county64_self_positive_control",
            "Embree mismatch",
            "separate Embree LSI degeneracy audit",
            "not release evidence by itself",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_warm_artifact_preserves_claim_flags_and_expected_parity_boundary(self) -> None:
        payload = json.loads(WARM.read_text(encoding="utf-8"))

        self.assertFalse(payload["claim_boundary"]["full_rayjoin_reproduction"])
        self.assertFalse(payload["claim_boundary"]["paper_scale_perf_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])

        for label, case in payload["cases"].items():
            for backend, row in case["backends"].items():
                with self.subTest(label=label, backend=backend):
                    self.assertEqual(row["status"], "ok")
                    self.assertTrue(row["row_count_consistent"])
                    if label == "lsi_county64_self_positive_control" and backend == "embree":
                        self.assertFalse(row["all_parity_vs_cpu_python_reference"])
                    else:
                        self.assertTrue(row["all_parity_vs_cpu_python_reference"])

    def test_cold_artifact_is_kept_as_cautionary_evidence(self) -> None:
        payload = json.loads(COLD.read_text(encoding="utf-8"))

        self.assertEqual(payload["commit"], "73e23e3559e8ef65c045275402887730e02fe6ed")
        self.assertIn("pip", payload["cases"])
        self.assertIn("overlay_seed", payload["cases"])


if __name__ == "__main__":
    unittest.main()
