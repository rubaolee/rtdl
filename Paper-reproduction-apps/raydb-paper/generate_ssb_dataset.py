from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import subprocess
from typing import Mapping, Sequence


DBGEN_REPOSITORY = "https://github.com/vadimtk/ssb-dbgen"
DBGEN_COMMIT = "0741e06d4c3e811bcec233378a39db2fc0be5d79"
VALIDATED_TABLES = ("lineorder", "customer", "supplier", "part")
GENERATION_PROFILE = (
    "ssb_dbgen_default_customer_supplier_then_individual_part_date_lineorder_v1"
)
TRACKED_SOURCE_TREE_HASH_ALGORITHM = (
    "sha256 over domain tag plus, for each HEAD blob sorted by raw Git path bytes, "
    "uint64be(path length), path bytes, uint64be(content length), and blob bytes"
)
_TRACKED_SOURCE_TREE_HASH_DOMAIN = (
    b"rtdl.raydb.ssb-dbgen.tracked-source-tree.path-content.v1\0"
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _line_count(path: Path) -> int:
    count = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            count += chunk.count(b"\n")
    return count


def _run_git(repo: Path, *args: str) -> bytes:
    command = ["git", "-C", str(repo), *args]
    try:
        return subprocess.run(
            command,
            check=True,
            capture_output=True,
        ).stdout
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or b"").decode("utf-8", errors="replace").strip()
        detail = f": {stderr}" if stderr else ""
        raise ValueError(f"git command failed ({shlex.join(command)}){detail}") from exc


def _hash_tracked_source_entries(entries: Sequence[tuple[bytes, bytes]]) -> str:
    digest = hashlib.sha256()
    digest.update(_TRACKED_SOURCE_TREE_HASH_DOMAIN)
    previous_path: bytes | None = None
    for path_bytes, content in sorted(entries, key=lambda entry: entry[0]):
        if not path_bytes:
            raise ValueError("tracked source entry path must not be empty")
        if previous_path == path_bytes:
            raise ValueError("tracked source entries contain a duplicate path")
        previous_path = path_bytes
        digest.update(len(path_bytes).to_bytes(8, byteorder="big"))
        digest.update(path_bytes)
        digest.update(len(content).to_bytes(8, byteorder="big"))
        digest.update(content)
    return digest.hexdigest()


def _tracked_source_tree_identity(repo: Path) -> tuple[str, int]:
    tree = _run_git(repo, "ls-tree", "-r", "-z", "--full-tree", "HEAD")
    entries: list[tuple[bytes, bytes]] = []
    for record in tree.split(b"\0"):
        if not record:
            continue
        try:
            header, path_bytes = record.split(b"\t", 1)
            _mode, object_type, object_id = header.split(b" ", 2)
        except ValueError as exc:
            raise ValueError("unexpected git ls-tree record while hashing source tree") from exc
        if object_type != b"blob":
            display_path = os.fsdecode(path_bytes)
            raise ValueError(
                f"tracked source tree entry is not a blob: {display_path!r} "
                f"({object_type.decode('ascii', errors='replace')})"
            )
        content = _run_git(repo, "cat-file", "blob", object_id.decode("ascii"))
        entries.append((path_bytes, content))
    if not entries:
        raise ValueError("dbgen checkout has no tracked source files at HEAD")
    return _hash_tracked_source_entries(entries), len(entries)


