#!/usr/bin/env python3
"""Bind independently verified Goal5801 clean-install bytes for Goal5802."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from experiments.goal5802_premeasurement import contract as premeasurement_contract
from scripts import goal5801_a3_verify_clean_install as clean_verifier
from scripts import goal5801_a3_verify_native_custody as custody_verifier


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_new(path: Path, value: object) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def _git(repository_root: Path, *arguments: str, text: bool = False):
    completed = subprocess.run(
        ["git", "-C", str(repository_root), *arguments],
        capture_output=True, check=False, text=text)
    if completed.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(arguments)} failed: {completed.stderr!r}")
    return completed.stdout


def _verify_full_package_source(
        repository_root: Path, source_commit: str, source_tree: str,
        clean_root: Path, rows: list[object]) -> int:
    repository_root = repository_root.resolve(strict=True)
    observed_tree = _git(
        repository_root, "rev-parse", f"{source_commit}^{{tree}}",
        text=True).strip()
    if observed_tree != source_tree:
        raise RuntimeError("source commit does not own declared source tree")
    git_paths = set(_git(
        repository_root, "ls-tree", "-r", "--name-only", source_commit,
        "--", "src/rtdsl", text=True).splitlines())
    saved: dict[str, dict[str, object]] = {}
    for raw in rows:
        if not isinstance(raw, dict):
            raise RuntimeError("clean-install input identity row malformed")
        role = str(raw.get("role"))
        if not role.startswith("source_package/"):
            continue
        relative = role.removeprefix("source_package/")
        git_path = f"src/rtdsl/{relative}"
        if git_path in saved:
            raise RuntimeError(f"duplicate clean saved package source: {git_path}")
        saved[git_path] = raw
    if not saved or set(saved) != git_paths:
        missing = sorted(git_paths - set(saved))
        extra = sorted(set(saved) - git_paths)
        raise RuntimeError({
            "clean_saved_package_source_set_differs": True,
            "missing_first_20": missing[:20], "extra_first_20": extra[:20],
            "git_count": len(git_paths), "saved_count": len(saved),
        })
    for git_path, raw in saved.items():
        blob = _git(repository_root, "show", f"{source_commit}:{git_path}")
        saved_path = clean_root / str(raw["saved_path"])
        if saved_path.is_symlink() or not saved_path.is_file():
            raise RuntimeError(f"clean saved source is not regular: {git_path}")
        saved_bytes = saved_path.read_bytes()
        if blob != saved_bytes or hashlib.sha256(blob).hexdigest() != raw["sha256"]:
            raise RuntimeError(f"clean saved source differs from Git blob: {git_path}")
    return len(saved)


def _verify_goal5802_candidate_manifest(value: object) -> None:
    """Forbid the legacy implicit-threshold candidate at Goal5802's gate."""

    if not isinstance(value, dict) \
            or value.get("schema") \
            != "rtdl.goal5801.lx1_untimed_candidate_manifest.v2":
        raise RuntimeError(
            "Goal5802 requires the explicit-threshold candidate manifest v2")
    relation = value.get("relation_protocol")
    expected = {
            "capacity": 4096,
            "minimum_overlap_boundary": "inclusive",
            "minimum_overlap_f32": 1.0,
            "minimum_overlap_f32_bits": 0x3F800000,
    }
    if not isinstance(relation, dict) \
            or set(relation) != set(expected) \
            or type(relation.get("capacity")) is not int \
            or type(relation.get("minimum_overlap_f32")) is not float \
            or type(relation.get("minimum_overlap_f32_bits")) is not int \
            or relation != expected:
        raise RuntimeError(
            "Goal5802 relation task requires exact capacity-4096 threshold-1.0")


