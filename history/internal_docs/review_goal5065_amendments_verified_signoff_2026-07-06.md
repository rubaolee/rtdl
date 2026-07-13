# Review Sign-Off: Goal5065 Amendments Verified

Date: 2026-07-06

## Verdict

```text
amendments_verified__authorize_goal5066_contract_schema_only
```

## Review Source

This sign-off records the post-amendment verification of the external review for:

- `history/internal_docs/review_goal5065_rt_barneshut_hierarchy_traversal_api_design_2026-07-06.md`
- `history/internal_docs/goal5065_review_amendment_response_2026-07-06.md`

The original review verdict was:

```text
approve_with_required_amendments
```

This follow-up sign-off verifies that the blocking findings and required amendments were addressed.

## Verified Amendments

### BF-1: `BarnesHutOpening` Naming Contradiction

Status: verified fixed.

The public design no longer proposes `BarnesHutOpening`. The generic opening policy name is now:

```text
SizeDistanceOpening(max_ratio=...)
```

The old name is retained only in review/amendment-history text as a historical reference, not in the proposed public API.

### BF-2: Completion Boolean Conflict

Status: verified fixed.

The app manifest separates full paper completion from bounded same-input completion:

```json
{
  "paper_reproduction_complete": false,
  "bounded_same_input_reproduction_complete": true
}
```

This prevents bounded same-input success from being misread as full paper reproduction.

### RA-1: Narrow Timing Ratio Must Carry Whole-Envelope Context

Status: verified fixed.

The RTDL narrow kernel ratio is now paired with the broader reported envelope:

```text
RTDL resident kernel min ~= 1.1905 ms
Author rt_core_force ~= 5.579 ms
Narrow ratio ~= 0.2134x

RTDL prepare + transfer + compile + kernel ~= 336.98 ms
Author preprocessing + execution ~= 99.91 ms
Whole envelope ~= 3.37x slower for RTDL
```

The report and README state that the whole-envelope comparison is not favorable to RTDL.

### RA-2: Min-Vs-Single Sampling Caveat

Status: verified fixed.

The design records that the narrow 0.2134x figure uses RTDL minimum over the author's single reported force value. It also reports the RTDL mean ratio:

```text
1.2389567852020265 / 5.579 ~= 0.2221
```

Future gates use the RTDL mean baseline.

### RA-3: Non-Isomorphic Genericity Proof

Status: verified fixed in plan.

Goal5070 now requires a substantially different reducer and opening policy. Another inverse-square force-field route is explicitly not sufficient as genericity proof.

### RA-4: Quantified Regression Gate

Status: verified fixed.

The Goal5069 migration gate is quantified as:

```text
resident_kernel_mean <= 1.37 ms
```

This is approximately +10% over the existing RTDL mean baseline.

## Authorization Boundary

Goal5066 is authorized only as contract/schema work:

- `AggregateHierarchy3D`
- `PreparedAggregateHierarchy3D`
- `SizeDistanceOpening`
- generic reducer contracts
- generic continuation columns
- aggregate-frontier reduce execution contract

Not authorized by this sign-off:

- backend rewrite
- native CUDA/OptiX implementation
- author comparator promotion into RTDL core
- `author-optix-payload` promotion into RTDL core
- full paper reproduction claim
