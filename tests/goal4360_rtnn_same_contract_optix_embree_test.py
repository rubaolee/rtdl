from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
APP = ROOT / "examples" / "current" / "research_benchmarks" / "rtnn" / "rtdl_rtnn_benchmark_app.py"
README = ROOT / "examples" / "current" / "research_benchmarks" / "rtnn" / "README.md"


class Goal4360RtnnSameContractOptixEmbreeTest(unittest.TestCase):
    def test_runner_records_raw_ranked_summary_signature(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("def _ranked_summary_raw_aggregate(rows)", source)
        self.assertIn('"raw_ranked_summary_aggregate": raw_ranked_summary_aggregate', source)
        self.assertIn('"raw_ranked_summary_batch_summaries": raw_ranked_summary_batch_summaries', source)
        for field in (
            "bounded_neighbor_count",
            "nearest_id_checksum",
            "kth_id_checksum",
            "zero_neighbor_query_count",
            "min_neighbor_count",
            "max_neighbor_count",
        ):
            self.assertIn(field, source)

    def test_current_app_exposes_backend_selectable_raw_mode(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn("def rtnn_prepared_ranked_summary_raw_payload", source)
        self.assertIn('"prepared_ranked_summary_raw"', source)
        self.assertIn('parser.add_argument("--backend", choices=("optix", "embree"), default="optix")', source)
        self.assertIn('result_mode="ranked-summary-raw"', source)
        self.assertIn('"comparison_key": "rtnn_prepared_3d_ranked_summary_raw"', source)
        self.assertIn('"same_contract_backend_comparison_candidate": True', source)

    def test_readme_documents_same_contract_commands(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("--mode prepared_ranked_summary_raw --backend optix", readme)
        self.assertIn("--mode prepared_ranked_summary_raw --backend embree", readme)
        self.assertIn("raw_ranked_summary_aggregate", readme)


if __name__ == "__main__":
    unittest.main()
