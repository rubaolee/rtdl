"""RTDL-owned identity and cache for verified V4 callback artifacts.

The cache starts after Callback IR verification and trusted code generation.
It never accepts Python source, a callable, an application name, or raw
user-supplied PTX.  A cache hit is usable only after the exact key, manifest,
composed PTX and construction receipt have all been rehashed.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Mapping, Sequence


class CallbackArtifactCacheError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


_ROLES = (
    "bounds", "make_ray", "intersection", "any_hit",
    "closest_hit", "miss", "finalize",
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_sha(name: str, value: str) -> None:
    if len(value) != 64 or any(item not in "0123456789abcdef" for item in value):
        raise CallbackArtifactCacheError("identity_sha256", f"{name} is not lowercase SHA-256")


def _validate_role_hashes(name: str, rows: Sequence[tuple[str, str]]) -> None:
    if tuple(role for role, _digest in rows) != _ROLES:
        raise CallbackArtifactCacheError(
            "identity_roles", f"{name} must contain the seven canonical roles in order")
    for role, digest in rows:
        _require_sha(f"{name}.{role}", digest)


@dataclasses.dataclass(frozen=True)
class V4CallbackProviderKey:
    callback_ir_sha256: str
    callback_abi_sha256: str
    generated_source_sha256_by_role: tuple[tuple[str, str], ...]
    leaf_ptx_sha256_by_role: tuple[tuple[str, str], ...]
    wrapper_source_sha256: str
    wrapper_template: str
    physical_template: str
    payload_layout_sha256: str
    attribute_layout_sha256: str
    sbt_layout_sha256: str
    native_provider_sha256: str
    target_compute_capability: tuple[int, int]
    python_version: str
    numba_version: str
    numpy_version: str
    llvmlite_version: str
    cuda_toolkit_version: str
    optix_sdk_version: str
    ptx_isa: str
    wrapper_numeric_policy: str
    leaf_numeric_policy: str
    composer_schema: str
    compile_options: tuple[str, ...]
    link_options: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in (
            "callback_ir_sha256", "callback_abi_sha256", "wrapper_source_sha256",
            "payload_layout_sha256", "attribute_layout_sha256", "sbt_layout_sha256",
            "native_provider_sha256",
        ):
            _require_sha(name, getattr(self, name))
        _validate_role_hashes("generated_source", self.generated_source_sha256_by_role)
        _validate_role_hashes("leaf_ptx", self.leaf_ptx_sha256_by_role)
        if (len(self.target_compute_capability) != 2 or
                any(not isinstance(item, int) or item < 0 for item in self.target_compute_capability)):
            raise CallbackArtifactCacheError("target_cc", "compute capability must be two nonnegative integers")
        for name in (
            "wrapper_template", "physical_template", "python_version", "numba_version",
            "numpy_version", "llvmlite_version", "cuda_toolkit_version", "optix_sdk_version",
            "ptx_isa", "wrapper_numeric_policy", "leaf_numeric_policy", "composer_schema",
        ):
            if not getattr(self, name):
                raise CallbackArtifactCacheError("identity_field", f"{name} must be nonempty")
        if len(set(self.compile_options)) != len(self.compile_options):
            raise CallbackArtifactCacheError("compile_options", "duplicate compile option")
        if len(set(self.link_options)) != len(self.link_options):
            raise CallbackArtifactCacheError("link_options", "duplicate link option")

    def to_dict(self) -> dict[str, object]:
        payload = dataclasses.asdict(self)
        payload["generated_source_sha256_by_role"] = [list(item) for item in self.generated_source_sha256_by_role]
        payload["leaf_ptx_sha256_by_role"] = [list(item) for item in self.leaf_ptx_sha256_by_role]
        payload["target_compute_capability"] = list(self.target_compute_capability)
        payload["compile_options"] = list(self.compile_options)
        payload["link_options"] = list(self.link_options)
        return payload

    @property
    def key_sha256(self) -> str:
        return _sha(_canonical({
            "schema": "rtdl.v4.callback_provider_key.v1",
            "key": self.to_dict(),
        }))

    @property
    def provider_identity(self) -> str:
        return f"rtdl.v4.generated_provider.{self.key_sha256}"


@dataclasses.dataclass(frozen=True)
class V4CachedCallbackArtifact:
    provider_key: V4CallbackProviderKey
    provider_identity: str
    composed_ptx: str
    composed_ptx_sha256: str
    construction_receipt: Mapping[str, object]
    construction_receipt_sha256: str
    artifact_manifest_sha256: str
    cache_hit: bool


_MANIFEST_KEYS = {
    "schema", "provider_identity", "provider_key", "provider_key_sha256",
    "composed_ptx_sha256", "construction_receipt", "construction_receipt_sha256",
}


def _key_from_dict(value: object) -> V4CallbackProviderKey:
    if not isinstance(value, dict):
        raise CallbackArtifactCacheError("manifest_key", "provider_key must be an object")
    expected = {field.name for field in dataclasses.fields(V4CallbackProviderKey)}
    if set(value) != expected:
        raise CallbackArtifactCacheError("manifest_key_fields", "provider_key fields are not exact")
    converted = dict(value)
    for name in ("generated_source_sha256_by_role", "leaf_ptx_sha256_by_role"):
        rows = converted[name]
        if not isinstance(rows, list) or any(not isinstance(row, list) or len(row) != 2 for row in rows):
            raise CallbackArtifactCacheError("manifest_role_hashes", f"malformed {name}")
        converted[name] = tuple((str(row[0]), str(row[1])) for row in rows)
    converted["target_compute_capability"] = tuple(converted["target_compute_capability"])
    converted["compile_options"] = tuple(converted["compile_options"])
    converted["link_options"] = tuple(converted["link_options"])
    return V4CallbackProviderKey(**converted)


def _load_exact(cache_root: Path, provider_key: V4CallbackProviderKey, *, cache_hit: bool) -> V4CachedCallbackArtifact:
    root = cache_root.resolve()
    directory = root / provider_key.key_sha256
    if not directory.is_dir() or directory.is_symlink():
        raise CallbackArtifactCacheError("cache_directory", "provider directory is missing or unsafe")
    members = sorted(item.name for item in directory.iterdir())
    if members != ["artifact.json", "composed.ptx"]:
        raise CallbackArtifactCacheError("cache_membership", f"unexpected cache members: {members!r}")
    manifest_path = directory / "artifact.json"
    ptx_path = directory / "composed.ptx"
    if manifest_path.is_symlink() or ptx_path.is_symlink():
        raise CallbackArtifactCacheError("cache_symlink", "cache payload may not be a symlink")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CallbackArtifactCacheError("cache_manifest", str(error)) from error
    if not isinstance(manifest, dict) or set(manifest) != _MANIFEST_KEYS:
        raise CallbackArtifactCacheError("cache_manifest_fields", "artifact manifest fields are not exact")
    if manifest["schema"] != "rtdl.v4.cached_callback_artifact.v1":
        raise CallbackArtifactCacheError("cache_schema", str(manifest["schema"]))
    recovered_key = _key_from_dict(manifest["provider_key"])
    if recovered_key != provider_key or manifest["provider_key_sha256"] != provider_key.key_sha256:
        raise CallbackArtifactCacheError("cache_key_replay", "cached provider key does not match the request")
    if manifest["provider_identity"] != provider_key.provider_identity:
        raise CallbackArtifactCacheError("cache_provider_replay", "cached provider identity does not match the key")
    ptx_bytes = ptx_path.read_bytes()
    if _sha(ptx_bytes) != manifest["composed_ptx_sha256"]:
        raise CallbackArtifactCacheError("cache_ptx_hash", "composed PTX changed after materialization")
    receipt = manifest["construction_receipt"]
    if not isinstance(receipt, dict):
        raise CallbackArtifactCacheError("cache_receipt", "construction receipt must be an object")
    receipt_sha = _sha(_canonical(receipt))
    if receipt_sha != manifest["construction_receipt_sha256"]:
        raise CallbackArtifactCacheError("cache_receipt_hash", "construction receipt changed")
    manifest_sha = _sha(_canonical(manifest))
    return V4CachedCallbackArtifact(
        provider_key=provider_key,
        provider_identity=provider_key.provider_identity,
        composed_ptx=ptx_bytes.decode("utf-8"),
        composed_ptx_sha256=manifest["composed_ptx_sha256"],
        construction_receipt=receipt,
        construction_receipt_sha256=receipt_sha,
        artifact_manifest_sha256=manifest_sha,
        cache_hit=cache_hit,
    )


def materialize_callback_artifact(
    cache_root: str | os.PathLike[str],
    provider_key: V4CallbackProviderKey,
    *,
    composed_ptx: str,
    construction_receipt: Mapping[str, object],
) -> V4CachedCallbackArtifact:
    """Create once or revalidate an exact trusted callback provider artifact."""

    if not composed_ptx:
        raise CallbackArtifactCacheError("composed_ptx", "composed PTX must be nonempty")
    if not isinstance(construction_receipt, Mapping):
        raise CallbackArtifactCacheError("construction_receipt", "receipt must be a mapping")
    root = Path(cache_root)
    root.mkdir(parents=True, exist_ok=True)
    if root.is_symlink():
        raise CallbackArtifactCacheError("cache_root_symlink", "cache root may not be a symlink")
    target = root.resolve() / provider_key.key_sha256
    if target.exists():
        existing = _load_exact(root, provider_key, cache_hit=True)
        if (existing.composed_ptx != composed_ptx or
                dict(existing.construction_receipt) != dict(construction_receipt)):
            raise CallbackArtifactCacheError("cache_collision", "existing key has different exact bytes")
        return existing

    receipt = dict(construction_receipt)
    receipt_sha = _sha(_canonical(receipt))
    ptx_bytes = composed_ptx.encode("utf-8")
    manifest = {
        "schema": "rtdl.v4.cached_callback_artifact.v1",
        "provider_identity": provider_key.provider_identity,
        "provider_key": provider_key.to_dict(),
        "provider_key_sha256": provider_key.key_sha256,
        "composed_ptx_sha256": _sha(ptx_bytes),
        "construction_receipt": receipt,
        "construction_receipt_sha256": receipt_sha,
    }
    temp = Path(tempfile.mkdtemp(prefix=".rtdl-v4-provider-", dir=root.resolve()))
    try:
        (temp / "composed.ptx").write_bytes(ptx_bytes)
        (temp / "artifact.json").write_bytes(_canonical(manifest) + b"\n")
        try:
            temp.rename(target)
        except FileExistsError:
            existing = _load_exact(root, provider_key, cache_hit=True)
            if (existing.composed_ptx != composed_ptx or
                    dict(existing.construction_receipt) != receipt):
                raise CallbackArtifactCacheError("cache_collision", "concurrent writer stored different bytes")
            return existing
    finally:
        if temp.exists():
            for item in temp.iterdir():
                item.unlink()
            temp.rmdir()
    return _load_exact(root, provider_key, cache_hit=False)


def load_callback_artifact(
    cache_root: str | os.PathLike[str], provider_key: V4CallbackProviderKey,
) -> V4CachedCallbackArtifact:
    return _load_exact(Path(cache_root), provider_key, cache_hit=True)


__all__ = [
    "CallbackArtifactCacheError", "V4CachedCallbackArtifact",
    "V4CallbackProviderKey", "load_callback_artifact",
    "materialize_callback_artifact",
]
