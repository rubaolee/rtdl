#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / "CAPSULE_MANIFEST.json").read_text(encoding="utf-8"))
expected = manifest["payloads"]
required_policy = {
    "status": "GOAL5836_COMPLETE__POST_A1_STRICT_AUDIT_CLAIM_NARROWED",
    "goal5835_strict_classification":
        "BOUNDED_APP_SEMANTIC_PROJECTION_WITH_INHERITED_TRUE_OPTIX_EVIDENCE",
    "goal5836_transaction_complete": True,
    "goal5836_successful_promotion_path_complete": False,
    "strict_audit_review_type": "INTERNAL_HOSTILE_SELF_AUDIT",
    "external_review_status": "DEFERRED_BY_OWNER_UNTIL_RETURN_FROM_TRAVEL",
    "external_review_count": 0,
    "consensus_claimed": False,
    "a2_reachable": False,
    "pod_authorized": False,
    "performance_authorized": False,
}
for key, value in required_policy.items():
    if manifest.get(key) != value:
        raise SystemExit(f"capsule policy mismatch: {key}")
optional_outer_capsule = {
    "history/internal_docs/goal5836_macbook_complete_handoff_capsule_20260831.tar.gz"
}


def is_environment_artifact(path: Path) -> bool:
    relative = path.relative_to(root)
    return (
        relative.parts[0] in {".git", ".venv-goal5836"}
        or "__pycache__" in relative.parts
        or ".pytest_cache" in relative.parts
        or any(part.endswith(".egg-info") for part in relative.parts)
        or path.name == ".DS_Store"
        or path.suffix in {".pyc", ".pyo"}
    )


actual_paths = {
    p.relative_to(root).as_posix() for p in root.rglob("*")
    if p.is_file()
    and p.name != "CAPSULE_MANIFEST.json"
    and not is_environment_artifact(p)
}
expected_paths = {row["path"] for row in expected}
if actual_paths - optional_outer_capsule != expected_paths:
    missing = sorted(expected_paths - actual_paths)
    extra = sorted(actual_paths - expected_paths - optional_outer_capsule)
    raise SystemExit(f"path-set mismatch missing={missing} extra={extra}")
for row in expected:
    path = root / row["path"]
    data = path.read_bytes()
    observed = hashlib.sha256(data).hexdigest()
    if len(data) != row["bytes"] or observed != row["sha256"]:
        raise SystemExit(f"payload mismatch: {row['path']}")
print(json.dumps({
    "status": "PASS__GOAL5836_MACBOOK_CAPSULE",
    "payload_count": len(expected),
    "payload_bytes": sum(row["bytes"] for row in expected),
}, sort_keys=True))
