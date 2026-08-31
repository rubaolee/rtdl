from __future__ import annotations

import ast
import io
import json
import os
import subprocess
import tarfile
import tempfile
from pathlib import Path
import unittest

from scripts import goal5793_x1_build_declared_exposure_registry as declared


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5793_x1_build_declared_exposure_registry.py"


class Goal5793X1DeclaredExposureRegistryTest(unittest.TestCase):
    def test_alias_extraction_uses_only_frozen_alias_vocabulary(self) -> None:
        text = json.dumps(
            {
                "citation_key": "Known2026",
                "doi": "https://doi.org/10.1145/ABC.1",
                "url": "https://arxiv.org/abs/2603.28771v2 https://openalex.org/w123456",
                "title": "A {General} Method",
                "author": "Doe, Jane and Roe, R.",
                "year": "2026",
            }
        )
        aliases, gaps = declared.extract_aliases(text, "record.json")
        self.assertEqual(gaps, [])
        self.assertIn("doi:10.1145/abc.1", aliases)
        self.assertIn("arxiv:2603.28771", aliases)
        self.assertIn("openalex:W123456", aliases)
        self.assertIn("citation_key:Known2026", aliases)
        self.assertEqual(sum(alias.startswith("fallback_sha256:") for alias in aliases), 1)

    def test_strict_text_classifier_fails_closed_on_binary_controls(self) -> None:
        self.assertEqual(declared.is_strict_text("语义\n".encode("utf-8")), (True, "语义\n"))
        self.assertEqual(declared.is_strict_text(b"a\x00b"), (False, None))
        self.assertEqual(declared.is_strict_text(b"\xff"), (False, None))
        self.assertEqual(declared.is_strict_text(b"a\x01b"), (False, None))

    def test_successor_workspace_is_never_relabelled_s0_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            (root / "scripts" / "paper.json").write_text(
                '{"doi":"10.1000/test"}', encoding="utf-8"
            )
            (root / "tmp").mkdir()
            (root / "tmp" / "hidden.md").write_text("doi:10.2000/hidden", encoding="utf-8")
            result = declared.scan_successor_workspace(root)
        self.assertFalse(result["complete_historical_s0_workspace_snapshot"])
        self.assertTrue(result["post_s0_or_x1_contamination_present"])
        rows = result["strict_utf8_text_rows"]
        self.assertEqual([row["path"] for row in rows], ["scripts/paper.json"])
        self.assertIn("doi:10.1000/test", rows[0]["aliases"])
        self.assertTrue(any(row["path"] == "tmp" for row in result["excluded_roots_or_directories"]))

    def test_successor_workspace_recurses_all_nonexcluded_roots_and_keeps_prefixed_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "history" / "ad_hoc_reviews").mkdir(parents=True)
            (root / "history" / "revisions").mkdir(parents=True)
            (root / "unlisted_root").mkdir()
            (root / "build").mkdir()
            (root / "history" / "ad_hoc_reviews" / "a.md").write_text(
                "doi:10.1000/history-a", encoding="utf-8"
            )
            (root / "history" / "revisions" / "b.md").write_text(
                "doi:10.1000/history-b", encoding="utf-8"
            )
            (root / "unlisted_root" / "c.md").write_text(
                "doi:10.1000/unlisted", encoding="utf-8"
            )
            (root / "build_notes.md").write_text(
                "doi:10.1000/root-build-file", encoding="utf-8"
            )
            (root / "tmp_notes.md").write_text(
                "doi:10.1000/root-tmp-file", encoding="utf-8"
            )
            (root / "kernel.ptx").write_text(
                "// doi:10.1000/text-source-despite-suffix", encoding="utf-8"
            )
            (root / "opaque.bin").write_bytes(b"binary\x00payload")
            (root / "build" / "omitted.md").write_text(
                "doi:10.1000/omitted", encoding="utf-8"
            )
            result = declared.scan_successor_workspace(root)

        observed = {row["path"] for row in result["strict_utf8_text_rows"]}
        self.assertTrue(
            {
                "history/ad_hoc_reviews/a.md",
                "history/revisions/b.md",
                "unlisted_root/c.md",
                "build_notes.md",
                "tmp_notes.md",
                "kernel.ptx",
            }.issubset(observed)
        )
        self.assertNotIn("build/omitted.md", observed)
        self.assertTrue(
            any(
                row["path"] == "build"
                and row["reason"]
                == "EXPLICIT_POST_S0_TRANSIENT_OR_BUILD_ROOT_DIRECTORY_EXCLUDED"
                for row in result["excluded_roots_or_directories"]
            )
        )
        self.assertEqual(
            result["enumeration_scope"],
            "REPOSITORY_ROOT_RECURSIVE_EXCEPT_EACH_EXPLICITLY_RECORDED_EXCLUSION",
        )
        self.assertTrue(result["root_regular_files_are_not_excluded_by_filename_prefix"])
        self.assertEqual(
            [row["path"] for row in result["non_strict_text_rows"]],
            ["opaque.bin"],
        )

    def test_git_scan_covers_all_commits_and_reconstructable_tree_dag(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            (root / "paper.md").write_text("doi:10.1000/one\n", encoding="utf-8")
            subprocess.run(["git", "add", "paper.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "one"], cwd=root, check=True)
            (root / "paper.md").write_text("arXiv:2603.28771v3\n", encoding="utf-8")
            subprocess.run(["git", "commit", "-q", "-am", "two"], cwd=root, check=True)
            result = declared.scan_git_history(root)
        self.assertEqual(result["counts"]["reachable_commits"], 2)
        self.assertEqual(len(result["reachable_commit_roots"]), 2)
        self.assertGreaterEqual(result["counts"]["reachable_trees"], 2)
        aliases = {alias for row in result["strict_utf8_regular_text_blobs"] for alias in row["aliases"]}
        self.assertIn("doi:10.1000/one", aliases)
        self.assertIn("arxiv:2603.28771", aliases)
        self.assertTrue(result["provenance_model"]["unchanged_file_occurrences_are_not_dropped"])

    def test_git_phase_cache_requires_out_of_band_file_identity_and_current_refs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.invalid"],
                cwd=root,
                check=True,
            )
            (root / "paper.md").write_text("doi:10.1000/one\n", encoding="utf-8")
            subprocess.run(["git", "add", "paper.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "one"], cwd=root, check=True)
            cache = declared.build_phase_cache(root, "git")
            cache_path = root / "git-phase.json"
            cache_path.write_bytes(declared.serialized_document(cache))
            trusted = declared.file_sha256(cache_path)
            data, identity = declared.load_validated_phase_cache(
                root, cache_path, "git", trusted
            )
            self.assertEqual(data["counts"]["reachable_commits"], 1)
            self.assertEqual(identity["file_sha256"], trusted)

            (root / "paper.md").write_text("doi:10.1000/two\n", encoding="utf-8")
            subprocess.run(["git", "commit", "-q", "-am", "two"], cwd=root, check=True)
            with self.assertRaisesRegex(
                declared.DeclaredExposureError, "GIT_PHASE_CACHE_REFS_DRIFT"
            ):
                declared.load_validated_phase_cache(root, cache_path, "git", trusted)

    def test_phase_cache_coordinated_reseal_cannot_reuse_old_trust_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.invalid"],
                cwd=root,
                check=True,
            )
            (root / "paper.md").write_text("doi:10.1000/one\n", encoding="utf-8")
            subprocess.run(["git", "add", "paper.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "one"], cwd=root, check=True)
            cache = declared.build_phase_cache(root, "git")
            cache_path = root / "git-phase.json"
            cache_path.write_bytes(declared.serialized_document(cache))
            trusted = declared.file_sha256(cache_path)

            cache["data"]["counts"]["reachable_commits"] = 999
            cache["phase_cache_sha256"] = declared.seal_document(
                cache,
                seal_field="phase_cache_sha256",
                domain="rtdl.goal5793.x1.declared_exposure.phase_cache",
                version=1,
            )
            cache_path.write_bytes(declared.serialized_document(cache))
            with self.assertRaisesRegex(
                declared.DeclaredExposureError,
                "PHASE_CACHE_OUT_OF_BAND_FILE_IDENTITY_MISMATCH",
            ):
                declared.load_validated_phase_cache(root, cache_path, "git", trusted)

    def test_archive_scan_reads_safe_text_and_rejects_linked_container(self) -> None:
        safe_buffer = io.BytesIO()
        with tarfile.open(fileobj=safe_buffer, mode="w") as archive:
            payload = b"doi:10.1000/archive\n"
            info = tarfile.TarInfo("docs/paper.md")
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
        rows: list[dict[str, object]] = []
        gaps: list[dict[str, object]] = []
        refs: set[str] = set()
        declared._scan_archive_payload(
            safe_buffer.getvalue(), "safe.tar", 0, {"available": False}, rows, gaps, refs
        )
        self.assertEqual(gaps, [])
        self.assertEqual(rows[0]["classification"], "STRICT_UTF8_TEXT")
        self.assertIn("doi:10.1000/archive", rows[0]["aliases"])

        linked_buffer = io.BytesIO()
        with tarfile.open(fileobj=linked_buffer, mode="w") as archive:
            info = tarfile.TarInfo("link")
            info.type = tarfile.SYMTYPE
            info.linkname = "target"
            archive.addfile(info)
        rows, gaps, refs = [], [], set()
        declared._scan_archive_payload(
            linked_buffer.getvalue(), "linked.tar", 0, {"available": False}, rows, gaps, refs
        )
        self.assertTrue(any("LINKED_ARCHIVE_MEMBER_FORBIDDEN" in row["reason"] for row in gaps))

    def test_repository_reference_extraction_is_bounded_to_local_paths(self) -> None:
        text = "`history/internal_docs/goal1.json` and https://example.com/no and scripts/x.py:12"
        self.assertEqual(
            declared.extract_repository_references(text, "x.md"),
            ["history/internal_docs/goal1.json", "scripts/x.py"],
        )

    def test_missing_owner_disclosure_is_blocking_not_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = declared.load_owner_disclosure(Path(temporary))
        self.assertFalse(result["provided"])
        self.assertFalse(result["complete_or_empty_claimed"])
        self.assertIn("BLOCKING_GAP", result["status"])

    def test_exact_survey_component_is_only_one_bounded_component(self) -> None:
        result = declared.load_survey_component(ROOT)
        self.assertEqual(result["counts"]["bibliography_entries"], 186)
        self.assertEqual(result["counts"]["old_goal5753_crosslinked_candidate_rows"], 35)
        self.assertEqual(result["counts"]["selection_eligible_entries"], 0)
        self.assertFalse(result["scope_boundary"]["complete_presearch_project_exposure_registry"])

    def test_s0_closure_seed_pins_file_identity_and_distinct_internal_seal(self) -> None:
        result = declared.verify_s0_closure_seed(ROOT)
        self.assertEqual(result["bytes"], 9317)
        self.assertEqual(
            result["file_sha256"],
            "4d6e37bc19c0f541537e2f9fc36a31b4d35a20bc0fb080ba495629c0d9fd1f41",
        )
        self.assertEqual(
            result["internal_seal_sha256"],
            "cc118989e6f7462eb236c414c08b7058ea4feacc8e4bac27898f9254bcb90a1a",
        )
        self.assertNotEqual(result["file_sha256"], result["internal_seal_sha256"])

    def test_static_scope_has_no_network_or_remote_execution_surface(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertTrue(imports.isdisjoint({"requests", "urllib", "http", "socket", "paramiko"}))
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("call_for_review_goal5793_x1_", declared.DEFAULT_OUTPUT.as_posix())
        self.assertIn("blocker", declared.DEFAULT_OUTPUT.name)


if __name__ == "__main__":
    unittest.main()
