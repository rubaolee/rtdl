# Call For Review: Phoenix V3 RTDBSCAN Component-Signature Optimized RTX Evidence

Please critically review whether the optimized RTDBSCAN component-signature
same-contract RTX evidence can become a Phoenix V3 M7-qualified row-scoped
claim.

Review packet:

```text
docs/rebuild/v3/phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2026-06-21.md
docs/rebuild/v3/phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2026-06-21.json
```

Raw copied evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_component_signature_optimized_20260621/summary.json
docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_component_signature_optimized_20260621/summary.md
docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_component_signature_optimized_large_repeat5_20260621/summary.json
docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_component_signature_optimized_large_repeat5_20260621/summary.md
```

Question:

Does the evidence justify exactly one row-scoped M7 claim for the generic
`component_union` capability, with wording limited to the same-contract
component-signature route, or should it remain internal/not-M7?

Facts to check:

- RTX pod: NVIDIA RTX 4000 Ada Generation.
- Serious same-contract rows: 65,536 / 262,144 / 524,288 points.
- Full-path OptiX-over-Embree speedups after the large repeat=5 repair:
  1.235686x / 1.123550x / 1.101995x.
- 4,096-point validation control passes CPU reference parity.
- Large canonical component signatures match with repeat=5/warmup=1.
- Large-row correctness is OptiX/Embree intra-run canonical component-signature
  agreement, not independent CPU reference validation.
- The dataset is zero-noise four-cluster synthetic `clustered3d`.
- The optimized OptiX route records no point-id or core-flag host materialization
  for the compact signature.
- Continuation still dominates the 262,144 and 524,288 OptiX rows.

Please return:

1. Verdict: approve row-scoped M7, approve only with changes, or reject.
2. Required wording boundary.
3. Any missing evidence before public docs may mention the row.
4. Whether the packet correctly avoids RTDBSCAN paper, full DBSCAN, broad V3,
   and V2 comparison claims.
