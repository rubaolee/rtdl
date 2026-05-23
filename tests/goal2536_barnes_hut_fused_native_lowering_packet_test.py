from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2536_barnes_hut_fused_native_lowering_packet_2026-05-23.md"


class Goal2536BarnesHutFusedNativeLoweringPacketTest(unittest.TestCase):
    def test_lowering_packet_records_generic_contract_and_no_app_native_abi(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "generic_aggregate_frontier_weighted_vector_sum_2d_v1",
            "generic_weighted_inverse_square_vector_sum_2d_v1",
            "materialized_frontier_rows=false",
            "materialized_contribution_rows=false",
            "native_engine_app_specific=false",
            "no `barnes_hut` symbols in native ABI",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_lowering_packet_records_backend_split_and_validation_gates(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "CPU/Embree Lowering",
            "OptiX Lowering",
            "Partner Lowering",
            "compare vector sums against `streamed_force_sum_bucketized_cpu`",
            "compare small cases against exact all-pairs force",
            "no public speedup wording",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_lowering_packet_records_stop_condition(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "CUDA/OptiX pod",
            "3-D reference semantics",
            "locally promoted",
            "next performance target is no longer blocked by missing Python reference contracts",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
