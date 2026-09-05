from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.goal5848_strong_baseline import contracts
from scripts import goal5848_build_cross_generation_authority as authority


class Goal5848CrossGenerationAuthorityTest(unittest.TestCase):
    @staticmethod
    def _write(path: Path, *, capability: str, uuid: str) -> None:
        value = {
            "schema": "rtdl.goal5848.single_generation_authority.v1",
            "status": "PASS__INDEPENDENT_BYTE_AND_GATE_RECOUNT",
            "source_commit": "a" * 40,
            "predecessor_commit": "b" * 40,
            "worker_count": 80,
            "process_count": 80,
            "direct_support_count": 16,
            "instrumentation_overhead": {
                "path": "/tmp/instrumentation.json",
                "bytes": 1,
                "sha256": "c" * 64,
            },
            "device_artifact_build_receipt": {
                "path": "/tmp/device_artifact_build_receipt.json",
                "bytes": 1,
                "sha256": "d" * 64,
            },
            "aot_cache_authority": {
                "path": "/tmp/aot_cache_authority.json",
                "bytes": 1,
                "sha256": "e" * 64,
            },
            "aot_cache_authority_sha256": "f" * 64,
            "retry_count": 0,
            "discard_count": 0,
            "recount": {
                "hardware": {
                    "gpu_uuid": uuid,
                    "compute_capability": capability,
                },
                "tasks": {
                    task: {"all_performance_gates_pass": True}
                    for task in contracts.TASKS
                },
            },
            "external_review_complete": False,
            "public_or_manuscript_claim_authorized": False,
        }
        value["authority_sha256"] = contracts.digest(value)
        payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
        path.write_text(payload)
        path.with_name(f"{path.stem}.recount{path.suffix}").write_text(payload)

    def test_distinct_ampere_and_ada_pass_without_cross_machine_ratio(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "ampere.json"
            second = root / "ada.json"
            self._write(first, capability="8.6", uuid="GPU-ampere")
            self._write(second, capability="8.9", uuid="GPU-ada")
            result = authority.build(first, second)
            self.assertEqual(result["architectures"], ["ADA", "AMPERE"])
            self.assertFalse(result["cross_machine_raw_time_ratio_computed"])

    def test_same_architecture_and_adverse_task_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first.json"
            second = root / "second.json"
            self._write(first, capability="8.9", uuid="GPU-one")
            self._write(second, capability="8.9", uuid="GPU-two")
            with self.assertRaisesRegex(RuntimeError, "not distinct"):
                authority.build(first, second)
            value = json.loads(second.read_text())
            value["recount"]["hardware"]["compute_capability"] = "8.6"
            value["recount"]["tasks"][contracts.TRIANGLE_TASK][
                "all_performance_gates_pass"
            ] = False
            value["authority_sha256"] = contracts.digest({
                key: item
                for key, item in value.items()
                if key != "authority_sha256"
            })
            payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
            second.write_text(payload)
            (root / "second.recount.json").write_text(payload)
            with self.assertRaisesRegex(RuntimeError, "gate evidence"):
                authority.build(first, second)

    def test_missing_or_nonidentical_recount_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first.json"
            second = root / "second.json"
            self._write(first, capability="8.6", uuid="GPU-one")
            self._write(second, capability="8.9", uuid="GPU-two")
            first_recount = root / "first.recount.json"
            first_recount.unlink()
            with self.assertRaisesRegex(RuntimeError, "byte-identical recount"):
                authority.build(first, second)
            first_recount.write_text(first.read_text() + "\n")
            with self.assertRaisesRegex(RuntimeError, "byte-identical recount"):
                authority.build(first, second)


if __name__ == "__main__":
    unittest.main()
