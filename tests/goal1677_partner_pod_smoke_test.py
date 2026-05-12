from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1677_partner_pod_smoke_2026-05-10.md"
PARTNER_REPORT = ROOT / "docs" / "reports" / "goal1675_partner_protocol_substrate_2026-05-10.md"
ROADMAP_GATE = ROOT / "docs" / "release_reports" / "v1_8_v2_0_python_partner_rtdl_gate.md"


class Goal1677PartnerPodSmokeTest(unittest.TestCase):
    def test_report_records_real_pytorch_and_cupy_cuda_partner_smokes(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "NVIDIA RTX A5000",
            "torch 2.4.1+cu124",
            "cuda_available True",
            "`rt.partner.auto()` selects `torch`",
            "grad-enabled tensors are rejected",
            "cupy 14.0.1",
            "`rt.partner.auto()` selects `cupy`",
            "`ctx.empty()` returns a CuPy-owned CUDA output array",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_keeps_native_runtime_and_zero_copy_claims_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "make build-optix` is blocked",
            "/opt/optix/include/optix.h",
            "Embree was then\nprovisioned and validated",
            "RTDL native internals are fully app-agnostic.",
            "RTDL has general true zero-copy support.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_partner_docs_link_the_pod_smoke(self) -> None:
        partner_text = PARTNER_REPORT.read_text(encoding="utf-8")
        gate_text = ROADMAP_GATE.read_text(encoding="utf-8")
        self.assertIn("goal1677_partner_pod_smoke_2026-05-10.md", partner_text)
        self.assertIn("goal1677_partner_pod_smoke_2026-05-10.md", gate_text)


if __name__ == "__main__":
    unittest.main()
