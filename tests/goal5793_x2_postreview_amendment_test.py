from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.goal5793_x1_canonical import seal_document, sha256_bytes
from scripts import goal5793_x2_build_postreview_amendment as amendment


class Goal5793X2PostreviewAmendmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = amendment.build_documents()
        cls.second = amendment.build_documents()
        cls.authority = json.loads(cls.first[amendment.AUTHORITY_NAME])
        cls.cfr = cls.first[amendment.CFR_NAME].decode("utf-8")

    def test_01_build_is_deterministic_and_authority_seal_is_exact(self) -> None:
        self.assertEqual(self.first, self.second)
        self.assertEqual(
            self.authority["authority_sha256"],
            seal_document(
                self.authority,
                seal_field="authority_sha256",
                domain=amendment.AUTHORITY_DOMAIN,
                version=1,
            ),
        )

    def test_02_p1_control_preserves_the_complete_denominator(self) -> None:
        p1 = self.authority["p1_1_unmapped_denominator_repair"]
        self.assertEqual(
            (p1["input_rows"], p1["validated_rows"], p1["mapped_rows"], p1["unmapped_rows"]),
            (3, 3, 2, 1),
        )
        self.assertTrue(p1["all_input_rows_accounted"])
        self.assertFalse(p1["batch_aborted"])
        self.assertFalse(p1["unrecorded_manual_deletion_needed"])
        self.assertEqual(p1["unmapped_by_axis"]["geometry_family"], 1)
        self.assertFalse(p1["unmapped_control_row"]["selection_eligible"])

    def test_03_p2_evidence_and_claim_ceilings_are_exact(self) -> None:
        friction = self.authority["p2_dispositions"]["P2_1_raw_token_lexer"]["evidence"]
        for token in ("<optix_stubs.h>", "<cuda_runtime_api.h>", "CUDA_SUCCESS", "OPTIX_SUCCESS", "optixAccelBuild"):
            self.assertIn(token, friction["c_cuda_optix_code_tokens"])
        self.assertEqual(friction["python_comment_and_string_cuda_optix_code_tokens"], 0)
        self.assertEqual(friction["ordinary_python_unresolved_rtdl_calls"], 0)
        self.assertFalse(friction["direct_cuda_optix_public_private_unresolved_comparison_allowed"])
        alias = self.authority["p2_dispositions"]["P2_4_alias_projection"]["exact_split"]
        self.assertEqual(alias, {
            "strong_identifier_rows": 7,
            "weak_author_year_fallback_rows": 176,
            "weak_exact_title_only_rows": 3,
        })
        ceiling = self.authority["p2_dispositions"]["P2_5_role_claim_language"]
        self.assertFalse(ceiling["role_diversity_supports_structural_novelty_or_coverage_claim"])
        self.assertFalse(ceiling["role_A_supports_arbitrary_literature_capability_claim"])

    def test_04_authorization_is_fail_closed(self) -> None:
        self.assertFalse(any(self.authority["authorization"].values()))
        boundary = self.authority["claim_boundary"]
        self.assertFalse(boundary["x3_provider_search_authorized"])
        self.assertEqual(boundary["generalization_exam_count"], 0)
        self.assertEqual(boundary["usability_study_count"], 0)
        self.assertEqual(boundary["functionally_matched_direct_cuda_optix_baseline_count"], 0)

    def test_05_sole_cfr_embeds_every_new_root_exactly(self) -> None:
        self.assertEqual(self.cfr.count("SEND ONLY " + "THIS FILE"), 1)
        self.assertIn("Do not send a second packet.", self.cfr)
        fence = "`" * 8
        embedded = {
            amendment.AUTHORITY_NAME: self.first[amendment.AUTHORITY_NAME],
            amendment.REPORT_NAME: self.first[amendment.REPORT_NAME],
            **{path: (amendment.ROOT / path).read_bytes() for path in amendment.SOURCE_ROOTS},
            "history/internal_docs/goal5793_x2_exposure_alias_authority_v2_20260822.json":
                (amendment.ROOT / "history/internal_docs/goal5793_x2_exposure_alias_authority_v2_20260822.json").read_bytes(),
        }
        for path, raw in embedded.items():
            language = "json" if path.endswith(".json") else "markdown" if path.endswith(".md") else "python"
            exact_block = f"## Embedded `{path}`\n\n{fence}{language}\n{raw.decode('utf-8').rstrip(chr(10))}\n{fence}"
            self.assertEqual(self.cfr.count(exact_block), 1)
        for name, data in self.first.items():
            self.assertEqual(sha256_bytes(data), sha256_bytes(self.second[name]))

    def test_06_create_only_and_verify_stored_bytes_in_fresh_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5793_x2_postreview_amendment_test_") as temp:
            root = Path(temp)
            for name, data in self.first.items():
                target = root / name
                self.assertFalse(target.exists())
                target.write_bytes(data)
                self.assertEqual(target.read_bytes(), data)
            self.assertEqual(set(path.name for path in root.iterdir()), set(self.first))


if __name__ == "__main__":
    unittest.main()
