from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1669_python_partner_rtdl_partner_choice_architecture_2026-05-10.md"


class Goal1669PythonPartnerRtdlPartnerChoiceArchitectureTest(unittest.TestCase):
    def test_report_selects_protocol_first_cupy_first_architecture(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "protocol-first and partner-pluggable",
            "DLPack-compatible handoff as the contract",
            "CuPy as the first blessed partner",
            "PyTorch as the first follow-up partner",
            "RTDL engine internals must be app-agnostic",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_requires_switchable_partner_registry(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "PartnerAdapter",
            'partner="auto"',
            "object module/type ownership wins",
            "generic DLPack\n   adapter",
            'partner="cupy"',
            'partner="torch"',
            'partner="none"',
            "fallback policy",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_resolves_preimplementation_semantics(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "primary path: Python Array API `__dlpack__` plus `__dlpack_device__`",
            "stream_handle=0",
            "operation guard",
            "lifetime_token` must not enter the v1.7 native ABI",
            "RtdlOutputSpec",
            "required_alignment_bytes",
            "Geometry partner semantics",
            "must fail unless the user\n  requests a documented transfer fallback",
            "grad-enabled tensors must be rejected or explicitly detached",
            "Embree NumPy host descriptor acceptance",
            "NumPy contiguous host arrays",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_blocks_overclaims_and_native_backdoors(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "must not become a new app-specific native backdoor",
            "must not claim true zero-copy",
            "RTDL accelerates arbitrary PyTorch/CuPy programs",
            "Blocked wording until separately proven",
            "RTDL native internals are fully app-agnostic",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
