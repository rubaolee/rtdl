from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest

from scripts import run_test_matrix


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "src" / "v4" / "include" / "rtdl" / "rtdl.h"
SOURCE = ROOT / "src" / "v4" / "rtdl_v4_c_api.cpp"
README = ROOT / "src" / "v4" / "README.md"
NOTE = ROOT / "docs" / "engineering" / "rtdl_v4_0_active_abi_slice_2026-06-19.md"
SYMBOL_MANIFEST = ROOT / "docs" / "engineering" / "rtdl_v4_0_active_abi_symbol_manifest_2026-06-19.json"
DESIGN = ROOT / "docs" / "engineering" / "rtdl_v4_0_design_review_packet_2026-06-19.md"
MAKEFILE = ROOT / "Makefile"
CTYPES_SMOKE = ROOT / "src" / "v4" / "examples" / "python_ctypes_aabb2_smoke.py"
LAYOUT_AUDIT = ROOT / "scripts" / "v4_0_active_abi_layout_audit.py"
LAYOUT_AUDIT_REPORT = ROOT / "docs" / "reports" / "v4_0_active_abi_layout_audit_2026-06-19.json"


def _load_ctypes_smoke():
    spec = importlib.util.spec_from_file_location("rtdl_v4_ctypes_smoke_test", CTYPES_SMOKE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {CTYPES_SMOKE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _header_struct_fields(header: str, struct_name: str) -> list[str]:
    match = re.search(rf"typedef struct {struct_name} \{{(?P<body>.*?)\}} {struct_name};", header, re.DOTALL)
    if match is None:
        raise AssertionError(f"missing struct {struct_name}")
    fields: list[str] = []
    for raw_line in match.group("body").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("/*") or line.startswith("*"):
            continue
        field = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[[^\]]+\])?;$", line)
        if field is not None:
            fields.append(field.group(1))
    return fields


class V40ActiveAbiControlPlaneTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.header = HEADER.read_text(encoding="utf-8")
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.makefile = MAKEFILE.read_text(encoding="utf-8")

    def test_active_v4_surface_exists_outside_user_front_door(self) -> None:
        self.assertTrue(HEADER.exists())
        self.assertTrue(SOURCE.exists())
        self.assertTrue(README.exists())
        self.assertTrue(NOTE.exists())
        self.assertTrue(SYMBOL_MANIFEST.exists())
        self.assertTrue(CTYPES_SMOKE.exists())
        self.assertTrue(LAYOUT_AUDIT.exists())
        self.assertTrue(LAYOUT_AUDIT_REPORT.exists())
        self.assertFalse((ROOT / "include" / "rtdl" / "rtdl.h").exists())
        self.assertFalse((ROOT / "packaging" / "rtdl-c-api.pc").exists())
        self.assertIn("Active ABI Slice", NOTE.read_text(encoding="utf-8"))

    def test_header_uses_v4_review_decision_shape(self) -> None:
        header = self.header
        self.assertIn("#define RTDL_ABI_VERSION_MAJOR 0", header)
        self.assertIn("#define RTDL_ABI_VERSION_MINOR 2", header)
        self.assertIn("typedef struct rtdl_query_plan rtdl_query_plan;", header)
        self.assertIn("typedef struct rtdl_result rtdl_result;", header)
        self.assertIn("typedef struct rtdl_event rtdl_event;", header)
        self.assertNotIn("typedef struct rtdl_query rtdl_query;", header)
        self.assertNotIn("rtdl_query_destroy", header)
        self.assertIn("RTDL_STATUS_RESULT_TRUNCATED", header)
        self.assertIn("rtdl_query_capability", header)
        self.assertIn("RTDL_OUTPUT_RTDL_OWNED_RESULT", header)
        self.assertIn("RTDL_OUTPUT_CALLER_PROVIDED_BUFFER", header)
        self.assertIn("RTDL_OWNERSHIP_EXPORTED_RTDL_VIEW", header)
        self.assertIn("Borrowed device pointers are caller-asserted", header)
        self.assertNotIn("rtdl_backend_is_supported", header)
        self.assertNotIn("rtdl_route_is_supported", header)

    def test_active_symbol_manifest_matches_header_and_source(self) -> None:
        manifest = json.loads(SYMBOL_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual("rtdl_v4_active_c_abi_symbol_manifest_v1", manifest["manifest_kind"])
        self.assertEqual("active_experimental_substrate_manifest", manifest["status"])
        self.assertEqual("0.2.0", manifest["abi_version"])
        self.assertFalse(manifest["stable"])
        self.assertEqual("src/v4/include/rtdl/rtdl.h", manifest["header"])
        self.assertEqual("src/v4/rtdl_v4_c_api.cpp", manifest["source"])
        self.assertEqual("make build-v4-c-api", manifest["build_target"])

        header_symbols = re.findall(
            r"^RTDL_API\s+[\w\s\*]+?\s+(rtdl_[A-Za-z0-9_]+)\s*\(",
            self.header,
            flags=re.MULTILINE,
        )
        source_symbols = re.findall(
            r"^RTDL_API\s+[\w\s\*]+?\s+(rtdl_[A-Za-z0-9_]+)\s*\(",
            self.source,
            flags=re.MULTILINE,
        )
        self.assertEqual(manifest["symbols"], header_symbols)
        self.assertEqual(manifest["symbols"], source_symbols)

        for removed_symbol in manifest["removed_archived_symbols"]:
            self.assertNotIn(removed_symbol, self.header)
            self.assertNotIn(removed_symbol, self.source)

        for claim_name, authorized in manifest["claim_boundaries"].items():
            self.assertFalse(authorized, claim_name)

    def test_ctypes_descriptor_layout_mirror_matches_header_fields(self) -> None:
        smoke = _load_ctypes_smoke()
        snapshot = smoke.layout_snapshot()
        self.assertEqual(8, snapshot["max_rank"])
        self.assertEqual(8, snapshot["pointer_size"])
        for struct_name, layout in snapshot["descriptors"].items():
            header_fields = _header_struct_fields(self.header, struct_name)
            self.assertEqual(header_fields, list(layout["fields"].keys()), struct_name)
            self.assertEqual("struct_size", header_fields[0], struct_name)
            self.assertEqual(0, layout["fields"]["struct_size"]["offset"], struct_name)
            self.assertGreater(layout["sizeof"], 0, struct_name)

    def test_layout_audit_compares_ctypes_mirror_with_c_header_when_cxx_is_available(self) -> None:
        if shutil.which("c++") is None:
            self.skipTest("no c++ compiler on this host")
        completed = subprocess.run(
            [sys.executable, str(LAYOUT_AUDIT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        if completed.returncode != 0:
            sys.stderr.write(completed.stdout)
            sys.stderr.write(completed.stderr)
        self.assertEqual(0, completed.returncode)
        payload = json.loads(completed.stdout)
        self.assertEqual("rtdl_v4_active_abi_layout_audit_v1", payload["manifest_kind"])
        self.assertEqual("0.2.0", payload["abi_version"])
        self.assertFalse(payload["stable"])
        self.assertTrue(payload["matches"])
        self.assertEqual(payload["c_header_layout"], payload["ctypes_layout"])
        for authorized in payload["claim_boundaries"].values():
            self.assertFalse(authorized)

    def test_layout_audit_report_records_matching_experimental_layout(self) -> None:
        report = json.loads(LAYOUT_AUDIT_REPORT.read_text(encoding="utf-8"))
        self.assertEqual("rtdl_v4_active_abi_layout_audit_v1", report["manifest_kind"])
        self.assertEqual("active_experimental_substrate_layout_audit", report["status"])
        self.assertEqual("0.2.0", report["abi_version"])
        self.assertFalse(report["stable"])
        self.assertTrue(report["matches"])
        self.assertEqual(report["c_header_layout"], report["ctypes_layout"])
        self.assertEqual(8, report["c_header_layout"]["pointer_size"])
        self.assertEqual(8, report["c_header_layout"]["max_rank"])
        for struct_name, layout in report["c_header_layout"]["descriptors"].items():
            self.assertEqual(set(_header_struct_fields(self.header, struct_name)), set(layout["fields"].keys()))
            self.assertEqual(0, layout["fields"]["struct_size"]["offset"], struct_name)
        for claim_name, authorized in report["claim_boundaries"].items():
            self.assertFalse(authorized, claim_name)

    def test_public_descriptors_start_with_struct_size(self) -> None:
        for name in (
            "rtdl_external_runtime_desc",
            "rtdl_context_desc",
            "rtdl_route_desc",
            "rtdl_buffer_desc",
            "rtdl_index_desc",
            "rtdl_output_desc",
            "rtdl_query_desc",
        ):
            needle = f"typedef struct {name} {{\n  size_t struct_size;"
            self.assertIn(needle, self.header, name)

    def test_result_output_contract_is_enforced_in_source(self) -> None:
        source = self.source
        for token in (
            "required_count_out",
            "written_count_out",
            "RTDL_STATUS_RESULT_TRUNCATED",
            "RTDL_OUTPUT_CALLER_PROVIDED_BUFFER",
            "RTDL_OUTPUT_RTDL_OWNED_RESULT",
            "rtdl_result_row_count",
            "rtdl_result_get_buffer",
        ):
            self.assertIn(token, source)
        self.assertIn("written_count < required_count", source)
        self.assertIn("std::memcpy(desc->output.caller_buffer.data", source)

    def test_ctypes_smoke_covers_owned_truncated_and_exact_outputs(self) -> None:
        smoke = CTYPES_SMOKE.read_text(encoding="utf-8")
        self.assertIn("RTDL_OUTPUT_RTDL_OWNED_RESULT", smoke)
        self.assertIn("RTDL_OUTPUT_CALLER_PROVIDED_BUFFER", smoke)
        self.assertIn("RTDL_STATUS_RESULT_TRUNCATED", smoke)
        self.assertIn("owned_result", smoke)
        self.assertIn("caller_output_truncated", smoke)
        self.assertIn("caller_output_exact", smoke)
        self.assertIn("old_size_compatibility", smoke)
        self.assertIn("context_desc_through_backend", smoke)
        self.assertIn("buffer_desc_through_strides", smoke)
        self.assertIn("query_desc_without_output_defaults_to_owned_result", smoke)

    def test_fail_closed_validation_tokens_are_present(self) -> None:
        source = self.source
        for token in (
            "validate_buffer_desc",
            "ndim exceeds RTDL_MAX_RANK",
            "null data with nonzero byte_count",
            "shape product overflows",
            "byte_count is smaller than dense shape extent",
            "release-callback ownership requires a release callback",
            "RTDL_STATUS_INVALID_ARGUMENT",
            "RTDL_STATUS_SHAPE_LAYOUT_MISMATCH",
        ):
            self.assertIn(token, source)

    def test_makefile_hides_v4_active_from_default_help_but_exposes_dev_help(self) -> None:
        default_help = self.makefile.split("help:", 1)[1].split("help-v4-prep:", 1)[0]
        self.assertNotIn("build-v4-c-api", default_help)
        self.assertNotIn("test-v4-active", default_help)
        self.assertIn("help-v4-dev:", self.makefile)
        self.assertIn("build-v4-c-api:", self.makefile)
        self.assertIn("test-v4-active:", self.makefile)

    def test_matrix_and_doctor_expose_v4_active_only_on_request(self) -> None:
        self.assertEqual(
            (
                "tests.v4_0_active_abi_control_plane_test",
                "tests.v4_0_reframed_product_design_test",
                "tests.v4_0_m1_fixed_radius_route_test",
                "tests.v4_0_m1_linux_gpu_release_gate_test",
                "tests.v4_0_user_tutorials_test",
            ),
            run_test_matrix.group_modules("v4_active"),
        )
        self.assertNotIn("tests.v4_0_active_abi_control_plane_test", run_test_matrix.group_modules("v3_current"))
        self.assertNotIn("tests.v4_0_reframed_product_design_test", run_test_matrix.group_modules("v3_current"))
        self.assertNotIn("tests.v4_0_m1_fixed_radius_route_test", run_test_matrix.group_modules("v3_current"))
        self.assertNotIn("tests.v4_0_m1_linux_gpu_release_gate_test", run_test_matrix.group_modules("v3_current"))
        self.assertNotIn("tests.v4_0_user_tutorials_test", run_test_matrix.group_modules("v3_current"))

        import scripts.rtdl_source_tree_doctor as doctor

        default_checks = {row["name"]: row for row in doctor.gather_checks()["checks"]}
        self.assertNotIn("V4 active experimental ABI surface", default_checks)

        active_checks = {
            row["name"]: row
            for row in doctor.gather_checks(include_v4_active=True)["checks"]
        }
        self.assertEqual("pass", active_checks["V4 active experimental ABI surface"]["status"])
        self.assertFalse(active_checks["V4 active experimental ABI surface"]["required"])

    def test_design_note_and_packet_agree_on_pre_1_0_boundary(self) -> None:
        combined = NOTE.read_text(encoding="utf-8") + "\n" + DESIGN.read_text(encoding="utf-8")
        design = DESIGN.read_text(encoding="utf-8")
        self.assertIn("pre-1.0", combined)
        self.assertIn("experimental SDK", combined)
        self.assertIn("D1: every query route supports RTDL-owned result handles", design)
        self.assertIn("caller-provided\n  output buffers", design)
        self.assertIn("D2: every public descriptor begins with `struct_size`", design)
        self.assertIn("D3: capability discovery uses one enum-keyed query function", design)

    def test_active_v4_library_builds_when_cxx_is_available(self) -> None:
        if shutil.which("c++") is None:
            self.skipTest("no c++ compiler on this host")
        completed = subprocess.run(
            ["make", "build-v4-c-api"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        if completed.returncode != 0:
            sys.stderr.write(completed.stdout)
            sys.stderr.write(completed.stderr)
        self.assertEqual(0, completed.returncode)
        smoke = subprocess.run(
            [sys.executable, str(CTYPES_SMOKE)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        if smoke.returncode != 0:
            sys.stderr.write(smoke.stdout)
            sys.stderr.write(smoke.stderr)
        self.assertEqual(0, smoke.returncode)
        payload = json.loads(smoke.stdout)
        self.assertTrue(payload["old_size_compatibility"]["context_desc_through_backend"])
        self.assertTrue(payload["old_size_compatibility"]["buffer_desc_through_strides"])
        self.assertEqual("borrowed", payload["old_size_compatibility"]["buffer_defaulted_ownership"])
        self.assertEqual(
            payload["owned_result"]["pairs"],
            payload["old_size_compatibility"]["query_desc_without_output_defaults_to_owned_result"]["pairs"],
        )


if __name__ == "__main__":
    unittest.main()
