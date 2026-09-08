from pathlib import Path
import sys
import tempfile
import unittest

from scripts import v4_long_workload_controller as controller
from scripts import v4_long_workload_independent_recount as recount
from scripts import v4_long_workload_worker as worker


def _config():
    units = {
        "particle": {
            "unit_id": "particle", "app": "particle_tracking",
            "operation": None, "prepared_repetitions": 32,
        },
        "graph_old": {
            "unit_id": "graph_old", "app": "triangle_counting",
            "operation": None, "prepared_repetitions": 4,
        },
        "librts_point": {
            "unit_id": "librts_point", "app": "librts",
            "operation": "point_contains", "prepared_repetitions": 4,
        },
        "librts_range": {
            "unit_id": "librts_range", "app": "librts",
            "operation": "range_contains", "prepared_repetitions": 4,
        },
        "graph_long": {
            "unit_id": "graph_long", "app": "triangle_counting",
            "operation": None, "prepared_repetitions": 3,
        },
    }
    implementation = {
        "source_root": "/source", "source_commit": "a" * 40,
        "source_tree": "b" * 40, "native_library_path": "/native.so",
        "native_library_sha256": "c" * 64,
    }
    return {
        "schema": controller.CONFIG_SCHEMA,
        "common": {"prepared_warmups": 1},
        "implementations": {
            "old_v4": implementation,
            "new_v4": implementation,
            "pyoptix": implementation,
        },
        "units": units,
    }


class V4LongWorkloadHarnessTest(unittest.TestCase):
    def test_independent_recount_validates_registered_machine_projection(self):
        common = {
            "registered_machine": {
                "cuda_visible_devices": "0",
                "gpu": {
                    "name": "GPU", "uuid": "uuid", "driver": "driver",
                    "compute_capability": "8.6",
                },
            },
            "python_version": "3.12.3",
            "python_executable": "/venv/bin/python",
        }
        observed = {
            **common["registered_machine"],
            "hostname": "pod",
            "platform": "Linux",
            "python": common["python_version"],
            "python_executable": common["python_executable"],
        }
        recount.validate_worker_machine(observed, common, ordinal=0)

        invalid = []
        changed_gpu = {**observed, "gpu": {**observed["gpu"], "uuid": "other"}}
        invalid.append(changed_gpu)
        invalid.append({**observed, "python": "3.11.0"})
        invalid.append({**observed, "unexpected": "not-authorized"})
        missing = dict(observed)
        del missing["platform"]
        invalid.append(missing)
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(RuntimeError):
                    recount.validate_worker_machine(value, common, ordinal=0)

    def test_formal_schedule_has_exact_population_and_balanced_pair_order(self):
        schedule = controller.build_schedule(_config(), mode="formal")
        self.assertEqual(len(schedule), 240)
        self.assertEqual({row["endpoint"] for row in schedule}, {
            "complete", "prepared"})
        for left, right in (
            ("old_v4", "new_v4"),
            ("old_v4", "pyoptix"),
            ("new_v4", "pyoptix"),
        ):
            before = sum(order.index(left) < order.index(right)
                         for order in controller.BLOCK_ORDERS)
            self.assertEqual(before, 4)
        particle_prepared = [
            row for row in schedule
            if row["unit_id"] == "particle" and row["endpoint"] == "prepared"
        ]
        self.assertEqual(len(particle_prepared), 24)
        self.assertTrue(all(row["repetitions"] == 32 and row["warmups"] == 1
                            for row in particle_prepared))
        long_prepared = [
            row for row in schedule
            if row["unit_id"] == "graph_long"
            and row["endpoint"] == "prepared"
        ]
        self.assertTrue(all(row["repetitions"] == 3 for row in long_prepared))

    def test_dry_schedule_covers_each_unit_and_arm_once(self):
        schedule = controller.build_schedule(_config(), mode="dry-run")
        self.assertEqual(len(schedule), 15)
        self.assertEqual(
            {(row["unit_id"], row["arm"]) for row in schedule},
            {(unit, arm) for unit in _config()["units"] for arm in controller.ARMS},
        )
        self.assertTrue(all(row["repetitions"] == 1 and row["warmups"] == 0
                            for row in schedule))

    def test_worker_selects_only_registered_arm_fields(self):
        config = _config()
        config["common"].update({"shared": 7, "source_root": "wrong"})
        config["implementations"]["new_v4"] = {
            **config["implementations"]["new_v4"], "source_root": "/new",
        }
        selected = worker._selected_config(config, "new_v4")
        self.assertEqual(selected["shared"], 7)
        self.assertEqual(selected["source_root"], "/new")
        with self.assertRaises(KeyError):
            worker._selected_config(config, "unknown")

    def test_launch_keeps_stdout_and_stderr_as_separate_raw_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            stdout = root / "stdout" / "worker.bin"
            stderr = root / "stderr" / "worker.bin"
            result = controller._launch(
                [sys.executable, "-c",
                 "import sys;sys.stdout.buffer.write(b'out\\x00');"
                 "sys.stderr.buffer.write(b'err\\xff')"],
                cwd=root, stdout_path=stdout, stderr_path=stderr,
                timeout_seconds=10,
            )
            self.assertEqual(result["return_code"], 0)
            self.assertFalse(result["timeout"])
            self.assertEqual(stdout.read_bytes(), b"out\x00")
            self.assertEqual(stderr.read_bytes(), b"err\xff")

    def test_launch_failure_is_retained_instead_of_raising(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = controller._launch(
                [str(root / "missing-executable")], cwd=root,
                stdout_path=root / "stdout.bin",
                stderr_path=root / "stderr.bin", timeout_seconds=10,
            )
            self.assertEqual(result["return_code"], 127)
            self.assertIn("FileNotFoundError", result["launch_error"])
            self.assertFalse(result["timeout"])

    def test_worker_journal_is_append_only_and_fsynced(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "events.jsonl"
            path.touch()
            worker._append(path, {"event": "one"})
            first = path.read_bytes()
            worker._append(path, {"event": "two"})
            second = path.read_bytes()
            self.assertTrue(second.startswith(first))
            self.assertEqual(second.count(b"\n"), 2)


if __name__ == "__main__":
    unittest.main()
