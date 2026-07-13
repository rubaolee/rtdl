# RayJoin Paper Reproduction App

This directory is a complete RayJoin paper-reproduction engineering project.
It is parallel to the benchmark-app suite: benchmark apps test RTDL broadly,
while this project reproduces selected RayJoin paper workloads with the
author program, fixed inputs, and RTDL implementations kept together.

The project covers the available Section 5.2, 5.3, and bounded Section 5.7
workloads.

## What Is Included

| Path | Purpose |
| --- | --- |
| `author_patches/` | Patches used to build the project comparator, called `AuthorOfficial`. |
| `data/public_sample_manifest.json` | Download URLs, sizes, and SHA-256 hashes for the public County x Soil sample. |
| `scripts/fetch_public_sample.py` | Downloads and verifies the public sample inputs and answer file. |
| `scripts/setup_author_official.sh` | Clones the RayJoin author repository, checks out the pinned commit, applies the comparator patches, and builds `query_exec` and `polyover_exec`. |
| `scripts/run_author_public_sample.sh` | Runs the patched author binaries for Section 5.2, 5.3, and 5.7 on the public sample. |
| `scripts/run_rtdl_public_sample.sh` | Runs the RTDL implementations for Section 5.2, 5.3, and 5.7 on the same public sample. |
| `scripts/run_full_public_sample.sh` | One-command public-sample reproduction runner: data, author comparator, RTDL implementation, and summary. |
| `section52_lsi.py` | RTDL Section 5.2 LSI runner using the public planar-map LSI primitive. |
| `section53_pip.py` | RTDL Section 5.3 PIP runner using the public directed point-location primitive. |
| `section57_overlay.py` | RTDL Section 5.7 overlay runner using public primitives plus app-layer output-chain assembly. |
| `section57_overlay_numba.py` | Same Section 5.7 route with Numba helpers for selected numeric app-layer continuations. |
| `section57_overlay_columnar_binary.py` | Writer-free numeric/binary Section 5.7 route for pipeline-style downstream consumers; this is not the paper text-output route. |
| `rayjoin_numba_overlay_kernels.py` | Shared Numba kernels used by the Numba Section 5.7 route. |

Generated data, author source/build products, and run outputs are intentionally
kept under local ignored directories:

- `_data/public_sample/`
- `_work/author_official/`
- `_runs/public_sample/`

## Comparator Definition

This project compares against `AuthorOfficial`: the pinned author RayJoin source
plus documented patches.

The patches are:

- `author_clean_compat_cuda12.patch`: modern CUDA/GCC build compatibility only.
- `author_sos_t_reported.patch`: implements the author-derived
  simulation-of-simplicity reported-distance rule so OptiX traversal preserves
  the intended tie-breaking behavior.
- `author_duplicate_half_edge_contract.patch`: documents the RTDL-defined
  deterministic duplicate-half-edge contract used for bounded overlay
  comparison cases.

The duplicate-half-edge rule is a deterministic comparison contract, not a claim
that the raw unpatched author binary used that exact rule.

## RTDL Design Boundary

RTDL provides generic primitives:

- planar-map line-segment-intersection rows/counts;
- directed planar-map point-location/PIP rows/counts;
- prepared/session-style execution where supported.

The RayJoin app owns paper-specific application logic:

- CDB input choices and author-compatible parameters;
- coordinate scaling and output-chain formatting;
- Section 5.7 overlay assembly;
- comparator labels such as exact available input versus representative input.

The public RTDL scripts do not call `rtdsl.rayjoin_overlay`.

## One-Command Public Sample Run

From the repository root on Linux:

```bash
bash Paper-reproduction-apps/rayjoin-paper/scripts/run_full_public_sample.sh
```

Useful environment variables:

```bash
OPTIX_PREFIX=/home/lestat/vendor/optix-dev
CUDA_PREFIX=/usr/lib/cuda
RAYJOIN_CUDA_ARCH=61
RUN_AUTHOR=1
```

`RAYJOIN_CUDA_ARCH` defaults to the detected GPU compute capability, or `61` if
it cannot be detected. The author setup script builds local `gflags` and `glog`
dependencies under `_work/author_official/deps/` when system packages are not
available, so it does not require `sudo`. Set `RUN_AUTHOR=0` to skip
author-binary execution and run only the RTDL side.

The full runner writes:

- `_runs/public_sample/author_official/summary.json`
- `_runs/public_sample/rtdl/summary.json`
- `_runs/public_sample/full_summary.json`

The key public-sample checks are:

- Section 5.7 author output byte-equal to the public answer;
- Section 5.7 RTDL output byte-equal to the same answer;
- Section 5.7 RTDL+Numba output byte-equal to the same answer.

## Individual Commands

Run only RTDL Section 5.2:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rayjoin-paper/section52_lsi.py \
  --poly1 /path/to/base.cdb \
  --poly2 /path/to/query.cdb \
  --expected-count 20860 \
  --expected-count-provenance author_official_public_sample \
  --label br_county_soil \
  --output /tmp/rayjoin_section52_lsi.json
