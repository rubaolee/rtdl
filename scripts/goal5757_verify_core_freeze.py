from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "history/internal_docs/goal5757_v4_core_freeze_manifest_20260811.json"
SUCCESSOR = ROOT / "history/internal_docs/goal5759_v4_core_successor_manifest_20260812.json"
SUCCESSOR_M2 = ROOT / "history/internal_docs/goal5760_v4_core_successor_manifest_20260812.json"
SUCCESSOR_M3 = ROOT / "history/internal_docs/goal5761_v4_core_successor_manifest_20260812.json"
SUCCESSOR_M4 = ROOT / "history/internal_docs/goal5762_v4_core_successor_manifest_20260812.json"
SUCCESSOR_M5 = ROOT / "history/internal_docs/goal5763_v4_core_successor_manifest_20260812.json"
SUCCESSOR_M6 = ROOT / "history/internal_docs/goal5764_v4_core_successor_manifest_20260812.json"
SUCCESSOR_5769 = ROOT / "history/internal_docs/goal5769_v4_core_successor_manifest_20260812.json"
SUCCESSOR_5773 = ROOT / "history/internal_docs/goal5773_v4_core_successor_manifest_20260813.json"


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert payload["schema"] == "rtdl.goal5757.v4_core_freeze.v1"
    assert payload["file_count"] == len(payload["files"]) == 19
    failures: list[dict[str, object]] = []
    baseline_rows = {str(row["path"]): row for row in payload["files"]}
    successor_rows: dict[str, dict[str, object]] = {}
    successor_manifests: list[str] = []
    seen_successor_paths: set[str] = set()
    goal5773 = None
    goal5773_added_replacements: dict[str, tuple[str, str]] = {}
    if SUCCESSOR_5773.is_file():
        goal5773 = json.loads(SUCCESSOR_5773.read_text(encoding="utf-8"))
        if goal5773.get("schema") != "rtdl.goal5773.v4_core_successor_manifest.v1" \
                or goal5773.get("baseline_manifest_sha256") != hashlib.sha256(
                    MANIFEST.read_bytes()).hexdigest() \
                or goal5773.get("predecessor_successor_manifest_sha256") \
                != hashlib.sha256(SUCCESSOR_5769.read_bytes()).hexdigest() \
                or goal5773.get("goal5769_result_replaced") is not False:
            raise RuntimeError("Goal5773 successor manifest does not bind its chain")
        goal5773_added_replacements = {
            str(path): (str(before), str(after))
            for path, before, after in goal5773[
                "authorized_added_module_replacements"]
        }

    def verify_added(path: str, expected_sha: str, label: str) -> None:
        product = ROOT / path
        accepted = expected_sha
        replacement = goal5773_added_replacements.get(path)
        if replacement is not None:
            if replacement[0] != expected_sha:
                raise RuntimeError(f"Goal5773 {label} predecessor mismatch")
            accepted = replacement[1]
        if not product.is_file() \
                or hashlib.sha256(product.read_bytes()).hexdigest() != accepted:
            raise RuntimeError(f"{label} added product module identity mismatch")
    if SUCCESSOR.is_file():
        successor = json.loads(SUCCESSOR.read_text(encoding="utf-8"))
        if successor.get("schema") != "rtdl.goal5759.v4_core_successor_manifest.v1" \
                or successor.get("baseline_manifest_sha256") != hashlib.sha256(
                    MANIFEST.read_bytes()).hexdigest():
            raise RuntimeError("Goal5759 successor manifest does not bind the baseline")
        successor_rows = {
            str(row["path"]): row for row in successor["authorized_replacements"]
        }
        if len(successor_rows) != len(successor["authorized_replacements"]):
            raise RuntimeError("duplicate Goal5759 successor path")
        successor_manifests.append(str(SUCCESSOR.relative_to(ROOT)))
    if SUCCESSOR_M2.is_file():
        m2 = json.loads(SUCCESSOR_M2.read_text(encoding="utf-8"))
        if m2.get("schema") != "rtdl.goal5760.v4_core_successor_manifest.v1" \
                or m2.get("baseline_manifest_sha256") != hashlib.sha256(
                    MANIFEST.read_bytes()).hexdigest() \
                or m2.get("predecessor_successor_manifest_sha256") \
                != hashlib.sha256(SUCCESSOR.read_bytes()).hexdigest():
            raise RuntimeError("Goal5760 successor manifest does not bind its chain")
        m2_rows = {
            str(row["path"]): row for row in m2["authorized_replacements"]
        }
        if len(m2_rows) != len(m2["authorized_replacements"]):
            raise RuntimeError("duplicate Goal5760 successor path")
        for path, row in m2_rows.items():
            predecessor = successor_rows.get(path)
            if predecessor is None \
                    or row["predecessor_sha256"] != predecessor["successor_sha256"]:
                raise RuntimeError(
                    "Goal5760 successor row does not bind Goal5759 identity")
            successor_rows[path] = {
                "path": path,
                "baseline_sha256": predecessor["baseline_sha256"],
                "successor_sha256": row["successor_sha256"],
                "successor_size_bytes": row["successor_size_bytes"],
            }
        successor_manifests.append(str(SUCCESSOR_M2.relative_to(ROOT)))
    if SUCCESSOR_M3.is_file():
        m3 = json.loads(SUCCESSOR_M3.read_text(encoding="utf-8"))
        if m3.get("schema") != "rtdl.goal5761.v4_core_successor_manifest.v1" \
                or m3.get("baseline_manifest_sha256") != hashlib.sha256(
                    MANIFEST.read_bytes()).hexdigest() \
                or m3.get("predecessor_successor_manifest_sha256") \
                != hashlib.sha256(SUCCESSOR_M2.read_bytes()).hexdigest():
            raise RuntimeError("Goal5761 successor manifest does not bind its chain")
        m3_rows = {
            str(row["path"]): row for row in m3["authorized_replacements"]
        }
        if len(m3_rows) != len(m3["authorized_replacements"]):
            raise RuntimeError("duplicate Goal5761 successor path")
        for path, row in m3_rows.items():
            predecessor = successor_rows.get(path)
            if predecessor is None \
                    or row["predecessor_sha256"] != predecessor["successor_sha256"]:
                raise RuntimeError(
                    "Goal5761 successor row does not bind Goal5760 identity")
            successor_rows[path] = {
                "path": path,
                "baseline_sha256": predecessor["baseline_sha256"],
                "successor_sha256": row["successor_sha256"],
                "successor_size_bytes": row["successor_size_bytes"],
            }
        successor_manifests.append(str(SUCCESSOR_M3.relative_to(ROOT)))
    if SUCCESSOR_M4.is_file():
        m4 = json.loads(SUCCESSOR_M4.read_text(encoding="utf-8"))
        if m4.get("schema") != "rtdl.goal5762.v4_core_successor_manifest.v1" \
                or m4.get("baseline_manifest_sha256") != hashlib.sha256(
                    MANIFEST.read_bytes()).hexdigest() \
                or m4.get("predecessor_successor_manifest_sha256") \
                != hashlib.sha256(SUCCESSOR_M3.read_bytes()).hexdigest() \
                or m4.get("authorized_replacements") != []:
            raise RuntimeError("Goal5762 successor manifest does not bind its chain")
        for path, expected_sha in m4.get("added_product_modules", []):
            verify_added(str(path), str(expected_sha), "Goal5762")
        successor_manifests.append(str(SUCCESSOR_M4.relative_to(ROOT)))
    if SUCCESSOR_M5.is_file():
        m5 = json.loads(SUCCESSOR_M5.read_text(encoding="utf-8"))
        if m5.get("schema") != "rtdl.goal5763.v4_core_successor_manifest.v1" \
                or m5.get("baseline_manifest_sha256") != hashlib.sha256(
                    MANIFEST.read_bytes()).hexdigest() \
                or m5.get("predecessor_successor_manifest_sha256") \
                != hashlib.sha256(SUCCESSOR_M4.read_bytes()).hexdigest() \
                or m5.get("authorized_replacements") != []:
            raise RuntimeError("Goal5763 successor manifest does not bind its chain")
        for path, expected_sha in m5.get("added_product_modules", []):
            verify_added(str(path), str(expected_sha), "Goal5763")
        successor_manifests.append(str(SUCCESSOR_M5.relative_to(ROOT)))
    if SUCCESSOR_M6.is_file():
        m6 = json.loads(SUCCESSOR_M6.read_text(encoding="utf-8"))
        if m6.get("schema") != "rtdl.goal5764.v4_core_successor_manifest.v1" \
                or m6.get("baseline_manifest_sha256") != hashlib.sha256(
                    MANIFEST.read_bytes()).hexdigest() \
                or m6.get("predecessor_successor_manifest_sha256") \
                != hashlib.sha256(SUCCESSOR_M5.read_bytes()).hexdigest() \
                or m6.get("authorized_replacements") != []:
            raise RuntimeError("Goal5764 successor manifest does not bind its chain")
        for path, expected_sha in m6.get("added_product_modules", []):
            verify_added(str(path), str(expected_sha), "Goal5764")
        consumer_path, consumer_sha = m6["real_second_consumer"]
        consumer = ROOT / consumer_path
        if not consumer.is_file() \
                or hashlib.sha256(consumer.read_bytes()).hexdigest() != consumer_sha:
            raise RuntimeError("Goal5764 second consumer identity mismatch")
        successor_manifests.append(str(SUCCESSOR_M6.relative_to(ROOT)))
    if SUCCESSOR_5769.is_file():
        current = json.loads(SUCCESSOR_5769.read_text(encoding="utf-8"))
        if current.get("schema") != "rtdl.goal5769.v4_core_successor_manifest.v1" \
                or current.get("baseline_manifest_sha256") != hashlib.sha256(
                    MANIFEST.read_bytes()).hexdigest() \
                or current.get("predecessor_successor_manifest_sha256") \
                != hashlib.sha256(SUCCESSOR_M6.read_bytes()).hexdigest():
            raise RuntimeError("Goal5769 successor manifest does not bind its chain")
        current_rows = {
            str(row["path"]): row for row in current["authorized_replacements"]
        }
        if len(current_rows) != len(current["authorized_replacements"]):
            raise RuntimeError("duplicate Goal5769 successor path")
        for path, row in current_rows.items():
            baseline = baseline_rows.get(path)
            if baseline is None:
                raise RuntimeError("Goal5769 replacement is outside frozen core")
            predecessor = successor_rows.get(path)
            predecessor_sha = (
                baseline["sha256"] if predecessor is None
                else predecessor["successor_sha256"]
            )
            if row["predecessor_sha256"] != predecessor_sha:
                raise RuntimeError(
                    "Goal5769 successor row does not bind predecessor identity")
            successor_rows[path] = {
                "path": path,
                "baseline_sha256": baseline["sha256"],
                "successor_sha256": row["successor_sha256"],
                "successor_size_bytes": row["successor_size_bytes"],
            }
        successor_manifests.append(str(SUCCESSOR_5769.relative_to(ROOT)))
    if goal5773 is not None:
        current_rows = {
            str(row["path"]): row for row in goal5773["authorized_replacements"]
        }
        if len(current_rows) != len(goal5773["authorized_replacements"]):
            raise RuntimeError("duplicate Goal5773 successor path")
        for path, row in current_rows.items():
            baseline = baseline_rows.get(path)
            if baseline is None:
                raise RuntimeError("Goal5773 baseline replacement is outside frozen core")
            predecessor = successor_rows.get(path)
            predecessor_sha = (
                baseline["sha256"] if predecessor is None
                else predecessor["successor_sha256"]
            )
            if row["predecessor_sha256"] != predecessor_sha:
                raise RuntimeError("Goal5773 successor row does not bind predecessor")
            successor_rows[path] = {
                "path": path,
                "baseline_sha256": baseline["sha256"],
                "successor_sha256": row["successor_sha256"],
                "successor_size_bytes": row["successor_size_bytes"],
            }
        for path, expected_sha in goal5773["added_product_modules"]:
            product = ROOT / str(path)
            if not product.is_file() \
                    or hashlib.sha256(product.read_bytes()).hexdigest() != expected_sha:
                raise RuntimeError("Goal5773 added product module identity mismatch")
        for path, predecessor_sha, successor_sha in goal5773[
                "external_dependency_replacements"]:
            product = ROOT / str(path)
            if not product.is_file() \
                    or hashlib.sha256(product.read_bytes()).hexdigest() != successor_sha:
                raise RuntimeError("Goal5773 external dependency identity mismatch")
            if predecessor_sha == successor_sha:
                raise RuntimeError("Goal5773 external dependency did not change")
        successor_manifests.append(str(SUCCESSOR_5773.relative_to(ROOT)))
    for row in payload["files"]:
        path = ROOT / row["path"]
        if not path.is_file():
            failures.append({"path": row["path"], "error": "missing"})
            continue
        data = path.read_bytes()
        observed = hashlib.sha256(data).hexdigest()
        accepted_sha = row["sha256"]
        accepted_size = row["size_bytes"]
        successor_row = successor_rows.get(row["path"])
        if successor_row is not None:
            seen_successor_paths.add(row["path"])
            if successor_row["baseline_sha256"] != row["sha256"]:
                raise RuntimeError("successor row does not bind baseline path identity")
            accepted_sha = successor_row["successor_sha256"]
            accepted_size = successor_row["successor_size_bytes"]
        if observed != accepted_sha or len(data) != accepted_size:
            failures.append({
                "path": row["path"],
                "error": "identity_mismatch",
                "expected_sha256": accepted_sha,
                "observed_sha256": observed,
                "expected_size": accepted_size,
                "observed_size": len(data),
            })
    if seen_successor_paths != set(successor_rows):
        raise RuntimeError("successor manifest names a non-baseline path")
    print(json.dumps({
        "schema": "rtdl.goal5757.v4_core_freeze_check.v1",
        "baseline_commit": payload["baseline_commit"],
        "checked": len(payload["files"]),
        "successor_manifest_applied": bool(successor_rows),
        "successor_manifests": successor_manifests,
        "authorized_successor_replacement_count": len(successor_rows),
        "failures": failures,
        "status": "PASS" if not failures else "FAIL_CLOSED",
    }, sort_keys=True, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
