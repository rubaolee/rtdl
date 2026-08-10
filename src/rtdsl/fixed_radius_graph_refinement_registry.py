"""Compiler-owned trust pin and proof capsule for reviewed fixed-radius evidence.

This file is generated only after the target materializer completes the full
semantic evidence validation.  Fresh runtime processes rehash the exact artifact
and every executable dependency source before consuming the capsule.
"""

from __future__ import annotations


TRUSTED_REFINEMENT_EVIDENCE_DIGEST: str | None = (
    "7f825cd421f2462739cad617258bdda76bcf2e01ee587625c1d614b8030b838a"
)
TRUSTED_REFINEMENT_EVIDENCE_CAPSULE: dict[str, object] | None = {
    "artifact_schema": "rtdl.fixed_radius_graph.refinement_evidence.v4",
    "artifact_sha256": "7f825cd421f2462739cad617258bdda76bcf2e01ee587625c1d614b8030b838a",
    "dependency_source_sha256": {
        "src/rtdsl/action_api.py": "0d7cbfee898d0686be05ea4e94329e022631635aed6088755400494eb75410b9",
        "src/rtdsl/action_native_identity.py": "a6e07e202ec01520334841824da8f2918c4c2f7187301fea8d79729af715cc42",
        "src/rtdsl/component_partition.py": "16cd1414f9bf8b94da50678c9409f129d9c6dc1591dc284016b6ce7151d41047",
        "src/rtdsl/fixed_radius_graph_compiler.py": "f54226fc97817177c27cfececb25fd9068fce946ccc24df1db8a8e51f67e25ca",
        "src/rtdsl/optix_runtime.py": "c6e553f6fb5533af8cc401914bb67c98368af29b4afbe335c0737f74dc08e9ac",
        "src/rtdsl/partner_adapters.py": "e8f059b4558afd5fa1ace11b7eca9c1bc4b018dac575928f0e9997f0a8cf93c8",
        "src/rtdsl/predicate_aware_boundary_union.py": "ca8fbab66be0dfd614ab958428b783cfb46030f54d08da20c0dfac97f6ec6601"
    },
    "executable_identity_digests": {
        "complete_pair_candidate_enumeration.v1": "c08229fc83931a4fbe40dc3db57d31bee5d050f0277f13b67e16b9407775e0e8",
        "prepared_spatial_radius_producer.v1": "b354a1cf189b720143f184a01939012fca35a974f3090f8ee1aeadaa4a0c8785"
    },
    "independent_reference_digest": "7e52b42d1b2235110a9925540bbf59bea016261fc8bf64142a5a6d22b2ca53ea",
    "native_evidence_identity": {
        "binary_sha256": "fa2b443dd96c0c22d5fecc1244410fcc56f4c994c6ab6834ef8d9614a14913b2",
        "optix_version": [
            8,
            0,
            0
        ],
        "required_symbols_digest": "d185ab86a79b5f328f73060c6f71dccecc5571232a322411b1911cd8c8ace2fa"
    },
    "schema": "rtdl.fixed_radius_graph.refinement_evidence_capsule.v1",
    "verified_case_count": 17
}


__all__ = [
    "TRUSTED_REFINEMENT_EVIDENCE_CAPSULE",
    "TRUSTED_REFINEMENT_EVIDENCE_DIGEST",
]
