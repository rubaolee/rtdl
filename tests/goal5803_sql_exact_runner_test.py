from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import zipfile

from experiments.goal5803_sql_integer_bag_equijoin.build_successor_wheel import (
    EXPECTED_REPAIRED_CORE_SHA256,
    EXPECTED_RTDSL_INIT_SHA256,
    source_build_input_projection,
    verify_wheel_against_source,
)
from experiments.goal5803_sql_integer_bag_equijoin.freeze_execution import (
    PROJECT_FILE_PATHS,
)
from experiments.goal5803_sql_integer_bag_equijoin.run_untimed import (
    EXPECTED_CAPACITY,
    EXPECTED_EXECUTABLE_IDENTITY_SHA256,
    EXPECTED_WHEEL_DIST_INFO_MEMBERS,
    EXPECTED_WHEEL_REGULAR_MEMBER_COUNT,
    F32_NEXT_DOWN_FROM_ONE,
    F32_NEXT_DOWN_FROM_ONE_BITS,
    _complete_wheel_projection,
    _execute_public_capacity_overflow,
    _execute_public_exact,
    _execute_public_paired_exact,
    _installed_site_regular_projection,
    _verify_embedded_self_seal,
    _verify_independent_evidence_manifest,
    _verify_execution_freeze,
    build_public_capacity_kat_inputs,
    build_public_threshold_kat_inputs,
)


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "experiments/goal5803_sql_integer_bag_equijoin"
RUNNER = CASE / "run_untimed.py"
WHEEL_BUILDER = CASE / "build_successor_wheel.py"
FREEZER = CASE / "freeze_execution.py"
ARCHIVED_REPAIRED_CORE = (
    ROOT / "history/internal_docs/goal5803_bed_post_core_change_regression_20260827"
    / "v4_rtdlexe.py.post_core_change_v2")
LIVE_PUBLIC_INIT = ROOT / "src/rtdsl/__init__.py"
INDEPENDENT_WHEEL_ROOT = (
    ROOT / "history/internal_docs/goal5803_repaired_v14_exact_offline_wheel_20260827_v3")
INDEPENDENT_WHEEL = (
    INDEPENDENT_WHEEL_ROOT / "rtdl_source_tree-4.0.0rc1-py3-none-any.whl")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _preserved_v14_init_bytes() -> bytes:
    """Read the frozen initializer from the preserved exact v14 wheel."""

    with zipfile.ZipFile(INDEPENDENT_WHEEL, "r") as archive:
        payload = archive.read("rtdsl/__init__.py")
    observed = hashlib.sha256(payload).hexdigest()
    if observed != EXPECTED_RTDSL_INIT_SHA256:
        raise RuntimeError({
            "preserved_v14_init_sha256_mismatch": {
                "expected": EXPECTED_RTDSL_INIT_SHA256,
                "observed": observed,
            }
        })
    return payload


class Static:
    def __init__(self, *, indexed_boxes):
        self.indexed_boxes = tuple(indexed_boxes)


class Batch:
    def __init__(self, *, source_boxes, expected_rows):
        self.source_boxes = tuple(source_boxes)
        self.expected_rows = expected_rows


PUBLIC_MODULE = type("PublicModule", (), {
    "BoundedRelationStaticInput": Static,
    "BoundedRelationBatch": Batch,
})


class OrderedPublicResult:
    def __init__(self, output, *, diagnostic=True):
        self._output = output
        self.status_observed = False
        self.executable_identity_sha256 = EXPECTED_EXECUTABLE_IDENTITY_SHA256
        self.output_sha256 = "a" * 64 if diagnostic else None
        self.traversal_receipt = ({
            "physical_executor_classification": "optix_traversal_observed",
        } if diagnostic else None)
        self._diagnostic = diagnostic

    @property
    def device_status(self):
        self.status_observed = True
        status = {"ok": True, "schema": "public-status"}
        if not self._diagnostic:
            status["operation_receipt"] = {
                "schema": "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2",
                "status_before_output": True,
                "output_d2h_bytes": len(self._output) * 8,
                "output_d2h_after_status_failure": 0,
            }
        return status

    @property
    def output(self):
        if not self.status_observed:
            raise AssertionError("output accepted before public status")
        return self._output

class PublicPrepared:
    def __init__(self, result):
        self.result = result

    def execute(self, batch, *, include_diagnostics):
        if include_diagnostics is not True:
            raise AssertionError("exact helper did not request diagnostics")
        return self.result


class PairedPrepared:
    def __init__(self, output):
        self.results = [
            OrderedPublicResult(output, diagnostic=False),
            OrderedPublicResult(output, diagnostic=True),
        ]

    def execute(self, batch, *, include_diagnostics):
        expected = len(self.results) == 1
        if include_diagnostics is not expected:
            raise AssertionError("paired execution order changed")
        return self.results.pop(0)


