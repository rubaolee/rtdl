#!/usr/bin/env python3
"""Offline create-only trust-root and deployment-freeze tool for ``.rtdlexe``.

This tool is intentionally separate from ``build_rtdlexe``.  Building a
candidate never authorizes it.  A project/operator creates and retains the
private key outside the repository, reviews a detached candidate authority,
and then explicitly freezes one deployment slot.  Runtime deployment receives
only the public root and signed package.

The RSA implementation uses the Python standard library so the workflow does
not depend on Numba, NVRTC, CUDA, or the RTDL compiler graph.  Production key
custody remains an operator responsibility; repository test keys, if any, are
never production roots.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import secrets
import sys
from typing import Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from rtdsl import v4_rtdlexe as runtime  # noqa: E402


_PRIVATE_SCHEMA = "rtdl.v4.rtdlexe.signer_private_key.v1"
_PRIVATE_NOTICE = "SECRET__STORE_OUTSIDE_REPOSITORY_AND_DEPLOYMENT_ARTIFACTS"
_DIGEST_INFO = bytes.fromhex("3031300d060960864801650304020105000420")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _b64_int(value: int) -> str:
    return base64.b64encode(value.to_bytes((value.bit_length() + 7) // 8, "big")).decode("ascii")


def _int_b64(value: object, path: str) -> int:
    if not isinstance(value, str):
        raise ValueError(f"{path}: base64 string required")
    raw = base64.b64decode(value, validate=True)
    if not raw:
        raise ValueError(f"{path}: empty integer")
    return int.from_bytes(raw, "big")


def _read(path: Path) -> Mapping[str, object]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, Mapping) or raw != _canonical(value) + b"\n":
        raise ValueError(f"{path}: exact canonical JSON plus LF required")
    return value


def _write_create_only(path: Path, value: Mapping[str, object], *, private: bool = False) -> None:
    payload = _canonical(value) + b"\n"
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"create-only output already exists: {path}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600 if private else 0o644)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def _probably_prime(value: int, rounds: int = 48) -> bool:
    if value < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)
    for prime in small:
        if value == prime:
            return True
        if value % prime == 0:
            return False
    odd = value - 1; shift = 0
    while odd % 2 == 0:
        shift += 1; odd //= 2
    for _ in range(rounds):
        base = secrets.randbelow(value - 3) + 2
        x = pow(base, odd, value)
        if x in (1, value - 1):
            continue
        for _ in range(shift - 1):
            x = pow(x, 2, value)
            if x == value - 1:
                break
        else:
            return False
    return True


def _prime(bits: int, exponent: int) -> int:
    while True:
        value = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if math.gcd(value - 1, exponent) == 1 and _probably_prime(value):
            return value


def create_root(*, private_path: Path, public_path: Path, key_id: str, bits: int) -> None:
    if not key_id or bits < 2048 or bits % 256:
        raise ValueError("nonempty key id and RSA bit size >=2048 divisible by 256 required")
    exponent = 65537
    p = _prime(bits // 2, exponent)
    q = _prime(bits // 2, exponent)
    while q == p:
        q = _prime(bits // 2, exponent)
    modulus = p * q
    private_exponent = pow(exponent, -1, (p - 1) * (q - 1))
    private = {
        "schema": _PRIVATE_SCHEMA,
        "key_id": key_id,
        "rsa_modulus_base64": _b64_int(modulus),
        "rsa_exponent": exponent,
        "rsa_private_exponent_base64": _b64_int(private_exponent),
        "security_notice": _PRIVATE_NOTICE,
    }
    public_body = {
        "schema": runtime._TRUST_ROOT_SCHEMA,
        "key_id": key_id,
        "rsa_modulus_base64": _b64_int(modulus),
        "rsa_exponent": exponent,
    }
    public = {
        **public_body,
        "trust_root_sha256": _sha_bytes(runtime._TRUST_ROOT_DOMAIN + _canonical(public_body)),
    }
    _write_create_only(private_path, private, private=True)
    try:
        _write_create_only(public_path, public)
    except Exception:
        # Do not leave a private key without its intended public certificate.
        private_path.expanduser().resolve().unlink(missing_ok=True)
        raise
    print(json.dumps({
        "key_id": key_id, "private_path": str(private_path.resolve()),
        "public_path": str(public_path.resolve()),
        "trust_root_sha256": public["trust_root_sha256"],
        "production_key_custody_attested": False,
    }, sort_keys=True))


def _private_key(path: Path, root: Mapping[str, object]) -> tuple[int, int, int]:
    private = _read(path)
    expected = {
        "schema", "key_id", "rsa_modulus_base64", "rsa_exponent",
        "rsa_private_exponent_base64", "security_notice",
    }
    if set(private) != expected or private["schema"] != _PRIVATE_SCHEMA \
            or private["security_notice"] != _PRIVATE_NOTICE \
            or private["key_id"] != root["key_id"] \
            or private["rsa_modulus_base64"] != root["rsa_modulus_base64"] \
            or private["rsa_exponent"] != root["rsa_exponent"]:
        raise ValueError("private key does not exactly match installed public root")
    return (
        _int_b64(private["rsa_modulus_base64"], "private.modulus"),
        int(private["rsa_exponent"]),
        _int_b64(private["rsa_private_exponent_base64"], "private.private_exponent"),
    )


def _sign(message: bytes, *, modulus: int, private_exponent: int) -> bytes:
    width = (modulus.bit_length() + 7) // 8
    digest_info = _DIGEST_INFO + hashlib.sha256(message).digest()
    padding = width - len(digest_info) - 3
    if padding < 8:
        raise ValueError("RSA modulus too small")
    encoded = b"\x00\x01" + b"\xff" * padding + b"\x00" + digest_info
    return pow(int.from_bytes(encoded, "big"), private_exponent, modulus).to_bytes(width, "big")


def _entry(authority_path: Path) -> dict[str, object]:
    authority = _read(authority_path)
    expected = {
        "schema", "authority_version", "artifact_sha256", "artifact_bytes",
        "product_projection_sha256", "protocol_decision_sha256",
        "executable_identity_sha256", "native_library_sha256", "target_sha256",
        "deployment_id", "family", "task_semantics_sha256",
        "target_compute_capability", "authority_seal",
    }
    if set(authority) != expected or authority["schema"] != runtime._AUTHORITY_SCHEMA \
            or type(authority["authority_version"]) is not int \
            or authority["authority_version"] != 1 \
            or type(authority["artifact_bytes"]) is not int \
            or authority["artifact_bytes"] <= 0:
        raise ValueError("detached authority schema invalid")
    body = dict(authority); seal = body.pop("authority_seal")
    if seal != _sha_bytes(runtime._AUTHORITY_DOMAIN + _canonical(body)):
        raise ValueError("detached authority seal invalid")
    return {
        "deployment_id": authority["deployment_id"],
        "family": authority["family"],
        "task_semantics_sha256": authority["task_semantics_sha256"],
        "authority_sha256": _sha_bytes(authority_path.read_bytes()),
        "artifact_sha256": authority["artifact_sha256"],
        "executable_identity_sha256": authority["executable_identity_sha256"],
        "target_sha256": authority["target_sha256"],
        "native_library_sha256": authority["native_library_sha256"],
        "compute_capability": authority["target_compute_capability"],
    }


def freeze(*, private_path: Path, root_path: Path, authority_path: Path,
           output_path: Path, head_output_path: Path,
           previous_path: Path | None) -> None:
    root = runtime._read_trust_root(root_path.resolve())
    modulus, exponent, private_exponent = _private_key(private_path.resolve(), root)
    if exponent != int(root["rsa_exponent"]):
        raise ValueError("RSA exponent mismatch")
    new_entry = _entry(authority_path.resolve())
    if previous_path is None:
        previous_sha = None; sequence = 1; entries: list[Mapping[str, object]] = []
    else:
        previous_path = previous_path.resolve()
        package, previous_entries = runtime._verify_trust_package(previous_path, root=root)
        previous_sha = _sha_bytes(previous_path.read_bytes())
        sequence = int(package["sequence"]) + 1
        entries = [dict(item) for item in previous_entries]
    prior = [item for item in entries if item["deployment_id"] == new_entry["deployment_id"]]
    if prior:
        if prior[0] != new_entry:
            raise ValueError("deployment id is append-only and already binds a different authority")
        raise ValueError("authority is already frozen for this deployment id")
    entries.append(new_entry)
    entries.sort(key=lambda item: str(item["deployment_id"]))
    body = {
        "schema": runtime._TRUST_PACKAGE_SCHEMA,
        "key_id": root["key_id"],
        "sequence": sequence,
        "previous_package_sha256": previous_sha,
        "authorities": entries,
        "signature_algorithm": "rsa-pkcs1-v1_5-sha256",
    }
    signature = _sign(
        runtime._TRUST_PACKAGE_DOMAIN + _canonical(body),
        modulus=modulus, private_exponent=private_exponent,
    )
    package = {**body, "signature_base64": base64.b64encode(signature).decode("ascii")}
    package_sha = _sha_bytes(_canonical(package) + b"\n")
    head_body = {
        "schema": runtime._TRUST_HEAD_SCHEMA,
        "key_id": root["key_id"],
        "current_package_sha256": package_sha,
        "current_sequence": sequence,
        "signature_algorithm": "rsa-pkcs1-v1_5-sha256",
    }
    head_signature = _sign(
        runtime._TRUST_HEAD_DOMAIN + _canonical(head_body),
        modulus=modulus, private_exponent=private_exponent,
    )
    head = {**head_body, "signature_base64": base64.b64encode(head_signature).decode("ascii")}
    _write_create_only(output_path, package)
    try:
        _write_create_only(head_output_path, head)
    except Exception:
        output_path.expanduser().resolve().unlink(missing_ok=True)
        raise
    print(json.dumps({
        "trust_package_path": str(output_path.resolve()),
        "trust_package_sha256": package_sha,
        "trust_head_path": str(head_output_path.resolve()),
        "trust_head_sha256": _sha_bytes(_canonical(head) + b"\n"),
        "sequence": sequence, "authority_count": len(entries),
        "deployment_id": new_entry["deployment_id"],
        "production_key_custody_attested": False,
    }, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-root")
    create.add_argument("--private-key", type=Path, required=True)
    create.add_argument("--public-root", type=Path, required=True)
    create.add_argument("--key-id", required=True)
    create.add_argument("--bits", type=int, default=3072)
    freeze_parser = commands.add_parser("freeze")
    freeze_parser.add_argument("--private-key", type=Path, required=True)
    freeze_parser.add_argument("--public-root", type=Path, required=True)
    freeze_parser.add_argument("--authority", type=Path, required=True)
    freeze_parser.add_argument("--output", type=Path, required=True)
    freeze_parser.add_argument("--head-output", type=Path, required=True)
    freeze_parser.add_argument("--previous", type=Path)
    arguments = parser.parse_args()
    if arguments.command == "create-root":
        create_root(private_path=arguments.private_key, public_path=arguments.public_root,
                    key_id=arguments.key_id, bits=arguments.bits)
    else:
        freeze(private_path=arguments.private_key, root_path=arguments.public_root,
               authority_path=arguments.authority, output_path=arguments.output,
               head_output_path=arguments.head_output,
               previous_path=arguments.previous)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
