# cit-Patents/4M prepared cross-GPU reproducibility result

Date: 2026-09-08 America/New_York.

Verdict:
`COMPLETE__REPLICATION_TARGET_MET__INDEPENDENT_RECOUNT_PASS`.

## Answer

On one separately registered NVIDIA RTX 4000 Ada Generation GPU, the exact
cit-Patents/4M prepared RT-2A1 computation reproduced within the preregistered
RTDL/PyOptiX engineering envelope. The median of eight paired block ratios was
`1.0166409558050167x`; the largest block ratio was
`1.0242642254370453x`. The frozen limits were `1.20x` and `1.35x`,
respectively.

This is a long natural computation rather than a microbenchmark. Every timed
sample executed the full 28-segment graph action and produced the checked U64
triangle count `7,515,023`. The timer includes the public checked adapter
action, output comparison/digest work, and compact execution-evidence
construction. It is not a pure traversal timer.

## Registered protocol

| Field | Value |
| --- | --- |
| Transaction | `citpatents4m-crossgpu-rtx4000ada-2a00572b-20260908` |
| Scope | `cross_gpu_reproducibility` |
| GPU | NVIDIA RTX 4000 Ada Generation |
| GPU UUID | `GPU-2a00572b-6cef-b9e6-db0a-c127783a5d46` |
| Driver / CC | `550.127.05` / `8.9` |
| Measured source | `02e84374fc092d2bb916cca633eda9592b4ecf07` |
| Source tree | `8aad15d686bbc9e1c3b11df998898a0a063a01f1` |
| Input SHA-256 | `c5b2c9203eeabb46414965755c33befdb1810e71cb51155eb940a68a6179d855` |
| Algorithm / cap | RT-2A1 / 4,000,000 relation rows |
| Arms | signed RTDL `.rtdlexe`; competent public PyOptiX |
| Endpoint | prepared checked adapter action |
| Population | 8 paired blocks, 16 fresh workers, 48 timed samples |
| Per worker | 1 warmup plus 3 retained samples |
| CPU affinity | exact logical CPU `{8}` before and after every worker |
| Retry / discard | 0 / 0; both forbidden |

Four blocks ran RTDL first and four ran PyOptiX first in the frozen alternating
order. Both arms used the same input relation, RT-2A1 algorithm, segmentation,
expected output, CUDA/OptiX stack, public output materialization, CPU affinity,
and worker lifecycle. RTDL used its verified family `.rtdlexe` general-leaf
device-column path; the comparison arm used public PyOptiX with semantically
matched RT-2A1 device weighted reduction. PyOptiX did not call private RTDL
native entry points.

## Block results

| Block | RTDL median (s) | PyOptiX median (s) | RTDL/PyOptiX |
| ---: | ---: | ---: | ---: |
| 0 | 8.764671078 | 8.559844317 | 1.023928795 |
| 1 | 8.743435267 | 8.629722092 | 1.013176922 |
| 2 | 8.857158593 | 8.647337643 | 1.024264225 |
| 3 | 8.837609598 | 8.715134383 | 1.014053164 |
| 4 | 8.879155447 | 8.669637110 | 1.024166910 |
| 5 | 8.803530213 | 8.665348234 | 1.015946500 |
| 6 | 8.774043112 | 8.624533281 | 1.017335411 |
| 7 | 8.828728826 | 8.752792470 | 1.008675672 |

Across the 24 retained samples per arm, the RTDL sample median was
8.801897942 s and the PyOptiX sample median was 8.664760994 s. These are
descriptive values; the registered estimator is the median of the eight paired
block ratios above.

## Reproduction relation

The prior RTX A4500 transaction reported a paired median of `1.057361x` and a
largest block of `1.083735x`. The new RTX 4000 Ada transaction reports
`1.016641x` and `1.024264x`. The replicated A/C prepared cell uses the same
measured source, input, algorithm, segment cap, eight-block A/C pairing, three
retained samples per worker, order pattern, affinity and thresholds, but a
different physical GPU model and UUID. The complete transaction populations
are not the same: the prior portfolio transaction had 240 workers across ten
rows and three arms, whereas this focused transaction has 16 workers for one
row and two arms. They are reported separately and are never pooled.

The result supports a narrow cross-GPU reproducibility statement: the measured
long prepared Graph path remained within about 2.5% of competent public
PyOptiX in every paired block on this second GPU. It does not prove a same-host
temporal replay, a cross-generation result, or a portfolio-wide overhead
bound.

## Independent verification

The controller retained all 16 worker JSON files, 16 journals, raw stdout and
stderr, the 17-row progress log, schedule, and summary. All 16 process IDs were
unique. Every worker reported the registered GPU, exact CPU affinity before and
after execution, clean source identity, exact native identity, matching input
identity, output SHA-256
`f3a9d76129db60b207374aef74b6d5abb6a126a6d4fc7bc88b830a7fc1995e2c`,
and zero retry/discard.

A standard-library-only recount from a different clean checkout reconstructed
all raw hashes, journals, schedule rows, identities, samples, paired ratios and
verdict. Its SHA-256 is
`725de89ca1eed63d9ef6ce2a6dd5557ca092bf7ba213153a43f48d466f1561e8`.
The deterministic archive was then verified and recounted from a fresh Pod
extraction and a fresh Mac extraction. Both recount outputs were byte-identical
to the first independent recount.

Deterministic archive:

- Path:
  `raw/rtdl-v4-citpatents-crossgpu-rtx4000ada-formal.tar.gz`.
- Size: 293,052 bytes.
- SHA-256:
  `ee461dd09ee5770aa21ed297e0cc73a5463e324fb6b05f6c663b272be80c9908`.
- Indexed evidence members: 104, all verified.

## Claim ceiling

This result answers one important performance objection: on a genuine
multi-second natural Graph computation, the measured RTDL path did not pay a
large language/runtime tax relative to a competent public PyOptiX program. It
does not establish the same fact for all callbacks, all nine applications,
complete lifecycle endpoints, arbitrary GPUs, author productivity, or engine
generality. It also does not convert the fixed-specialization Particle result
into evidence for a general generated-leaf route.

GPU clocks were observed but not locked, formal peak memory was not captured,
and the transaction was scheduled after the prior A4500 result was known. The
original A4500 endpoint was unavailable, so same-host temporal replication
remains absent. Public or manuscript wording still requires lead integration
and exact-byte review; no external review or submission authorization is
created by this internal result alone.
