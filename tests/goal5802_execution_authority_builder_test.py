from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from experiments.goal5802_premeasurement.controller import (
    OWNER_WAIVER_REASON,
    validate_execution_authority,
)
from experiments.goal5802_premeasurement.independent_recount import (
    _validate_execution_authority_bytes,
)
from scripts.goal5802_build_formal_execution_authority import (
    build_authority,
    build_owner_waiver_authority,
)


class Goal5802ExecutionAuthorityBuilderTest(unittest.TestCase):
    def _inputs(self, root: Path) -> tuple[Path, Path, Path, str]:
        freeze = root / "freeze.json"
        runtime = root / "runtime.json"
        cfr = root / "cfr.md"
        freeze.write_bytes(b"freeze\n")
        runtime.write_bytes(b"runtime\n")
        cfr.write_bytes(b"exact reviewed CFR\n")
        return freeze, runtime, cfr, hashlib.sha256(cfr.read_bytes()).hexdigest()

    def _build(self, root: Path, **changes):
        freeze, runtime, cfr, cfr_sha = self._inputs(root)
        values = {
            "freeze": freeze,
            "runtime_manifest": runtime,
            "external_cfr": cfr,
            "expected_external_cfr_sha256": cfr_sha,
            "external_review_p0": 0,
            "external_review_p1": 0,
            "external_exact_byte_approval": True,
            "owner_execution_authorized": True,
            "formal_worker_zero_authorized": True,
            "pod_gpu_timing_authorized": True,
        }
        values.update(changes)
        return build_authority(**values)

    def test_exact_positive_authority_validates(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            authority = self._build(root)
            validate_execution_authority(
                authority,
                freeze_sha256=hashlib.sha256(b"freeze\n").hexdigest(),
                runtime_manifest_sha256=hashlib.sha256(
                    b"runtime\n").hexdigest(),
            )
            _validate_execution_authority_bytes(
                authority,
                freeze_sha=hashlib.sha256(b"freeze\n").hexdigest(),
                runtime_sha=hashlib.sha256(b"runtime\n").hexdigest(),
            )
            unsigned = dict(authority)
            observed = unsigned.pop("execution_authority_sha256")
            from experiments.goal5802_premeasurement import contract
            self.assertEqual(
                observed, hashlib.sha256(contract.canonical(unsigned)).hexdigest())

    def test_nonzero_review_or_missing_approval_is_rejected(self):
        for changes in (
                {"external_review_p0": 1},
                {"external_review_p1": 1},
                {"external_exact_byte_approval": False},
                {"owner_execution_authorized": False},
                {"formal_worker_zero_authorized": False},
                {"pod_gpu_timing_authorized": False}):
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as temporary:
                with self.assertRaises(RuntimeError):
                    self._build(Path(temporary), **changes)

    def test_wrong_or_mutated_cfr_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            freeze, runtime, cfr, cfr_sha = self._inputs(root)
            cfr.write_bytes(b"changed after review\n")
            with self.assertRaisesRegex(RuntimeError, "differs"):
                build_authority(
                    freeze=freeze, runtime_manifest=runtime,
                    external_cfr=cfr,
                    expected_external_cfr_sha256=cfr_sha,
                    external_review_p0=0, external_review_p1=0,
                    external_exact_byte_approval=True,
                    owner_execution_authorized=True,
                    formal_worker_zero_authorized=True,
                    pod_gpu_timing_authorized=True,
                )

    def test_exact_owner_waiver_is_honest_and_validates(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            freeze, runtime, cfr, cfr_sha = self._inputs(root)
            authority = build_owner_waiver_authority(
                freeze=freeze,
                runtime_manifest=runtime,
                preexecution_cfr=cfr,
                expected_preexecution_cfr_sha256=cfr_sha,
                owner_explicit_external_review_waiver=True,
                owner_waiver_reason=OWNER_WAIVER_REASON,
                owner_execution_authorized=True,
                formal_worker_zero_authorized=True,
                pod_gpu_timing_authorized=True,
            )
            self.assertFalse(
                authority["external_preexecution_review_claimed"])
            self.assertFalse(authority["external_exact_byte_approval"])
            self.assertTrue(
                authority["owner_explicit_external_review_waiver"])
            validate_execution_authority(
                authority,
                freeze_sha256=hashlib.sha256(b"freeze\n").hexdigest(),
                runtime_manifest_sha256=hashlib.sha256(
                    b"runtime\n").hexdigest(),
            )
            _validate_execution_authority_bytes(
                authority,
                freeze_sha=hashlib.sha256(b"freeze\n").hexdigest(),
                runtime_sha=hashlib.sha256(b"runtime\n").hexdigest(),
            )

    def test_owner_waiver_cannot_be_missing_or_relabelled(self):
        for changes in (
                {"owner_explicit_external_review_waiver": False},
                {"owner_waiver_reason": "EXTERNAL_REVIEW_APPROVED"},
                {"owner_execution_authorized": False},
                {"formal_worker_zero_authorized": False},
                {"pod_gpu_timing_authorized": False}):
            with self.subTest(changes=changes), \
                    tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                freeze, runtime, cfr, cfr_sha = self._inputs(root)
                values = {
                    "freeze": freeze,
                    "runtime_manifest": runtime,
                    "preexecution_cfr": cfr,
                    "expected_preexecution_cfr_sha256": cfr_sha,
                    "owner_explicit_external_review_waiver": True,
                    "owner_waiver_reason": OWNER_WAIVER_REASON,
                    "owner_execution_authorized": True,
                    "formal_worker_zero_authorized": True,
                    "pod_gpu_timing_authorized": True,
                }
                values.update(changes)
                with self.assertRaises(RuntimeError):
                    build_owner_waiver_authority(**values)


if __name__ == "__main__":
    unittest.main()
