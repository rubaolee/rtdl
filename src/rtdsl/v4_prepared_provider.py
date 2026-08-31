"""Uniform verified-provider entry for the explicit V4 prepared lifecycle.

The provider is not a process-global execution cache and does not select an
application algorithm.  It names one exact verified callback artifact.  Every
session construction reloads and rehashes that artifact before handing it to
the existing prepared partner runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .v4_callback_artifact_cache import (
    V4CallbackProviderKey,
    load_callback_artifact,
)


@dataclass(frozen=True)
class V4VerifiedCallbackProvider:
    cache_root: Path
    provider_key: V4CallbackProviderKey
    provider_identity: str
    provider_key_sha256: str
    composed_ptx_sha256: str
    construction_receipt_sha256: str
    artifact_manifest_sha256: str

    def _revalidate(self):
        artifact = load_callback_artifact(self.cache_root, self.provider_key)
        observed = (
            artifact.provider_identity,
            artifact.provider_key.key_sha256,
            artifact.composed_ptx_sha256,
            artifact.construction_receipt_sha256,
            artifact.artifact_manifest_sha256,
        )
        expected = (
            self.provider_identity,
            self.provider_key_sha256,
            self.composed_ptx_sha256,
            self.construction_receipt_sha256,
            self.artifact_manifest_sha256,
        )
        if observed != expected or artifact.cache_hit is not True:
            raise RuntimeError("V4 prepared provider identity changed")
        return artifact

    def prepare_partner_session(
        self,
        *,
        spheres: Sequence[tuple[Sequence[float], float, int]],
        semantic_digest: str,
        library: object | None = None,
    ):
        """Reverify exact provider bytes and create one explicit owner."""

        self._revalidate()
        from .v4_callback_partner_runtime import prepare_v4_partner_session

        return prepare_v4_partner_session(
            self.cache_root,
            self.provider_key,
            spheres=spheres,
            semantic_digest=semantic_digest,
            library=library,
        )

    def to_metadata(self) -> Mapping[str, object]:
        self._revalidate()
        return {
            "schema": "rtdl.v4.verified_callback_provider.v1",
            "provider_identity": self.provider_identity,
            "provider_key_sha256": self.provider_key_sha256,
            "composed_ptx_sha256": self.composed_ptx_sha256,
            "construction_receipt_sha256": self.construction_receipt_sha256,
            "artifact_manifest_sha256": self.artifact_manifest_sha256,
            "cache_rehashed_before_session_prepare": True,
            "application_algorithm_selected": False,
            "prepared_execution_cached_globally": False,
        }


def open_v4_callback_provider(
    cache_root: str | Path,
    provider_key: V4CallbackProviderKey,
) -> V4VerifiedCallbackProvider:
    """Open one exact cached provider; missing or mutated bytes fail closed."""

    root = Path(cache_root)
    artifact = load_callback_artifact(root, provider_key)
    if artifact.cache_hit is not True:
        raise RuntimeError("V4 callback provider requires a materialized artifact")
    return V4VerifiedCallbackProvider(
        cache_root=root.resolve(),
        provider_key=provider_key,
        provider_identity=artifact.provider_identity,
        provider_key_sha256=artifact.provider_key.key_sha256,
        composed_ptx_sha256=artifact.composed_ptx_sha256,
        construction_receipt_sha256=artifact.construction_receipt_sha256,
        artifact_manifest_sha256=artifact.artifact_manifest_sha256,
    )


__all__ = ["V4VerifiedCallbackProvider", "open_v4_callback_provider"]