def build_binding(clean_root: Path, *, source_commit: str,
                  source_tree: str, repository_root: Path,
                  standalone_verifier: Path, native_custody_root: Path,
                  standalone_native_custody_verifier: Path,
                  qualification_only_expected_trust_root_file_sha256:
                  str | None = None) -> dict[str, object]:
    if clean_root.is_symlink():
        raise RuntimeError("clean-install root must not be a symlink")
    clean_root = clean_root.resolve(strict=True)
    if standalone_verifier.is_symlink():
        raise RuntimeError("standalone clean verifier must not be a symlink")
    standalone_verifier = standalone_verifier.resolve(strict=True)
    imported_verifier = Path(clean_verifier.__file__).resolve(strict=True)
    if not standalone_verifier.is_file() \
            or standalone_verifier.read_bytes() != imported_verifier.read_bytes():
        raise RuntimeError(
            "standalone clean verifier differs from binder-imported verifier")
    if native_custody_root.is_symlink():
        raise RuntimeError("native-custody root must not be a symlink")
    native_custody_root = native_custody_root.resolve(strict=True)
    if not native_custody_root.is_dir():
        raise RuntimeError("native-custody root must be a directory")
    if standalone_native_custody_verifier.is_symlink():
        raise RuntimeError("standalone native-custody verifier must not be a symlink")
    standalone_native_custody_verifier = (
        standalone_native_custody_verifier.resolve(strict=True))
    imported_custody_verifier = Path(custody_verifier.__file__).resolve(strict=True)
    if not standalone_native_custody_verifier.is_file() \
            or standalone_native_custody_verifier.read_bytes() \
            != imported_custody_verifier.read_bytes():
        raise RuntimeError(
            "standalone native-custody verifier differs from binder-imported verifier")
    verified = clean_verifier.verify(
        clean_root,
        qualification_only_expected_trust_root_file_sha256=(
            qualification_only_expected_trust_root_file_sha256))
    standalone_command = [
        sys.executable, str(standalone_verifier), str(clean_root)]
    if qualification_only_expected_trust_root_file_sha256 is not None:
        standalone_command.extend([
            "--qualification-only-expected-trust-root-file-sha256",
            qualification_only_expected_trust_root_file_sha256,
        ])
    standalone = subprocess.run(
        standalone_command, capture_output=True, check=False)
    try:
        standalone_result = json.loads(standalone.stdout)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError("standalone clean verifier output is not JSON") from error
    if standalone.returncode != 0 or standalone.stderr \
            or standalone_result != verified:
        raise RuntimeError("standalone and imported clean verification differ")
    custody_verified = custody_verifier.verify(native_custody_root)
    custody_standalone = subprocess.run(
        [sys.executable, str(standalone_native_custody_verifier),
         str(native_custody_root)], capture_output=True, check=False)
    try:
        custody_standalone_result = json.loads(custody_standalone.stdout)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(
            "standalone native-custody verifier output is not JSON") from error
    if custody_standalone.returncode != 0 or custody_standalone.stderr \
            or custody_standalone_result != custody_verified:
        raise RuntimeError(
            "standalone and imported native-custody verification differ")
    run = json.loads((clean_root / "run.json").read_text(encoding="utf-8"))
    rows = run.get("input_identities")
    if not isinstance(rows, list):
        raise RuntimeError("clean-install input identity rows absent")
    by_role = {str(row.get("role")): row for row in rows if isinstance(row, dict)}
    if len(by_role) != len(rows):
        raise RuntimeError("clean-install input roles duplicate or malformed")
    source_file_count = _verify_full_package_source(
        repository_root, source_commit, source_tree, clean_root, rows)
    clean_result = json.loads(
        (clean_root / "result.json").read_text(encoding="utf-8"))
    if not isinstance(clean_result, dict) \
            or type(clean_result.get("wheel_rtdsl_file_count")) is not int \
            or clean_result["wheel_rtdsl_file_count"] != source_file_count \
            or not isinstance(
                clean_result.get("wheel_rtdsl_tree_sha256"), str) \
            or len(clean_result["wheel_rtdsl_tree_sha256"]) != 64:
        raise RuntimeError("clean-install package-tree identity absent")

    def row(role: str) -> dict[str, object]:
        value = by_role.get(role)
        if value is None:
            raise RuntimeError(f"clean-install role absent: {role}")
        saved = clean_root / str(value["saved_path"])
        if not saved.is_file() or _sha(saved) != value["sha256"]:
            raise RuntimeError(f"clean-install saved role differs: {role}")
        return value

    def bound_json(role: str) -> dict[str, object]:
        identity = row(role)
        saved = clean_root / str(identity["saved_path"])
        raw = saved.read_bytes()
        if hashlib.sha256(raw).hexdigest() != identity["sha256"]:
            raise RuntimeError(f"clean-install saved role changed while read: {role}")
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise RuntimeError(f"clean-install JSON role invalid: {role}") from error
        if not isinstance(value, dict):
            raise RuntimeError(f"clean-install JSON role not an object: {role}")
        return value

    candidate_manifest = bound_json("candidate_manifest")
    _verify_goal5802_candidate_manifest(candidate_manifest)
    clean_verifier._verify_candidate_relation_protocol(
        candidate_manifest, bound_json("relation_artifact"))

    custody = json.loads(
        (native_custody_root / "custody.json").read_text(encoding="utf-8"))
    custody_source = json.loads(
        (native_custody_root / "source/manifest.json").read_text(
            encoding="utf-8"))
    if not isinstance(custody, dict) or not isinstance(custody_source, dict):
        raise RuntimeError("native-custody authority documents invalid")
    if custody_verified.get("status") \
            != "PASS__INDEPENDENT_NATIVE_CUSTODY_VERIFICATION" \
            or custody_verified.get("source_commit") != source_commit \
            or custody_verified.get("source_tree") != source_tree \
            or custody_verified.get("origin_commit") != source_commit \
            or custody_verified.get("origin_tree") != source_tree \
            or custody.get("source_commit") != source_commit \
            or custody.get("source_tree") != source_tree \
            or custody.get("origin_commit") != source_commit \
            or custody.get("origin_tree") != source_tree \
            or custody_source.get("source_commit") != source_commit \
            or custody_source.get("source_tree") != source_tree \
            or custody_source.get("origin_commit") != source_commit \
            or custody_source.get("origin_tree") != source_tree:
        raise RuntimeError(
            "native custody does not bind the exact final Git commit/tree")
    clean_native = clean_root / str(row("native")["saved_path"])
    custody_native = native_custody_root / "native/librtdl_optix.so"
    if custody_verified.get("native_sha256") != row("native")["sha256"] \
            or custody.get("native_sha256") != row("native")["sha256"] \
            or custody_native.read_bytes() != clean_native.read_bytes():
        raise RuntimeError(
            "native custody binary differs from final clean-install native")

    relation_descriptor = bound_json("relation_descriptor")
    triangle_descriptor = bound_json("triangle_descriptor")
    relation_authority = bound_json("relation_authority")
    triangle_authority = bound_json("triangle_authority")
    for label, authority in (
            ("relation", relation_authority),
            ("triangle", triangle_authority)):
        identity = authority.get("executable_identity_sha256")
        if not isinstance(identity, str) or len(identity) != 64 \
                or any(ch not in "0123456789abcdef" for ch in identity):
            raise RuntimeError(f"{label} executable identity absent")
    init_row = row("source_package/__init__.py")
    module_row = row("source_package/v4_rtdlexe.py")
    binding = {
        "schema": "rtdl.goal5802.final_clean_rtdlexe_binding.v4",
        "status": "PASS__FINAL_CLEAN_INSTALLED_RTLEXE",
        "clean_install_verifier_status": verified["status"],
        "clean_install_verifier_sha256": _sha(standalone_verifier),
        "clean_install_run_sha256": _sha(clean_root / "run.json"),
        "clean_install_result_sha256": _sha(clean_root / "result.json"),
        "wheel_sha256": row("wheel")["sha256"],
        "native_sha256": row("native")["sha256"],
        "native_custody_verifier_status": custody_verified["status"],
        "native_custody_verifier_sha256": _sha(
            standalone_native_custody_verifier),
        "native_custody_manifest_sha256": _sha(
            native_custody_root / "manifest.json"),
        "native_custody_custody_sha256": _sha(
            native_custody_root / "custody.json"),
        "native_custody_source_file_count": custody_verified[
            "source_file_count"],
        "native_custody_dependency_file_count": custody_verified[
            "dependency_file_count"],
        "native_custody_toolchain_payload_count": custody_verified[
            "toolchain_payload_count"],
        "native_custody_source_commit": custody_verified["source_commit"],
        "native_custody_source_tree": custody_verified["source_tree"],
        "native_custody_hermetic_native_rebuild_claimed": custody_verified[
            "hermetic_native_rebuild_claimed"],
        "trust_root_sha256": row("trust_root")["sha256"],
        "trust_head_sha256": row("trust_head")["sha256"],
        "trust_predecessor_package_sha256": row(
            "trust_predecessor_package")["sha256"],
        "trust_package_sha256": row("trust_package")["sha256"],
        "triangle_artifact_sha256": row("triangle_artifact")["sha256"],
        "triangle_authority_sha256": row("triangle_authority")["sha256"],
        "triangle_deployment_id": triangle_descriptor["deployment_id"],
        "triangle_executable_identity_sha256": triangle_authority[
            "executable_identity_sha256"],
        "relation_artifact_sha256": row("relation_artifact")["sha256"],
        "relation_authority_sha256": row("relation_authority")["sha256"],
        "relation_deployment_id": relation_descriptor["deployment_id"],
        "relation_executable_identity_sha256": relation_authority[
            "executable_identity_sha256"],
        "source_commit": source_commit,
        "source_tree": source_tree,
        "source_package_file_count": source_file_count,
        "rtdsl_package_file_count": clean_result["wheel_rtdsl_file_count"],
        "rtdsl_package_tree_sha256": clean_result[
            "wheel_rtdsl_tree_sha256"],
        "rtdsl_init_sha256": init_row["sha256"],
        "rtdlexe_module_sha256": module_row["sha256"],
    }
    # The successor forecast treats this v4 object as an exact closed schema.
    # Validate it at the producer boundary so a new field cannot survive until
    # a later stage (or silently change the product identity).
    validated = premeasurement_contract._validate_product_binding(
        binding, repository_root.resolve(strict=True))
    if validated != binding:
        raise RuntimeError("frozen product-binding contract projection differs")
    return binding


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean-root", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-tree", required=True)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--standalone-verifier", type=Path, required=True)
    parser.add_argument(
        "--qualification-only-expected-trust-root-file-sha256")
    parser.add_argument("--native-custody-root", type=Path, required=True)
    parser.add_argument(
        "--standalone-native-custody-verifier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for label, value in (
            ("source commit", args.source_commit),
            ("source tree", args.source_tree)):
        if len(value) != 40 or any(ch not in "0123456789abcdef" for ch in value):
            raise ValueError(f"{label} must be a lowercase SHA-1")
    binding = build_binding(
        args.clean_root, source_commit=args.source_commit,
        source_tree=args.source_tree, repository_root=args.repository_root,
        standalone_verifier=args.standalone_verifier,
        native_custody_root=args.native_custody_root,
        standalone_native_custody_verifier=(
            args.standalone_native_custody_verifier),
        qualification_only_expected_trust_root_file_sha256=(
            args.qualification_only_expected_trust_root_file_sha256))
    _write_new(args.output, binding)
    print(json.dumps(binding, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
