from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "librts-paper"
RUNNER_PATH = APP_DIR / "run_same_input_mutation_gate.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("librts_mutation_gate", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LibRtsSameInputMutationGateTest(unittest.TestCase):
    def test_committed_linux_gate_matches(self) -> None:
        payload = json.loads(
            (APP_DIR / "results" / "librts_goal5460_same_input_mutation.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["author"]["counts"], [2, 1, 0, 1, 0])
        self.assertEqual(payload["rtdl"]["counts"], [2, 1, 0, 1, 0])
        self.assertEqual(payload["author"]["implicit_inserted_id"], 2)
        self.assertEqual(payload["rtdl"]["inserted_ids"], [2])
        self.assertEqual(
            payload["execution_model_difference"],
            {
                "author": "native_incremental_gas_ias_update",
                "performance_comparison_authorized": False,
                "rtdl": "atomic_snapshot_rebuild",
            },
        )

    def test_cpu_gate_matches_author_sequence(self) -> None:
        module = _load_runner()
        author = {
            "schema": "librts.author_mutation_probe.v1",
            "counts": [2, 1, 0, 1, 0],
            "expected": [2, 1, 0, 1, 0],
            "implicit_inserted_id": 2,
            "matched": True,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "author.json"
            path.write_text(json.dumps(author), encoding="utf-8")
            payload = module.run_gate(author_probe_output=path, backend="cpu")

        self.assertTrue(payload["matched"])
        self.assertEqual(payload["comparison"]["counts"], [2, 1, 0, 1, 0])
        self.assertEqual(payload["rtdl"]["inserted_ids"], [2])
        self.assertEqual(payload["execution_model_difference"]["rtdl"], "atomic_snapshot_rebuild")
        self.assertFalse(payload["claim_boundary"]["native_incremental_rtdl_insert_delete_claimed"])
        self.assertFalse(payload["claim_boundary"]["embree_used"])

    def test_author_output_requires_expected_schema(self) -> None:
        module = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"schema":"wrong"}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                module.load_author_probe(path)

    def test_author_probe_is_app_owned_and_core_is_neutral(self) -> None:
        probe = (APP_DIR / "author_patches" / "goal5460_author_mutation_probe.cu").read_text(
            encoding="utf-8"
        )
        core = (ROOT / "src" / "rtdsl" / "mutable_aabb_index.py").read_text(encoding="utf-8").lower()
        self.assertIn("SpatialIndex<float, 2>", probe)
        self.assertIn("index.Update", probe)
        self.assertIn("index.Delete", probe)
        self.assertIn("index.Clear", probe)
        patch = (
            APP_DIR / "author_patches" / "goal5460_fix_instance_update_temp_buffer.patch"
        ).read_text(encoding="utf-8")
        self.assertIn("tempUpdateSizeInBytes", patch)
        self.assertIn("tempSizeInBytes", patch)
        for forbidden in ("librts", "rtspatial", "ray multicast", "paper"):
            self.assertNotIn(forbidden, core)


if __name__ == "__main__":
    unittest.main()