def collect_generator_identity(
    *, dbgen_repo: Path, expected_commit: str
) -> dict[str, object]:
    repo = dbgen_repo.resolve()
    if not repo.is_dir():
        raise FileNotFoundError(repo)

    git_root_output = _run_git(repo, "rev-parse", "--show-toplevel").rstrip(b"\r\n")
    git_root = Path(os.fsdecode(git_root_output)).resolve()
    if git_root != repo:
        raise ValueError(f"--dbgen-repo must name the Git checkout root: {git_root}")

    commit = _run_git(repo, "rev-parse", "--verify", "HEAD^{commit}").decode(
        "ascii"
    ).strip()
    if commit != expected_commit:
        raise ValueError(
            f"dbgen commit mismatch: expected {expected_commit}, got {commit}"
        )

    status = _run_git(
        repo,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    )
    if status:
        detail = status.decode("utf-8", errors="backslashreplace").replace("\0", " | ")
        raise ValueError(f"dbgen checkout must be clean; git status reported: {detail}")

    dbgen = (repo / "dbgen").resolve()
    dists = (repo / "dists.dss").resolve()
    if not dbgen.is_file() or not dists.is_file():
        raise FileNotFoundError("dbgen and dists.dss must exist in --dbgen-repo")
    tracked_dists = _run_git(repo, "ls-files", "--", "dists.dss")
    if not tracked_dists.splitlines():
        raise ValueError("dists.dss must be tracked by the pinned dbgen checkout")

    source_tree_sha256, source_file_count = _tracked_source_tree_identity(repo)
    return {
        "dbgen_commit": commit,
        "dbgen_checkout_clean": True,
        "dbgen_checkout_path": str(repo),
        "dbgen_tracked_source_tree_sha256": source_tree_sha256,
        "dbgen_tracked_source_tree_file_count": source_file_count,
        "dbgen_tracked_source_tree_hash_algorithm": TRACKED_SOURCE_TREE_HASH_ALGORITHM,
        "dbgen_binary_path": str(dbgen),
        "dbgen_binary_sha256": _sha256_file(dbgen),
        "dists_dss_path": str(dists),
        "dists_dss_sha256": _sha256_file(dists),
    }


def _require_sha256(identity: Mapping[str, object], key: str) -> str:
    value = identity.get(key)
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"generator identity {key} must be a SHA256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"generator identity {key} must be a SHA256 hex digest") from exc
    return value.lower()


def generation_commands(dbgen: Path, scale_factor: int) -> list[list[str]]:
    """Return the pinned SSB generator command sequence.

    The default invocation deliberately generates customer and supplier in one
    process. Splitting those tables into separate ``-T c`` / ``-T s`` runs
    changes the generator random stream and therefore the customer bytes.
    """
    executable = str(dbgen)
    scale = str(scale_factor)
    return [
        [executable, "-s", scale, "-f"],
        [executable, "-fF", "-s", scale, "-T", "p"],
        [executable, "-fF", "-s", scale, "-T", "d"],
        [executable, "-fF", "-s", scale, "-T", "l"],
    ]


