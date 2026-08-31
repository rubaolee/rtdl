#!/usr/bin/env python3
"""Untimed Linux KAT for sealed native-image identity and glibc cache reuse."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl import physical_execution_provenance as provenance
from rtdsl import v4_rtdlexe as runtime


SCHEMA = "rtdl.goal5801.native_loader_identity_kat.v3"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8") + b"\n"


def _registry_absent(library: object) -> bool:
    with provenance._LOADED_PROVIDER_IDENTITIES_LOCK:
        return (
            id(library) not in provenance._LOADED_PROVIDER_IDENTITIES
            and id(library) not in provenance._AUDIT_ABI_REGISTERED
        )


def _mapped_image_rows(image_sha256: str) -> list[str]:
    needle = f"memfd:rtdl-native-{image_sha256[:16]}"
    return [
        row for row in Path("/proc/self/maps").read_text(
            encoding="utf-8").splitlines()
        if needle in row
    ]


def _load(path: Path):
    library = runtime._load_verified_native_file_descriptor(
        path,
        expected_sha256=_sha(path),
        code="RX032_NATIVE_IDENTITY_MISMATCH",
        identity_path="kat.native_library_path",
    )
    marker = library.marker
    marker.argtypes = []
    marker.restype = ctypes.c_int
    return library, int(marker())


def run(*, host_cc: Path, work_directory: Path, output: Path) -> dict[str, object]:
    if os.name != "posix" or not hasattr(os, "memfd_create"):
        raise RuntimeError("Linux memfd support is required")
    host_cc = host_cc.resolve(strict=True)
    work_directory.mkdir(parents=True, exist_ok=False)
    built: dict[str, Path] = {}
    for label, expected_marker in (("a", 111), ("b", 222)):
        source = work_directory / f"{label}.c"
        image = work_directory / f"{label}.so"
        source.write_bytes(
            f"int marker(void){{return {expected_marker};}}\n".encode("ascii"))
        command = [
            str(host_cc), "-shared", "-fPIC", str(source), "-o", str(image),
        ]
        completed = subprocess.run(
            command, check=False, capture_output=True, env={
                "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
            })
        if completed.returncode != 0:
            raise RuntimeError(
                f"host compiler failed for {label}: {completed.stderr!r}")
        built[label] = image

    a1, marker_a1 = _load(built["a"])
    a2, marker_a2 = _load(built["a"])
    digest_a = _sha(built["a"])
    a_before = {
        "source_sha256": _sha(work_directory / "a.c"),
        "image_sha256": digest_a,
        "observed_markers": [marker_a1, marker_a2],
        "shared_entry_identity": (
            a1._rtdl_native_cache_entry_identity
            == a2._rtdl_native_cache_entry_identity),
        "shared_handle": a1._handle == a2._handle,
        "shared_descriptor": (
            a1._rtdl_native_image_fd == a2._rtdl_native_image_fd),
        "shared_alias": (
            a1._rtdl_native_loader_alias == a2._rtdl_native_loader_alias),
        "lease_ids_distinct": (
            a1._rtdl_native_cache_lease_id
            != a2._rtdl_native_cache_lease_id),
        "entry_identity": a1._rtdl_native_cache_entry_identity,
        "loader_handle": int(a1._handle),
        "sealed_image_fd": int(a1._rtdl_native_image_fd),
        "sealed_image_seals": int(a1._rtdl_native_image_seals),
        "loader_alias": str(a1._rtdl_native_loader_alias),
        "active_lease_count": int(a1._rtdl_native_cache_active_lease_count),
        "acquisition_count": int(a1._rtdl_native_cache_acquisition_count),
        "mapped_rows": _mapped_image_rows(digest_a),
    }
    runtime._release_native_library_image(a1)
    a_after_first_release = {
        "released_lease_handle": int(a1._handle),
        "released_lease_fd": int(a1._rtdl_native_image_fd),
        "released_registry_absent": _registry_absent(a1),
        "survivor_marker": int(a2.marker()),
        "survivor_active_lease_count": int(
            a2._rtdl_native_cache_active_lease_count),
        "mapped_rows": _mapped_image_rows(digest_a),
    }
    runtime._release_native_library_image(a2)
    runtime._release_native_library_image(a2)
    a_after_all_release = {
        "registry_absent": _registry_absent(a2),
        "active_lease_count": int(a2._rtdl_native_cache_active_lease_count),
        "mapped_rows": _mapped_image_rows(digest_a),
    }

    b1, marker_b1 = _load(built["b"])
    digest_b = _sha(built["b"])
    b_before = {
        "source_sha256": _sha(work_directory / "b.c"),
        "image_sha256": digest_b,
        "observed_marker": marker_b1,
        "entry_identity": b1._rtdl_native_cache_entry_identity,
        "loader_handle": int(b1._handle),
        "sealed_image_fd": int(b1._rtdl_native_image_fd),
        "sealed_image_seals": int(b1._rtdl_native_image_seals),
        "loader_alias": str(b1._rtdl_native_loader_alias),
        "active_lease_count": int(b1._rtdl_native_cache_active_lease_count),
        "acquisition_count": int(b1._rtdl_native_cache_acquisition_count),
        "mapped_rows": _mapped_image_rows(digest_b),
    }
    runtime._release_native_library_image(b1)
    b_after_release = {
        "released_lease_handle": int(b1._handle),
        "released_lease_fd": int(b1._rtdl_native_image_fd),
        "registry_absent": _registry_absent(b1),
        "active_lease_count": int(b1._rtdl_native_cache_active_lease_count),
        "mapped_rows": _mapped_image_rows(digest_b),
    }

    snapshot = runtime._native_image_cache_snapshot()

    result = {
        "schema": SCHEMA,
        "status": (
            "PASS__CONTENT_ADDRESSED_SEALED_DSO_CACHE__"
            "BOUNDED_ONE_IMAGE_PER_DIGEST"
        ),
        "a_two_simultaneous_leases": a_before,
        "a_after_first_release": a_after_first_release,
        "a_after_all_release": a_after_all_release,
        "b_distinct_digest": b_before,
        "b_after_release": b_after_release,
        "cache_snapshot": snapshot,
        "different_digest_entries_distinct": (
            a_before["entry_identity"] != b_before["entry_identity"]),
        "different_digest_descriptors_distinct": (
            a_before["sealed_image_fd"] != b_before["sealed_image_fd"]),
        "different_digest_aliases_distinct": (
            a_before["loader_alias"] != b_before["loader_alias"]),
        "process_lifetime_dso_cache_retained": True,
        "explicit_dlclose_used": False,
        "required_seals_decimal": 15,
        "registered_performance_timing_count": 0,
    }
    if not (
        a_before["observed_markers"] == [111, 111]
        and a_before["shared_entry_identity"] is True
        and a_before["shared_handle"] is True
        and a_before["shared_descriptor"] is True
        and a_before["shared_alias"] is True
        and a_before["lease_ids_distinct"] is True
        and a_before["sealed_image_seals"] == 15
        and a_before["active_lease_count"] == 2
        and a_before["acquisition_count"] == 2
        and len(a_before["mapped_rows"]) > 0
        and a_after_first_release["released_lease_handle"] == 0
        and a_after_first_release["released_lease_fd"] == -1
        and a_after_first_release["released_registry_absent"] is True
        and a_after_first_release["survivor_marker"] == 111
        and a_after_first_release["survivor_active_lease_count"] == 1
        and a_after_first_release["mapped_rows"] == a_before["mapped_rows"]
        and a_after_all_release["registry_absent"] is True
        and a_after_all_release["active_lease_count"] == 0
        and a_after_all_release["mapped_rows"] == a_before["mapped_rows"]
        and b_before["observed_marker"] == 222
        and b_before["sealed_image_seals"] == 15
        and b_before["active_lease_count"] == 1
        and b_before["acquisition_count"] == 1
        and len(b_before["mapped_rows"]) > 0
        and b_after_release["released_lease_handle"] == 0
        and b_after_release["released_lease_fd"] == -1
        and b_after_release["registry_absent"] is True
        and b_after_release["active_lease_count"] == 0
        and b_after_release["mapped_rows"] == b_before["mapped_rows"]
        and result["different_digest_entries_distinct"] is True
        and result["different_digest_descriptors_distinct"] is True
        and result["different_digest_aliases_distinct"] is True
        and set(snapshot) == {digest_a, digest_b}
        and snapshot[digest_a]["active_lease_count"] == 0
        and snapshot[digest_b]["active_lease_count"] == 0
    ):
        raise RuntimeError("sealed native-image identity KAT failed")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(_canonical(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host-cc", type=Path, required=True)
    parser.add_argument("--work-directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(run(
        host_cc=arguments.host_cc,
        work_directory=arguments.work_directory,
        output=arguments.output,
    ), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
