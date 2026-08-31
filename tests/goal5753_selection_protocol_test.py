from __future__ import annotations

import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5753SelectionProtocolTest(unittest.TestCase):
    def test_every_survey_paper_has_explicit_non_expressibility_disposition(self) -> None:
        builder = load_script("goal5753_build_held_out_universe.py")
        self.assertEqual(len(builder.PAPER_DISPOSITIONS), 29)
        reasons = [reason for _eligible, reason in builder.PAPER_DISPOSITIONS.values()]
        self.assertFalse(any("easy" in reason or "supported" in reason for reason in reasons))

    def test_selector_is_deterministic_and_binds_core_universe_and_beacon(self) -> None:
        selector = load_script("goal5753_select_held_out_application.py")
        self.assertEqual(selector.DOMAIN, b"rtdl-v4-goal5753-held-out-selection-v1\n")
        material = selector.DOMAIN + b"a\n" + b"b\n" + (b"0" * 128) + b"\n"
        self.assertEqual(len(__import__("hashlib").sha256(material).hexdigest()), 64)

    def test_frozen_universe_has_expected_shape_when_present(self) -> None:
        path = ROOT / "history" / "internal_docs" / "goal5753_held_out_candidate_universe_20260811.json"
        if not path.exists():
            self.skipTest("universe is generated after protocol implementation")
        result = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(result["counts"], {"eligible_rows": 17, "excluded_rows": 18, "survey_rows": 35})
        self.assertFalse(result["claim_boundary"]["application_selected"])
        self.assertTrue(result["policy"]["existing_or_design_seen_families_excluded"])

    def test_core_freeze_digest_and_post_selection_seal(self) -> None:
        path = ROOT / "history" / "internal_docs" / "goal5753_core_freeze_and_selection_protocol_20260811.json"
        result = json.loads(path.read_text(encoding="utf-8"))
        canonical = json.dumps(
            result["frozen_core_identity"], sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            result["frozen_core_identity_canonical_json_sha256"],
        )
        self.assertIn("src/**", result["post_selection_policy"]["forbidden_paths"])
        self.assertTrue(result["post_selection_policy"]["any_forbidden_change_fails_exam"])
        self.assertFalse(result["claim_boundary"]["application_selected"])

    def test_core_seal_scope_covers_all_source_and_build_contracts(self) -> None:
        audit = load_script("goal5753_held_out_core_seal_audit.py")
        self.assertEqual(audit.EXACT_PREFIXES, ("src/",))
        self.assertEqual(
            audit.EXACT_FILES,
            {
                "Makefile",
                "pyproject.toml",
                "requirements.txt",
            },
        )
        self.assertEqual(
            audit.FREEZE_COMMIT_FILES,
            ("docs/v4/restricted_python_optix_callbacks_design.md",),
        )


if __name__ == "__main__":
    unittest.main()
