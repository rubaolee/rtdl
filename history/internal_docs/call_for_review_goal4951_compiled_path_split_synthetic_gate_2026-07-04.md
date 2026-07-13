# Call For Review: Goal4951 Compiled Path-Split Synthetic Gate

Date: 2026-07-04

Review target:

- `history/internal_docs/goal4951_compiled_path_split_synthetic_gate_2026-07-04.md`
- `history/internal_docs/goal4951_compiled_path_split_spike.py`
- `tests/goal4951_compiled_path_split_spike_test.py`

Requested verdict label:

`approve_goal4951_gate_a_b_authorize_gate_c`

or, if blocked:

`block_goal4951_gate_c_until_amended`

## Context

Goal4951 is the first Layer 3 implementation spike after Layer 1/2 was closed
as capability success but RayJoin performance no-go.

The approved Goal4951 plan required:

- no app-identity semantics in the compiled materializer;
- no binary map / map0-map1 assumption;
- non-RayJoin synthetic correctness before any RayJoin app wiring;
- no public API productization before the performance gate.

This packet claims only Gate A and Gate B completion. It does not claim RayJoin
byte equality or performance.

## Questions For Reviewer

1. Does `goal4951_compiled_path_split_spike.py` satisfy the genericity boundary
   for this internal spike, or does it hide RayJoin / overlay / Section 5.7
   assumptions?

2. Is the source genericity gate sufficient for this phase, especially the
   absence of `rayjoin`, `overlay`, `section57`, `author`, `map0`, and `map1` in
   the spike source?

3. Is the non-RayJoin synthetic test sufficient to prove Gate B before RayJoin
   app wiring?

4. Does the POD evidence avoid the earlier archive-tree / fake-clean problem?
   Specifically, is it acceptable that the POD Git checkout is at
   `7d30acd19ab253116fe210949918ec2bb5b987a8` and has only the two Goal4951
   files as untracked additions?

5. Does the packet correctly avoid claiming RayJoin correctness, writer
   speedup, public API readiness, or release status?

6. Should Gate C be authorized: wire the compiled materializer into the RayJoin
   paper reproduction app as an app adapter, require byte equality, and only
   then measure writer speedup?

7. If not authorized, what exact amendment is required before Gate C?

## Non-Authorization Boundary

Approval of this packet would authorize only Goal4951 Gate C. It would not
authorize:

- default route promotion;
- public API exposure;
- broad performance claims;
- RayJoin correctness claims before byte equality;
- any app-specific output formatting in RTDL core.
