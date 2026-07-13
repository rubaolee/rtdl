# X-HD Data Provenance

This directory records data provenance for the X-HD paper app.

Current status:

```text
same-input directed HDResult reproduction complete and externally approved;
exact original paper input bytes and all-figure reproduction remain unavailable
```

Public sources located:

- paper page: `https://gengl.me/publications/ics26/`
- ACM DOI: `https://doi.org/10.1145/3797905.3800509`
- PDF: `https://rubaolee.github.io/paper_pdfs/2026-xhd.pdf`
- author repository: `https://github.com/pwrliang/X-HD`

Pinned source snapshot:

```text
commit=7bf41c8442d059c94f4178355c6d5a10571d9658
branch=main
```

Author repository evidence:

- `README.md` documents `hd_exec` and `variant=rt`;
- `src/flags.cc` documents input flags, execution variants, and JSON output;
- `src/main.cpp` maps `variant=rt` to `Variant::kRT`;
- `src/run_hausdorff_distance.cu` writes `HDResult`, `Running.AvgTime`, and
  `Running.Repeats`;
- `src/hd_impl/hausdorff_distance_rt.h` writes X-HD iteration phase fields such
  as `RTTime`, `CUDATime`, `OffloadingSize`, and bounds.

The repository includes many JSON logs under:

```text
expr/logs/
```

Those logs are useful schema/performance evidence, but they are not a substitute
for the actual paper input files. Paper input provenance remains open.

First bounded data target:

```text
small same-input WKT or PLY fixture accepted by author hd_exec
```

The first fixture is deliberately tiny, deterministic, and easy to verify with
a brute-force CPU Hausdorff implementation:

```text
fixtures/tiny2d_a.wkt
fixtures/tiny2d_b.wkt
fixtures/tiny2d_expected.json
```

Expected result:

```text
directed_a_to_b = 1.0
directed_b_to_a = 1.0
hausdorff       = 1.0
tolerance       = 1e-9
```

This fixture packet was executed with author `hd_exec` and the RTDL route. It
is retained as bounded same-input evidence. Goal5451 extends the approved
same-input directed-HDResult matrix to seven primary cases, while preserving
each case's actual input-identity level.

Forbidden wording:

```text
exact paper input
paper figure reproduced
X-HD performance reproduced
```

until the exact dataset and comparator are pinned.
