from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1435V151CollectKReadinessEvidenceRegistryTest(unittest.TestCase):
    def test_readiness_evidence_registry_names_each_required_gate_in_order(self) -> None:
        gate = rt.validate_v1_5_1_collect_k_bounded_readiness_gate()

        self.assertEqual(
            tuple(name for name, _path in gate["evidence_files"]),
            rt.V1_5_1_COLLECT_K_BOUNDED_READINESS_REQUIRED_GATES,
        )
        for name, relative_path in gate["evidence_files"]:
            with self.subTest(name=name):
                self.assertTrue((ROOT / relative_path).exists())

    def test_summary_records_no_new_public_authorization(self) -> None:
        summary = (
            ROOT
            / "docs/reports/goal1435_v1_5_1_collect_k_readiness_evidence_registry_hardening_2026-05-07.md"
        ).read_text(encoding="utf-8")

        self.assertIn("ACCEPTED as a readiness evidence registry hardening patch", summary)
        self.assertIn("naming an evidence entry for every required gate", summary)
        self.assertIn("does not authorize stable `COLLECT_K_BOUNDED` promotion", summary)
        self.assertIn("release action", summary)


if __name__ == "__main__":
    unittest.main()
