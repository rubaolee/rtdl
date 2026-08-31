from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest

from scripts import goal5793_x1_registry_derivation as registry
from scripts import goal5793_x1_run_generic_examiner as runner
from scripts.goal5793_x1_canonical import seal_document


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts/goal5793_x1_run_generic_examiner.py"


def _write(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


class Goal5793X1FreshRunnerTest(unittest.TestCase):
    def _files(self, root: Path):
        payload, receipt = registry.historical_registered_fixture(
            registry.POSITIVE_IDS[0]
        )
        authority, stage_pin, trusted = registry.historical_registry_context()
        candidate = root / "candidate.json"
        authority_path = root / "authority.json"
        pin_path = root / "stage_pin.json"
        output = root / "result.json"
        _write(candidate, {
            "schema": runner.INPUT_ENVELOPE_SCHEMA,
            "payload": payload,
            "registry_receipt": receipt,
        })
        _write(authority_path, authority)
        _write(pin_path, stage_pin)
        return candidate, authority_path, pin_path, output, trusted

    def _command(self, files, trusted=None):
        candidate, authority, pin, output, expected = files
        return [
            sys.executable,
            str(RUNNER_PATH),
            "--candidate-input", str(candidate),
            "--registry-authority", str(authority),
            "--registry-stage-pin", str(pin),
            "--trusted-stage-pin-sha256", trusted or expected,
            "--output", str(output),
        ]

    def test_fresh_subprocess_receipt_is_compatible_and_explicitly_nonhermetic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            files = self._files(Path(temp))
            environment = dict(os.environ)
            environment["PYTHONPATH"] = os.pathsep.join((str(ROOT), str(ROOT / "src")))
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            completed = subprocess.run(
                self._command(files), cwd=ROOT, env=environment,
                capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            result = json.loads(files[3].read_text(encoding="utf-8"))
            self.assertEqual(
                result["examiner_result"]["status"],
                "VALID_LAYERED_EXAMINATION",
            )
            self.assertEqual(
                result["examiner_result"]["final_verdict"],
                "COMPATIBLE_FOR_DECLARED_DOMAIN",
            )
            self.assertTrue(result["boundary"]["fresh_subprocess_required"])
            self.assertFalse(result["boundary"]["hermetic"])
            self.assertTrue(result["boundary"]["python_interpreter_in_tcb"])
            self.assertFalse(result["examiner_result"]["execution_authorized"])
            self.assertEqual(
                result["receipt_sha256"],
                seal_document(
                    result,
                    seal_field="receipt_sha256",
                    domain="rtdl.goal5793.x1.fresh_process_exam_receipt",
                    version=1,
                ),
            )

    def test_parent_preloaded_fake_examiner_cannot_cross_process_boundary(self) -> None:
        fake = types.ModuleType("scripts.goal5793_x1_generic_examiner")
        fake.examine = lambda *args, **kwargs: {
            "status": "FAKE", "final_verdict": "COMPATIBLE_FOR_DECLARED_DOMAIN"
        }
        previous = sys.modules.get(fake.__name__)
        sys.modules[fake.__name__] = fake
        try:
            with tempfile.TemporaryDirectory() as temp:
                files = self._files(Path(temp))
                environment = dict(os.environ)
                environment["PYTHONPATH"] = os.pathsep.join((str(ROOT), str(ROOT / "src")))
                completed = subprocess.run(
                    self._command(files), cwd=ROOT, env=environment,
                    capture_output=True, text=True, timeout=60, check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                result = json.loads(files[3].read_text(encoding="utf-8"))
                self.assertNotEqual(result["examiner_result"]["status"], "FAKE")
        finally:
            if previous is None:
                sys.modules.pop(fake.__name__, None)
            else:
                sys.modules[fake.__name__] = previous

    def test_wrong_out_of_band_pin_fails_closed_and_is_receipted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            files = self._files(Path(temp))
            environment = dict(os.environ)
            environment["PYTHONPATH"] = os.pathsep.join((str(ROOT), str(ROOT / "src")))
            completed = subprocess.run(
                self._command(files, "0" * 64), cwd=ROOT, env=environment,
                capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
            result = json.loads(files[3].read_text(encoding="utf-8"))
            self.assertEqual(result["examiner_result"]["status"], "INFRA_INVALID")
            self.assertTrue(any(
                "out_of_band_trusted_stage_pin_mismatch" in reason
                for reason in result["examiner_result"]["reasons"]
            ))

    def test_candidate_envelope_cannot_embed_authority_or_stage_pin(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            files = self._files(Path(temp))
            candidate = json.loads(files[0].read_text(encoding="utf-8"))
            candidate["registry_authority"] = json.loads(
                files[1].read_text(encoding="utf-8")
            )
            _write(files[0], candidate)
            completed = subprocess.run(
                self._command(files), cwd=ROOT, env=dict(os.environ),
                capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(files[3].exists())
            self.assertIn("candidate_envelope_keyset_mismatch", completed.stderr)


if __name__ == "__main__":
    unittest.main()
