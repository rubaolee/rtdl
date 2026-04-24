import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal821PublicDocsRequireRtCoreTest(unittest.TestCase):
    def test_public_docs_explain_optix_is_not_rt_core_claim(self) -> None:
        for relative in (
            "README.md",
            "docs/quick_tutorial.md",
            "docs/application_catalog.md",
            "docs/release_facing_examples.md",
            "docs/rtdl_feature_guide.md",
        ):
            with self.subTest(relative=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("--backend optix", text)
                self.assertIn("--require-rt-core", text)
                self.assertIn("not", text.lower())
                self.assertIn("NVIDIA RT", text)

    def test_docs_list_current_claim_sensitive_command_shapes(self) -> None:
        text = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in (
                "README.md",
                "docs/application_catalog.md",
                "docs/release_facing_examples.md",
                "docs/tutorials/db_workloads.md",
            )
        )
        for phrase in (
            "--backend optix --output-mode compact_summary --require-rt-core",
            "--backend optix --optix-summary-mode gap_summary_prepared --require-rt-core",
            "--backend optix --optix-summary-mode count_summary_prepared --require-rt-core",
            "--backend optix --optix-summary-mode rt_count_threshold_prepared",
            "--backend optix --optix-summary-mode rt_core_flags_prepared",
            "--backend optix --optix-summary-mode prepared_count",
            "prepared_pose_flags",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_tutorials_record_rejected_app_families(self) -> None:
        checks = {
            "docs/tutorials/graph_workloads.md": (
                "host-indexed CSR fallback",
                "--optix-graph-mode native",
                "reject `--require-rt-core` intentionally",
            ),
            "docs/tutorials/nearest_neighbor_workloads.md": (
                "not NVIDIA RT-core claims",
                "reject these apps today",
            ),
            "docs/tutorials/segment_polygon_workloads.md": (
                "also reject\n`--require-rt-core` today",
                "not released NVIDIA RT-core claims",
            ),
        }
        for relative, phrases in checks.items():
            with self.subTest(relative=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                for phrase in phrases:
                    self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
