import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Section56ScalabilityTest(unittest.TestCase):
    def test_synthetic_polygon_generation_is_deterministic(self) -> None:
        a = rt.generate_synthetic_polygons(count=8, distribution="uniform", seed=7)
        b = rt.generate_synthetic_polygons(count=8, distribution="uniform", seed=7)
        c = rt.generate_synthetic_polygons(count=8, distribution="gaussian", seed=7)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_artifact_generation_smoke(self) -> None:
        cfg = rt.ScalabilityConfig(
            build_polygons=40,
            probe_series=(10, 20, 30, 40, 50),
            iterations=1,
            warmup=0,
            base_seed=11,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts = rt.generate_section_5_6_artifacts(
                output_dir=tmpdir,
                config=cfg,
                publish_docs=False,
            )
            for key in ("json", "figure13_svg", "figure14_svg", "markdown", "pdf"):
                self.assertTrue(Path(artifacts[key]).exists(), key)

            payload = Path(artifacts["json"]).read_text(encoding="utf-8")
            self.assertIn("rtdl_section_5_6_scalability", payload)
            self.assertIn("Figure 13 analogue", Path(artifacts["markdown"]).read_text(encoding="utf-8"))
            self.assertGreater(Path(artifacts["pdf"]).stat().st_size, 200)


if __name__ == "__main__":
    unittest.main()
