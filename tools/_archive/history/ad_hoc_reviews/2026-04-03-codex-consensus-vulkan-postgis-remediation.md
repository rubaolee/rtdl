# Codex Consensus: Vulkan/PostGIS Remediation

Date: 2026-04-03
Status: accepted by 2-AI external review plus Codex review

## Consensus

- Gemini: `APPROVE`
- Claude: `APPROVE`
- Codex: `APPROVE`

## Final decision

1. Keep the Vulkan backend on `main`, but treat it as provisional rather than fully accepted.
2. Accept the remediation patch that:
   - fixes Vulkan output-capacity guardrails
   - expands committed Vulkan workload coverage
   - downgrades Vulkan readiness wording
   - updates Goal 50 docs/tests to enforce indexed PostGIS query mode
3. Reject the previously running remote PostGIS measurement because it did not use the required `geom &&` predicate and therefore was not a fair indexed-database comparison.

## Residual boundary

- Goal 50 itself is still in progress. The accepted change in this round is the policy/test/doc correction, not the final PostGIS benchmark result.
