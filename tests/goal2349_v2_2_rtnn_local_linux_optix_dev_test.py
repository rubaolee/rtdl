from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2349_v2_2_rtnn_local_linux_optix_dev_2026-05-18.md"


class Goal2349RtnnLocalLinuxOptixDevTest(unittest.TestCase):
    def test_report_records_local_linux_as_smoke_only(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("NVIDIA GeForce GTX 1070", text)
        self.assertIn("not accepted RT-core hardware", text)
        self.assertIn("not accepted RT-core performance evidence", text)

    def test_report_records_rtdl_optix_smoke(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("e733685a", text)
        self.assertIn("build/librtdl_optix.so", text)
        self.assertIn("optix_version() == (9, 0, 0)", text)
        self.assertIn("run-rtdl-current-2d-smoke", text)
        self.assertIn("local_linux_gtx1070_2d_smoke", text)

    def test_report_records_rtnn_cuda12_compatibility_patches(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("GCC 12", text)
        self.assertIn("thrust/count.h", text)
        self.assertIn("thrust/unique.h", text)
        self.assertIn("thrust/tuple.h", text)
        self.assertIn("thrust/host_vector.h", text)
        self.assertIn("__uint_as_float", text)
        self.assertIn("__float_as_uint", text)

    def test_report_records_external_rtnn_smoke_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("local_linux_gtx1070_rtnn_radius_smoke_after_intrinsic_patch", text)
        self.assertIn("RTNN return code | `0`", text)
        self.assertIn("time search compute", text)
        self.assertIn("does not authorize RTDL speedup claims", text)
        self.assertIn("performance comparison and primitive-design validation still pending", text)


if __name__ == "__main__":
    unittest.main()
