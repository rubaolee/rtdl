from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2496_raydb_style_embree_lowering_decision_2026-05-22.md"
EMBREE_RUNTIME = ROOT / "src/rtdsl/embree_runtime.py"


class Goal2496RaydbStyleEmbreeLoweringDecisionTest(unittest.TestCase):
    def test_report_chooses_existing_columnar_payload_not_new_db_abi(self) -> None:
        text = REPORT.read_text()
        self.assertIn("do not add new native DB/RayDB ABI", text)
        self.assertIn("rtdl_embree_columnar_payload_create_from_columns", text)
        self.assertIn("ColumnarRecordSet + ColumnarAggregatePlan", text)
        self.assertIn("generic Embree columnar payload descriptor", text)

    def test_embree_runtime_has_required_columnar_payload_symbols(self) -> None:
        runtime = EMBREE_RUNTIME.read_text()
        for symbol in [
            "rtdl_embree_columnar_payload_create",
            "rtdl_embree_columnar_payload_create_from_columns",
            "rtdl_embree_columnar_payload_grouped_reduction_count",
            "rtdl_embree_columnar_payload_grouped_reduction_sum",
        ]:
            self.assertIn(symbol, runtime)

    def test_report_blocks_native_app_specific_vocabulary_expansion(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "add native `raydb`, `sql`, `database`, `table`, `ssb`, or query-name symbols",
            "add a new RayDB native API",
            "claim RayDB reproduction",
            "time authors code",
            "claim public speedup",
        ]:
            self.assertIn(phrase, text)

    def test_report_defers_unimplemented_reduction_modes(self) -> None:
        text = REPORT.read_text()
        self.assertIn("First backend result modes:", text)
        self.assertIn("`count`", text)
        self.assertIn("`sum`", text)
        self.assertIn("Deferred backend result modes:", text)
        self.assertIn("`min`", text)
        self.assertIn("`max`", text)
        self.assertIn("`avg_as_sum_count`", text)


if __name__ == "__main__":
    unittest.main()
