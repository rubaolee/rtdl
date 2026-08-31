from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py"


def _load_app():
    spec = importlib.util.spec_from_file_location("goal5776_rtbh_app", APP)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Goal5776RtBarnesHutRealScaleInputTest(unittest.TestCase):
    def test_author_state_and_force_file_form_one_generic_spec(self) -> None:
        app = _load_app()
        fixture = app._fixture_module()
        author = fixture._load_author()
        bodies = author.make_synthetic_bodies(32)
        payload = author.author_tree_prepared_arrays_payload(bodies)
        expected = author.compute_author_contract_forces(bodies)["force_rows"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prepared_path = root / "prepared.json"
            forces_path = root / "forces.txt"
            prepared_path.write_text(
                json.dumps(payload, sort_keys=True), encoding="utf-8")
            with forces_path.open("w", encoding="utf-8") as stream:
                for row in expected:
                    stream.write(
                        f"{int(row['source_id'])} {float(row['scalar_force']):.9g}\n")
            data = app.load_real_scale_v4_input(
                prepared_path,
                forces_path,
                expected_prepared_sha256=_sha256(prepared_path),
                expected_forces_sha256=_sha256(forces_path),
            )
        self.assertEqual(data["spec"].prepared_hierarchy.hierarchy.point_count, 32)
        self.assertEqual(len(data["expected_rows"]), 32)
        self.assertTrue(data["real_scale_author_state"])

    def test_force_rows_reject_sparse_identity(self) -> None:
        app = _load_app()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "forces.txt"
            path.write_text("0 1.0\n2 3.0\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "dense and source-ordered"):
                app._read_force_rows(path)

    def test_real_scale_force_contract_uses_the_frozen_relative_tolerance(self) -> None:
        app = _load_app()
        expected = ({"source_id": 0, "scalar_force": 866_778_846.0},)
        within = ({"source_id": 0, "scalar_force": 866_777_016.0},)
        outside = ({"source_id": 0, "scalar_force": 866_760_000.0},)
        accepted = app._compare_force_rows(within, expected)
        rejected = app._compare_force_rows(outside, expected)
        self.assertTrue(accepted["matched"])
        self.assertLessEqual(
            accepted["maximum_rel_delta"], app.FORCE_RELATIVE_TOLERANCE)
        self.assertFalse(rejected["matched"])
        self.assertEqual(rejected["mismatch_count"], 1)

    def test_force_contract_never_tolerates_source_identity_drift(self) -> None:
        app = _load_app()
        result = app._compare_force_rows(
            ({"source_id": 1, "scalar_force": 1.0},),
            ({"source_id": 0, "scalar_force": 1.0},),
        )
        self.assertFalse(result["matched"])
        self.assertEqual(result["mismatch_count"], 1)


if __name__ == "__main__":
    unittest.main()
