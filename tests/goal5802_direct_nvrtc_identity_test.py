from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from experiments.goal5802_premeasurement.direct_source_audit import (
    DirectSourceAuditError,
    audit_direct_source,
)
from experiments.goal5802_premeasurement.runtime_manifest import (
    direct_nvrtc_identity_stdout_bytes,
)
from scripts.goal5802_build_direct_worker_untimed import (
    _DIRECT_BUILD_RECEIPT_SCHEMA,
    _NVRTC_COMPILE_SOURCE,
    _parse_nvrtc_identity_stdout,
    _validate_direct_recipe_linkage,
    _validate_nvrtc_identity_document,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"


def _file_identity(path: Path) -> tuple[str, int, str]:
    canonical = path.resolve(strict=True)
    payload = canonical.read_bytes()
    return (
        str(canonical), len(payload), hashlib.sha256(payload).hexdigest())


def identity_document(
        library: Path, builtins: Path) -> dict[str, object]:
    library_path, library_bytes, library_sha256 = _file_identity(library)
    builtins_path, builtins_bytes, builtins_sha256 = _file_identity(builtins)
    product = b"synthetic-minimal-nvrtc-ptx\0"
    return {
        "schema": "rtdl.goal5802.direct_loaded_nvrtc_identity.v2",
        "status": "PASS__UNTIMED_NO_GPU",
        "discovery": (
            "MINIMAL_NVRTC_COMPILE_THEN_DLADDR_NVRTCVERSION_AND_"
            "PROC_SELF_MAPS_UNIQUE_BUILTINS_REALPATH_OPEN_NOFOLLOW_FSTAT"),
        "loaded_library_path": library_path,
        "loaded_library_bytes": library_bytes,
        "loaded_library_sha256": library_sha256,
        "loaded_builtins_path": builtins_path,
        "loaded_builtins_bytes": builtins_bytes,
        "loaded_builtins_sha256": builtins_sha256,
        "nvrtc_version": {"major": 12, "minor": 4},
        "nvrtc_compile_kat": {
            "source_utf8": _NVRTC_COMPILE_SOURCE,
            "source_sha256": hashlib.sha256(
                _NVRTC_COMPILE_SOURCE.encode("utf-8")).hexdigest(),
            "compile_options": ["--std=c++11"],
            "product_bytes": len(product),
            "product_sha256": hashlib.sha256(product).hexdigest(),
            "compile_success": True,
            "program_destroyed": True,
        },
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
    }


def make_identity_files(raw: str) -> tuple[Path, Path]:
    root = Path(raw)
    library = root / "libnvrtc.so.12"
    builtins = root / "libnvrtc-builtins.so.12.4"
    library.write_bytes(b"synthetic-nvrtc-exact-bytes")
    builtins.write_bytes(b"synthetic-nvrtc-builtins-exact-bytes")
    return library, builtins


class Goal5802DirectNvrtcIdentityTest(unittest.TestCase):
    def test_build_receipt_schema_is_v2_without_inert_v1_literal(self) -> None:
        self.assertEqual(
            _DIRECT_BUILD_RECEIPT_SCHEMA,
            "rtdl.goal5802.direct_worker_untimed_build_receipt.v2")
        builder = (
            ROOT / "scripts/goal5802_build_direct_worker_untimed.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn(
            "rtdl.goal5802.direct_worker_untimed_build_receipt.v1", builder)

    def test_exact_source_binds_compile_library_and_builtins(self) -> None:
        result = audit_direct_source(SOURCE)
        self.assertEqual(
            result["schema"],
            "rtdl.goal5802.direct_source_operation_audit.v2")
        guard = result["loaded_nvrtc_identity_guard"]
        self.assertFalse(guard["accepts_caller_reported_path"])
        self.assertTrue(guard["version_required"])
        self.assertTrue(
            guard["minimal_compile_before_builtins_discovery_required"])
        self.assertTrue(guard["builtins_current_process_maps_required"])
        self.assertTrue(guard["builtins_unique_canonical_identity_required"])
        self.assertTrue(guard["canonical_regular_file_required"])
        self.assertTrue(guard["symlink_ambiguity_rejected"])
        self.assertEqual(guard["clock_read_count"], 0)
        self.assertEqual(guard["gpu_kernel_launch_count"], 0)
        self.assertEqual(guard["formal_worker_count"], 0)

    def _hostile_source(
            self, old: str, new: str, *, expected_count: int = 1) -> Path:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(source.count(old), expected_count)
        root = Path(tempfile.mkdtemp(prefix="goal5802_nvrtc_source_"))
        target = root / "direct_scalar_worker.cpp"
        target.write_text(source.replace(old, new), encoding="utf-8")
        self.addCleanup(lambda: root.rmdir())
        self.addCleanup(lambda: target.unlink(missing_ok=True))
        return target

    def test_source_audit_rejects_self_reported_nvrtc_path(self) -> None:
        hostile = self._hostile_source(
            "::realpath(info.dli_fname, nullptr)",
            "::realpath(std::getenv(\"NVRTC_SELF_REPORTED_PATH\"), nullptr)")
        with self.assertRaises(DirectSourceAuditError):
            audit_direct_source(hostile)

    def test_source_audit_rejects_missing_nvrtc_version(self) -> None:
        hostile = self._hostile_source(
            "NVRTC_CHECK(nvrtcVersion(&result.version_major, &result.version_minor));",
            "result.version_major = 12; result.version_minor = 4;")
        with self.assertRaises(DirectSourceAuditError):
            audit_direct_source(hostile)

    def test_source_audit_rejects_weakened_library_regular_file_gate(self) -> None:
        hostile = self._hostile_source(
            "S_ISLNK(path_before.st_mode)", "false", expected_count=2)
        with self.assertRaises(DirectSourceAuditError):
            audit_direct_source(hostile)

    def test_source_audit_rejects_weakened_library_nofollow_gate(self) -> None:
        hostile = self._hostile_source(
            "result.resolved_path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW",
            "result.resolved_path.c_str(), O_RDONLY | O_CLOEXEC")
        with self.assertRaises(DirectSourceAuditError):
            audit_direct_source(hostile)

    def test_source_audit_rejects_compile_not_executed(self) -> None:
        hostile = self._hostile_source(
            "run_minimal_nvrtc_compile_kat();",
            "MinimalNvrtcCompileKat{};")
        with self.assertRaises(DirectSourceAuditError):
            audit_direct_source(hostile)

    def test_source_audit_rejects_ignored_compile_failure(self) -> None:
        hostile = self._hostile_source(
            "if (compile_result != NVRTC_SUCCESS)",
            "if (false && compile_result != NVRTC_SUCCESS)",
            expected_count=2)
        with self.assertRaises(DirectSourceAuditError):
            audit_direct_source(hostile)

    def test_source_audit_rejects_alternate_compile_source(self) -> None:
        hostile = self._hostile_source(
            "goal5802_nvrtc_identity_probe() {}\\n",
            "goal5802_nvrtc_identity_probe(int value) {}\\n")
        with self.assertRaises(DirectSourceAuditError):
            audit_direct_source(hostile)

    def test_source_audit_rejects_non_process_maps_discovery(self) -> None:
        hostile = self._hostile_source(
            'std::ifstream maps("/proc/self/maps", std::ios::binary);',
            'std::ifstream maps("/tmp/reported-maps", std::ios::binary);')
        with self.assertRaises(DirectSourceAuditError):
            audit_direct_source(hostile)

    def test_source_audit_rejects_ambiguous_builtins_acceptance(self) -> None:
        hostile = self._hostile_source(
            "if (candidates.size() != 1)", "if (candidates.empty())")
        with self.assertRaises(DirectSourceAuditError):
            audit_direct_source(hostile)

    def test_source_audit_rejects_weakened_builtins_nofollow_gate(self) -> None:
        hostile = self._hostile_source(
            "canonical_path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW",
            "canonical_path.c_str(), O_RDONLY | O_CLOEXEC")
        with self.assertRaises(DirectSourceAuditError):
            audit_direct_source(hostile)

    def test_document_validator_independently_rehashes_both_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            value = identity_document(library, builtins)
            self.assertEqual(_validate_nvrtc_identity_document(value), value)

    def test_document_validator_rejects_missing_builtins_fields(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            value = identity_document(library, builtins)
            del value["loaded_builtins_sha256"]
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)

    def test_document_validator_rejects_missing_builtins_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            value = identity_document(library, builtins)
            builtins.unlink()
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)

    def test_document_validator_rejects_builtins_byte_tamper(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            value = identity_document(library, builtins)
            builtins.write_bytes(b"post-report-tamper")
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)

    def test_document_validator_rejects_self_reported_library_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            reported = Path(raw) / "libnvrtc.so.99"
            reported.write_bytes(b"self-reported")
            value = identity_document(library, builtins)
            value["loaded_library_path"] = str(reported.resolve(strict=True))
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)

    def test_document_validator_rejects_nonregular_builtins_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            builtins.unlink()
            builtins.mkdir()
            value = identity_document(library, Path(__file__))
            value["loaded_builtins_path"] = str(builtins.resolve(strict=True))
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)

    def test_document_validator_rejects_builtins_symlink(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            target = Path(raw) / "libnvrtc-builtins.so.12.4.1"
            link = Path(raw) / "libnvrtc-builtins.so.12.4-link"
            target.write_bytes(b"loaded-builtins")
            try:
                os.symlink(target.name, link)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"file symlinks unavailable: {error}")
            value = identity_document(library, target)
            value["loaded_builtins_path"] = str(link.absolute())
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)

    def test_document_validator_rejects_wrong_builtins_basename(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            reported = Path(raw) / "not-builtins.so"
            reported.write_bytes(builtins.read_bytes())
            value = identity_document(library, reported)
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)

    def test_document_validator_rejects_hardlink_alias(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library = Path(raw) / "libnvrtc.so.12"
            builtins = Path(raw) / "libnvrtc-builtins.so.12.4"
            library.write_bytes(b"same-inode")
            try:
                os.link(library, builtins)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"hard links unavailable: {error}")
            value = identity_document(library, builtins)
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)

    def test_document_validator_rejects_compile_not_executed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            value = identity_document(library, builtins)
            value["nvrtc_compile_kat"]["compile_success"] = False
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)

    def test_document_validator_rejects_jointly_resealed_compile_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            value = identity_document(library, builtins)
            alternate = 'extern "C" __global__ void alternate() {}\n'
            value["nvrtc_compile_kat"]["source_utf8"] = alternate
            value["nvrtc_compile_kat"]["source_sha256"] = hashlib.sha256(
                alternate.encode("utf-8")).hexdigest()
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)

    def test_document_validator_rejects_compile_options_or_product_tamper(
            self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            value = identity_document(library, builtins)
            value["nvrtc_compile_kat"]["compile_options"] = ["--std=c++17"]
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)
            value = identity_document(library, builtins)
            value["nvrtc_compile_kat"]["product_sha256"] = "A" * 64
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)

    def test_document_validator_rejects_bool_as_zero_counter(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            value = identity_document(library, builtins)
            value["gpu_kernel_launch_count"] = False
            with self.assertRaises(RuntimeError):
                _validate_nvrtc_identity_document(value)

    def test_stdout_parser_binds_exact_single_json_line(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            value = identity_document(library, builtins)
            exact = json.dumps(
                value, ensure_ascii=False,
                separators=(",", ":")).encode("utf-8") + b"\n"
            self.assertEqual(_parse_nvrtc_identity_stdout(exact), value)
            with self.assertRaises(RuntimeError):
                _parse_nvrtc_identity_stdout(b" " + exact)
            with self.assertRaises(RuntimeError):
                _parse_nvrtc_identity_stdout(exact + b"\n")

    def test_target_projection_detects_forged_document_stdout_mismatch(
            self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5802_nvrtc_doc_") as raw:
            library, builtins = make_identity_files(raw)
            value = identity_document(library, builtins)
            original_stdout = direct_nvrtc_identity_stdout_bytes(value)
            self.assertEqual(
                _parse_nvrtc_identity_stdout(original_stdout), value)
            forged = copy.deepcopy(value)
            forged["nvrtc_compile_kat"]["product_sha256"] = "0" * 64
            self.assertNotEqual(
                direct_nvrtc_identity_stdout_bytes(forged), original_stdout)

    def test_formal_controller_preflight_precedes_every_worker_start(
            self) -> None:
        controller = (
            ROOT / "experiments/goal5802_premeasurement/controller.py"
        ).read_text(encoding="utf-8")
        start = controller.index("def execute_formal(")
        end = controller.index("\ndef main(", start)
        body = controller[start:end]
        preflight = body.index(
            "runtime_preflight = _formal_runtime_preflight(")
        first_worker = body.index("_execute_one(")
        self.assertLess(preflight, first_worker)
        self.assertNotIn("_execute_one(", body[:preflight])

    def test_recipe_requires_and_records_one_nvrtc_and_dl_link(self) -> None:
        recipe = {
            "argv_template": [
                "{CXX}", "{DIRECT_SOURCE}", "-lnvrtc", "-ldl", "-o",
                "{OUTPUT}",
            ],
        }
        result = _validate_direct_recipe_linkage(recipe)
        self.assertEqual(result["nvrtc_link_flag_count"], 1)
        self.assertEqual(result["dl_link_flag_count"], 1)
        hostile = copy.deepcopy(recipe)
        hostile["argv_template"].remove("-ldl")
        with self.assertRaises(RuntimeError):
            _validate_direct_recipe_linkage(hostile)


if __name__ == "__main__":
    unittest.main()
