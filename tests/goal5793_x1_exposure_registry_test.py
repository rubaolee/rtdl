from __future__ import annotations

import ast
import io
import json
import tarfile
import tempfile
from pathlib import Path
import unittest
from unittest import mock

from scripts import goal5793_x1_build_exposure_registry as registry
from scripts.goal5793_x1_canonical import seal_document, sha256_bytes


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / registry.DEFAULT_ARCHIVE
GOAL5753 = ROOT / registry.DEFAULT_GOAL5753_UNIVERSE
SCRIPT = ROOT / "scripts" / "goal5793_x1_build_exposure_registry.py"
OUTPUT = ROOT / "history" / "internal_docs" / "goal5793_x1_project_exposure_registry_v2_20260822.json"
OUTPUT_SHA256 = "9695545df7b2908f9845bc7b825fa9e226b0d05d506b7b3c74305560393af804"
REJECTED_V1 = ROOT / "history" / "internal_docs" / "goal5793_x1_project_exposure_registry_20260822.json"


def alias(kind: str, value: str, *, edge: bool) -> dict[str, object]:
    return {
        "component_edge": edge,
        "controlling_for_exposure_match": kind != "citation_key",
        "kind": kind,
        "value": value,
    }


def entry(node: str, key: str, aliases: list[dict[str, object]]) -> dict[str, object]:
    return {"aliases": aliases, "citation_key": key, "node_id": node}


