# Goal5132 - X-HD Stanford Graphics Same-Source Acquisition

## Verdict

`xhd_stanford_graphics_same_source_acquired__gate_not_yet_run`

## Purpose

Goal5132 starts the first Level B same-source representative path selected by
Goal5131. It acquires the public Stanford graphics meshes for Dragon and
HappyBuddha, records hashes and PLY header counts, and identifies the next
bridge work needed before a correctness gate can run.

This is not a correctness gate and not a performance result.

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford/README.md
Paper-reproduction-apps/x-hd-paper/results/xhd_stanford_graphics_acquisition_2026-07-08.json
```

The raw archives and extracted PLY files are local external data under:

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford/
```

They are intentionally ignored by git; the manifest records source URLs and
hashes instead.

## Acquired Archives

| Dataset | URL | Bytes | SHA256 |
| --- | --- | ---: | --- |
| Dragon | `https://graphics.stanford.edu/pub/3Dscanrep/dragon/dragon_recon.tar.gz` | 11197764 | `74AC1D90989C9B1732EDEE82D57E9CE71452144CF4355F108D8C9C616D28D02F` |
| HappyBuddha | `https://graphics.stanford.edu/pub/3Dscanrep/happy/happy_recon.tar.gz` | 14456495 | `409CD294EFBFD8244E15A382B95A9423F153B7776E736C9B09F19EC9D3C10ED0` |

## Full-Resolution PLY Headers

| Dataset | File | Vertices | Faces | SHA256 |
| --- | --- | ---: | ---: | --- |
| Dragon | `dragon_vrip.ply` | 437645 | 871414 | `FEA87FF48F2ABA22FB53E7B67C3FF3F7B8C2A3B3A0653AF62C48BBA67C6D5744` |
| HappyBuddha | `happy_vrip.ply` | 543652 | 1087716 | `2283371216D748A08376A3C88698E283CC8F18D10CED348D6D133051BCF217AB` |

These vertex counts match the scale of the paper's Table 1 graphics rows
(`Dragon` about `0.4M`, `HappyBuddha` about `0.5M`). This is useful evidence
for same-source selection, but it is still not exact paper dataset proof.

## Reduced-Resolution Files Available

The Stanford archives also contain reduced PLY files:

| Dataset | File | Vertices | Faces |
| --- | --- | ---: | ---: |
| Dragon | `dragon_vrip_res2.ply` | 100250 | 202520 |
| Dragon | `dragon_vrip_res3.ply` | 22998 | 47794 |
| Dragon | `dragon_vrip_res4.ply` | 5205 | 11102 |
| HappyBuddha | `happy_vrip_res2.ply` | 144647 | 293232 |
| HappyBuddha | `happy_vrip_res3.ply` | 32328 | 67240 |
| HappyBuddha | `happy_vrip_res4.ply` | 7108 | 15536 |

These are good candidates for a bounded Level B gate because the current exact
RTDL reference path materializes pairwise rows and full-resolution
Dragon x HappyBuddha would require roughly 238 billion candidate rows.

## What Was Learned

1. The graphics source family is accessible and small enough to acquire locally.
2. Dragon and HappyBuddha full-resolution vertex counts match the paper scale.
3. Current X-HD gates are still WKT-only.
4. The author binary can accept `ply`/`off` by contract, but the local gate
   runner currently forces `-input_type wkt`.
5. RTDL's current exact columnar route is a correct reference route, not a
   scalable X-HD RT-core algorithmic route.

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- representative same-source correctness;
- author `hd_exec` success on these PLY files;
- RTDL route success on these PLY files;
- performance ratio;
- paper Figure 5 graphics reproduction.

## Next Work

Goal5133 should be an app-owned PLY input bridge and bounded graphics gate:

1. add a PLY vertex loader for app fixtures;
2. extend the author gate runner so `input_type=ply` is a parameter;
3. run author `hd_exec` on a reduced-resolution Dragon/HappyBuddha pair on POD;
4. run RTDL exact/reference route only on bounded reduced-resolution or sampled
   data;
5. keep the label Level B same-source representative.
