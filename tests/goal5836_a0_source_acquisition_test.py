from __future__ import annotations

import copy
import json
from pathlib import Path, PurePosixPath
import tarfile
import unittest

from scripts import goal5836_a0_build_source_acquisition as a0


class Goal5836A0SourceAcquisitionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.output = a0.DEFAULT_OUTPUT
        cls.authority = a0.verify_stored(cls.output)
        cls.inventory = json.loads(
            (cls.output / "AUTHOR_SOURCE_TREE_INVENTORY.json").read_text(
                encoding="ascii"
            )
        )
        cls.selected = json.loads(
            (cls.output / "AUTHOR_SELECTED_SOURCE_MANIFEST.json").read_text(
                encoding="ascii"
            )
        )

    def _reseal(self, document: dict) -> dict:
        document["source_acquisition_authority_sha256"] = a0._seal(document)
        return document

    def test_01_exact_stored_authority_rebuilds(self) -> None:
        self.assertEqual(self.authority, a0.verify_stored(self.output))
        self.assertEqual(
            self.authority["source_acquisition_authority_sha256"],
            a0._seal(self.authority),
        )

    def test_02_a0_is_consumed_and_every_later_stage_is_locked(self) -> None:
        authorization = self.authority["authorization"]
        self.assertEqual(
            {key for key, value in authorization.items() if value},
            {
                "a0_owner_authorized",
                "a0_acquisition_completed",
                "a0_authorization_consumed",
            },
        )
        self.assertEqual(
            self.authority["next_owner_gate"],
            "AUTHORIZE_STAGE_A1_AUTHOR_SOURCE_FIDELITY_CLASSIFICATION_ONLY",
        )

    def test_03_no_build_execution_gpu_or_timing_observation_exists(self) -> None:
        observation = self.authority["a0_observation"]
        self.assertTrue(observation["paper_identity_metadata_inspected"])
        self.assertTrue(
            observation["paper_method_text_incidentally_exposed_by_discovery_tool"]
        )
        self.assertFalse(observation["author_source_semantics_inspected"])
        self.assertFalse(observation["source_fidelity_classification_made"])
        for field in (
            "author_build_count",
            "author_execution_count",
            "rtdl_goal5836_execution_count",
            "gpu_worker_count",
            "timing_count",
            "performance_result_count",
        ):
            self.assertEqual(observation[field], 0)

    def test_04_paper_is_exact_arxiv_v2_not_publisher_pdf(self) -> None:
        paper = self.authority["paper_identity"]
        self.assertEqual(paper["arxiv_id"], "2409.09918v2")
        self.assertEqual(paper["sha256"], a0.PAPER_SHA256)
        self.assertEqual(paper["bytes"], a0.PAPER_BYTES)
        self.assertFalse(paper["publisher_pdf_acquired"])
        self.assertIn("NOT_IEEE_PUBLISHER_PDF", paper["kind"])

    def test_05_exact_planned_commit_and_root_tree_are_observed(self) -> None:
        source = self.authority["author_source_identity"]
        self.assertEqual(source["planned_commit"], a0.AUTHOR_COMMIT)
        self.assertEqual(source["observed_commit"], a0.AUTHOR_COMMIT)
        self.assertEqual(source["root_tree_git_oid_sha1"], a0.AUTHOR_ROOT_TREE)
        self.assertFalse(source["commit_pin_changed"])

    def test_06_inventory_rederives_root_tree_and_exact_totals(self) -> None:
        rows = self.inventory["rows"]
        self.assertEqual(a0._rederive_tree_oid(rows), a0.AUTHOR_ROOT_TREE)
        self.assertEqual(self.inventory["file_count"], len(rows))
        self.assertEqual(
            self.inventory["total_blob_bytes"],
            sum(row["bytes"] for row in rows),
        )
        self.assertEqual(len({row["path"] for row in rows}), len(rows))

    def test_07_selected_source_is_exact_mechanical_subset(self) -> None:
        expected = [row for row in self.inventory["rows"] if a0._selected(row)]
        self.assertEqual(self.selected["rows"], expected)
        self.assertEqual(self.selected["selected_file_count"], len(expected))
        self.assertEqual(
            self.selected["selection_rule"]["kind"],
            "MECHANICAL_BASENAME_OR_SUFFIX__NO_SEMANTIC_INSPECTION",
        )

    def test_08_selected_archive_paths_are_safe_and_exact(self) -> None:
        prefix = self.selected["archive_prefix"]
        expected = [f"{prefix}/{row['path']}" for row in self.selected["rows"]]
        with tarfile.open(
            self.output / "AUTHOR_SELECTED_SOURCE.tar.gz", mode="r:gz"
        ) as archive:
            names = archive.getnames()
        self.assertEqual(names, expected)
        for name in names:
            path = PurePosixPath(name)
            self.assertFalse(path.is_absolute())
            self.assertNotIn("..", path.parts)

    def test_09_commit_object_and_license_are_byte_bound(self) -> None:
        commit = (self.output / "AUTHOR_COMMIT_OBJECT.txt").read_bytes()
        license_bytes = (self.output / "AUTHOR_LICENSE.txt").read_bytes()
        self.assertEqual(a0._git_oid("commit", commit), a0.AUTHOR_COMMIT)
        self.assertEqual(
            a0._git_oid("blob", license_bytes),
            "0ec3c9a8cb0bb8fe2de6ad03ca465ccd12e1c4a5",
        )
        self.assertTrue(license_bytes.startswith(b"MIT License\n"))

    def test_10_coordinated_reseal_cannot_authorize_a1(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["authorization"]["a1_source_fidelity_inspection_authorized"] = True
        self._reseal(changed)
        with self.assertRaisesRegex(a0.A0Error, "AUTHORIZATION_DOCUMENT_MISMATCH"):
            a0.validate_policy(changed)

    def test_11_coordinated_reseal_cannot_claim_semantic_inspection(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["a0_observation"]["author_source_semantics_inspected"] = True
        self._reseal(changed)
        with self.assertRaisesRegex(
            a0.A0Error, "A1_SEMANTIC_INSPECTION_LEAKED_INTO_A0"
        ):
            a0.validate_policy(changed)

    def test_12_coordinated_reseal_cannot_hide_paper_text_exposure(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["a0_observation"][
            "paper_method_text_incidentally_exposed_by_discovery_tool"
        ] = False
        self._reseal(changed)
        with self.assertRaisesRegex(a0.A0Error, "PAPER_DISCOVERY_EXPOSURE"):
            a0.validate_policy(changed)

    def test_13_coordinated_reseal_cannot_add_worker_or_timing(self) -> None:
        for field in ("gpu_worker_count", "timing_count"):
            changed = copy.deepcopy(self.authority)
            changed["a0_observation"][field] = 1
            self._reseal(changed)
            with self.assertRaisesRegex(a0.A0Error, "UNAUTHORIZED_A0_OBSERVATION"):
                a0.validate_policy(changed)

    def test_14_tree_inventory_mutation_changes_the_root(self) -> None:
        changed = copy.deepcopy(self.inventory["rows"])
        changed[0]["git_oid_sha1"] = "0" * 40
        self.assertNotEqual(a0._rederive_tree_oid(changed), a0.AUTHOR_ROOT_TREE)

    def test_15_existing_goal5835_claim_ceiling_is_preserved(self) -> None:
        claim = self.authority["claim_boundary"]
        self.assertEqual(claim["paper_app_status"], "NOT_A_PAPER_APP")
        self.assertEqual(
            claim["source_relation"],
            "SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES",
        )
        self.assertFalse(claim["paper_app_claimed"])
        self.assertFalse(claim["performance_claimed"])
        self.assertFalse(claim["complete_rtccd_claimed"])


if __name__ == "__main__":
    unittest.main()
