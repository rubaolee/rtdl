"""Target-generated fixed-radius evidence identity and proof capsule.

Generated only after all 17 exact routes pass on the bound target native.
"""

from __future__ import annotations


TRUSTED_REFINEMENT_EVIDENCE_DIGEST: str | None = "47ba88d5fa9e7521f66ea7f377413d495fd1b11cf9dc09e24a60f96ab63631cd"
TRUSTED_REFINEMENT_EVIDENCE_CAPSULE: dict[str, object] | None = {'artifact_schema': 'rtdl.fixed_radius_graph.refinement_evidence.v4',
 'artifact_sha256': '47ba88d5fa9e7521f66ea7f377413d495fd1b11cf9dc09e24a60f96ab63631cd',
 'dependency_source_sha256': {'src/rtdsl/action_api.py': '11b3460ddf506a1081d1e0f0a07d4495c9155d9cfb2698fddeb92b61b4822d4d',
                              'src/rtdsl/action_native_identity.py': 'ea04d58313be4046c5794326a8bcdb521130d297407ac5fe4be688da79d01ee8',
                              'src/rtdsl/component_partition.py': '16cd1414f9bf8b94da50678c9409f129d9c6dc1591dc284016b6ce7151d41047',
                              'src/rtdsl/fixed_radius_graph_compiler.py': '362fd14f4fa66cf33c7c9e8347a0b583bb35ae467c0a9347b78cb73034865ddd',
                              'src/rtdsl/optix_runtime.py': 'f27859dd5de5401fcd7da590ddf5d3dbef4b8d51363af9d9b7cd54d821fd32ea',
                              'src/rtdsl/partner_adapters.py': '17a995b314abed08ab5865ca3391a372ef5a7d4272538754edb84da3fd9424d1',
                              'src/rtdsl/predicate_aware_boundary_union.py': 'ca8fbab66be0dfd614ab958428b783cfb46030f54d08da20c0dfac97f6ec6601'},
 'executable_identity_digests': {'complete_pair_candidate_enumeration.v1': 'c08229fc83931a4fbe40dc3db57d31bee5d050f0277f13b67e16b9407775e0e8',
                                 'prepared_spatial_radius_producer.v1': 'b354a1cf189b720143f184a01939012fca35a974f3090f8ee1aeadaa4a0c8785'},
 'independent_reference_digest': '7e52b42d1b2235110a9925540bbf59bea016261fc8bf64142a5a6d22b2ca53ea',
 'native_evidence_identity': {'binary_sha256': '74fbb7c573bd020052a5c8b7dac8f11c6adecec0f29b655694bc4f39932566c5',
                              'optix_version': [9, 0, 0],
                              'required_symbols_digest': 'd185ab86a79b5f328f73060c6f71dccecc5571232a322411b1911cd8c8ace2fa'},
 'schema': 'rtdl.fixed_radius_graph.refinement_evidence_capsule.v1',
 'verified_case_count': 17}


__all__ = [
    "TRUSTED_REFINEMENT_EVIDENCE_CAPSULE",
    "TRUSTED_REFINEMENT_EVIDENCE_DIGEST",
]
