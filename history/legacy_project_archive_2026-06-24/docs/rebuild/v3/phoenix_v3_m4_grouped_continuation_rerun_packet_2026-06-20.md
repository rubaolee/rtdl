# Phoenix V3 M4 Grouped-Continuation Rerun Packet

Status: ready for pod after external review, not executed, 2026-06-20.

None of the M9, M10, M11, M18, M23, or M28 results in this packet may be
cited, quoted, paraphrased, or summarized in public-facing or partner-facing
material until a separate authorization step changes
`public_speedup_claim_authorized` to true.

This packet defines the first Phoenix P0 pod rerun. It is deliberately
capability-first:

```text
Goal4392 M4: generic fused/grouped continuation with cross-app reuse.
```

It is not release evidence and does not authorize public speedup wording.

Machine-readable packet:

```text
docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.json
```

## Why M4 First

M4 is the most direct test of the V3 thesis. If V3 cannot turn RTDBSCAN-style
continuation work into a reusable generic continuation shared by another
workload, then V3 is still just benchmark-specific repair.

This rerun therefore targets:

- `component_union` on RTDBSCAN-style grouped streams;
- `grouped_reduction` on RayDB-style count/sum;
- CuPy and Numba partner evidence;
- same-stream and measured-window no-hidden-copy evidence;
- same-contract OptiX/Embree grouped-reduction rows;
- claim flags locked false.

## Required Pod Scale

The packet does not downshift to tiny rows:

| Evidence | Scale |
| --- | ---: |
| M9 grouped partner | 65,536 points |
| M10 same-stream | 65,536 points |
| M11 measured-window no-hidden-copy | 65,536 points |
| M18 device-side grouped contract | 65,536 rays / 1,024 groups |
| M23 DBSCAN component signature | 65,536 copies / 524,288 points |
| M28 RayDB grouped reduction | 262,144 generated rows / 1,024 groups |

If a serious-scale row fails, the failure is preserved. It must not be silently
replaced by a smaller row without a supersession packet.

A failed run at the stated scale must be recorded as a failed M4 evidence row at
that same scale. It must not be backfilled, averaged, or footnoted against older
small-scale evidence, including the old 8,192-ray M18 row.

## Remote Target

```text
ssh root@213.173.108.14 -p 11592 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
cd /root/rtdl_v3_rebuild_20260620/current
export ART=/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m4_grouped_continuation_20260620
export PY=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
```

The binding execution environment is the rebuild venv at
`/root/rtdl_v3_rebuild_20260620/.venv/bin/python`, Python 3.12.3, with
`cupy-cuda12x==14.1.1`, `numba==0.65.1`, `torch==2.6.0+cu124`,
`nvidia-cuda-nvcc-cu12==12.4.131`, `nvidia-cuda-nvrtc-cu12==12.9.86`, and
`nvidia-cuda-runtime-cu12==12.9.79`.

System `python3` on this pod failed the GPU partner preflight because CuPy and
Numba were missing. That is an environment/packaging gap, not evidence that the
V3 M4 code path failed. The packet therefore requires the GPU partner gate,
source identity gate, and claim-boundary gate to be reverified on the pod with
the binding venv path before measurement proceeds.

The focused M4 test and measurement commands use the binding venv explicitly.
The M4/M9/M10/M11/M18/M23/M28 scripts and focused tests use `sys.executable`
for Python re-exec/subprocess paths. The Makefile contains unrelated
`python3` targets, but this packet calls only `build-embree` and `build-optix`.

## Command Batch

