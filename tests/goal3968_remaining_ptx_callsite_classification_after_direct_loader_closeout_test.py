import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NATIVE_ROOT = ROOT / "src" / "native"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OPTIX_CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3968_remaining_ptx_callsite_classification_after_direct_loader_closeout_2026-06-08.md"
)


class Goal3968RemainingPtxCallsiteClassificationAfterDirectLoaderCloseoutTest(unittest.TestCase):
    def test_remaining_workload_ptx_call_sites_feed_optix_pipeline_builds(self) -> None:
        lines = OPTIX_WORKLOADS.read_text(encoding="utf-8", errors="ignore").splitlines()
        ptx_lines: list[tuple[int, str]] = []
        non_pipeline: list[tuple[int, str]] = []
        for index, line in enumerate(lines):
            if "compile_to_ptx(" not in line:
                continue
            ptx_lines.append((index + 1, line.strip()))
            window = "\n".join(lines[index : index + 8])
            if "build_pipeline(" not in window:
                non_pipeline.append((index + 1, line.strip()))

        self.assertEqual(57, len(ptx_lines))
        self.assertEqual([], non_pipeline)

    def test_compile_to_ptx_helper_definition_count_is_stable(self) -> None:
        text = OPTIX_CORE.read_text(encoding="utf-8", errors="ignore")
        self.assertEqual(1, text.count("std::string compile_to_ptx(const char* cuda_src,"))

    def test_no_cuda_driver_module_load_uses_ptx_payload_anywhere_in_native_tree(self) -> None:
        offenders: list[tuple[Path, int, str]] = []
        for path in sorted(NATIVE_ROOT.rglob("*")):
            if path.suffix not in {".cpp", ".cu", ".h", ".hpp"}:
                continue
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for index, line in enumerate(lines):
                if "cuModuleLoadData" not in line:
                    continue
                window = "\n".join(lines[max(0, index - 8) : index + 2])
                if "ptx.c_str()" in window or "ptx.data()" in window:
                    offenders.append((path, index + 1, line.strip()))

        self.assertEqual([], offenders)

    def test_report_records_classification_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "workload PTX call followed by `build_pipeline(...)` | 57",
            "direct CUDA driver load using PTX payload | 0",
            "does not recommend converting OptiX pipeline PTX to CUBIN",
            "does not authorize release",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
