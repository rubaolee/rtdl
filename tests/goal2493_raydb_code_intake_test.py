from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2493_raydb_local_external_code_intake_2026-05-22.md"


class Goal2493RaydbCodeIntakeTest(unittest.TestCase):
    def test_intake_records_external_artifact_without_vendoring(self) -> None:
        text = REPORT.read_text()
        self.assertIn("https://github.com/LonelySlim/myOptixDB/tree/fin", text)
        self.assertIn("a610c00d7334d8907435cc0a124f9ca8392ee456", text)
        self.assertIn("No third-party source was", text)
        self.assertIn("/tmp/rtdl_goal2493_myOptixDB", text)

    def test_intake_blocks_immediate_authors_code_baseline(self) -> None:
        text = REPORT.read_text()
        self.assertIn("Do not use authors-code performance comparison as the next step", text)
        self.assertIn("Treat\nlicense as unresolved", text)
        self.assertIn("authors-code was built or timed", text)
        self.assertIn("SSB data was generated", text)

    def test_intake_defines_synthetic_contract_first_path(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "small denormalized table fixture",
            "columnar RTDL descriptors",
            "CPU reference grouped scan/aggregate",
            "Embree same-contract path",
            "OptiX same-contract path",
        ]:
            self.assertIn(phrase, text)

    def test_goal2494_candidates_are_app_agnostic_contracts(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "ColumnarRecordAxis",
            "PredicateAxisRange",
            "GroupSlotDescriptor",
            "AggregateDescriptor",
            "PreparedColumnarScene",
            "GroupedAggregateResult",
        ]:
            self.assertIn(phrase, text)
        self.assertIn("native Embree/OptiX should gain database, SQL, or RayDB-specific vocabulary", text)


if __name__ == "__main__":
    unittest.main()
