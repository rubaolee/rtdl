from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PY_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2229_ray_segment_group_count_primitive_2026-05-17.md"


def _function_body(text: str, name: str) -> str:
    start = text.index(name)
    brace = text.index("{", start)
    depth = 0
    for index in range(brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise AssertionError(f"could not parse function body for {name}")


class Goal2229RaySegmentGroupCountPrimitiveTest(unittest.TestCase):
    def test_native_abi_is_generic_and_exposes_count_parity_rows(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        self.assertIn("struct RtdlRaySegmentGroupCountRow", prelude)
        self.assertIn("uint32_t ray_id, group_id, hit_count, parity", prelude)
        self.assertIn("rtdl_optix_run_ray_segment_group_count_2d", prelude)
        self.assertIn("rtdl_optix_run_ray_segment_group_count_2d", api)
        self.assertIn("run_ray_segment_group_count_2d_optix", api)

    def test_workload_uses_existing_segment_traversal_and_host_group_aggregation(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        body = _function_body(workloads, "run_ray_segment_group_count_2d_optix")
        self.assertIn("run_segment_pair_intersection_optix", body)
        self.assertIn("group_by_segment_id", body)
        self.assertIn("hit_count & 1u", body)
        self.assertIn("requires unique segment ids", body)
        self.assertIn("std::sort(rows.begin(), rows.end()", body)
        forbidden = re.compile(r"\b(pip|polygon|rayjoin|spatial_join)\b", re.IGNORECASE)
        self.assertIsNone(forbidden.search(body))

    def test_python_wrapper_preserves_generic_contract(self) -> None:
        text = PY_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("class _RtdlRaySegmentGroupCountRow", text)
        self.assertIn("def ray_segment_group_count_2d_optix", text)
        self.assertIn("segment_group_ids length must match segment count", text)
        self.assertIn('"rtdl_optix_run_ray_segment_group_count_2d"', text)
        self.assertIn('field_names=("ray_id", "group_id", "hit_count", "parity")', text)

    def test_report_locks_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2229", text)
        self.assertIn("app-agnostic", text)
        self.assertIn("does not authorize", text)
        self.assertIn("host aggregation", text)
        self.assertIn("device-resident grouped reduction", text)
        self.assertIn("Pod:", text)


if __name__ == "__main__":
    unittest.main()
