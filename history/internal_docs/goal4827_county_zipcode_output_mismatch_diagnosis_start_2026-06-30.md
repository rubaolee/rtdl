# Goal4827 County x Zipcode Output Mismatch Diagnosis Start

Date: 2026-06-30

## Authorization

Goal4827 is authorized by Antigravity review of Goal4826:

`approve_goal4826_correctly_blocks_county_zipcode_and_authorize_goal4827_mismatch_diagnosis`

## Purpose

Diagnose why the current repaired RTDL line completes County x Zipcode overlay
but does not match the author baseline byte-for-byte.

This goal remains on the current v2.14-centered RTDL product line. It is not V4
continuation.

## Starting Evidence

Goal4826 after finite-query repair:

| Item | Current RTDL | Author baseline |
|---|---:|---:|
| SHA256 | `5a1808def771992e6532bbd1edd05a9625531b9e39a235578a11b5e29c395267` | `e8fed3e7e4691c028ee6c8e8a16a74eb06de5a0ffb20cc2b132ce8646b797b2a` |
| bytes | `2,388,737,142` | `2,390,767,769` |
| chain count | `29,253,910` | old author/Goal4806 report: `29,254,027` |
| face count | `115,515` | old author/Goal4806 report: `115,490` |

Goal4826 fixed the nonfinite midpoint crash, but did not restore
byte-equality.

## First Difference Probe

Remote probe:

`/workspace/rtdl_goal4820_sos_fix/artifacts/goal4826_county_zipcode_current_revalidation/first_line_diff_probe.json`

Result:

```json
{
  "first_different_line": 25,
  "rtdl_line": "9 1 8 8 5 6",
  "author_line": "9 2 8 9 1 2"
}
```

The first eight output chains are identical. The first mismatch starts at chain
9.

## First 12 Chain Probe

Remote probe:

`/workspace/rtdl_goal4820_sos_fix/artifacts/goal4826_county_zipcode_current_revalidation/first12_chain_probe.json`

Key difference:

Author chain 9:

```text
9 2 8 9 1 2
-86.413116 32.707386
-86.413116 32.707386
```

Current RTDL chain 9:

```text
9 1 8 8 5 6
-86.413116 32.707386
```

The problem is not a late-file drift. It appears in the first dozen chains.

## Initial Diagnosis Hypotheses

The leading candidates are:

1. **Coordinate materialization mismatch.** The author may store two distinct
   internal coordinates that print the same at six decimals. Current RTDL may
   materialize them as exactly identical Python floats, causing exact
   deduplication to collapse a two-point chain into a one-point chain.
2. **Output-chain deduplication mismatch.** Current RTDL uses
   `_dedupe_consecutive_points` before writing chains. Removing this blindly is
   risky because earlier Goal4806 explicitly warned that tolerance-based
   deduplication changes author semantics. The right fix must match the
   author's exact materialization and `std::unique` behavior, not simply stop
   deduping.
3. **Face-id creation cascade.** The one-point chain changes
   `create_polygon(...)` ordering, producing different face ids from chain 9
   onward.

## Goal4827 Exit Gate

Goal4827 must identify which of these is the first causal mismatch:

- coordinate materialization;
- dedupe policy;
- midpoint face assignment;
- output-chain face-id creation order.

Performance remains forbidden.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   I would be foolish if I "fixed" this by blindly disabling dedupe just because
   the first diff has a one-point chain.

2. **What actions would make the decision foolish?**
   Changing output semantics before comparing author source behavior; ignoring
   that printed-equal coordinates may be internally distinct; running larger
   data before resolving the first mismatch.

3. **Is there another path that avoids being stuck?**
   Yes. Use the first-difference chain to trace exactly how author and RTDL
   materialize the two points and assign faces.

4. **Can I start a different path that truly solves the problem?**
   Yes. The immediate next step is a focused chain-9 provenance probe: find the
   RTDL intersections and author-style internal coordinates that produce chain
   9, then decide whether the product repair is coordinate materialization,
   dedupe policy, or face assignment.
