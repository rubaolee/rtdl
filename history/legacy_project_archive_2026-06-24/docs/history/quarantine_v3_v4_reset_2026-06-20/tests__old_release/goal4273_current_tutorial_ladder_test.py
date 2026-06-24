"""Goal4273: current v2.10 tutorial ladder stays beginner-safe."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_TUTORIAL_DIR = ROOT / "tutorials" / "current"


class CurrentTutorialLadderTest(unittest.TestCase):
    def test_ordered_current_tutorial_files_exist(self) -> None:
        expected = [
            "README.md",
            "01_source_tree_first_run.md",
            "02_kernel_shape_and_backends.md",
            "03_primitives_and_discovery.md",
            "04_python_app_structure.md",
            "05_partner_columns_cupy_numba.md",
            "06_prepared_execution_measurement.md",
            "07_benchmark_app_python_rtdl_partner.md",
            "08_spatial_join_rayjoin_reference.md",
        ]
        missing = [
            name for name in expected if not (CURRENT_TUTORIAL_DIR / name).is_file()
        ]
        self.assertEqual([], missing)

    def test_current_track_is_front_door(self) -> None:
        tutorials_readme = (ROOT / "tutorials" / "README.md").read_text(encoding="utf-8")
        learn_readme = (ROOT / "docs" / "learn" / "README.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("current/README.md", tutorials_readme)
        self.assertIn("current/01_source_tree_first_run.md", tutorials_readme)
        self.assertIn("../../tutorials/current/README.md", learn_readme)

    def test_current_tutorial_links_resolve(self) -> None:
        docs = list(CURRENT_TUTORIAL_DIR.glob("*.md")) + [
            ROOT / "tutorials" / "README.md",
            ROOT / "docs" / "learn" / "README.md",
        ]
        broken: list[str] = []
        link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for doc in docs:
            text = doc.read_text(encoding="utf-8")
            for raw_target in link_re.findall(text):
                target = raw_target.split("#", 1)[0]
                if not target or target.startswith(("http://", "https://", "mailto:")):
                    continue
                resolved = (doc.parent / target).resolve()
                if not resolved.exists():
                    broken.append(f"{doc.relative_to(ROOT)} -> {raw_target}")
        self.assertEqual([], broken)

    def test_current_track_has_no_legacy_example_path_or_version_soup(self) -> None:
        blocked = [
            "examples/v2_0",
            "examples\\v2_0",
            "examples.v2_0",
            "v2.6",
            "v2.7",
            "v2.8",
            "v2.9",
            "PyTorch",
            "Triton",
        ]
        hits: list[str] = []
        for doc in CURRENT_TUTORIAL_DIR.glob("*.md"):
            text = doc.read_text(encoding="utf-8")
            for token in blocked:
                if token in text:
                    hits.append(f"{doc.relative_to(ROOT)} contains {token}")
        self.assertEqual([], hits)

    def test_benchmark_tutorial_teaches_both_partner_choices(self) -> None:
        text = (
            CURRENT_TUTORIAL_DIR / "07_benchmark_app_python_rtdl_partner.md"
        ).read_text(encoding="utf-8")
        required = [
            "partner_cupy_grid_components_3d",
            "partner_numba_grid_components_3d",
            "partner_numba_prepared_grid_components_3d",
            "optix_rt_core_flags_numba_prepared_grid_components_3d",
            "cpu_reference",
            "rtdl_cpu_rows",
            "RTDL engine sees generic fixed-radius and grouped-stream contracts",
        ]
        missing = [token for token in required if token not in text]
        self.assertEqual([], missing)
        self.assertIn("CuPy and Numba are explicit choices", text)
        self.assertIn("optional OptiX", text)

    def test_spatial_join_reference_is_in_tutorial_track(self) -> None:
        index = (CURRENT_TUTORIAL_DIR / "README.md").read_text(encoding="utf-8")
        tutorial_index = (ROOT / "tutorials" / "README.md").read_text(encoding="utf-8")
        reference = (
            CURRENT_TUTORIAL_DIR / "08_spatial_join_rayjoin_reference.md"
        ).read_text(encoding="utf-8")

        self.assertIn("08_spatial_join_rayjoin_reference.md", index)
        self.assertIn("08_spatial_join_rayjoin_reference.md", tutorial_index)
        self.assertIn("CODE_WALKTHROUGH.md", reference)
        self.assertIn("RayJoin-style spatial join", reference)


if __name__ == "__main__":
    unittest.main()
