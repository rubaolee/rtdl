from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/nine_app_authored_particle_formal_compare.py"


def _load():
    name = "nine_app_authored_particle_formal_compare_test_module"
    specification = importlib.util.spec_from_file_location(name, SCRIPT)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load authored Particle formal protocol")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


class NineAppAuthoredParticleFormalProtocolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = _load()

    def test_schedule_has_eight_balanced_fresh_process_pairs(self):
        self.assertEqual(len(self.protocol.ORDERS), 8)
        self.assertEqual(
            sum(order == ("rtdl", "pyoptix")
                for order in self.protocol.ORDERS),
            4,
        )
        self.assertEqual(
            sum(order == ("pyoptix", "rtdl")
                for order in self.protocol.ORDERS),
            4,
        )

    def test_source_closure_is_unique_and_present(self):
        self.assertEqual(
            len(self.protocol.SOURCE_PATHS),
            len(set(self.protocol.SOURCE_PATHS)),
        )
        for relative in self.protocol.SOURCE_PATHS:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_json_rejects_nonfinite_values_on_write_and_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(ValueError):
                self.protocol.write_new(root / "write.json", {
                    "bad": float("inf"),
                })
            path = root / "read.json"
            path.write_text('{"bad": NaN}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                self.protocol.read_json(path)

    def test_block_bootstrap_is_deterministic_and_bounded(self):
        values = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]
        first = self.protocol.bootstrap_interval(values)
        second = self.protocol.bootstrap_interval(values)
        self.assertEqual(first, second)
        self.assertLessEqual(min(values), first[0])
        self.assertLessEqual(first[0], first[1])
        self.assertLessEqual(first[1], max(values))

    def test_worker_validation_recounts_median_and_lifecycle_fields(self):
        prereg = {
            "source_commit": "commit",
            "source_tree": "tree",
            "data_manifest": {"sha256": "input"},
            "independent_oracle_sha256": "oracle",
            "output_sha256": "output",
            "pyoptix_ptx": {"sha256": "ptx"},
            "worker_machine": {"gpu_uuid": "gpu"},
        }
        result = {
            "schema": "rtdl.v4.authored_particle_worker.v2",
            "status": "PASS",
            "arm": "pyoptix",
            "source": {"commit": "commit", "tree": "tree"},
            "input_sha256": "input",
            "independent_oracle_sha256": "oracle",
            "query_count": 5_000,
            "output_shape": [5_000, 3],
            "output_sha256": "output",
            "warmup_count": 1,
            "sample_count": 3,
            "samples_ns": [11, 13, 17],
            "median_ns": 13,
            "prepare_ns": 19,
            "close_ns": 23,
            "lifecycle_ns": 29,
            "retained_output_owned": True,
            "retained_output_read_only": True,
            "machine": {"gpu_uuid": "gpu"},
            "metadata": {
                "pyoptix_ptx_sha256": "ptx",
                "prevalidated_execution_input_used": True,
                "prepared_query_batch_used": True,
                "prepared_query_batch_device_resident": True,
                "prepared_query_batch_operation_counts": {
                    "query_h2d_copy_call_count": 7,
                    "query_h2d_bytes": 140_000,
                },
            },
            "last_execution_evidence": {
                "control": [5000, 0xFFFFFFFF, 0, 0],
                "operation_counts": {
                    "query_h2d_copy_call_count": 0,
                    "query_h2d_bytes": 0,
                    "optix_launch_call_count": 1,
                    "output_d2h_bytes": 60_000,
                },
            },
        }
        self.protocol.validate_worker(
            prereg, result, "pyoptix", warmups=1, samples=3)

        bad_median = json.loads(json.dumps(result))
        bad_median["median_ns"] = 12
        with self.assertRaises(ValueError):
            self.protocol.validate_worker(
                prereg, bad_median, "pyoptix", warmups=1, samples=3)

        bad_lifecycle = json.loads(json.dumps(result))
        bad_lifecycle["close_ns"] = 0
        with self.assertRaises(ValueError):
            self.protocol.validate_worker(
                prereg, bad_lifecycle, "pyoptix", warmups=1, samples=3)


if __name__ == "__main__":
    unittest.main()
