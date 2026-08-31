from __future__ import annotations

import base64
import copy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

from scripts import goal5793_x2_offline_source_resolver as resolver
from scripts.goal5793_x2_offline_core import X2Error


ROOT = Path(__file__).resolve().parents[1]
PDF = base64.b64decode((ROOT / "tests/fixtures/goal5793_x2_pdf/synthetic_identity.pdf.b64").read_text(encoding="ascii").strip(), validate=True)


def _utc(seconds: float) -> str:
    value = datetime(2026, 8, 22, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"


def _component():
    return {
        "component_id": "doi:10.9999/goal5793.synthetic", "doi": ["10.9999/goal5793.synthetic"],
        "arxiv": ["2501.01234"], "openalex": ["W123"], "title": ["synthetic hardware ray tracing work"],
        "first_author": ["smith"], "year": [2025],
        "source_url_slots": [
            {"slot_kind": "ARXIV_PDF", "url": "https://arxiv.org/pdf/2501.01234"},
            {"slot_kind": "DOI_ACCEPT_PDF", "url": "https://doi.org/10.9999/goal5793.synthetic"},
        ],
        "direct_link_slots": [],
    }


def _attempt(body: bytes, *, start: float = 0, status: int = 200, content_type: str = "application/pdf"):
    return {
        "attempt": 1, "scheduled_delay_seconds": 0, "request_url": "https://arxiv.org/pdf/2501.01234",
        "request_headers": [], "request_started_at_utc": _utc(start), "redirect_chain": [],
        "final_url": "https://arxiv.org/pdf/2501.01234", "status": status,
        "response_headers": [{"name": "Content-Type", "value": content_type}],
        "response_received_at_utc": _utc(start + 0.1), "body_base64": base64.b64encode(body).decode("ascii"), "error": None,
    }


def _fixture():
    return {
        "schema": "rtdl.goal5793.x2.offline_source_resolution_fixture.v1", "mode": "OFFLINE_SYNTHETIC_FIXTURES_ONLY",
        "synthetic_fixture": True, "network_call_count": 0, "component": _component(),
        "source_lineages": [{"slot_kind": "ARXIV_PDF", "url": "https://arxiv.org/pdf/2501.01234", "attempts": [_attempt(PDF)]}],
    }


class Goal5793X2OfflineSourceResolverTest(unittest.TestCase):
    def test_01_exact_pdf_identity_qualifies_and_exposes_direct_code_link(self):
        result = resolver.validate_resolution_fixture(_fixture())
        self.assertTrue(result["source_qualified"])
        self.assertEqual(result["author_code_direct_link_plan"], [{"source": "PDF_ANNOTATION", "url": "https://github.com/example/goal5793-synthetic"}])
        self.assertFalse(any(result["authorization"].values()))

    def test_02_first_http_200_pdf_controls_even_if_identity_mismatches(self):
        fixture = _fixture()
        fixture["component"].update(doi=["10.9999/other"], arxiv=["2501.99999"], title=["Other"], first_author=["jones"], year=[2024])
        result = resolver.validate_resolution_fixture(fixture)
        self.assertFalse(result["source_qualified"])
        self.assertEqual(result["status"], "SOURCE_GAP__SELECTION_INELIGIBLE__NO_MANUAL_VERSION_SUBSTITUTION")

    def test_03_later_slot_after_pdf_success_rejected(self):
        fixture = _fixture()
        second = copy.deepcopy(fixture["source_lineages"][0])
        second["slot_kind"] = "DOI_ACCEPT_PDF"; second["url"] = "https://doi.org/10.9999/goal5793.synthetic"
        second["attempts"][0]["request_url"] = second["url"]; second["attempts"][0]["final_url"] = second["url"]
        second["attempts"][0]["request_headers"] = [{"name": "Accept", "value": "application/pdf"}]
        second["attempts"][0]["request_started_at_utc"] = _utc(1); second["attempts"][0]["response_received_at_utc"] = _utc(1.1)
        fixture["source_lineages"].append(second)
        with self.assertRaisesRegex(X2Error, "SOURCE_LINEAGES_AFTER_FIRST_SUCCESS"):
            resolver.validate_resolution_fixture(fixture)

    def test_04_no_slots_is_explicit_source_gap_without_network(self):
        fixture = _fixture(); fixture["component"]["source_url_slots"] = []; fixture["source_lineages"] = []
        result = resolver.validate_resolution_fixture(fixture)
        self.assertFalse(result["source_qualified"])
        self.assertEqual(result["activity"]["network_calls"], 0)

    def test_05_redirect_or_header_drift_rejected(self):
        fixture = _fixture(); fixture["source_lineages"][0]["attempts"][0]["request_headers"] = [{"name": "Accept", "value": "application/pdf"}]
        with self.assertRaisesRegex(X2Error, "SOURCE_REQUEST_IDENTITY_OR_HEADERS_DRIFT"):
            resolver.validate_resolution_fixture(fixture)
        fixture = _fixture(); fixture["source_lineages"][0]["attempts"][0]["final_url"] = "https://evil.invalid/paper.pdf"
        with self.assertRaisesRegex(X2Error, "SOURCE_REDIRECT_FINAL_URL_MISMATCH"):
            resolver.validate_resolution_fixture(fixture)


if __name__ == "__main__":
    unittest.main()