```

Run only RTDL Section 5.3:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rayjoin-paper/section53_pip.py \
  --poly1 /path/to/base.cdb \
  --poly2 /path/to/query.cdb \
  --label br_county_soil \
  --output /tmp/rayjoin_section53_pip.json \
  --chunk-size 500000
```

Run only RTDL Section 5.7:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rayjoin-paper/section57_overlay.py \
  --left /path/to/left.cdb \
  --right /path/to/right.cdb \
  --pair-name br_county_soil \
  --dataset-label available_bounded_pair \
  --output /tmp/rayjoin_section57_overlay.txt \
  --author-output /path/to/answer.txt \
  --summary /tmp/rayjoin_section57_overlay.json
```

Run the Numba-assisted Section 5.7 route:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py \
  --left /path/to/left.cdb \
  --right /path/to/right.cdb \
  --pair-name br_county_soil \
  --dataset-label available_bounded_pair \
  --output /tmp/rayjoin_section57_overlay_numba.txt \
  --author-output /path/to/answer.txt \
  --summary /tmp/rayjoin_section57_overlay_numba.json
```

Run the writer-free columnar binary Section 5.7 route:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left /path/to/left.cdb \
  --right /path/to/right.cdb \
  --pair-name br_county_soil \
  --summary /tmp/rayjoin_section57_overlay_columnar_binary.json
```

This route reports a numeric/binary downstream descriptor summary instead of
writing the paper's text output-chain file. Use it to measure RTDL as a
pipeline operator; use `section57_overlay.py` or `section57_overlay_numba.py`
when the goal is byte-for-byte paper text output.

Treat the writer-free binary route as a bounded pipeline-operator measurement,
not as a paper text-output replacement. On the top4 County x Zipcode
representative input, the final v2.14.4 evidence shows:

| Route boundary | Timing interpretation |
| --- | --- |
| Warm-process fresh writer-free route | About `4.22s`; includes LSI production and first-use app-layer setup, but excludes cold Python/CUDA process startup. |
| Prepared binary route, six distinct query batches | Median six-batch sum `0.328842s`; median per-batch time `0.046956s`. This is the final v2.14.4 prepared-pipeline gate. |
| AuthorOfficial top4 core phases | `0.187042s`; RTDL is about `1.76x` slower under this bounded comparison. Author output polygons and RTDL binary descriptors are not semantically identical products. |
| Prepared/cached LSI replay diagnostics | Diagnostic only; do not compare this as a fresh overlay computation. |

No top4 author overlay-compute denominator is currently published for this
binary route. Do not reuse the smaller public-sample author timing as a top4
denominator.

The prepared binary number is for a pipeline-style workload where one
base/right LSI session serves multiple distinct chain-contiguous query batches
and the result is consumed as binary descriptors. It is not a cold-start
number, not a paper text-output number, and not an author-parity claim.
Descriptor ordering and carrier construction use the generic native
lexicographic ordering and device-carrier APIs promoted in v2.14.4.

On a CUDA system with Numba available, the same route can push the numeric
intersection reprojection and xsect ordering into Numba CUDA and use a compiled
columnar group builder:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left /path/to/left.cdb \
  --right /path/to/right.cdb \
  --pair-name br_county_soil \
  --device-columnar \
  --compiled-group \
  --validate-device-order \
  --summary /tmp/rayjoin_section57_overlay_device_binary.json
```

`--validate-device-order` compares the CUDA xsect ordering with the CPU
long-double reference and fails closed on mismatch. It is recommended for
correctness checks; omit it for steady-state timing once the route has been
validated on the same input class.

For diagnostics on repeated execution of the same prepared pair, measure the
exact pair-id rows as a cached prepared replay:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left /path/to/left.cdb \
  --right /path/to/right.cdb \
  --pair-name br_county_soil \
  --device-columnar \
  --compiled-group \
  --bounded-exact-lsi-device-columns \
  --bounded-exact-lsi-capacity 1000000 \
  --point-location-device-face-columns \
  --fast-scaled-point-pack \
  --prepared-operator-session \
  --warmup-runs 3 \
  --repeat 5 \
  --summary /tmp/rayjoin_section57_overlay_prepared_hot_binary.json
```

This still records `prepare_lsi_session_sec` and
`lsi_public_rows_warmup_sec`, but `writer_free_hot_sec` uses the second exact
`lsi_prepared_replay_rows_sec`. Use this only to understand cached/replay cost
after exact LSI pair ids have already been computed once. It is not a
cold-start timing, not a fresh overlay timing, and not a paper text-output
timing.

## Evidence And Boundaries

The consolidated v2.14 evidence pages are:

- [RayJoin Reproduction Packet](../../docs/release_reports/v2_14/rayjoin_reproduction_packet.md)
- [Section 5.7 Bounded Reproduction](../../docs/release_reports/v2_14/rayjoin_section57_bounded_reproduction.md)

In short:

- Section 5.2 and 5.3 are primitive-level paper workload reproductions for
  available and representative inputs.
- Section 5.7 is a bounded overlay reproduction for available paper-style pairs
  and representative regenerated pairs.
- The project does not claim all hidden Section 5.7 inputs are available.
- The project does not claim broad RayJoin-system speedup.
- RayJoin output formatting remains paper-app logic, not a generic RTDL engine
  feature.
