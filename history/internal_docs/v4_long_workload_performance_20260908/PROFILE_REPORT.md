# Prepared-path profile and strong-C workload calibration

Date: 2026-09-08, America/New_York. Status: diagnostic only. None of the
measurements in this report are preregistered or eligible for pooling into a
formal transaction.

## Bound environment

- GPU: NVIDIA RTX A4500, UUID
  `GPU-5dbda20d-af85-650e-7250-10b265a77143`, compute capability 8.6.
- Driver: 550.127.05.
- Retained baseline source: `c5c8be48b743aa001e9c16c3344cc97c200600d1`,
  tree `e3bb0001f4c2d1e3171ab0431c0479500dfc7136`.
- Baseline native and Python environment are those bound by
  `/workspace/rtdl-v4-paper-apps-run/CONFIG_c5c8be48b.json` on the pod.
- Raw JSON, `cProfile` binaries, and human-readable profiles are under
  `diagnostics/`.

## Registered-provider identity diagnosis

The old LibRTS path resolved the native provider path three times per action:
once in the explicit-path branch of audit open, again in provider digest lookup,
and once while capturing the snapshot. On this pod's filesystem, 48 resolves
over 16 actions consumed 152.640 ms for point and 145.455 ms for range. The DSO
content digest was already cached; this was path resolution, not repeated DSO
hashing.

The candidate uses the exact provider identity already registered against the
loaded library object and carries its frozen absolute path into internal
capture. The public external snapshot helper and explicit-path admission still
resolve and validate paths. Relevant local tests report 19/19 PASS.

| Old registered input | Baseline profiled median | Candidate profiled median | Path resolves/action after warmup | Output |
| --- | ---: | ---: | ---: | --- |
| LibRTS point contains | 8.705 ms | 0.374 ms | 0 | exact 112,729 |
| LibRTS range contains | 9.134 ms | 0.373 ms | 0 | exact 105,826 |
| Particle cell transition | 21.053 ms | 18.151 ms | 0 | exact ordered 5,000 x 3 U32 |

These are profiler-instrumented medians, so they establish a mechanism and a
large directional effect, not publishable speedups. In the candidate LibRTS
profile, native prepared traversal/reduction took about 0.12 ms/action,
audit open about 0.027 ms, and capture plus full receipt construction about
0.155 ms. These intervals are inclusive and must not be summed. Particle's
remaining dominant costs are two 5,000-row expected-output conversions and the
runtime's repeated row/result representation work.

## Graph strong-C selection

The calibration executes the competent public-PyOptiX RT-2A1 route. Every
fresh process prepares the owner, performs one untimed full-graph warmup, then
times one full natural action. Input loading, owner preparation, action, and
close are separate. All actions returned the exact registered U64 oracle.

`com-dblp` at 1,000,000 relation rows took 0.443 s after warmup, so it does not
qualify as the long prepared computation. The selected candidate is
`cit-Patents` at 4,000,000 relation rows:

- edge SHA-256:
  `c5b2c9203eeabb46414965755c33befdb1810e71cb51155eb940a68a6179d855`;
- 28 deterministic segments;
- 15,853,615 total segment primitives and 69,850,749 total segment queries;
- maximum segment sizes: 896,130 primitives and 3,212,681 queries;
- exact triangle count: 7,515,023;
- three fresh-process prepared action times: 8.671 s, 8.719 s, 8.816 s;
- median: 8.719 s.

Retained exploration also includes 1M, 2M, 4M cold, and 8M cold segment-capacity
runs. The 8M action took 75.036 s and is retained as an adverse memory/working-
set result. Selection used only C time, correctness, and memory behavior; no
RTDL result was observed before selecting this long workload.

## Reproduction commands

Profiles used `diagnose_prepared_hot_path.py` with the bound config, one warmup,
16 repetitions, `CUDA_VISIBLE_DEVICES=0`, and `PYTHONPATH=src:.`. Graph
calibration used `calibrate_triangle_pyoptix_c.py` with one warmup and one timed
action per fresh process. The scripts, exact output JSON, and raw profiles are
part of this diagnostic directory; future formal workers will use a new
create-only, partial-sample-preserving protocol.

## Next decisions

1. Validate the provider-identity repair without profiler instrumentation and
   compare it to the same strong PyOptiX old-input endpoint.
2. Remove Particle's duplicate expected/result conversions while retaining the
   complete independent oracle check and immutable-output behavior.
3. Reuse Graph's immutable module/program-group/pipeline/SBT across segments,
   then test both `com-dblp` and selected `cit-Patents` before preregistration.
4. If LibRTS still exceeds the 1.20 ratio target, use a generic eagerly
   validated compact audit representation; do not remove decision-bearing
   validation.

## Successor scheduling diagnosis

The first complete 240-worker successor transaction at source `0c3420f42`
retained every worker with correct output, zero retry, zero discard, and zero
timeout. It passed eight of ten unit-endpoint engineering rows. Two prepared
rows failed only the every-block `<= 1.35` gate while their eight-ratio medians
passed:

| Row | Paired median A/C | Worst block A/C | Gate |
| --- | ---: | ---: | --- |
| Particle prepared | 0.818599x | 1.462108x | FAIL |
| LibRTS range prepared | 0.958249x | 1.563658x | FAIL |

Both are sub-millisecond prepared actions. Pod inspection found 48 visible
logical CPUs under a cgroup-v1 quota of `1020000/100000`, approximately 10.2
CPU cores, with host frequency and scheduler state varying between fresh
processes. The GPU was observed at P8/210 MHz while idle and rose under work.
An attempted `nvidia-smi -lgc 1650,1650` lock was rejected by container
permissions, so no locked-clock statement is authorized.

A new, explicitly non-evidence diagnosis kept the same tasks, inputs, prepared
repetitions, warmup count, output checks, timer, and thresholds, while launching
both arms with `taskset -c 8`. Eight balanced paired blocks produced:

| Row | Paired median A/C | Worst block A/C | RTDL median range | PyOptiX median range |
| --- | ---: | ---: | ---: | ---: |
| Particle prepared | 0.723949x | 0.946571x | 0.353--0.463 ms | 0.486--0.590 ms |
| LibRTS range prepared | 0.948064x | 1.013219x | 0.238--0.265 ms | 0.247--0.293 ms |

The diagnostic summary SHA-256 is
`67cc82bc6f558bc21b2f60cd0946b83cbd3c02068df765531e31597bb7c52a7f`.
This is strong evidence that host CPU migration/scheduling state was capable of
producing the two adverse worst blocks; it is not proof that scheduling was the
only possible source of variance, and it is not pooled into formal evidence.

Commit `02e84374fc092d2bb916cca633eda9592b4ecf07` therefore promotes exact
one-CPU affinity from an external launcher choice into the generic measurement
contract. The worker applies it before implementation imports, records exact
preflight and postflight observations, and fails closed on mismatch. Config,
controller, preregistration, and independent recount all validate the same
contract. No application/runtime implementation, GPU kernel, workload, output,
timer, repetition count, or threshold changed in that commit. A wholly fresh
transaction is required; the unlocked transaction remains immutable adverse
evidence.
