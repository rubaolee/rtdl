# Goal2184 RayJoin Phase 0/1 Protocol And Sample Evidence

Date: 2026-05-17

Status: local Linux source/protocol/sample evidence complete; full paper-scale
reproduction remains blocked pending RTX pod execution.

## Purpose

This report advances Goal2184 from a project definition into executable
evidence. It verifies that the real RayJoin repository can be cloned, audited,
locally built, and run on its sample data, and that RTDL v2.0 can run the same
RayJoin sample CDB data through its Python+RTDL app boundary without adding
RayJoin-specific native engine code.

Source repository:

- `https://github.com/rubaolee/RayJoin`

Source commit used:

- `02bf6220d6d20b04af77ee20364eced75cc029c9`

RayJoin license:

- MIT License.

## Local Linux Environment

Host:

- `192.168.1.20`
- hostname: `lx1`
- GPU: `NVIDIA GeForce GTX 1070`
- driver: `580.126.09`
- CUDA compiler: `nvcc 12.0.140`
- CMake: `3.28.3`
- OptiX SDK prefix: `/home/lestat/vendor/optix-dev`

Boundary:

- This is build/protocol/sample evidence only.
- The GTX 1070 host is not RTX-release performance evidence and is not used to
  claim RayJoin-paper speedups.

## RayJoin Build Result

RayJoin was cloned outside the RTDL source tree at:

- `/home/lestat/work/rayjoin_goal2184/RayJoin`

The repository built both release and debug binaries:

- `build-release/bin/query_exec`
- `build-release/bin/polyover_exec`
- `build-debug/bin/query_exec`
- `build-debug/bin/polyover_exec`

Because the local host does not provide passwordless sudo, `gflags` and `glog`
were vendored under the external comparison workspace:

- `/home/lestat/work/rayjoin_goal2184/vendor/gflags-install`
- `/home/lestat/work/rayjoin_goal2184/vendor/glog-install`

External comparison-checkout patches were required only to build RayJoin on the
local Linux host:

1. Add vendored `glog`/`gflags` include paths to RayJoin's custom NVCC PTX rule.
2. Set `ENABLED_ARCHS` to `61` for the GTX 1070 smoke host.
3. Add a local vector hash/equality predicate for one `unordered_map` use in
   `src/app/output_chain.h`, because the current GCC/CUDA toolchain rejects
   the original `double2` equality lookup.

The patch is recorded verbatim in:

- `docs/reports/goal2184_rayjoin_build_protocol_linux_raw_2026-05-17.txt`

These are external RayJoin build-compatibility patches. No RTDL native source
file was changed for this step.

## Protocol Reconstruction

The RayJoin README and source flags establish the protocol surface:

| Area | RayJoin protocol |
| --- | --- |
| Query binary | `query_exec` |
| Overlay binary | `polyover_exec` |
| Query types | `-query=lsi` and `-query=pip` |
| Modes | `-mode=grid`, `-mode=lbvh`, `-mode=rt` |
| Dataset inputs | `-poly1 path`, `-poly2 path` CDB files |
| Repeats | `-warmup`, `-repeat` |
| LSI queue sizing | `-xsect_factor` |
| RT correctness check | `-check=true` compares RT against grid where supported |
| Overlay output | `-output path` |
| Serialized preload path | `-serialize path` |

RayJoin's checked-in sample data is:

- `test/dataset/br_county_clean_25_odyssey_final.txt`
- `test/dataset/br_soil_ascii_odyssey_final.txt`
- `test/dataset/br_countyXbr_soil_answer.txt`

The sample files are CDB-shaped text files and can also drive RTDL's external
CDB adapter.

## RayJoin Sample Execution

The release sample overlay was run against the repository answer file.

| Binary | Mode | Output check |
| --- | --- | --- |
| `polyover_exec` | `grid` | diff passed |
| `polyover_exec` | `lbvh` | diff passed |
| `polyover_exec` | `rt` | diff passed |

The debug sample `rt` mode failed on the GTX 1070 host with
`OPTIX_ERROR_INTERNAL_COMPILER_ERROR` while compiling the custom LSI module.
The release `rt` mode succeeded on the same sample. This is recorded as a local
toolchain/hardware boundary, not a RayJoin protocol failure.

`query_exec` was also run on the same sample pair:

