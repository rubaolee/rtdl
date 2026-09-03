# Goal5842R1 Premeasurement Plan: Public Reuse and Scalar-Only Triangle Lowering

Date: 2026-09-03

## Purpose

Repair implementation costs exposed by the frozen Goal5842 V12 experiment
without weakening generic admission or changing any V12 evidence. The repair is
app-neutral and has two parts:

1. expose the existing content-addressed formal-leaf cache as an explicit
   `V4Toolchain` policy rather than requiring process-global environment
   variables;
2. connect the public checked-U64 triangle scalar contract to the existing
   native device-resident product/sum ABI, leaving per-ray and event-row output
   behind an explicit diagnostic flag.

The prepared owner remains the unit of target and input reuse. One owner builds
its target once, uploads an exact immutable query batch once, and reuses both
for subsequent executions. This goal does not add a cross-process GPU-handle
cache: OptiX contexts, pipelines, GAS objects, and device pointers are
process-local resources.

## Pre-existing observations

This is not a blind experiment. Before this plan, an unregistered engineering
probe on the frozen A6000 checkout observed that the already implemented hidden
leaf cache reduced fresh-process materialization from about 6.0 seconds to
about 0.29 seconds for relation and from about 3.3 seconds to about 0.23 seconds
for triangle. Goal5842 V12 also already showed adverse public triangle steady
performance and identified host per-ray materialization/reduction as avoidable.

Those observations motivated the implementation. They are not accepted as this
goal's result, are not pooled with the planned samples, and define no pass
threshold.

## Frozen boundary

- Goal5842 V12 source commit, archives, recounts, and authorities remain
  byte-for-byte unchanged.
- The three Goal5838 frozen semantic-core files remain unchanged.
- The native engine keeps only generic callback status and checked-U64
  reduction behavior. No graph, triangle-counting, database, or application
  semantic is introduced.
- The diagnostic route remains available as
  `include_diagnostics=True`; the ordinary public scalar route defaults to
  `False` and must not expose per-ray or event rows.

## Functional gates before GPU timing

1. Explicit cache policy overrides any process-global cache environment and
   retains exact key, PTX audit, manifest digest, membership, and read-only
   checks.
2. Public `V4Toolchain` passes the policy through both admitted protocol
   compilers.
3. Scalar execution calls the native device reduction ABI and never calls the
   diagnostic execute ABI or host reduction helper.
4. Scalar and diagnostic outputs match the same exact oracle.
5. A malformed native product summary fails before cache publication or public
   output construction.
6. Non-Boolean diagnostic mode requests fail closed.

## GPU diagnostic

The owner supplied one RTX A6000 endpoint. The run uses the existing Goal5842
triangle workload, exact native-library bytes, one clean Git commit, and the
runner `scripts/goal5842r1_public_reuse_scalar_pod_runner.py`.

The runner records:

- three uncached materializations;
- one explicit cache fill;
- three explicit cache-hit materializations;
- separately timed scalar and diagnostic native prepare;
- one first execution for each route;
- eight untimed warmups and 64 alternating timed steady executions per route;
- exact scalar and full diagnostic per-ray oracle checks;
- execution receipts proving whether input reuse and host detail materialization
  occurred.

All raw samples are retained. Medians are descriptive. There is no speedup
threshold, no retry-on-adverse rule, and no permission to discard an
unfavorable row.

## Required conclusions

The goal can close technically only if the functional gates pass and one clean
GPU run records exact correctness. A faster scalar median is useful evidence,
but is not itself a completion condition. A slower or equal result must be
retained and explained.

The result may support an internal statement that the implementation now avoids
host per-ray output for the public scalar contract. It cannot authorize a
public speedup, intrinsic-language, application, Paper App, usability, or CGO
claim. A fresh fair Direct/PyOptiX/RTDL baseline and deferred external review
remain separate manuscript gates.
