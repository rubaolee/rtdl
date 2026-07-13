from __future__ import annotations

import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "prepare_xhd_scaled_ply_candidate.py"
)
SCRIPT_DIR = SCRIPT.parent

import sys

sys.path.insert(0, str(SCRIPT_DIR))

from xhd_input_loader import load_points_matrix


def _load_module():
    spec = importlib.util.spec_from_file_location("prepare_xhd_scaled_ply_candidate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_binary_be_ply(path: Path) -> None:
    header = "\n".join(
        [
            "ply",
            "format binary_big_endian 1.0",
            "element vertex 2",
            "property float x",
            "property float y",
            "property float z",
            "element face 0",
            "property list uchar int vertex_indices",
            "end_header",
        ]
    ).encode("ascii") + b"\n"
    path.write_bytes(
        header
        + struct.pack(">fff", 1000.0, -2000.0, 3000.0)
        + struct.pack(">fff", 4000.0, 5000.0, -6000.0)
    )


class Goal5234XhdScaledPlyCandidateTest(unittest.TestCase):
    def test_scaled_candidate_writes_binary_big_endian_vertices(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "raw.ply"
            dst = root / "scaled.ply"
            summary = root / "summary.json"
            _write_binary_be_ply(src)

            result = module.build_summary(
                type(
                    "Args",
                    (),
                    {
                        "input": src,
                        "output": dst,
                        "summary": summary,
                        "scale": 0.001,
                        "n_dims": 3,
                        "run_goal": "Goal5234",
                    },
                )()
            )
            matrix = load_points_matrix(dst, n_dims=3, input_type="ply")

        self.assertEqual(result["vertex_count"], 2)
        self.assertEqual(result["output_format"], "binary_big_endian 1.0")
        self.assertFalse(result["claim_boundary"]["exact_paper_dataset_identity_claimed"])
        np.testing.assert_allclose(
            matrix,
            np.asarray([[1.0, -2.0, 3.0], [4.0, 5.0, -6.0]], dtype=np.float64),
        )

    def test_script_remains_app_owned(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8").lower()
        self.assertIn("app_owned_input_preprocessing", text)
        for forbidden in ("rtdsl", "optix", "native_symbol", "figure 6 reproduced"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
