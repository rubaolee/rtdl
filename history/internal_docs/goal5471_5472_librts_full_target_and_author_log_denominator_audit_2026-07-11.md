# Goals5471-5472: LibRTS Full Target And Author-Log Denominator Audit

Date: 2026-07-11

Status:

```text
completed_full_target_and_author_log_audit__exact_inputs_not_acquired__review_pending
```

## Objective

Move the LibRTS paper app from bounded operation gates to a precise full-paper
work plan without downloading the 23.1 GB Zenodo archive or spending a POD
before the evidence says either is necessary.

The audit answers:

1. What are the final paper's actual reproduction targets?
2. Which author scripts and logs correspond to each target?
3. Which denominator does each figure use?
4. Are author target values available without the exact datasets?
5. What remains missing before an author/RTDL performance comparison is fair?

## Provenance

The official AE repository was shallow-cloned without recursive submodule
contents or datasets:

```text
repository: https://github.com/RTSpatial/PPoPPAE
HEAD: d605fe1bd5708cbf3c457a3a9698e0cc7bcdc14b
checkout size: about 110 MB
RTSpatial submodule: 7c54c181b1058c87768767998c00e225cc58666e
RayJoin submodule: 2151f56d09cbcfd4edbff259d97ac3123705411b
SpatialQueryBenchmark submodule: 9140ad997519713bb5fdceba639a357afa4609ad
paper_logs.zip SHA-256: d44d3c31fe14387c97b51229d1b9f99770efd4ca94334f76954885336a5fd655
```

The official paper states that the intended reproduction machine is Linux with
an RTX 3090, at least 24 GB VRAM, driver 535+, CUDA 12+, and about 64 GB RAM.
The current GTX 1070 is valid for bounded functional evidence, not full-paper
performance reproduction.

## Figure-Numbering Trap

The final paper and AE output filenames cannot be matched mechanically by
number. The source-verified mapping is:

| Final paper | Scientific target | AE output |
|---:|---|---|
| Figure 6 | Point query | `fig7.pdf` |
| Figure 7 | Range-Contains | `fig8.pdf` |
| Figure 8 | Range-Intersects | `fig9.pdf` |
| Figure 9 | Ray-Multicast | `fig10.pdf` |
| Figure 10 | Build/mutation/update sensitivity | `fig12.pdf` |
| Figure 11 | Scalability | `fig11.pdf` |
| Figure 12 | PIP application | `fig13.pdf` |

In particular, update and scalability are not ordered monotonically in the AE
filenames. Future reports must identify the scientific target and source script,
not infer semantics from `figN.pdf` alone.

## Author Evidence Available Now

`expr/query/paper_logs.zip` contains 264 real author/baseline log files in 54
experiment categories. Every final-paper target from Figure 6 through Figure 12
has corresponding checked-in author logs.

| Paper figure | All log records | RTSpatial records | Author source |
|---:|---:|---:|---|
| 6 | 60 | 10 | `query.sh`, point-contains |
| 7 | 40 | 10 | `query.sh`, range-contains |
| 8 | 88 | 22 | `query.sh`, range-intersects |
| 9 | 6 | 6 | `query.sh`, vary parallelism |
| 10 | 28 | 28 | `update.sh` |
| 11 | 30 | 30 | `scalability.sh` |
| 12 | 12 | 4 | `pip.sh` |

These logs are author reference targets. Their presence is not RTDL
reproduction and does not remove the exact-input blocker.

## Denominator Matrix

The plotting/source audit establishes:

| Figure | Denominator used by author plot |
|---:|---|
| 6 | internal `Query Time`; index `Loading Time` excluded |
| 7 | internal `Query Time`; index `Loading Time` excluded |
| 8 | internal `Query Time`; incoming-query BVH construction included |
| 9 | per-k forward cast + query BVH build + backward cast; prediction separate |
| 10 | mixed: build `Loading Time`, mutation throughput, update slowdown ratio |
| 11 | internal `Query Time`, including result storage |
| 12 | end-to-end PIP = `Loading Time + Query Time` |

There is no single author-time denominator across the paper. Any future RTDL
comparison must select and reproduce the figure-specific denominator instead of
placing route wall, process wall, and author internal time in one ratio.

## Ray-Multicast Author Targets

The six Figure-9 logs each contain ten sweep points. Log indices `0..9` are
`log2(k)`, so the machine-readable audit normalizes them to actual
`k=1,2,...,512`.

Example, USCensus:

```text
k=1: 24.26 ms
k=16: 3.101 ms
predicted k: 32
prediction time: 0.11 ms
```

This agrees with the paper narrative after normal rounding. It also sharpens
Goal5470's interpretation: the author technique is real on the exact paper
workload/hardware, while RTDL's temporary current-row-route implementation did
not transfer that benefit on the GTX 1070 controls. Goal5470 remains a no-go for
that RTDL execution model, not a refutation of the paper.

## Dataset State

The AE source pins three independently downloaded archives:

| Archive | MD5 |
|---|---|
| polygons | `d5c2a8053fd0b7359a5b83391f7d0b82` |
| queries | `64b560c3d067262b7ef7d7422c64225a` |
| synthetic | `ebe7dcf4001132d297a8022c110cedeb` |

The audit checkout has no `.datasets` marker and no exact input files. Direct
HEAD probes against the three SharePoint links returned 401; this does not prove
the author `onedrivedownloader` path is broken, because that path uses a
different resolution flow. The 23.1 GB Zenodo package was not downloaded.

Therefore:

```text
author target values available = true
exact paper inputs available = false
full paper reproduction complete = false
POD required for the next audit step = false
performance ratio authorized = false
```

## Current RTDL Coverage

| Paper target | Current strongest RTDL evidence |
|---|---|
| Figure 6 | bounded same-input point count |
| Figure 7 | bounded direction-discriminating contains count |
| Figure 8 | bounded predicate-discriminating exact intersects rows |
| Figure 9 | source/reference contract; native current-row spike no-go/reverted |
| Figure 10 | bounded mutation sequence + generic sparse-refit system speedup |
| Figure 11 | not reproduced |
| Figure 12 | one Level-B representative same-input PIP relation gate |

This is substantial semantic and system evidence, but it is not a reproduced
paper figure matrix.

## Next Decision

The next action is not another RTDL kernel optimization and not a POD run.

1. Probe the official dataset resolver without downloading full payloads if
   possible, recording archive size/access metadata.
2. If exact inputs are obtainable within owner resource bounds, acquire the
   smallest archive needed for one exact same-input figure gate first.
3. If exact inputs are not presently obtainable, select one explicitly bounded
   same-input figure-shaped gate using available data, without calling it exact
   paper reproduction.
4. Request an RTX 3090-class 24 GB POD only after inputs and a same-denominator
   command are ready.

## Claim Boundary

Authorized:

- the official full target/source/log matrix is pinned;
- 264 author logs cover all final-paper Figures 6-12;
- figure-specific timing denominators are identified;
- exact datasets are not currently acquired.

Not authorized:

- any paper figure reproduced by RTDL;
- exact paper dataset identity;
- author-vs-RTDL performance ratio;
- RTX 3090 performance evidence from GTX 1070;
- treating checked-in author logs as RTDL results;
- reintroducing Embree.
