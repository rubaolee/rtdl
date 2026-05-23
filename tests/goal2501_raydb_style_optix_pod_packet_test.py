from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2501_raydb_style_optix_pod_validation_packet_2026-05-22.md"


class Goal2501RaydbStyleOptixPodPacketTest(unittest.TestCase):
    def test_packet_records_no_pod_evidence_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("No pod evidence is claimed", text)
        self.assertIn("could not load `libcuda.so.1`", text)

    def test_packet_contains_required_optix_commands(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("tests.goal2498_raydb_style_optix_count_sum_parity_test", text)
        self.assertIn("--backend optix --mode all", text)
        self.assertIn("scripts/goal2500_raydb_style_backend_matrix.py", text)
        self.assertIn("goal2501_raydb_style_backend_matrix_pod_2026-05-22.json", text)

    def test_packet_acceptance_criteria_preserve_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            '"all_match_cpu_reference": true',
            '"native_abi_added": false',
            "columnar_grouped_aggregate_optix_columnar_payload",
            "lowering_plan.true_zero_copy_authorized == false",
            "lowering_plan.uses_compatibility_wrapper == true",
            "no min/max/avg native mode claim",
        ):
            self.assertIn(phrase, text)

    def test_packet_blocks_public_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "RayDB reproduction",
            "authors-code comparison",
            "SQL engine or DBMS behavior",
            "public speedup wording",
            "true zero-copy wording",
            "new app-specific native ABI",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