class PublicOverflowError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


class OverflowPrepared:
    def __init__(self, code="RX041_OUTPUT_OVERFLOW"):
        self.code = code

    def execute(self, batch, *, include_diagnostics):
        if include_diagnostics is not False:
            raise AssertionError("capacity failure helper changed public mode")
        raise PublicOverflowError(self.code)


class Goal5803SqlExactRunnerTest(unittest.TestCase):
    def test_repaired_core_identity_is_exact_and_not_the_live_evolving_core(self):
        self.assertEqual(_sha(ARCHIVED_REPAIRED_CORE),
                         EXPECTED_REPAIRED_CORE_SHA256)
        self.assertEqual(
            hashlib.sha256(_preserved_v14_init_bytes()).hexdigest(),
            EXPECTED_RTDSL_INIT_SHA256)
        self.assertNotEqual(_sha(LIVE_PUBLIC_INIT), EXPECTED_RTDSL_INIT_SHA256)
        self.assertNotEqual(_sha(ROOT / "src/rtdsl/v4_rtdlexe.py"),
                            EXPECTED_REPAIRED_CORE_SHA256)

    def test_runner_uses_no_private_prepared_state_clock_or_network(self):
        source = RUNNER.read_text(encoding="utf-8")
        self.assertNotIn("._owner", source)
        self.assertNotIn("_last_fast_", source)
        self.assertNotIn("perf_counter", source)
        self.assertNotIn("monotonic", source)
        tree = ast.parse(source)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        for forbidden in ("time", "requests", "urllib", "socket"):
            self.assertFalse(any(name == forbidden or name.startswith(
                forbidden + ".") for name in imported), forbidden)
        lifecycle = ("install_rtdlexe_deployment", "load_rtdlexe",
                     "product_projection", ".prepare(", ".execute(", ".close(")
        for leaf in lifecycle:
            self.assertIn(leaf, source)

    def test_threshold_kat_brackets_exact_public_effective_boundary(self):
        self.assertEqual(F32_NEXT_DOWN_FROM_ONE_BITS, 0x3F7FFFFF)
        self.assertEqual(
            struct.unpack("<I", struct.pack("<f", F32_NEXT_DOWN_FROM_ONE))[0],
            0x3F7FFFFF,
        )
        self.assertLess(F32_NEXT_DOWN_FROM_ONE, 1.0)
        static, batch = build_public_threshold_kat_inputs(PUBLIC_MODULE)
        self.assertIsNone(batch.expected_rows)
        self.assertEqual(static.indexed_boxes,
                         ((0.0, 0.0, 1.0, 1.0, 900),))
        self.assertEqual(batch.source_boxes[0],
                         (0.0, 0.0, 1.0, 1.0, 800))
        self.assertEqual(batch.source_boxes[1][2], F32_NEXT_DOWN_FROM_ONE)
        accepted = []
        indexed = static.indexed_boxes[0]
        for source in batch.source_boxes:
            width = max(0.0, min(source[2], indexed[2])
                        - max(source[0], indexed[0]))
            height = max(0.0, min(source[3], indexed[3])
                         - max(source[1], indexed[1]))
            if width * height >= 1.0:
                accepted.append((source[4], indexed[4]))
        self.assertEqual(accepted, [(800, 900)])

    def test_capacity_kat_is_exact_K_and_K_plus_one_with_no_oracle_field(self):
        for count in (EXPECTED_CAPACITY, EXPECTED_CAPACITY + 1):
            static, batch, expected = build_public_capacity_kat_inputs(
                PUBLIC_MODULE, source_count=count)
            self.assertEqual(len(static.indexed_boxes), 1)
            self.assertEqual(len(batch.source_boxes), count)
            self.assertEqual(len(expected), count)
            self.assertIsNone(batch.expected_rows)
            self.assertEqual(len(set(expected)), count)
        with self.assertRaises(ValueError):
            build_public_capacity_kat_inputs(PUBLIC_MODULE, source_count=0)
        with self.assertRaises(ValueError):
            build_public_capacity_kat_inputs(PUBLIC_MODULE, source_count=True)

    def test_public_exact_helper_checks_status_before_output_acceptance(self):
        expected = ((10, 100),)
        result = OrderedPublicResult(expected)
        returned, payload = _execute_public_exact(
            prepared=PublicPrepared(result), batch=object(),
            expected=expected, label="unit")
        self.assertIs(returned, result)
        self.assertTrue(result.status_observed)
        self.assertTrue(payload["public_status_checked_before_output_acceptance"])
        self.assertFalse(payload["private_prepared_state_read"])

    def test_sql_pair_splits_fast_ordering_and_diagnostic_optix_evidence(self):
        expected = ((10, 100), (11, 101))
        fast, diagnostic, payload = _execute_public_paired_exact(
            prepared=PairedPrepared(expected), batch=object(),
            expected=expected, label="sql")
        self.assertIsNone(fast.output_sha256)
        self.assertIsNotNone(diagnostic.output_sha256)
        self.assertTrue(payload["paired_public_observation"])
        self.assertTrue(payload[
            "paired_outputs_and_executable_identity_equal"])
        self.assertTrue(payload["fast_status_before_output_observation"][
            "status_before_output"])
        self.assertIn("no single API result", payload[
            "evidence_split_disclosed"])

    def test_public_K_plus_one_helper_returns_no_result_and_exact_RX041(self):
        payload = _execute_public_capacity_overflow(
            prepared=OverflowPrepared(), batch=object(),
            executable_error_type=PublicOverflowError)
        self.assertEqual(payload["public_failure_code"],
                         "RX041_OUTPUT_OVERFLOW")
        self.assertFalse(payload["result_object_returned"])
        self.assertFalse(payload["partial_application_result_published"])
        self.assertFalse(payload["private_prepared_state_read"])
        with self.assertRaisesRegex(RuntimeError, "non-capacity"):
            _execute_public_capacity_overflow(
                prepared=OverflowPrepared("RX035_DEVICE_STATUS_INVALID"),
                batch=object(), executable_error_type=PublicOverflowError)

    def test_wheel_projection_requires_every_rtdsl_byte_to_match_source(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source"
            package = source / "src/rtdsl"
            package.mkdir(parents=True)
            shutil.copyfile(ARCHIVED_REPAIRED_CORE,
                            package / "v4_rtdlexe.py")
            (package / "__init__.py").write_bytes(
                _preserved_v14_init_bytes())
            (source / "pyproject.toml").write_text(
                "[build-system]\nrequires=['setuptools>=69']\n"
                "build-backend='setuptools.build_meta'\n",
                encoding="utf-8")
            (source / "README.md").write_text("test\n", encoding="utf-8")
            wheel = root / "test.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.write(package / "__init__.py", "rtdsl/__init__.py")
                archive.write(package / "v4_rtdlexe.py",
                              "rtdsl/v4_rtdlexe.py")
            receipt = verify_wheel_against_source(source, wheel)
            self.assertEqual(receipt["rtdsl_member_count"], 2)
            self.assertTrue(receipt[
                "source_and_wheel_member_bytes_identical"])
            projection = source_build_input_projection(source)
            self.assertEqual(len(projection), 4)
            mismatched = root / "mismatched.whl"
            with zipfile.ZipFile(mismatched, "w") as archive:
                archive.writestr("rtdsl/__init__.py", b"wrong")
                archive.write(package / "v4_rtdlexe.py",
                              "rtdsl/v4_rtdlexe.py")
            with self.assertRaisesRegex(RuntimeError,
                                        "wheel_source_projection_mismatch"):
                verify_wheel_against_source(source, mismatched)
            (package / "__init__.py").write_bytes(
                b"# unexpected bytes in a supplied frozen source root\n")
            with self.assertRaisesRegex(
                    RuntimeError, "unexpected public package initializer"):
                source_build_input_projection(source)

    def test_wheel_builder_never_uses_original_source_as_build_directory(self):
        source = WHEEL_BUILDER.read_text(encoding="utf-8")
        self.assertIn("_copy_build_inputs(source_root, staging, source_before)",
                      source)
        self.assertIn("str(staging)", source)
        self.assertIn("source_after = source_build_input_projection(source_root)",
                      source)
        self.assertIn("original_source_unchanged", source)
        self.assertIn('output_receipt.open("xb")', source)
        self.assertIn('output_wheel.open("xb")', source)

    def test_independent_wheel_manifest_self_seal_and_complete_member_set(self):
        evidence = INDEPENDENT_WHEEL_ROOT / "evidence_manifest.json"
        payload = json.loads(evidence.read_text(encoding="utf-8"))
        self.assertEqual(_verify_embedded_self_seal(
            payload, field="manifest_sha256",
            expected=payload["manifest_sha256"]), payload["manifest_sha256"])
        checked = _verify_independent_evidence_manifest(
            evidence, verify_payloads=False)
        self.assertEqual(checked["file_count"], 37)
        rows = _complete_wheel_projection(INDEPENDENT_WHEEL)
        self.assertEqual(len(rows), EXPECTED_WHEEL_REGULAR_MEMBER_COUNT)
        self.assertEqual(tuple(
            row["path"] for row in rows
            if not str(row["path"]).startswith("rtdsl/")),
            EXPECTED_WHEEL_DIST_INFO_MEMBERS)
        with tempfile.TemporaryDirectory() as raw:
            hostile = Path(raw) / "hostile.whl"
            with zipfile.ZipFile(INDEPENDENT_WHEEL, "r") as source, \
                    zipfile.ZipFile(hostile, "w") as target:
                for info in source.infolist():
                    target.writestr(info, source.read(info))
                target.writestr("sitecustomize.py", b"raise SystemExit(1)\n")
            with self.assertRaisesRegex(RuntimeError, "unowned top-level"):
                _complete_wheel_projection(hostile)

    def test_installed_site_projection_rejects_startup_hooks_and_rtdsl_pyc(self):
        with tempfile.TemporaryDirectory() as raw:
            site = Path(raw)
            (site / "safe.py").write_text("x=1\n", encoding="utf-8")
            self.assertEqual(len(_installed_site_regular_projection(site)), 1)
            (site / "sitecustomize.py").write_text(
                "raise SystemExit(1)\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "startup hook"):
                _installed_site_regular_projection(site)
        with tempfile.TemporaryDirectory() as raw:
            site = Path(raw)
            (site / "rtdsl").mkdir()
            (site / "rtdsl/x.pyc").write_bytes(b"hostile")
            with self.assertRaisesRegex(RuntimeError, "contains bytecode"):
                _installed_site_regular_projection(site)

    def test_execution_freeze_rejects_duplicate_missing_or_extra_project_rows(self):
        rows = [{
            "path": relative,
            "bytes": (ROOT / relative).stat().st_size,
            "sha256": _sha(ROOT / relative),
        } for relative in PROJECT_FILE_PATHS]
        base = {
            "schema": "rtdl.goal5803.sql_integer_bag_equijoin.execution_freeze.v1",
            "status": "FROZEN_BEFORE_FIRST_SQL_GPU_CALL__NO_SCIENTIFIC_RESULT_YET",
            "creation_rule": {
                "create_only": True, "existing_output_refused": True,
                "reseal_or_update_allowed": False,
            },
            "execution": {
                "wheel_execution_mode": True,
                "source_tree_import_allowed": False,
                "private_execution_api_allowed": False,
                "performance_timing_allowed": False,
            },
        }
        hostile_sets = (
            rows[:-1], rows + [rows[0]], rows + [{**rows[0], "path": "extra"}],
        )
        with tempfile.TemporaryDirectory() as raw:
            for index, hostile in enumerate(hostile_sets):
                path = Path(raw) / f"freeze_{index}.json"
                path.write_text(json.dumps({**base, "project_files": hostile}),
                                encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "set/order"):
                    _verify_execution_freeze(ROOT, path)

    def test_freezer_binds_all_required_classes_and_is_create_only(self):
        required_suffixes = (
            "success_gate_interpretation.json", "integer_bag_equijoin.py",
            "sqlite_oracle.py", "run_untimed.py",
            "build_successor_wheel.py", "freeze_execution.py",
            "goal5803_sql_integer_bag_equijoin_test.py",
            "goal5803_sql_exact_runner_test.py",
            "goal5803_runtime_overflow_hostile_test.py",
            "goal5803_runtime_overflow_hostile_v14_successor_test.py",
            "v4_rtdlexe.py.post_core_change_v2",
            "goal5803_post_core_change_regression_result.json",
        )
        for suffix in required_suffixes:
            self.assertTrue(any(path.endswith(suffix)
                                for path in PROJECT_FILE_PATHS), suffix)
        source = FREEZER.read_text(encoding="utf-8")
        self.assertIn('output.open("xb")', source)
        self.assertIn("first_sql_gpu_call_count_at_freeze", source)
        self.assertIn("wheel_execution_mode", source)
        self.assertIn("attempt_journal_path", source)
        self.assertIn("result_output_path", source)
        self.assertIn("-I -S -B", RUNNER.read_text(encoding="utf-8"))
        self.assertIn("whole_regular_file_projection_sha256", source)
        self.assertNotIn("import rtdsl", source)
        self.assertNotIn("perf_counter", source)

    def test_runner_persists_create_only_attempt_before_prepare(self):
        source = RUNNER.read_text(encoding="utf-8")
        start = source.index(
            '"ATTEMPT_STARTED_BEFORE_FIRST_PREPARE_OR_GPU_EXECUTE"')
        prepare = source.index("prepared = loaded.prepare(")
        self.assertLess(start, prepare)
        self.assertIn('mode = "xb" if create else "ab"', source)
        self.assertIn("os.fsync(stream.fileno())", source)
        self.assertIn('args.output.open("xb")', source)


if __name__ == "__main__":
    unittest.main()