def build_provenance_manifest(
    *,
    output_dir: Path,
    scale_factor: int,
    generation_command_argv: list[list[str]],
    generator_identity: Mapping[str, object],
    generation_host_class: str,
) -> dict[str, object]:
    if generator_identity.get("dbgen_checkout_clean") is not True:
        raise ValueError("generator identity must attest a clean dbgen checkout")
    dbgen_commit = generator_identity.get("dbgen_commit")
    if dbgen_commit != DBGEN_COMMIT:
        raise ValueError(
            f"generator identity commit must be pinned to {DBGEN_COMMIT}, got {dbgen_commit}"
        )
    source_tree_sha256 = _require_sha256(
        generator_identity, "dbgen_tracked_source_tree_sha256"
    )
    dbgen_binary_sha256 = _require_sha256(generator_identity, "dbgen_binary_sha256")
    dists_dss_sha256 = _require_sha256(generator_identity, "dists_dss_sha256")
    source_file_count = generator_identity.get("dbgen_tracked_source_tree_file_count")
    if not isinstance(source_file_count, int) or source_file_count <= 0:
        raise ValueError("generator identity source file count must be positive")
    source_hash_algorithm = generator_identity.get(
        "dbgen_tracked_source_tree_hash_algorithm"
    )
    if source_hash_algorithm != TRACKED_SOURCE_TREE_HASH_ALGORITHM:
        raise ValueError("generator identity source tree hash algorithm is unsupported")
    if not generation_command_argv or any(
        not command
        or any(not isinstance(argument, str) for argument in command)
        for command in generation_command_argv
    ):
        raise ValueError("generation command argv must contain non-empty string arrays")
    command_argv = [list(command) for command in generation_command_argv]
    command_strings = [shlex.join(command) for command in command_argv]

    tables: dict[str, dict[str, object]] = {}
    for name in VALIDATED_TABLES:
        path = output_dir / f"{name}.tbl"
        if not path.is_file():
            raise FileNotFoundError(path)
        tables[name] = {
            "file_name": path.name,
            "row_count": _line_count(path),
            "sha256": _sha256_file(path),
        }

    expected = {
        "customer": 30_000 * scale_factor,
        "supplier": 2_000 * scale_factor,
        "part": 200_000 * math.floor(1.0 + math.log2(float(scale_factor))),
    }
    for name, cardinality in expected.items():
        actual = int(tables[name]["row_count"])
        if actual != cardinality:
            raise ValueError(
                f"generated {name} cardinality mismatch: expected {cardinality}, got {actual}"
            )
    lineorder_count = int(tables["lineorder"]["row_count"])
    if not 5_500_000 * scale_factor <= lineorder_count <= 6_500_000 * scale_factor:
        raise ValueError("generated lineorder cardinality is outside the pinned scale envelope")

    return {
        "schema": "rtdl.paper_reproduction.raydb.ssb_generated_dataset_provenance.v1",
        "dbgen_repository": DBGEN_REPOSITORY,
        "dbgen_commit": dbgen_commit,
        "dbgen_checkout_clean": True,
        "dbgen_checkout_path": str(generator_identity.get("dbgen_checkout_path", "")),
        "dbgen_tracked_source_tree_sha256": source_tree_sha256,
        "dbgen_tracked_source_tree_file_count": source_file_count,
        "dbgen_tracked_source_tree_hash_algorithm": source_hash_algorithm,
        "dbgen_binary_path": str(generator_identity.get("dbgen_binary_path", "")),
        "dbgen_binary_sha256": dbgen_binary_sha256,
        "dists_dss_path": str(generator_identity.get("dists_dss_path", "")),
        "dists_dss_sha256": dists_dss_sha256,
        "scale_factor": scale_factor,
        "dataset_identity_level": "deterministic_generated_same_source_not_exact_paper_input",
        "provenance_scope": "bounded_same_source_only_not_exact_paper",
        "generation_host_class": generation_host_class,
        "generation_date": date.today().isoformat(),
        "generation_working_directory": str(output_dir.resolve()),
        "generation_invocation_mode": "subprocess argv with shell=false",
        "generation_profile": GENERATION_PROFILE,
        "generation_commands": command_strings,
        "generation_command_argv": command_argv,
        "generation_command_string_format": (
            "POSIX shell escaping via shlex.join; generation_command_argv is authoritative"
        ),
        "cardinality_validation": {
            "customer_formula": "30000 * scale_factor",
            "supplier_formula": "2000 * scale_factor",
            "part_formula": "200000 * floor(1 + log2(scale_factor))",
            "lineorder_validation": (
                "observed row count must be within [5.5M, 6.5M] * scale_factor "
                "because generated orders have variable line cardinality"
            ),
        },
        "lineorder_row_count": lineorder_count,
        "tables": tables,
        "claim_boundary": {
            "bounded_same_source_only": True,
            "deterministic_generated_same_source_claimed": True,
            "exact_paper_input_claimed": False,
            "paper_dataset_hash_claimed": False,
            "exact_paper_dataset_claimed": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a pinned same-source SSB dataset and hash provenance"
    )
    parser.add_argument("--dbgen-repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--scale-factor", type=int, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--generation-host-class", default="remote_gpu_pod")
    args = parser.parse_args(argv)
    if args.scale_factor <= 0:
        parser.error("--scale-factor must be positive")

    generator_identity = collect_generator_identity(
        dbgen_repo=args.dbgen_repo,
        expected_commit=DBGEN_COMMIT,
    )
    dbgen = Path(str(generator_identity["dbgen_binary_path"]))
    dists = Path(str(generator_identity["dists_dss_path"]))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    local_dists = args.output_dir / "dists.dss"
    if local_dists.exists() or local_dists.is_symlink():
        local_dists.unlink()
    local_dists.symlink_to(dists)

    commands = generation_commands(dbgen, args.scale_factor)
    for command in commands:
        subprocess.run(command, check=True, cwd=args.output_dir)
    for table in (*VALIDATED_TABLES, "date"):
        expected_output = args.output_dir / f"{table}.tbl"
        if not expected_output.is_file():
            raise FileNotFoundError(expected_output)

    final_generator_identity = collect_generator_identity(
        dbgen_repo=args.dbgen_repo,
        expected_commit=DBGEN_COMMIT,
    )
    if final_generator_identity != generator_identity:
        raise ValueError("dbgen source, binary, or dists.dss identity changed during generation")

    manifest = build_provenance_manifest(
        output_dir=args.output_dir,
        scale_factor=args.scale_factor,
        generation_command_argv=commands,
        generator_identity=final_generator_identity,
        generation_host_class=args.generation_host_class,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output_json.with_name(args.output_json.name + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output_json)
    print(json.dumps({"scale_factor": args.scale_factor, "output_json": str(args.output_json)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
