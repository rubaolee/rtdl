from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1232PublicDocMapTest(unittest.TestCase):
    def test_public_doc_map_covers_user_priorities(self) -> None:
        text = (ROOT / "docs" / "public_documentation_map.md").read_text(encoding="utf-8")

        for phrase in (
            "Front page and project promise",
            "Tutorials",
            "Apps",
            "Examples",
            "Architecture",
            "Programming model",
            "IR and lowering",
            "Performance",
            "v1.5 is the current public release",
            "v1.0 remains the foundation proof line",
            "v1.5 is not a whole-app speedup release",
            "v2.0 is the broader performance target",
            "`--backend optix` is not by itself an NVIDIA RT-core speedup claim",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_ir_and_performance_docs_record_current_boundaries(self) -> None:
        ir_text = (ROOT / "docs" / "rtdl" / "ir_and_lowering.md").read_text(encoding="utf-8")
        perf_text = (ROOT / "docs" / "performance_model.md").read_text(encoding="utf-8")

        for phrase in (
            "CompiledKernel",
            "RTExecutionPlan",
            "rtdl-plan-v1alpha1",
            "Current lowering is predicate-specific",
            "ANY_HIT",
            "COUNT_HITS",
            "REDUCE_FLOAT",
            "REDUCE_INT",
            "COLLECT_K_BOUNDED",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, ir_text)

        for phrase in (
            "Python is the authoring/control plane",
            "Only level 4 is a public speedup claim",
            "Raw/prepared/native summary paths are the serious performance path",
            "v1.5 keeps the v1.0 app-shaped proof history",
            "v2.0 is the broader performance target",
            "RTDL accelerates <exact prepared/native sub-path>",
            "Embree is a ray-tracing/BVH backend",
            "optix_still_slower_with_reason",
            "slower OptiX result is acceptable engineering evidence",
            "cannot authorize\npositive public RTX speedup wording",
            "The released v1.5 package has pod-verified standalone Embree+OptiX subpaths",
            "COLLECT_K_BOUNDED` remains experimental",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, perf_text)

    def test_entry_points_link_the_map_ir_and_perf_docs(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        language_index = (ROOT / "docs" / "rtdl" / "README.md").read_text(encoding="utf-8")

        self.assertIn("[Public Documentation Map](docs/public_documentation_map.md)", readme)
        self.assertIn("[App And Example Quickstart](docs/app_example_quickstart.md)", readme)
        self.assertIn("[Performance Model](docs/performance_model.md)", readme)
        self.assertIn("[IR And Lowering](docs/rtdl/ir_and_lowering.md)", readme)
        self.assertIn("[Public Documentation Map](public_documentation_map.md)", docs_index)
        self.assertIn("[App And Example Quickstart](app_example_quickstart.md)", docs_index)
        self.assertIn("[Performance Model](performance_model.md)", docs_index)
        self.assertIn("[IR And Lowering](rtdl/ir_and_lowering.md)", docs_index)
        self.assertIn("[IR And Lowering](ir_and_lowering.md)", language_index)

    def test_app_example_quickstart_is_short_and_honest(self) -> None:
        text = (ROOT / "docs" / "app_example_quickstart.md").read_text(encoding="utf-8")
        compact = " ".join(text.split())

        for phrase in (
            "First Three Commands",
            "Choose An App",
            "Choose An Example Type",
            "RTX Rule For App Runs",
            "Recommended v1.0 Demo Path",
            "--backend optix is not a public NVIDIA RT-core speedup claim",
            "Only claim the exact prepared/native sub-path",
            "RTDL can express real app-shaped RT workloads from Python",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

        self.assertLessEqual(len(text.splitlines()), 140)
        self.assertIn("whole-app acceleration", compact)


if __name__ == "__main__":
    unittest.main()
