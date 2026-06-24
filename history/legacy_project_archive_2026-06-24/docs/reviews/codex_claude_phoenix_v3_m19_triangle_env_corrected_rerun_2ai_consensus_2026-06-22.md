# Codex + Claude 2-AI Consensus: Phoenix V3 M19 Triangle Environment-Corrected Replacement Run

Date: 2026-06-22

Status: `authorize_one_env_corrected_triangle_replacement_pod_after_prelaunch_check`

## Verdict

Codex accepts Claude's external verdict:

```text
authorize_m19_one_env_corrected_triangle_replacement_pod
```

The authorization is for exactly one environment-corrected focused Triangle POD
run, using the verified project venv and a new output directory.

## External Review

```text
review: docs/reviews/claude_phoenix_v3_m19_triangle_env_corrected_rerun_review_2026-06-22.md
stderr: docs/reviews/claude_phoenix_v3_m19_triangle_env_corrected_rerun_review_2026-06-22.stderr.txt
verdict: authorize_m19_one_env_corrected_triangle_replacement_pod
```

Claude confirmed:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_replacement_pod_authorized_now: true, one run only
all_app_pod_authorized: false
attempt_1_is_performance_evidence: false
triangle_counts_as_third_strict_set_a_material_probe_now: false
```

## Required Pre-Launch Check

Claude required a zero-cost check that the M18 harness subprocess variants use
the driver interpreter rather than hardcoding `/usr/bin/python3` or `python3`.

Codex ran:

```text
rg -n "sys\\.executable|python3|/usr/bin/python|subprocess|command =|base_command|legacy_app_front_door_optix|embree_same_contract_control" scripts/v3_phoenix_triangle_runner_m18_pod_ab.py
```

Result:

```text
generate_edge_file command: sys.executable
Embree command: sys.executable
Legacy OptiX command: sys.executable
Runner command metadata: sys.executable
no literal /usr/bin/python3 in command construction
no bare python3 in command construction except the script shebang
```

Pre-launch check status:

```text
pass
```

## Authorized Command

Run exactly once:

```text
cd /root/rtdl_v3_rebuild_20260620/current &&
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python scripts/v3_phoenix_triangle_runner_m18_pod_ab.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_venv_20260622 \
  --edge-file build/phoenix_v3_m18_triangle/k4_cliques_80000.edge \
  --cliques 80000 \
  --partner cupy \
  --warmup 1 \
  --repeat 5 \
  --require-rt-hardware \
  --generate-edge-file
```

Stop after this one run. Copy artifacts back. Do not rerun for a better number.

## Non-Authorization

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
third_strict_set_a_material_probe_closed_before_result: false
```

The replacement run may only answer the focused Triangle M19 question under the
existing M17/M18 success bars.

## Goal-Level Decision Audit

Decision: run exactly one environment-corrected focused Triangle POD job after
Claude authorization and the subprocess-interpreter prelaunch check.

1. Was I foolish?
   Not in this decision. The earlier M18 attempt was foolish because it used
   generic `python3` without a venv preflight.
2. If yes, what actions made the decision foolish?
   The risk now would be expanding this into multiple runs, all-app spend, or a
   public performance claim. This consensus explicitly forbids that.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Stop entirely after attempt 1 and never obtain the intended Triangle
   evidence. That would waste the harness and leave the wrong-interpreter
   failure unresolved.
4. Can I now try a different path that actually solves the problem?
   Yes. Use the verified venv, run exactly once, copy evidence back, classify
   the result honestly, and return to review before any broader action.
