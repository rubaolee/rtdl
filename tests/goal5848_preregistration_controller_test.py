from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from experiments.goal5848_strong_baseline import contracts, controller
from scripts import (
    goal5848_build_transaction_authority as transaction_authority,
)
from scripts import goal5848_freeze_preregistration as freeze


class Goal5848PreregistrationControllerTest(unittest.TestCase):
    def _arguments(self, root: Path) -> argparse.Namespace:
        values = {
            "python": Path(__import__("sys").executable),
            "expected_source_commit": "a" * 40,
            "predecessor_root": root / "predecessor",
            "expected_predecessor_commit": "b" * 40,
            "pyoptix_source": root / "pyoptix",
            "expected_pyoptix_commit": "c" * 40,
            "expected_pyoptix_tree": "d" * 40,
            "expected_optix_sdk": "8.0.0",
        }
        values["predecessor_root"].mkdir()
        values["pyoptix_source"].mkdir()
        for index, argument in enumerate(
            contracts.PREREGISTRATION_ARTIFACT_ARGUMENTS.values()
        ):
            path = root / f"artifact-{index}"
            path.write_bytes(f"artifact-{argument}".encode("ascii"))
            values[argument] = path
        return argparse.Namespace(**values)

    def test_freeze_binds_schedule_thresholds_and_every_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._arguments(root)
            identities = [
                {
                    "path": str(freeze.ROOT.resolve()),
                    "commit": "a" * 40,
                    "tree": "1" * 40,
                    "status": "",
                    "clean": True,
                },
                {
                    "path": str(args.predecessor_root.resolve()),
                    "commit": "b" * 40,
                    "tree": "2" * 40,
                    "status": "",
                    "clean": True,
                },
                {
                    "path": str(args.pyoptix_source.resolve()),
                    "commit": "c" * 40,
                    "tree": "d" * 40,
                    "status": "",
                    "clean": True,
                },
            ]
            with mock.patch.object(
                freeze, "_git_identity", side_effect=identities
            ), mock.patch.object(
                freeze, "load_device_artifact_receipt"
            ) as load, mock.patch.object(
                freeze, "load_aot_cache_authority"
            ) as load_aot:
                value = freeze.build_preregistration(args)
            unsigned = dict(value)
            seal = unsigned.pop("preregistration_sha256")
            self.assertEqual(seal, contracts.digest(unsigned))
            self.assertEqual(len(value["schedule"]), 80)
            self.assertEqual(
                set(value["artifacts"]),
                set(contracts.PREREGISTRATION_ARTIFACT_ARGUMENTS),
            )
            self.assertEqual(value["retry_count"], 0)
            self.assertEqual(value["discard_count"], 0)
            load.assert_called_once()
            load_aot.assert_called_once()

    def test_run_once_invokes_one_process_and_binds_exact_stdout(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "worker.json"
            process = root / "process.json"
            support = root / "support"
            support.mkdir()
            receipt = {"worker_id": "worker-0", "value": 7}
            output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            completed = subprocess.CompletedProcess(
                args=["worker"],
                returncode=0,
                stdout=(json.dumps(receipt, sort_keys=True) + "\n").encode(),
                stderr=b"",
            )
            args = argparse.Namespace(worker_timeout_seconds=1)
            row = {"worker_id": "worker-0"}
            with (
                mock.patch.object(controller, "_command", return_value=["worker"]),
                mock.patch.object(
                    controller.subprocess, "run", return_value=completed
                ) as run,
            ):
                observed = controller._run_once(
                    row,
                    args,
                    output=output,
                    process_output=process,
                    support_root=support,
                )
            self.assertEqual(observed, receipt)
            self.assertEqual(run.call_count, 1)
            process_value = json.loads(process.read_text())
            self.assertEqual(process_value["worker_id"], "worker-0")
            self.assertEqual(process_value["exit_code"], 0)
            self.assertEqual(
                process_value["execution_context"]["cwd"],
                str(controller.ROOT.resolve()),
            )
            self.assertEqual(
                process_value["execution_context"]["environment"]["PYTHONPATH"],
                f"{controller.ROOT / 'src'}:{controller.ROOT}",
            )

    def test_controller_and_authority_reconstruct_all_commands_and_context(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(strict=True)
            args = self._arguments(root)
            preregistration_path = root / "preregistration.json"
            preregistration_path.write_text("{}\n")
            args.preregistration = preregistration_path
            artifacts = {
                label: transaction_authority._file_identity(
                    Path(getattr(args, argument))
                )
                for label, argument in (
                    contracts.PREREGISTRATION_ARTIFACT_ARGUMENTS.items()
                )
            }
            preregistration = {
                "source_commit": args.expected_source_commit,
                "predecessor_commit": args.expected_predecessor_commit,
                "expected_optix_sdk": args.expected_optix_sdk,
                "python": transaction_authority._file_identity(
                    args.python.resolve(strict=True)
                ),
                "source_identity": {
                    "path": str(controller.ROOT.resolve(strict=True)),
                },
                "predecessor_identity": {
                    "path": str(args.predecessor_root.resolve(strict=True)),
                },
                "pyoptix_identity": {
                    "path": str(args.pyoptix_source.resolve(strict=True)),
                },
            }
            transaction_root = root / "transaction"
            support_root = transaction_root / "direct_support"
            for row in contracts.build_schedule():
                output = transaction_root / "workers" / f"{row['worker_id']}.json"
                self.assertEqual(
                    controller._command(row, args, output, support_root),
                    transaction_authority._expected_process_command(
                        row,
                        preregistration=preregistration,
                        artifacts=artifacts,
                        preregistration_path=preregistration_path,
                        transaction_root=transaction_root,
                    ),
                )

            formal_environment = {
                "PYTHONPATH": f"{controller.ROOT / 'src'}:{controller.ROOT}",
                "CUDA_VISIBLE_DEVICES": "0",
                "CUDA_CACHE_DISABLE": "1",
                "RTDL_OPTIX_DISK_CACHE_POLICY": "disabled",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONNOUSERSITE": "1",
            }
            self.assertEqual(
                controller._worker_execution_context(formal_environment),
                transaction_authority._expected_execution_context(
                    preregistration
                ),
            )

    def test_formal_output_root_rejects_repository_and_existing_path(self):
        with self.assertRaisesRegex(RuntimeError, "outside source Git"):
            controller._new_output_root(controller.ROOT / "formal-output")
        with (
            tempfile.TemporaryDirectory() as temporary,
            self.assertRaises(FileExistsError),
        ):
            controller._new_output_root(Path(temporary))

    def test_formal_worker_environment_fails_before_worker_zero(self):
        expected = dict(controller._FORMAL_INHERITED_ENVIRONMENT)
        with mock.patch.dict(os.environ, expected, clear=True):
            controller._require_formal_worker_environment()
        for name in expected:
            with (
                self.subTest(name=name),
                mock.patch.dict(os.environ, {**expected, name: "wrong"}, clear=True),
                self.assertRaisesRegex(RuntimeError, "environment differs"),
            ):
                controller._require_formal_worker_environment()
        for name in controller._FORMAL_SANITIZED_ENVIRONMENT:
            with (
                self.subTest(sanitized=name),
                mock.patch.dict(
                    os.environ,
                    {**expected, name: "unexpected"},
                    clear=True,
                ),
                self.assertRaisesRegex(RuntimeError, "environment differs"),
            ):
                controller._require_formal_worker_environment()


if __name__ == "__main__":
    unittest.main()
