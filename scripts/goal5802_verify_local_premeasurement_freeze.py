#!/usr/bin/env python3
"""Independent entrypoint for the Goal5802 local freeze validator."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from experiments.goal5802_premeasurement.contract import validate_freeze
from scripts import goal5801_a3_verify_native_custody as custody_verifier
from scripts import goal5802_bind_final_clean_install as final_binder


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_native_custody_projection(
        binding: dict[str, object], native_custody_root: Path,
        standalone_verifier: Path) -> dict[str, object]:
    """Re-run custody verification and bind its actual bytes to the product.

    This is deliberately mandatory at the independent freeze entrypoint.  A
    syntactically coherent product-binding JSON is not evidence that its named
    Git commit, source archive, toolchain archive, or native binary exists.
    """

    if standalone_verifier.expanduser().is_symlink():
        raise RuntimeError("standalone native-custody verifier is a symlink")
    standalone = standalone_verifier.expanduser().resolve(strict=True)
    imported = Path(custody_verifier.__file__).resolve(strict=True)
    if not standalone.is_file() or standalone.read_bytes() != imported.read_bytes():
        raise RuntimeError(
            "standalone native-custody verifier differs from imported verifier")
    observed = custody_verifier.verify(native_custody_root)
    completed = subprocess.run(
        [sys.executable, str(standalone), str(native_custody_root)],
        capture_output=True, check=False)
    try:
        independently_observed = json.loads(completed.stdout)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(
            "standalone native-custody verifier output is not JSON") from error
    if completed.returncode != 0 or independently_observed != observed:
        raise RuntimeError(
            "imported and standalone native-custody verification differ")
    if observed.get("source_commit") != observed.get("origin_commit") \
            or observed.get("source_tree") != observed.get("origin_tree"):
        raise RuntimeError(
            "native-custody source identity is not the raw-proven origin identity")
    custody_root = native_custody_root.expanduser().resolve(strict=True)
    expected = {
        "native_custody_verifier_status": observed["status"],
        "native_custody_verifier_sha256": _sha(standalone),
        "native_custody_manifest_sha256": _sha(custody_root / "manifest.json"),
        "native_custody_custody_sha256": _sha(custody_root / "custody.json"),
        "native_custody_source_file_count": observed["source_file_count"],
        "native_custody_dependency_file_count": observed[
            "dependency_file_count"],
        "native_custody_toolchain_payload_count": observed[
            "toolchain_payload_count"],
        "native_custody_source_commit": observed["source_commit"],
        "native_custody_source_tree": observed["source_tree"],
        "source_commit": observed["origin_commit"],
        "source_tree": observed["origin_tree"],
        "native_custody_hermetic_native_rebuild_claimed": observed[
            "hermetic_native_rebuild_claimed"],
        "native_sha256": observed["native_sha256"],
    }
    for key, value in expected.items():
        if binding.get(key) != value:
            raise RuntimeError(
                f"product binding/native-custody projection differs: {key}")
    return {**observed,
            "outer_manifest_sha256": expected[
                "native_custody_manifest_sha256"]}


def verify_final_product_binding_from_evidence(
        binding: dict[str, object], *, clean_install_root: Path,
        repository_root: Path, standalone_clean_verifier: Path,
        native_custody_root: Path,
        standalone_native_custody_verifier: Path,
        qualification_only_expected_trust_root_file_sha256:
        str | None = None) -> dict[str, object]:
    """Rebuild the complete binding from the two mandatory evidence roots."""

    source_commit = binding.get("source_commit")
    source_tree = binding.get("source_tree")
    if not isinstance(source_commit, str) or not isinstance(source_tree, str):
        raise RuntimeError("product binding final Git identity absent")
    rebuilt = final_binder.build_binding(
        clean_install_root, source_commit=source_commit,
        source_tree=source_tree, repository_root=repository_root,
        standalone_verifier=standalone_clean_verifier,
        native_custody_root=native_custody_root,
        standalone_native_custody_verifier=(
            standalone_native_custody_verifier),
        qualification_only_expected_trust_root_file_sha256=(
            qualification_only_expected_trust_root_file_sha256))
    if rebuilt != binding:
        differing = sorted(
            key for key in set(rebuilt).union(binding)
            if rebuilt.get(key) != binding.get(key))
        raise RuntimeError(
            f"frozen product binding differs from evidence rebuild: {differing}")
    return rebuilt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--clean-install-root", type=Path, required=True)
    parser.add_argument(
        "--standalone-clean-install-verifier", type=Path, required=True)
    parser.add_argument(
        "--qualification-only-expected-trust-root-file-sha256")
    parser.add_argument("--native-custody-root", type=Path, required=True)
    parser.add_argument(
        "--standalone-native-custody-verifier", type=Path, required=True)
    args = parser.parse_args()
    value = json.loads(args.freeze.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Goal5802 freeze root is not an object")
    validate_freeze(value, args.root.resolve())
    binding = value.get("product_binding")
    if not isinstance(binding, dict):
        raise RuntimeError("Goal5802 product binding root is not an object")
    rebuilt = verify_final_product_binding_from_evidence(
        binding, clean_install_root=args.clean_install_root,
        repository_root=args.root.resolve(),
        standalone_clean_verifier=args.standalone_clean_install_verifier,
        native_custody_root=args.native_custody_root,
        standalone_native_custody_verifier=(
            args.standalone_native_custody_verifier),
        qualification_only_expected_trust_root_file_sha256=(
            args.qualification_only_expected_trust_root_file_sha256))
    custody = {
        key: rebuilt[key] for key in (
            "native_custody_verifier_status",
            "native_custody_verifier_sha256",
            "native_custody_manifest_sha256",
            "native_custody_custody_sha256",
            "native_custody_source_commit", "native_custody_source_tree",
            "native_custody_source_file_count",
            "native_custody_dependency_file_count",
            "native_custody_toolchain_payload_count",
            "native_custody_hermetic_native_rebuild_claimed",
            "native_sha256")}
    print(json.dumps({
        "status": "PASS__GOAL5802_LOCAL_FREEZE_VERIFIED",
        "freeze_sha256": value["freeze_sha256"],
        "worker_row_count": value["worker_row_count"],
        "formal_worker_zero": False,
        "registered_performance_timing_count": 0,
        "native_custody_projection": custody,
        "complete_product_binding_rebuilt_from_evidence": True,
        "complete_product_binding_sha256": hashlib.sha256(
            json.dumps(rebuilt, allow_nan=False, separators=(",", ":"),
                       sort_keys=True).encode("utf-8")).hexdigest(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
