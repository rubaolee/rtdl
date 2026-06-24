# Phoenix V3 修订版 Goals — 先把 Barnes-Hut 的数摊出来

Date: 2026-06-24
Author: Claude(独立评审）— 对主AI 12-goal 列表的严格修订，**非发布/POD 授权**
对照：主AI 2026-06-24 的 Goal 1–12；本版按 7 点严格审核意见重排。

## 贯穿规则（每个 Goal 都适用）

1. **进展只有一个定义**：某个命名 scorecard blocker 在同合约同硬件上移动 + `hot_path_host_materialization: false` + 记录 `win_source` + **`parity_pass: true`**。绿测试、审计、里程碑号、被阻塞的评审都不算进展。
2. **Correctness parity 与性能是并列的门。** 算错的“更快”等于零。
3. **禁止 process churn。** 除 Goal 1/3/10 明确允许的文档外，不开任何审计/评审/协议里程碑。
4. **“完成”不等于“更快”。** 见 Goal 11 两种合法完成形态。
5. **Goal 0 没出数之前，禁止一切“泛化/第二 blocker”工作。**

---

## Goal 0 —（新增·前置闸门）摊出 Barnes-Hut 对 0.844x 的实测，并据此分叉

这是整组 goals 的地基。原列表跳过了它，直接去“选第二个 blocker”，这是最大硬伤。

- 同硬件、同合约、同 scorecard 行：barnes_hut 走 runner vs 0.844x incumbent 的**实测比值**。
- 同时产出：`parity_pass`、`win_source`、`runtime_executed`、`hot_path_host_materialization`、`phase_seconds`。
- **分叉（硬性）：**
  - 比值达到 Goal 3 冻结的 Set-A 阈值且 `parity_pass` → 进 Goal 1。
  - 未移动 / parity 不过，且 Goal 0 诊断瓶颈在 kernel 本身 → **直接进 Goal 11 的 No-Go（能力转向），不许往下做泛化。**
- **禁止：** 在这个数出来之前做任何 Goal 1+ 的工作。“拉回泛化”只有在 barnes_hut 真动了的前提下才正确；否则它就是逃避第一个负结果。

## Goal 1 — 冻结事实基线（压缩成指针）+ 仓库卫生

- 不写新“事实表”。指向已有的 paired run（1.012x）与 Set-A/Set-B scorecard，**并写明 Goal 0 的 barnes_hut 实测数**。一段话。
- **仓库真相（安全、可早做）：** 收敛提交 06-20 以来的 V3 重建工作，按 06-20 决定退役 HEAD 那个“V4.0.0 promoted”。现在仓库已提交真相与“只做 V3”冲突。

## Goal 2 — 选第二个 blocker，且 win_source 必须与 Barnes-Hut 不同

- 从 scorecard 现在就**点名候选 + 当前数**（如 `librts_spatial_index` 0.937x / RTNN），选真正控盘的行，不选易刷小胜的行。
- **硬约束：** 选一个**预期 `win_source` 与 barnes_hut 不同**的。若 barnes_hut 靠 `residency_wall`，第二个最好能测 `partner_continuation` 或 `kernel`，反之亦然。两次都靠同一个把戏（如都 CuPy reduction）证明不了 runtime 泛化。

## Goal 3 — 写可证伪协议，并**冻结数值 bar**

- 通过/失败用**数字**，跑前定义、跑后不许改：
  - Set-A：≥ 1.20x **且胜出来自 runtime path**；
  - Set-B：≥ 0.98x（持平）；
  - `parity_pass` 必须为 true；`hot_path_host_materialization` 必须为 false。
- 同硬件、同数据规模、同合约、同 runner、同 scorecard row。

## Goal 4 — 接入同一 trunk（复用，非 app patch）

- 复用 prepared-session runner / device residency / phase telemetry / continuation core node。新代码只能是**通用 runtime primitive**，不得是 app-special native ABI/route。
- **带 correctness parity 验证**（同结果对照参考实现）。

## Goal 5 — focused POD 实验（不跑 all-app）

- 只跑 focused experiment。输出 JSON evidence + summary + claim flags + `win_source` + `runtime_executed` + `hot_path_host_materialization` + **`parity_pass`**。

## Goal 6 — 判定泛化 + win_source 多样性 + 早退闸门

- 判据：barnes_hut（Goal 0）与第二 blocker 是否都**实质 runtime-sourced 地移动了各自 scorecard 行**（对照 Goal 3 数值 bar）且 parity 通过。
- **win_source 多样性检查：** 若两次胜出全靠同一 source，只能声称该**窄能力**，不能声称“trunk 泛化”。
- **早退（硬性）：** 任一未达标 → 立即停，进 Goal 11 No-Go，**不许跳去 Goal 7**。

## Goal 7 — 第三个 family，机检复用（非 app-special）

- 第三 family 必须调用**同名** runner/core-node 机制；用 prepared-session surface ledger 做 shared-symbol 审计，**机检证明**无新 app-special route。带 parity。

## Goal 8 — residency/phase accounting 强制输出（缺字段即失败）

- 所有 routed families 统一输出 `phase_seconds` / `runtime_executed` / `internal_residency` / `hot_path_host_materialization` / `win_source` / **`parity_pass`**。缺字段 fail-closed。

## Goal 9 — focused scorecard 重读（只读已 routed 行）

- 只重读已 routed 的 Set-A/Set-B 行，判“主干是否真移动 scorecard”。
- **明确区分：本步证明的是“泛化（3 个 family）”，不是“清 bar / release-ready”。** 清 bar 需要路由**剩余全部 Set-A** 并清掉所有回归（Goal 11 Go 分支之后）。

## Goal 10 — 外部审核包（此处才需严肃 review）

- code diff + POD evidence + scorecard movement + **win_source 分布** + **parity 结果** + 失败项 + claim boundaries。给 Claude/Antigravity 检查。

## Goal 11 — Go / No-Go（显式双分支）

- **Go：** ≥2 blocker 实质移动（win_source 多样更佳）+ 第三 family 证明泛化 + parity 全过 → 进 Phase B：路由**剩余全部 Set-A** + 清掉所有 Set-A(<0.90x)/Set-B(<0.95x) 回归 → 再申请 all-app。
- **No-Go：** 做不到 → V3 改 **capability/quality release**，去掉一切“普遍比 V2 快”措辞。**这同样是完成 V3，不是失败。**

## Goal 12 — 只有 Go 才跑 all-app

- all-app 是最终验证，不是探索工具。跑完按 Set-A/Set-B 两数记分卡做发布判断；**每个意外行用用户语言解释**。

---

## 与原 12-goal 的关键差异（即 7 点严格审核落地）

1. 新增 **Goal 0 前置闸门**：先摊 barnes_hut 的数，据此分叉——原列表把这个决定一切的二元事实糊掉了。
2. 全程加 **correctness parity** 门（原列表完全没有）。
3. Goal 3 **冻结数值 bar**，Goal 6 据数判定——堵住“实质 gain”事后解释。
4. Goal 2/6 加 **win_source 多样性**——两个 blocker 都靠 CuPy 不叫泛化。
5. Goal 1 并入**仓库卫生/版本真相**（退役 V4.0.0 的 HEAD）。
6. Goal 6 加**显式早退**；Goal 1 由“写事实表”压缩成“指针”，去掉可疑的安全替代品。
7. Goal 9/11 **区分“泛化(3 family)”与“清 bar(全 Set-A)”**——别把前者误读成 release-ready。

## 非授权

本文件不授权任何发布、POD 花费、all-app run、公开/广义 V3-over-V2 措辞、V4/embedding/C-ABI。Gate 维持 `redo_required`，直到 Goal 11 Go + Goal 12 + 外部 verdict。
