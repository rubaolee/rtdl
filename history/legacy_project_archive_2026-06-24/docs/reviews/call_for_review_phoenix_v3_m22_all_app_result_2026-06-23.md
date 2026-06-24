# Call For Review: Phoenix V3 M22 All-App POD Result

Reviewer: Claude
Requested by: Codex
Date: 2026-06-23

## Review Target

Please critically review the Phoenix V3 M22 same-RT-hardware all-app V2.14 vs
Phoenix V3 result. The goal is not to rubber-stamp release; it is to determine
what the evidence authorizes and what it blocks.

Primary files:

- `docs/reports/phoenix_v3_m22_all_app_pod_result_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/summary.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/m21_protocol_gate.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/m21_protocol_gate.json`

## Facts To Verify

- Same RT hardware run completed with runner `exit_code=0`.
- M21 protocol gate returned `protocol_fail_invalid_or_out_of_scope`.
- Overall geomean V3 speedup vs V2.14 is `1.049x`.
- Set-A geomean is `1.013x`; Set-B geomean is `1.210x`.
- Only 4 of 10 app geomeans are above `1.05x`.
- `barnes_hut` app geomean is `0.831x`, below the severe regression floor.
- Row-level correctness failures exist in V2.14 and current Phoenix V3 suites.
- LibRTS OptiX AABB index is a watch-row regression at `0.803x`.
- Public release, broad speedup, and "V3 is broadly faster than V2.x" claims are
  currently not authorized.

## Questions

1. Is Codex's conclusion correct that this evidence does not authorize Phoenix
   V3 release as a performance-major version?
2. Is the report correct to distinguish suite-driver `rc=0` from row-level
   benchmark validity?
3. Does the Set-A/Set-B split support stopping all-app POD spending until the
   Set-A execution/residency trunk shows material runtime-sourced gains?
4. Are the listed next blockers correct: row-level correctness failures,
   Barnes-Hut regression, LibRTS OptiX watch row, and Set-A trunk proof?
5. Are any numbers, interpretations, or boundaries in the report misleading?
6. What concrete changes would you require before another all-app run?

## Required Output

Please return:

- One verdict label, preferably one of:
  - `release_ready`
  - `approve_blocked_not_release`
  - `redo_required`
  - `invalid_evidence`
- A short bottom-line paragraph.
- Findings ordered by severity.
- Specific corrections to the report if needed.
- Concrete next actions.
- An explicit non-authorization block if release/public speedup claims are not
  authorized.

Do not approve release unless the evidence supports it.
