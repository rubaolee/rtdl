# RayJoin Reproduction Packet

Status: current bounded RTDL v2.14 RayJoin reproduction packet.

This packet is the reader-facing index for the current RayJoin reproduction
evidence. It links the low-level Section 5.2 and 5.3 evidence, the Section 5.7
overlay evidence, the comparator disclosure, and the performance boundary.

## Short Answer

RTDL v2.14 has a bounded RayJoin reproduction:

- Section 5.2 LSI is reproduced for the available and representative pairs
  listed in the reproduction reports.
- Section 5.3 point-location/PIP has exact raw-author evidence on the strongest
  available US pairs and bounded representative evidence for the remaining
  public-source line.
- Section 5.7 polygon overlay has two available paper-style pairs and two
  current-source representative pairs matching the documented comparator.

This is a correctness and engineering-reproduction packet. It is not a broad
RTDL speedup claim.

## Evidence Index

| Topic | Reader-facing page |
| --- | --- |
| Section 5.7 bounded public page | [RayJoin Section 5.7 Bounded Reproduction](rayjoin_section57_bounded_reproduction.md) |
| Comparator boundary | This page, "Comparator Boundary" |
| Programming shape | This page, "Programming Shape" |
| Performance boundary | This page, "Current Performance Boundary" |

## Comparator Boundary

The current overlay comparator is the documented author-contract comparator:
the author source plus deterministic contract updates needed to make ambiguous
degenerate cases reproducible.

Use that disclosure when reading any Section 5.7 byte-equality statement. In
particular, duplicate-half-edge ambiguous cases are equality against the
deterministic comparator, not a claim about every unpatched historical author
binary behavior.

## Programming Shape

The current public RTDL route uses generic planar-map primitives:

```text
public planar-map LSI
-> public planar-map point-location / PIP
-> Python or partner continuation owned by the app
-> app output writer
```

The public primitive front doors are:

```python
prepare_planar_map_lsi_2d_optix(...)
prepare_planar_map_point_location_2d_optix(...)
prepare_planar_map_workspace_2d_optix(...)
```

The application layer owns RayJoin-specific file choices, command parameters,
output-chain formatting, and representative-vs-exact labeling.

## What This Packet Does Not Claim

Do not read this packet as:

- a full all-eight exact hidden-input Section 5.7 reproduction;
- a broad RTDL speedup over the author program;
- proof that Python text output formatting is performance-optimal;
- proof that Numba closes the remaining RayJoin output gap;
- permission to hide RayJoin-specific semantics inside RTDL core.

## Current Performance Boundary

Correctness is now much stronger than performance.

For paper text-output runs, Python output-chain formatting remains expensive
and should not be presented as solved. That text-output route exists as a
byte-equality correctness anchor.

For the writer-free binary route, the text writer is removed and RTDL is
measured as a pipeline operator. On the current top4 County x Zipcode
representative input, the bounded v2.14.3 evidence is:

| Route boundary | Timing interpretation |
| --- | --- |
| Warm-process fresh writer-free route | About `4.22s`; includes LSI production and first-use app-layer setup, but excludes cold Python/CUDA process startup. |
| Prepared LSI base-session, six distinct query batches | Current v2.14.3 operator-body evidence is about `0.755s` for the six-batch sum after generic native lexsort and atomic-append device carrier construction. |
| Prepared/cached LSI replay diagnostics | Diagnostic only; not a fresh overlay result. |

The warm-process fresh route is the conservative long-lived-process one-shot
boundary; cold CLI startup is a separate runtime-startup cost and must not be
hidden inside the `4.22s` wording. The prepared LSI base-session route is a
separate pipeline-style boundary: it measures one prepared base session consumed
by multiple distinct chain-contiguous query batches as binary descriptors, not a
paper text-output run. Within that prepared route, descriptor ordering and
carrier construction have been reduced; the remaining stable floor is mainly LSI
pair-id production plus downstream binary continuation work.

No author overlay-compute denominator has been measured for the top4
representative input. Do not reuse a smaller public-sample author timing as a
top4 performance ratio.

Further optimization must keep these route boundaries separate.
