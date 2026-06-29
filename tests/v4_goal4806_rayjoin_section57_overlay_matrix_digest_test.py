from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "scripts" / "rayjoin_section57_overlay_matrix.py"


def _load_matrix_module():
    spec = importlib.util.spec_from_file_location("rayjoin_section57_overlay_matrix_for_test", MATRIX_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {MATRIX_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class V4Goal4806RayJoinSection57OverlayMatrixDigestTest(unittest.TestCase):
    def test_command_output_json_update_also_updates_overlay_output(self) -> None:
        matrix = _load_matrix_module()
        command = [
            "python",
            "suite.py",
            "run-author",
            "--output-json",
            "old.json",
            "--overlay-output",
            "old.overlay.txt",
        ]

        updated = matrix._command_with_output_json(command, Path("new_iter3.json"))

        self.assertEqual(updated[updated.index("--output-json") + 1], "new_iter3.json")
        self.assertEqual(updated[updated.index("--overlay-output") + 1], "new_iter3.overlay.txt")

    def test_summary_records_raw_overlay_digest_matches(self) -> None:
        matrix = _load_matrix_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "out"
            output_dir.mkdir()
            paths = matrix._artifact_paths(output_dir, "county_zipcode")

            author_overlay = paths["author_rt"].with_suffix(".overlay.txt")
            optix_overlay = output_dir / "optix.overlay.txt"
            embree_overlay = output_dir / "embree.overlay.txt"
            author_overlay.write_text("chain 1\n0 0\n1 1\n", encoding="utf-8")
            optix_overlay.write_text("chain 1\n0 0\n1 1\n", encoding="utf-8")
            embree_overlay.write_text("chain 1\n0 0\n1 2\n", encoding="utf-8")

            paths["author_rt"].write_text(
                json.dumps(
                    {
                        "elapsed_sec": 1.25,
                        "overlay_output_digest": matrix._overlay_output_digest(author_overlay),
                    }
                ),
                encoding="utf-8",
            )
            paths["rtdl_optix"].write_text(
                json.dumps(
                    {
                        "phase_seconds": {"total_sec": 0.75},
                        "lsi": {"intersection_count": 7},
                        "output": {"path": str(optix_overlay)},
                    }
                ),
                encoding="utf-8",
            )
            paths["rtdl_embree"].write_text(
                json.dumps(
                    {
                        "phase_seconds": {"total_sec": 0.80},
                        "lsi": {"intersection_count": 7},
                        "output": {"path": str(embree_overlay)},
                    }
                ),
                encoding="utf-8",
            )
            paths["v4_numba"].write_text(
                json.dumps(
                    {
                        "claim_classification": "candidate_measurement",
                        "selected_plan": {
                            "plan_id": "p",
                            "measured_total_sec": 0.5,
                            "correctness_status": "pass",
                        },
                    }
                ),
                encoding="utf-8",
            )

            summary = matrix.summarize_results(
                Namespace(
                    pairs="county_zipcode",
                    output_dir=output_dir,
                    dataset_root=root / "dataset",
                )
            )

        row = summary["rows"][0]
        self.assertTrue(row["rtdl_optix_author_raw_output_digest_match"])
        self.assertFalse(row["rtdl_embree_author_raw_output_digest_match"])
        self.assertFalse(row["rtdl_optix_embree_raw_output_digest_match"])
        self.assertEqual(row["rtdl_optix_lsi_count"], 7)
        self.assertEqual(row["rtdl_embree_lsi_count"], 7)
        self.assertTrue(row["complete"])


if __name__ == "__main__":
    unittest.main()