class Goal5793X1ExposureRegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = registry.build_registry(ARCHIVE, GOAL5753)

    def test_exact_pinned_archive_and_full_186_entry_inventory(self) -> None:
        doc = self.document
        self.assertEqual(doc["source_authorities"]["survey_archive"]["sha256"], registry.SURVEY_ARCHIVE_SHA256)
        self.assertEqual(doc["source_authorities"]["survey_archive"]["bytes"], 752_766)
        self.assertEqual(doc["source_authorities"]["sample_bib"]["sha256"], registry.SAMPLE_BIB_SHA256)
        self.assertEqual(doc["counts"]["bibliography_entries"], 186)
        self.assertEqual(len(doc["bibliography_entries"]), 186)
        self.assertEqual(len({row["citation_key"] for row in doc["bibliography_entries"]}), 186)
        self.assertEqual(len({row["node_id"] for row in doc["bibliography_entries"]}), 186)

    def test_all_entries_and_components_are_permanently_ineligible(self) -> None:
        doc = self.document
        self.assertEqual(doc["counts"]["selection_eligible_entries"], 0)
        self.assertTrue(all(row["selection_eligible"] is False for row in doc["bibliography_entries"]))
        self.assertTrue(all("PERMANENTLY_SELECTION_INELIGIBLE" in row["selection_disposition"] for row in doc["bibliography_entries"]))
        self.assertTrue(all(row["selection_eligible"] is False for row in doc["components"]))
        self.assertTrue(doc["selection_policy"]["all_186_bibliography_entries_permanently_selection_ineligible"])

    def test_source_citations_and_bibliography_only_entries_are_both_retained(self) -> None:
        doc = self.document
        self.assertEqual(doc["counts"]["main_tex_paper_body_citation_macro_occurrences"], 85)
        self.assertEqual(doc["counts"]["main_tex_paper_body_citation_key_occurrences"], 99)
        self.assertEqual(doc["counts"]["main_tex_paper_body_unique_citation_keys"], 72)
        self.assertEqual(doc["counts"]["all_scanned_source_citation_macro_occurrences"], 184)
        self.assertEqual(doc["counts"]["all_scanned_source_citation_key_occurrences"], 206)
        self.assertEqual(doc["counts"]["all_scanned_source_unique_citation_keys"], 80)
        self.assertEqual(doc["counts"]["bibliography_entries_cited_in_scanned_source"], 80)
        self.assertEqual(doc["counts"]["bibliography_entries_not_cited_in_scanned_source"], 106)
        self.assertEqual(doc["counts"]["unresolved_source_citation_keys"], 0)
        self.assertEqual(doc["unresolved_source_citation_keys"], [])
        uncited = [row for row in doc["bibliography_entries"] if not row["cited_in_scanned_source"]]
        self.assertEqual(len(uncited), 106)
        self.assertTrue(all(row["selection_eligible"] is False for row in uncited))
        surfaces = {row["member_path"]: row for row in doc["citation_surface_summary"]["rows"]}
        self.assertEqual(surfaces["main.tex"]["surface_kind"], "PAPER_BODY_MAIN_TEX")
        self.assertTrue(all("NOT_PAPER_BODY_CITATION" in surfaces[name]["surface_kind"] for name in ("characteristics1.csv", "characteristics2.csv", "prob.csv")))

    def test_all_35_goal5753_rows_are_crosslinked(self) -> None:
        doc = self.document
        self.assertEqual(doc["counts"]["old_goal5753_crosslinked_candidate_rows"], 35)
        self.assertEqual(doc["counts"]["old_goal5753_unique_citation_keys"], 29)
        linked = [candidate for row in doc["bibliography_entries"] for candidate in row["old_goal5753_candidate_ids"]]
        self.assertEqual(len(linked), 35)
        self.assertEqual(len(set(linked)), 35)

    def test_coverage_gaps_are_explicit_and_cannot_create_unseen_claim(self) -> None:
        doc = self.document
        self.assertEqual(doc["counts"]["coverage_gaps"], 10)
        self.assertEqual(len(doc["coverage_gaps"]), 10)
        self.assertTrue(all(row["selection_or_unseen_effect"] == "NO_ELIGIBILITY__NO_UNSEEN_OR_BLIND_CLAIM" for row in doc["coverage_gaps"]))
        self.assertFalse(doc["bibliography_completeness"]["complete_published_reference_list_claimed"])
        self.assertFalse(doc["bibliography_completeness"]["complete_literature_universe_claimed"])
        self.assertFalse(doc["bibliography_completeness"]["complete_author_mental_exposure_claimed"])
        self.assertFalse(doc["scope_boundary"]["complete_presearch_project_exposure_registry"])
        self.assertFalse(doc["selection_policy"]["coverage_gap_allows_unseen_blind_or_held_out_claim"])

    def test_identity_missingness_is_visible_not_favorably_imputed(self) -> None:
        doc = self.document
        self.assertEqual(doc["counts"]["missing_strong_identifier_entries"], 179)
        self.assertEqual(doc["counts"]["missing_fallback_identity_entries"], 3)
        no_strong = [row for row in doc["bibliography_entries"] if not row["strong_identifier_present"]]
        self.assertEqual(len(no_strong), 179)
        self.assertTrue(all(row["selection_eligible"] is False for row in no_strong))

    def test_document_is_deterministic_and_internal_seal_recomputes(self) -> None:
        rebuilt = registry.build_registry(ARCHIVE, GOAL5753)
        self.assertEqual(registry.serialized_document(rebuilt), registry.serialized_document(self.document))
        expected = seal_document(
            self.document,
            seal_field="registry_sha256",
            domain="rtdl.goal5793.x1.survey_exposure.registry_document",
            version=1,
        )
        self.assertEqual(self.document["registry_sha256"], expected)

    def test_create_only_formal_output_is_exact(self) -> None:
        payload = OUTPUT.read_bytes()
        self.assertEqual(payload, registry.serialized_document(self.document))
        self.assertEqual(len(payload), 476_230)
        self.assertEqual(sha256_bytes(payload), OUTPUT_SHA256)

    def test_path_dependent_v1_is_preserved_but_noncontrolling(self) -> None:
        self.assertEqual(sha256_bytes(REJECTED_V1.read_bytes()), registry.REJECTED_CREATE_ONLY_V1["file_sha256"])
        self.assertEqual(REJECTED_V1.stat().st_size, registry.REJECTED_CREATE_ONLY_V1["bytes"])
        self.assertEqual(self.document["superseded_create_only_lineage"], registry.REJECTED_CREATE_ONLY_V1)

    def test_bibtex_parser_handles_nested_values_and_rejects_duplicate_keys(self) -> None:
        text = '@article{k1,title={A {Nested} Title},author="Doe, Jane and Roe, R.",year=2024,doi={10.1/x}}'
        rows = registry.parse_bibtex(text)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["fields"]["title"], "A {Nested} Title")
        self.assertEqual(rows[0]["fields"]["year"], "2024")
        with self.assertRaisesRegex(registry.RegistryInputError, "DUPLICATE_BIBTEX_CITATION_KEY"):
            registry.parse_bibtex(text + "\n" + text)
        with self.assertRaisesRegex(registry.RegistryInputError, "UNTERMINATED_BIBTEX_ENTRY"):
            registry.parse_bibtex("@article{x,title={broken}")

    def test_strong_identifier_closure_is_order_invariant_and_fallback_does_not_merge(self) -> None:
        same_arxiv = [
            entry("n2", "b", [alias("doi", "doi:10.2/b", edge=True), alias("arxiv", "arxiv:2601.1", edge=True)]),
            entry("n1", "a", [alias("doi", "doi:10.2/a", edge=True), alias("arxiv", "arxiv:2601.1", edge=True)]),
        ]
        forward = registry.derive_components(same_arxiv)
        reverse = registry.derive_components(list(reversed(same_arxiv)))
        self.assertEqual(forward, reverse)
        self.assertEqual(len(forward), 1)
        self.assertTrue(forward[0]["identity_conflict"])
        self.assertEqual(forward[0]["selection_disposition"], "IDENTITY_CONFLICT__PERMANENTLY_SELECTION_INELIGIBLE")

        shared_fallback = [
            entry("n1", "a", [alias("fallback_identity_sha256", "fallback_sha256:x", edge=False)]),
            entry("n2", "b", [alias("fallback_identity_sha256", "fallback_sha256:x", edge=False)]),
        ]
        components = registry.derive_components(shared_fallback)
        self.assertEqual(len(components), 2)
        self.assertTrue(all(row["fallback_identity_ambiguous"] for row in components))
        self.assertTrue(all(row["selection_disposition"] == "FALLBACK_IDENTITY_AMBIGUOUS__PERMANENTLY_SELECTION_INELIGIBLE" for row in components))

    def test_normalized_aliases_are_stable(self) -> None:
        self.assertEqual(registry.normalize_doi("https://doi.org/10.1145/ABC.1."), "10.1145/abc.1")
        self.assertEqual(registry.extract_arxiv_ids("arXiv:2603.28771v4"), ["2603.28771"])
        self.assertEqual(registry.extract_openalex_ids("https://openalex.org/w123456"), ["W123456"])
        self.assertEqual(registry.normalize_first_author("Doe, Jane and Roe, Richard"), "doe")

    def test_tar_path_and_member_type_hostiles_fail_closed(self) -> None:
        for path in ("../escape", "/absolute", "C:/drive", "a\\b", "a/./b"):
            with self.subTest(path=path), self.assertRaises(registry.RegistryInputError):
                registry._safe_member_path(path)

        with tempfile.TemporaryDirectory() as tmp:
            archive_path = Path(tmp) / "linked.tar"
            with tarfile.open(archive_path, "w") as tar:
                info = tarfile.TarInfo("safe")
                info.type = tarfile.SYMTYPE
                info.linkname = "target"
                tar.addfile(info)
            payload = archive_path.read_bytes()
            with mock.patch.object(registry, "SURVEY_ARCHIVE_BYTES", len(payload)), mock.patch.object(
                registry, "SURVEY_ARCHIVE_SHA256", sha256_bytes(payload)
            ):
                with self.assertRaisesRegex(registry.RegistryInputError, "LINKED_ARCHIVE_MEMBER_FORBIDDEN"):
                    registry.read_safe_tar(archive_path)

    def test_create_only_writer_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.json"
            registry.write_create_only(path, b"one")
            self.assertEqual(path.read_bytes(), b"one")
            with self.assertRaises(FileExistsError):
                registry.write_create_only(path, b"two")
            self.assertEqual(path.read_bytes(), b"one")

    def test_static_surface_has_no_network_search_entropy_or_product_write_route(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertTrue(imports.isdisjoint({"requests", "urllib", "http", "socket", "subprocess", "random", "secrets"}))
        scope = self.document["scope_boundary"]
        for key in (
            "network_or_live_provider_call_count",
            "entropy_anchor_or_draw_count",
            "candidate_selection_count",
            "candidate_implementation_or_execution_count",
            "gpu_home_pod_or_ssh_count",
            "registered_or_performance_timing_count",
        ):
            self.assertEqual(scope[key], 0)
        self.assertFalse(scope["x2_search_implemented_or_authorized"])


if __name__ == "__main__":
    unittest.main()
