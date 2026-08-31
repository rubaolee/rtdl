from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "librts-paper"
APP_PATH = APP_DIR / "librts_reproduction.py"


def _load_app():
    sys.path.insert(0, str(APP_DIR))
    spec = importlib.util.spec_from_file_location("librts_goal5464_app", APP_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5464LibRtsPipContractAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = _load_app()

    def test_cpu_fixture_requires_exact_polygon_refine(self) -> None:
        payload = self.app.run_pip(backend="cpu")
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["result_count"], 4)
        self.assertEqual(payload["bbox_only_candidate_count"], 5)
        self.assertTrue(payload["polygon_refine_discriminating"])
        self.assertEqual(
            payload["candidate_id_rows"],
            [[0, 0], [0, 2], [2, 1], [4, 0]],
        )
        self.assertEqual(payload["public_program"], "traverse -> point_in_polygon -> emit")
        self.assertFalse(payload["native_engine_customization"])

    def test_polygon_parser_fails_closed_for_holes_and_degenerate_rings(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not support polygon holes"):
            self.app.parse_polygon_wkt(
                "POLYGON ((0 0, 4 0, 0 4, 0 0), (1 1, 2 1, 1 2, 1 1))"
            )
        with self.assertRaisesRegex(ValueError, "at least three distinct vertices"):
            self.app.parse_polygon_wkt("POLYGON ((0 0, 1 0, 0 0))")

    def test_cli_pip_mode_writes_matching_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "pip.json"
            code = self.app.main(["--mode", "pip", "--backend", "cpu", "--output", str(output)])
            self.assertEqual(code, 0)
            self.assertIn('"matched": true', output.read_text(encoding="utf-8"))

    def test_author_build_wrapper_is_app_owned_and_algorithm_neutral(self) -> None:
        wrapper = (
            APP_DIR
            / "author_patches"
            / "goal5464_spatialquerybenchmark_pip_only_CMakeLists.txt"
        ).read_text(encoding="utf-8")
        self.assertIn("src/query/pip.cpp", wrapper)
        self.assertIn("src/query/rtspatial/pip_query.cu", wrapper)
        self.assertIn('"query/rtspatial/pip_handler.h"', wrapper)
        self.assertNotIn("Embree", wrapper)
        self.assertNotIn("point_in_polygon", wrapper)


if __name__ == "__main__":
    unittest.main()
