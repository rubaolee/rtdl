from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import tarfile
import unittest


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts/goal5790_build_home_evidence.py"
SPEC = importlib.util.spec_from_file_location("goal5790_evidence_builder", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class Goal5790HomeEvidenceBuilderTest(unittest.TestCase):
    def test_preserved_home_closure_rehashes_and_raw_totals_reconstruct(self) -> None:
        candidate = BUILDER._verified_candidate(
            BUILDER.DEFAULT_BUNDLE, BUILDER.DEFAULT_SOURCE)
        state = BUILDER._verify_closure(BUILDER.DEFAULT_CLOSURE, candidate)
        self.assertEqual(state["event_counts"], {
            "fusion_on": 10, "fusion_off": 35})
        self.assertEqual(state["receipt_counts"], {
            "fusion_on": 5, "fusion_off": 5})
        self.assertEqual(state["recount"]["exact_lane_count"], 10)
        self.assertEqual(state["recount"][
            "behavioral_true_optix_lane_count"], 10)

    def test_nonself_manifest_and_cache_boundary_are_explicit(self) -> None:
        payloads = {"payload.txt": b"goal5790"}
        rows = [{
            "path": name, "size_bytes": len(data),
            "sha256": BUILDER._sha(data),
        } for name, data in sorted(payloads.items())]
        manifest = {
            "manifest_self_referential": False,
            "manifest_member_listed_in_payloads": False,
            "payload_count": 1,
            "payload_bytes": len(b"goal5790"),
            "payloads": rows,
        }
        archived = dict(payloads)
        archived["MANIFEST.json"] = BUILDER._json_bytes(manifest)
        data = BUILDER._archive(archived)
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            found = json.load(archive.extractfile("MANIFEST.json"))
        self.assertFalse(found["manifest_self_referential"])
        self.assertNotIn("MANIFEST.json", {
            row["path"] for row in found["payloads"]})
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("cache_cubin_non_authority", source)
        self.assertIn("raw_generated_ptx_bytes_preserved", source)


if __name__ == "__main__":
    unittest.main()