```bash
mkdir -p "$ART"
nvidia-smi > "$ART/nvidia-smi.txt"
PYTHONPATH=src:. python3 scripts/v3_gpu_python_env_gate.py \
  --json-out "$ART/system_python3_gpu_env_gate.json" \
  > "$ART/system_python3_gpu_env_gate.stdout" \
  2> "$ART/system_python3_gpu_env_gate.stderr" || true
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git rev-parse HEAD > "$ART/current_commit.txt"
else
  echo no_git_worktree > "$ART/current_commit.txt"
  cat VERSION > "$ART/source_version.txt"
  {
    printf 'expected_source_version=v3-rebuild-2026-06-20\n'
    printf 'actual_source_version='
    cat VERSION
    printf '\n'
    if grep -qx 'v3-rebuild-2026-06-20' VERSION; then
      printf 'source_version_match=pass\n'
    else
      printf 'source_version_match=fail\n'
      exit 1
    fi
  } > "$ART/source_identity_check.txt"
  {
    echo searched_git_and_build_provenance
    find /root/rtdl_v3_rebuild_20260620 \
      /workspace/rtdl_v2_vs_v3_pod_20260620_024503 \
      -maxdepth 4 -type d -name .git 2>/dev/null || true
    ls -l /root/rtdl_v3_rebuild_20260620/*build*.log \
      /root/rtdl_v3_rebuild_20260620/run_current*.log 2>/dev/null || true
  } > "$ART/provenance_search.txt"
  {
    sha256sum VERSION README.md Makefile \
      build/librtdl_embree.so \
      build/librtdl_optix.so
    find src scripts -type f \
      \( -name '*.py' -o -name '*.cu' -o -name '*.cpp' -o -name '*.c' -o \
      -name '*.hpp' -o -name '*.h' \) \
      -print0 | sort -z | xargs -0 sha256sum
  } > "$ART/source_manifest.sha256"
fi
PYTHONPATH=src:. "$PY" scripts/v3_gpu_python_env_gate.py --json-out "$ART/gpu_env_gate.json"

"$PY" - <<'PY' > "$ART/pre_run_packet_gate.txt"
import json
from pathlib import Path

packet = Path("docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.json")
payload = json.loads(packet.read_text())
assert payload["release_authorized"] is False
assert payload["public_speedup_claim_authorized"] is False
assert payload["phoenix_m7_qualified_release_rows"] == 0
print("packet claim-boundary gate ok")
PY

test -w "$ART"
df -h "$ART" > "$ART/artifact_df_before.txt"
"$PY" - <<'PY' > "$ART/artifact_preflight.txt"
import os
import shutil

path = os.environ["ART"]
free = shutil.disk_usage(path).free
assert free >= 2147483648, f"insufficient artifact free space: {free}"
print(f"artifact_dir={path} free_bytes={free}")
PY

make build-embree build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0

PYTHONPATH=src:. "$PY" -m unittest \
  tests.goal4396_v3_0_m4_component_union_pilot_test \
  tests.goal4403_v3_0_m9_grouped_stream_partner_test \
  tests.goal4406_v3_0_m10_same_stream_evidence_test \
  tests.goal4407_v3_0_m11_no_hidden_copy_evidence_test \
  tests.goal4415_v3_0_m18_device_side_grouped_contract_test \
  tests.goal4420_v3_0_m23_dbscan_component_bridge_test \
  tests.goal4425_v3_0_m28_raydb_prepared_grouped_refresh_test

PYTHONPATH=src:. "$PY" scripts/v3_0_m9_grouped_stream_partner_measure.py \
  --point-count 65536 --component-threshold 7 --warmups 2 --repeats 5 \
  --output "$ART/m9_grouped_stream_partner_65536.json"

PYTHONPATH=src:. "$PY" scripts/v3_0_m10_same_stream_evidence_measure.py \
  --point-count 65536 --component-threshold 7 --warmups 2 --repeats 5 \
  --output "$ART/m10_same_stream_65536.json"

PYTHONPATH=src:. "$PY" scripts/v3_0_m11_no_hidden_copy_measure.py \
  --point-count 65536 --component-threshold 7 --warmups 2 --repeats 5 \
  --output "$ART/m11_no_hidden_copy_65536.json"

PYTHONPATH=src:. "$PY" scripts/v3_0_m18_device_side_grouped_contract_measure.py \
  --ray-count 65536 --group-count 1024 --warmups 2 --repeats 5 \
  --output "$ART/m18_device_grouped_65536.json"

PYTHONPATH=src:. "$PY" scripts/v3_0_m23_dbscan_component_bridge_measure.py \
  --copies 65536 --warmups 2 --repeats 5 --app-call-warmups 1 \
  --output-mode component_signature \
  --output "$ART/m23_dbscan_component_signature_524288.json"

PYTHONPATH=src:. "$PY" scripts/v3_0_m28_raydb_prepared_grouped_refresh.py \
  --generated-rows 262144 --generated-groups 1024 \
  --modes count,sum --backends embree,optix --warmup 1 \
  --include-iteration-walls \
  --output "$ART/m28_raydb_grouped_reduction_262144.json"
```

M28 must be reported as four independent labeled evidence rows:
`embree/count`, `embree/sum`, `optix/count`, and `optix/sum`. These rows must
not be merged or averaged.

## Acceptance

This packet is successful only if:

- the runner reads this packet before measurement and verifies
  `release_authorized=false`, `public_speedup_claim_authorized=false`, and
  `phoenix_m7_qualified_release_rows=0`;
- the artifact directory exists, is writable, and free space is recorded before
  large M23/M28 outputs;
- source identity is recorded as a git commit when available, or as
  `source_version.txt` plus `source_manifest.sha256` when the pod tree is an
  expanded non-git worktree;
- if the no-git fallback is used, `source_identity_check.txt` must show
  `source_version_match=pass` for expected version `v3-rebuild-2026-06-20`;
- if the no-git fallback is used, `source_manifest.sha256` must include
  `build/librtdl_embree.so`, `build/librtdl_optix.so`, and the `src/` and
  `scripts/` source files, and `provenance_search.txt` must record where git
  and rebuild provenance were checked;
- any downstream report must state prominently that no-git source identity is
  VERSION-string plus file-hash based, not git-commit based;
- GPU partner, source identity, and claim-boundary gates are reverified on the
  pod using `/root/rtdl_v3_rebuild_20260620/.venv/bin/python` before
  measurement;
- system `python3` failure is recorded as a missing-CuPy/Numba packaging gap,
  not as a V3 M4 code-path failure;
- system `python3` gate output is preserved in
  `system_python3_gpu_env_gate.json`, stdout, and stderr, and does not replace
  the binding venv gate;
- no focused test or measurement command in this packet uses plain
  `python3`/`python` instead of the binding venv interpreter;
- required commands either pass or preserve failure artifacts;
- CuPy and Numba rows both exist where partner evidence is required;
- RTDBSCAN and RayDB both pass correctness checks;
- M28 Embree/OptiX and count/sum results are recorded as independent labeled
  rows, not merged or averaged;
- at least one non-DBSCAN grouped/fused continuation row exists;
- public speedup, whole-app speedup, automatic partner/backend selection, and
  release authorization remain false;
- no broad V2.14-vs-V3 geomean is recomputed over a subset.

## Goal-Level Decision Audit

Decision: make M4 grouped/fused continuation the first Phoenix P0 rerun.

1. Was I foolish?

   The corrected decision is not foolish. It follows Goal4392 rather than
   chasing the largest historical ratio.

2. What action would make it foolish?

   Downshifting failed serious rows to toy rows, or treating partial success as
   release evidence, would be foolish.

3. Was there another path?

   Yes. Barnes-Hut regression or RayJoin topology could also be first, but M4
   is the root generic-continuation gate.

4. Can I now try a different path that actually solves the problem?

   Yes. This packet tests whether V3 has reusable continuation machinery across
   DBSCAN and non-DBSCAN workloads before any release wording.
