from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LOWERING = ROOT / "src/rtdsl/v4_partitioned_grouped_i64_lowering.py"
RUNNER = ROOT / "Paper-reproduction-apps/raydb-paper/run_ssb_packet_rtdl.py"


class Goal5776PartitionedGroupedI64LoweringTest(unittest.TestCase):
    def test_lowering_is_app_neutral_and_consumes_verified_program(self):
        source = LOWERING.read_text(encoding="utf-8")
        lowered = source.lower()
        for forbidden in ("raydb", "ssb", "q11", "paper app"):
            self.assertNotIn(forbidden, lowered)
        self.assertIn("compile_keyed_callback()", source)
        self.assertIn("keyed_i64_sum_schema(callback)", source)
        self.assertIn("consume_verified_triangle_reduction_executable", source)
        self.assertIn("OptixTraversalAuditSession", source)

    def test_packet_members_resolve_against_packet_directory(self):
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("packet_root = packet_path.resolve().parent", source)
        self.assertIn("packet_member(packet[\"data_path\"])", source)


if __name__ == "__main__":
    unittest.main()
