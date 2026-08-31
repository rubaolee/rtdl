from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile

from rtdsl.v4_callback_frontend import compile_callback_source
from rtdsl.v4_callback_ir import CallbackVerificationError

from scripts.goal5757_lane_probe_framework import LaneClassification, validate_lane_probe
from scripts import goal5757_run_lane_probes as generation
from scripts.goal5757_semantic_coverage import (
    LaneSemanticCoverageError,
    fragment_capabilities,
    require_complete_lane,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "history/internal_docs/goal5757_lane_probe_evidence_20260811"
ARCHIVE = ROOT / "history/internal_docs/goal5757_lane_probe_evidence_20260811.tar.gz"
ARCHIVE_TWIN = ROOT / "history/internal_docs/goal5757_lane_probe_evidence_twin_20260811.tar.gz"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    manifest = load(EVIDENCE / "MANIFEST.json")
    members = [path for path in EVIDENCE.rglob("*") if path.is_file() and path.name != "MANIFEST.json"]
    assert len(members) == manifest["payload_count"]
    assert sum(path.stat().st_size for path in members) == manifest["payload_bytes"]
    registered = {item["path"]: item for item in manifest["payloads"]}
    assert set(registered) == {path.relative_to(EVIDENCE).as_posix() for path in members}
    for path in members:
        item = registered[path.relative_to(EVIDENCE).as_posix()]
        assert item["bytes"] == path.stat().st_size
        assert item["sha256"] == sha(path)
    assert ARCHIVE.read_bytes() == ARCHIVE_TWIN.read_bytes()
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        archived = [item for item in archive.getmembers() if item.isfile()]
        assert len(archived) == len(members) + 1
        for item in archived:
            assert item.name.startswith("goal5757_lane_probe_evidence/")
            relative = item.name.split("/", 1)[1]
            extracted = archive.extractfile(item)
            assert extracted is not None
            assert extracted.read() == (EVIDENCE / relative).read_bytes()

    matrix = load(EVIDENCE / "MATRIX.json")
    assert matrix["paper_app_count"] == 9
    assert matrix["lane_count"] == 13
    assert matrix["classification_counts"] == {
        "SUPPORTED_NOW": 1,
        "PARTNER_ONLY_GAP": 0,
        "MISSING_GENERIC_SEMANTIC": 12,
    }
    assert all(value is False for value in matrix["claim_boundary"].values())

    results = []
    for row in matrix["results"]:
        path = EVIDENCE / row["result_file"]
        assert sha(path) == row["result_sha256"]
        payload = load(path)
        assert validate_lane_probe(payload).value == row["classification"]
        assert payload["app_id"] == row["app_id"]
        assert payload["lane_id"] == row["lane_id"]
        paper_path = EVIDENCE / "paper_contracts" / f"{payload['app_id']}__{payload['lane_id'].replace('.', '_')}.json"
        paper = load(paper_path)
        if row["classification"] != LaneClassification.SUPPORTED_NOW.value:
            assert payload["paper_semantic_evidence_sha256"] == paper["paper_semantic_evidence_sha256"]
            counterexamples = list((EVIDENCE / "counterexamples").glob(f"{payload['app_id']}__{payload['lane_id'].replace('.', '_')}.json"))
            assert len(counterexamples) == 1
            assert sha(counterexamples[0]) == payload["minimal_counterexample_sha256"]
        results.append(payload)

    supported = [item for item in results if item["classification"] == "SUPPORTED_NOW"]
    assert [(item["app_id"], item["lane_id"]) for item in supported] == [
        ("particle_tracking", "tetrahedral_face_point_location_and_boundary_detection")
    ]
    particle = supported[0]
    partner = EVIDENCE / "partner/particle_tracking_partner_preflight.json"
    target = EVIDENCE / "partner/particle_tracking_target_compile_preflight.json"
    assert particle["partner_preflight_sha256"] == sha(partner)
    assert particle["target_compile_preflight_sha256"] == sha(target)
    goal5756 = ROOT / "history/internal_docs/goal5756_builtin_triangle_runtime_and_home_result_20260811.json"
    assert load(partner)["goal5756_result_sha256"] == sha(goal5756)
    assert load(target)["goal5756_result_sha256"] == sha(goal5756)
    goal5756_data = load(goal5756)
    assert goal5756_data["functional_result"]["behavioral_executor"] == "optix_traversal_observed"
    assert goal5756_data["functional_result"]["cpu_device_differential_exact"] is True

    # Recompile every successful fragment from the evidence source and compare
    # the exact callback identity.  This uses the frozen V4 frontend, not a
    # submitted result digest.
    fragment_specs = {
        "sphere_nearest": (generation._sphere_manifest if hasattr(generation, "_sphere_manifest") else None),
        "box_overlap": generation._box_manifest,
        "directed_segment": generation._segment_manifest,
    }
    from tests.goal5750_v4_callback_ir_test import manifest as sphere_manifest
    fragment_specs["sphere_nearest"] = sphere_manifest
    for name, manifest_factory in fragment_specs.items():
        source = (EVIDENCE / "sources" / f"{name}.py").read_text(encoding="utf-8")
        observed = compile_callback_source(source, manifest_factory())
        recorded = load(EVIDENCE / "fragments" / f"{name}_callback_ir.json")
        assert observed.ir_sha256 == recorded["verified"]["ir_sha256"]
        assert observed.effect_digest == recorded["verified"]["effect_digest"]

    # Both early failures are reproduced through the actual frozen frontend.
    early = [item for item in results if item["fail_closed_stage"] == "frontend"]
    assert len(early) == 2
    for item in early:
        source_path = next((EVIDENCE / "sources").glob(
            f"failure__{item['app_id']}__{item['lane_id'].replace('.', '_')}.py"))
        manifest_factory = generation._box_manifest if item["app_id"] == "rt_barneshut" else generation._triangle_manifest
        try:
            compile_callback_source(source_path.read_text(encoding="utf-8"), manifest_factory())
        except CallbackVerificationError as error:
            assert error.code == item["fail_closed_code"] == "call_forbidden"
        else:
            raise AssertionError(f"frontend failure no longer fails: {item['lane_id']}")

    # The one shared built-in-triangle schema gap is reproduced, not inferred
    # from a grep.  It supports RayDB and both Triangle Counting dispositions.
    triangle_source = (EVIDENCE / "sources/triangle_count.py").read_text(encoding="utf-8")
    triangle_callback, _ = generation._program_evidence(
        triangle_source, generation._triangle_manifest(), generation.GeometryFamily.BUILTIN_TRIANGLE)
    code, _, _ = generation._triangle_schema_failure(triangle_callback)
    assert code == "required_semantic"
    typed_rows = [item for item in results if item["fail_closed_stage"] == "typed_schema"]
    assert len(typed_rows) == 3 and all(item["fail_closed_code"] == code for item in typed_rows)

    canonical_rows = [item for item in results if item["fail_closed_stage"] == "canonical_plan"]
    assert len(canonical_rows) == 7
    for item in canonical_rows:
        try:
            require_complete_lane(
                item["lane_id"],
                fragment_capabilities(geometry_family="custom_aabb", has_any_hit=True),
            )
        except LaneSemanticCoverageError as error:
            assert error.code == item["fail_closed_code"]
        else:
            raise AssertionError(f"canonical lane unexpectedly covered: {item['lane_id']}")

    # Re-run all previously frozen guards.  A coverage result is invalid if it
    # drifted the Goal5756 core or the pre-support contracts.
    verifier_names = (
        "goal5757_verify_core_freeze.py",
        "goal5757_verify_roster_gate.py",
        "goal5757_verify_roster_amendment_a1.py",
        "goal5757_verify_lane_contract_freeze.py",
        "goal5757_verify_capability_vocabulary.py",
    )
    for name in verifier_names:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / name)], cwd=ROOT,
            check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        if completed.returncode:
            raise AssertionError(f"{name} failed:\n{completed.stdout}")

    print(json.dumps({
        "status": "PASS",
        "manifest_payload_count": manifest["payload_count"],
        "manifest_payload_bytes": manifest["payload_bytes"],
        "archive_sha256": sha(ARCHIVE),
        "archive_twin_identical": True,
        "paper_apps": matrix["paper_app_count"],
        "lanes": matrix["lane_count"],
        "classifications": matrix["classification_counts"],
        "core_and_contract_verifiers": len(verifier_names),
        "frontend_failures_reproduced": len(early),
        "typed_schema_failures_reproduced": len(typed_rows),
        "canonical_plan_failures_reproduced": len(canonical_rows),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
