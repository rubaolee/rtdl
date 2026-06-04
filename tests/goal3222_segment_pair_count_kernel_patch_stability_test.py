from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3222_segment_pair_count_kernel_patch_stability_guard_2026-06-03.md"


OLD_RECORD_STRUCT = """struct SegmentPairIntersectionRecord {
    unsigned int left_id, right_id;
    unsigned int left_index, right_index;
};

"""

OLD_PARAMS = """struct SegmentPairIntersectionParams {
    OptixTraversableHandle traversable;
    const GpuSegment* left_segs;
    const GpuSegment* right_segs;
    SegmentPairIntersectionRecord* output;
    unsigned int* output_count;
    unsigned int  output_capacity;
    unsigned int  probe_count;
    unsigned int  left_offset;
};
"""

OLD_WRITE = """    const unsigned int slot = atomicAdd(params.output_count, 1u);
    if (slot < params.output_capacity) {
        SegmentPairIntersectionRecord r;
        r.left_id  = left.id;
        r.right_id = right.id;
        r.left_index = params.left_offset + pidx;
        r.right_index = bidx;
        params.output[slot] = r;
    }
    optixIgnoreIntersection();
"""

LEFT_ID_COUNT_PARAMS = """struct SegmentPairIntersectionParams {
    OptixTraversableHandle traversable;
    const GpuSegment* left_segs;
    const GpuSegment* right_segs;
    unsigned long long* counts;
    unsigned long long* candidate_event_count;
    unsigned int* overflow;
    unsigned int group_capacity;
    unsigned int probe_count;
};
"""

LEFT_ID_COUNT_WRITE = """    atomicAdd(params.candidate_event_count, 1ull);
    if (left.id < params.group_capacity) {
        atomicAdd(&params.counts[left.id], 1ull);
    } else {
        atomicOr(params.overflow, 1u);
    }
    optixIgnoreIntersection();
"""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def _between(text: str, start_marker: str, end_marker: str) -> str:
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[start:end]


def _patched_left_id_count_kernel() -> str:
    core = _read(CORE)
    kernel = _between(
        core,
        'static const char* kSegmentPairIntersectionKernelSrc = R"CUDA(',
        ")CUDA\";\n\n// ---------- segment first-hit kernel",
    )
    kernel = kernel.replace(OLD_RECORD_STRUCT, "")
    kernel = kernel.replace(OLD_PARAMS, LEFT_ID_COUNT_PARAMS)
    kernel = kernel.replace(OLD_WRITE, LEFT_ID_COUNT_WRITE)
    return kernel


class Goal3222SegmentPairCountKernelPatchStabilityTest(unittest.TestCase):
    def test_canonical_segment_pair_kernel_still_contains_expected_patch_anchors(self) -> None:
        core = _read(CORE)

        self.assertEqual(core.count(OLD_RECORD_STRUCT), 1)
        self.assertEqual(core.count(OLD_PARAMS), 1)
        self.assertEqual(core.count(OLD_WRITE), 1)
        self.assertIn("kSegmentPairIntersectionKernelSrc", core)
        self.assertIn("__anyhit__segment_pair_intersection_anyhit", core)

    def test_candidate_and_count_pipelines_patch_the_same_canonical_anchors(self) -> None:
        workloads = _read(WORKLOADS)

        self.assertEqual(workloads.count(OLD_RECORD_STRUCT), 2)
        self.assertEqual(workloads.count(OLD_PARAMS), 2)
        self.assertEqual(workloads.count(OLD_WRITE), 2)

        for phrase in (
            "segment-pair candidate device-column kernel record snippet not found",
            "segment-pair candidate device-column kernel params snippet not found",
            "segment-pair candidate device-column kernel write snippet not found",
            "segment-pair left-id count kernel record snippet not found",
            "segment-pair left-id count kernel params snippet not found",
            "segment-pair left-id count kernel write snippet not found",
        ):
            self.assertIn(phrase, workloads)

    def test_left_id_count_replacement_is_atomic_and_not_row_streaming(self) -> None:
        workloads = _read(WORKLOADS)
        block = _between(
            workloads,
            "static void ensure_segment_pair_left_id_count_device_columns_pipeline()",
            "static void ensure_segment_first_hit_pipeline()",
        )

        self.assertIn(LEFT_ID_COUNT_PARAMS, block)
        self.assertIn(LEFT_ID_COUNT_WRITE, block)
        self.assertIn("segment_pair_left_id_count_device_columns_kernel.cu", block)

        patched_kernel = _patched_left_id_count_kernel()
        self.assertIn(LEFT_ID_COUNT_PARAMS, patched_kernel)
        self.assertIn(LEFT_ID_COUNT_WRITE, patched_kernel)
        self.assertNotIn("SegmentPairIntersectionRecord* output;", patched_kernel)
        self.assertNotIn("params.output[slot] = r;", patched_kernel)
        self.assertNotIn("*params.overflow = 1u;", patched_kernel)

    def test_report_records_scope_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        single_line_report = " ".join(report.split())

        for phrase in (
            "static kernel-patch stability guard",
            "does not change the native ABI",
            "ordinary unit tests",
        ):
            self.assertIn(phrase, report)
        for phrase in (
            "does not authorize release",
            "does not authorize public speedup claims",
        ):
            self.assertIn(phrase, single_line_report)


if __name__ == "__main__":
    unittest.main()
