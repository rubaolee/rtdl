# Goal4776 - Clean Checkout And Wheel Smoke

Status: `clean_checkout_wheel_smoke_passed_for_release_candidate_and_final_v4_0_0_tag_target`

Date: 2026-06-27

## Purpose

Goal4776 verifies that the bounded V4.0 release candidate is not only working
from the original dirty development tree. It must be reproducible from a clean
committed checkout and from an installed wheel.

This is the practical release hygiene step between external review approval and
the public `v4.0.0` tag.

## Candidate Commit Checked

Initial release-candidate commit:

```text
b134fa770 Prepare bounded V4.0 release candidate
```

Clean worktree:

```text
C:\Users\Lestat\Desktop\work\rtdl_v4_0_release_verify_b134fa770
```

Clean worktree status before wheel build:

```text
git status --short --untracked-files=all
# no output
```

## Wheel Build

Command:

```powershell
py -m pip wheel . --no-deps -w dist/goal4776_clean_verify
```

Result:

```text
Successfully built rtdl-source-tree
wheel: rtdl_source_tree-4.0.0-py3-none-any.whl
size: 1523527
sha256: 64897daae0d5dc6185a790cc081be73834154b2b0939ebee7d14448436381f32
```

## Installed-Wheel Smoke

Command:

```powershell
py scripts/v4_goal4758_installed_wheel_smoke.py `
  --wheel dist/goal4776_clean_verify/rtdl_source_tree-4.0.0-py3-none-any.whl `
  --out-dir future/v4/evidence/v4_goal4776_clean_wheel_smoke_2026-06-27
```

Result:

```text
status: passed
install_status: passed
smoke_status: passed
install_returncode: 0
smoke_returncode: 0
matrix_apps: 10
matrix_rows: 30
measured_partners: cupy, numba, rtdl_native, torch
cupy_grouped_vector_sum_status: certified_partner_measured_ready
numba_component_union_status: tier2_measured_ready
venv_removed: true
```

## Boundary

This closes the packaging hygiene question for the candidate commit checked
above. Because this record itself was added after that first clean-smoke run,
the amended final tag target was clean-checkout and installed-wheel smoked
again before creating `v4.0.0`.

Final tag target:

```text
1c8f63cbadbb1edfc994c1c2477a94a7f00a8639
```

Final wheel:

```text
rtdl_source_tree-4.0.0-py3-none-any.whl
sha256: 30257f006e8508542b6eb46c3076ca2e5fca3c31620d2bc048f503cfd4d29f58
```

Final installed-wheel smoke:

```text
status: passed
install_status: passed
smoke_status: passed
matrix_apps: 10
matrix_rows: 30
measured_partners: cupy, numba, rtdl_native, torch
```

This goal does not authorize:

- broad all-app speedup wording;
- broad V4-over-V2.14 or V4-over-V3 speedup wording;
- Tier-3 callback/PTX public support;
- raw OptiX callback support;
- true-zero-copy claims;
- no-copy Barnes-Hut tree-build wording;
- public paper-reproduction speedup wording.

## Goal-Level Decision Audit

1. 我是否愚蠢了？
   - 没有。真正愚蠢的动作是拿 dirty tree 或旧 `dist/` wheel 去打公共 tag。
2. 如果是，我做了哪些动作使决策成为愚蠢的？
   - 前一步已经避免了：没有 tag stale HEAD，也没有把 raw logs、V3 Phoenix history、zero-byte evidence 打进 release commit。
3. 是不是有别的路径避免卡在某一个坏思路？
   - 有：用 Goal4775 pathspec 做 clean commit，再用 clean worktree 构建并安装 wheel。
4. 我是否可以开始尝试不同路径真正解决问题？
   - 可以。最终动作是对 amended final tag target 再跑 clean smoke，然后创建 `v4.0.0` tag。
