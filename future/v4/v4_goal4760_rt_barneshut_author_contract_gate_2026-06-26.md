# Goal4760: RT-BarnesHut Author-Contract Gate

Date: 2026-06-26

Status: complete as semantic gate; not complete as V4 RT-core performance route.

## Decision

We should not continue comparing the existing RTDL 2D Barnes-Hut-style workflow against the authors' 3D RT-BarnesHut program. I added the missing same-semantics gate first: RTDL can now load author-format datasets, preserve author CSV scaling, build the author-style 3D bucketed Barnes-Hut CPU oracle, parse author binary timing, create trimmed author datasets, and produce a non-release probe record.

This is the first real implementation step toward a fair author comparison. It does **not** claim V2/V3/V4 performance parity or speedup yet.

## Code Added

- `src/rtdsl/rt_barneshut_author_contract.py`
  - author treelogy loader;
  - author CSV loader with `x/y/z * 10.0` and `mass * 1e5`;
  - author-compatible 3D z-order comparator;
  - bucket size 32 tree construction;
  - Barnes-Hut CPU force oracle using the author threshold and force formula;
  - author stdout timing parser;
  - trimmed dataset writer.

- `scripts/rt_barneshut_author_contract_probe.py`
  - creates same-input trimmed author datasets;
  - runs the RTDL CPU author-semantics oracle;
  - optionally runs the authors' `rtbarneshut` binary on the same trimmed dataset;
  - emits a JSON evidence payload with explicit non-speed claim boundaries.

- `tests/v4_goal4760_rt_barneshut_author_contract_test.py`
  - verifies treelogy trim/load;
  - verifies CSV scaling;
  - verifies deterministic CPU oracle and non-release claim boundary;
  - verifies author stdout phase parser;
  - verifies probe JSON output.

- `tools/rtbarneshut_author_force_checksum_audit.patch`
  - adds read-only RT force checksum output to the authors' binary;
  - does not change traversal, force computation, timing regions, or data semantics.

## Validation

Local:

```text
py -m unittest tests.v4_goal4760_rt_barneshut_author_contract_test
Ran 5 tests in 1.399s
OK
```

POD:

```text
cd /root/rtdl_v4_candidate_pod
/root/rtdl_v4_venv/bin/python -m unittest tests.v4_goal4760_rt_barneshut_author_contract_test
Ran 5 tests in 0.768s
OK
```

## POD Same-Input Probe Evidence

Evidence directory:

`future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/`

| Probe | Input | Same input author binary? | Author execution | Author RT force | RTDL CPU oracle checksum | Performance comparison authorized? |
|---|---:|---|---:|---:|---:|---|
| `rtdl_author_contract_4096.json` | 4,096 treelogy points | yes | 0.255172s | 0.005209s | `8.954052688202874e-06` | no |
| `rtdl_author_contract_8192.json` | 8,192 treelogy points | yes | 1.425780s | 0.005420s | `3.6015691175709494e-05` | no |

Checksum validation after the read-only author-binary checksum patch:

| Probe | Author RT checksum | RTDL CPU oracle checksum | Relative error |
|---|---:|---:|---:|
| `rtdl_author_contract_4096_checksum.json` | `8.95407e-06` | `8.954052688202874e-06` | `1.933403535816373e-06` |
| `rtdl_author_contract_8192_checksum.json` | `3.60157e-05` | `3.6015691175709494e-05` | `2.450123881979025e-07` |

This proves the CPU oracle is not merely parsing the same file. On these two trimmed Treelogy probes it matches the authors' RT force result to float-output precision. It is still not a performance route.

Why no performance comparison: the RTDL row is a CPU semantic oracle. It validates the author input/tree/force contract. It is not the V4 RT-core route.

## What This Fixes

Before Goal4760, the project had:

- authors' binary built and run;
- old RTDL V2/V3/V4 Barnes-Hut-style numbers;
- no same-semantics bridge between the two.

Goal4760 adds that bridge at the contract level. It prevents the old mistake of dividing unlike programs.

## What Remains

The next engineering goal must implement the actual V4 RT-core performance route against this contract:

1. consume the same author-format datasets;
2. reuse the Goal4760 author-compatible tree/frontier contract;
3. run the V4 RT-core/continuation path on that contract;
4. emit the same phase split as the author program;
5. run V2.14, V3.0.2, V4.0, and authors' binary on the same trimmed and then full datasets;
6. only then authorize a fair performance table.

## Goal-Level Decision Audit

1. Was I being stupid?
   - Partly before this goal: yes, because the project had been comparing old RTDL Barnes-Hut-style numbers without a same-semantics author contract.

2. What action made it stupid?
   - Treating a 2D aggregate-frontier workflow as if it were adjacent enough to the authors' 3D RT-BarnesHut program to discuss performance in the same breath.

3. Is there another path that avoids getting stuck on a bad premise?
   - Yes: build the author-contract gate first, then require every later speed number to pass through it.

4. Can I now try the different path that actually solves the problem?
   - Yes. Goal4760 creates the gate. The next goal is the V4 RT-core route that runs against this gate.

## Non-Authorization

Goal4760 does not authorize:

- public RT-BarnesHut paper reproduction wording;
- authors-code speedup wording;
- V2/V3/V4 RT-BarnesHut performance comparison wording;
- V4 release claims based on the CPU oracle;
- claims that the current V4 route is the authors' RT-BarnesHut algorithm.

It authorizes only:

> RTDL now has a same-input RT-BarnesHut author-contract gate and CPU oracle. The V4 RT-core performance route still has to be implemented against that gate before any fair V2/V3/V4/author performance comparison exists.