| Query | Mode | Status |
| --- | --- | --- |
| `lsi` | `grid` | completed |
| `lsi` | `lbvh` | completed |
| `lsi` | `rt` | completed with `-check=true` |
| `pip` | `grid` | completed |
| `pip` | `lbvh` | completed |
| `pip` | `rt` | completed with `-check=true` |

This completes the local RayJoin build/protocol/sample lane. It does not
complete the paper-scale performance lane.

## RTDL Same-Sample Evidence

RTDL was validated from a clean Linux clone at:

- `/home/lestat/work/rtdl_rayjoin_goal2184_check`

RTDL commit:

- `f54441a4475bbbf96e20ffc28127255c30aeb850`

The RayJoin sample files were copied as CDB inputs and sliced by the existing
RTDL RayJoin runner. Artifact:

- `docs/reports/goal2184_rtdl_same_rayjoin_sample_bounded_linux_2026-05-17.json`

Post-review metadata note:

- Claude noted that the artifact inherited `"goal": "2159"` from the older
  runner used to execute the bounded sample cases. The artifact metadata was
  corrected to `"goal": "2184"` before commit; row counts, timing values,
  dataset paths, parity flags, and claim-boundary flags were unchanged.

Results:

| Case | Workload | Backend | Rows | Median app sec | Parity |
| --- | --- | --- | ---: | ---: | --- |
| `pip_county512` | PIP | CPU | 1,430 | 5.502369 | true |
| `pip_county512` | PIP | Embree | 1,430 | 0.018953 | true |
| `lsi_county256_soil256_count128` | LSI | CPU | 56 | 0.010143 | true |
| `lsi_county256_soil256_count128` | LSI | Embree | 56 | 0.030658 | true |
| `overlay_county128_soil128` | overlay seed | CPU | 14,036 | 0.196814 | true |
| `overlay_county128_soil128` | overlay seed | Embree | 14,036 | 0.020784 | true |

This same-sample RTDL evidence proves that the RTDL v2 app can ingest RayJoin
CDB-shaped data and run PIP, LSI, and overlay-seed workloads with parity on
bounded slices. It intentionally does not claim that these bounded slices
reproduce the full RayJoin paper protocol.

## App-Agnostic Engine Boundary

No RTDL native RayJoin customization was added.

RTDL continues to see generic:

- point/polygon positive-hit rows
- segment/segment intersection rows
- shape-pair relation rows
- Python app policy
- partner/reduction code outside the native engine

The RayJoin-specific pieces remain outside the RTDL engine:

- CDB file interpretation
- sample slicing
- workload naming
- overlay dependency policy
- comparison/reporting logic

## What Is Finished

Goal2184 now has:

1. Real RayJoin source provenance.
2. Real RayJoin dependency/build notes.
3. Real RayJoin release/debug build evidence on local Linux.
4. RayJoin sample overlay execution for `grid`, `lbvh`, and `rt`.
5. RayJoin sample query execution for LSI/PIP across `grid`, `lbvh`, and `rt`.
6. RTDL same-RayJoin-sample bounded evidence for PIP, LSI, and overlay seed.
7. A clear claim boundary for why this is not yet a paper-scale result.

## What Still Requires A Pod

The remaining Goal2184 work needs an RTX pod or equivalent hardware:

1. Build RayJoin with an RTX-era SM target such as `86` or `89`, not the local
   GTX 1070 `61` smoke target.
2. Run RayJoin release `query_exec` and `polyover_exec` on larger public or
   paper-aligned CDB datasets.
3. Run RTDL v2.0 OptiX on the same datasets.
4. Compare RayJoin `grid`, `lbvh`, `rt` with RTDL Embree, RTDL OptiX one-shot,
   RTDL OptiX prepared paths, and CUDA/CuPy spatial baselines.
5. Obtain Gemini and Claude review before any public performance claim.

## Verdict

Goal2184 is accepted as complete for local source/protocol/sample execution.

Goal2184 is still `accept-with-boundary` for the full reproduction ambition:
paper-scale RayJoin reproduction and competitive public performance claims
remain blocked until RTX pod evidence and 3-AI consensus exist.

This report authorizes continuing to the pod reproduction phase. It does not
authorize claims that RTDL reproduces RayJoin paper results, beats RayJoin, or
is ready for a v2.0 release on the basis of this evidence alone.
