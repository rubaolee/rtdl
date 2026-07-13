# Call For Review: Goal4867 Duplicate Half-Edge Contract Before Continuing Section 5.7

## Requested Verdict Labels

Choose one:

- `approve_define_deterministic_duplicate_half_edge_contract_then_continue`
- `block_until_author_duplicate_half_edge_contract_is_obtained`
- `approve_author_traversal_compatibility_only_with_explicit_limitation`
- `reject_current_direction_as_overfitting`

## Context

We are trying to reproduce RayJoin Section 5.7 Block x Water using RTDL/OptiX/Python/Numba-facing machinery, comparing against AuthorPatch.

We have narrowed the current correctness issue away from:

- LSI count/path,
- output formatting only,
- normal same-height/different-slope PIP SoS,
- midpoint face overwrite,
- AABB height/final rounding,
- block-merge64 grouping existence,
- GAS compaction.

The active issue is duplicate half-edge point-location:

- same vertical hit height,
- same scaled line coefficients `(a, b, c)`,
- opposite directed half-edges / different adjacent faces,
- same slope, so the author `t_reported` slope perturbation cannot distinguish them.

## Key Evidence

Status note:

`history/internal_docs/goal4867_block_water_section57_controlled_debug_status_2026-07-02.md`

Micro probe:

`history/internal_docs/goal4867_duplicate_half_edge_micro_probe.py`

POD artifact:

`/workspace/goal4867_duplicate_half_edge_micro_probe.json`

Micro probe result:

```json
{
  "records": [
    {
      "case": "forward_then_reverse",
      "input_segment_ids": [100, 200],
      "face_id": 0,
      "segment_id": 100
    },
    {
      "case": "reverse_then_forward",
      "input_segment_ids": [200, 100],
      "face_id": 22,
      "segment_id": 200
    }
  ]
}
```

This proves the selected face/segment can change when only duplicate half-edge input order changes.

Block x Water witness after latest repairs:

`/workspace/goal4867_specific_pip_probe_after_actual_compaction.json`

| point index | current RTDL face | current segment | status |
|---:|---:|---:|---|
| 1069665 | 323443 | 15220835 | matches expected witness |
| 5693875 | 0 | 828110 | still suspect; author output contains this coordinate in kept chains |
| 7386601 | 0 | 880129 | matches corrected witness; avoids previous spurious chain |
| 7906217 | 38799 | 1839712 | matches expected witness |
| 9926545 | 0 | 16153901 | matches expected witness |

The still-suspect `5693875` candidate pair:

- edge 827259 / segment 827260 / face-by-direction 17144;
- edge 828109 / segment 828110 / face-by-direction 0;
- identical scaled `(a, b, c)` and same slope.

Author output contains:

```text
2540635 2 2528349 2528350 180035 179975
-121.746176 36.810027
-121.746818 36.808321
2540636 2 2528350 2528351 180035 179975
-121.746818 36.808321
-121.747041 36.807702
```

So this point is output-relevant.

## Author Source Fact

The author clarification/patch encodes slope preference into `t_reported`.

It handles same-height/different-slope pruning, but it does not define a second-order rule for exact same-line duplicate half-edges. In the author source, same-slope duplicates are effectively left to traversal/source order after the slope perturbation has no separating power.

## Question For Review

What is the correct engineering next step?

1. Define a deterministic generic directed-planar-map duplicate-half-edge contract in RTDL, even if it can differ from the original author traversal artifact.
2. Treat exact AuthorPatch byte reproduction as requiring author traversal compatibility for this undefined case, and label that limitation explicitly.
3. Block until a new author clarification supplies the intended same-line duplicate-half-edge rule.
4. Another option.

## Constraints

- No RayJoin-only output patch.
- No hard-coded dataset point/edge exceptions.
- Any fix must be a generic directed point-location / planar-map contract repair.
- If the selected contract knowingly differs from the AuthorPatch traversal artifact, Section 5.7 exact-byte reproduction must not be claimed.

## Specific Review Questions

1. Is the diagnosis credible that the remaining bug is duplicate half-edge PIP contract, not LSI/writer/normal SoS?
2. Does the micro probe sufficiently prove order-dependent duplicate-half-edge behavior?
3. Is it valid to introduce a deterministic duplicate-half-edge contract as a generic RTDL core repair?
4. If yes, what contract should be used?
5. If no, should the line be blocked pending author clarification?
6. Is exact AuthorPatch byte reproduction still a valid target if the author behavior is traversal-order-dependent in this case?
7. What is the smallest next experiment you would require before another full Block x Water run?
