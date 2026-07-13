# 治理纪律补充：App-Artifact Parity 的止损/淘汰闸门

Date: 2026-07-10
背景：X-HD `-lb` 线用约 164 个目标去逐字节复现作者一个实现级 offload 流，
成功即违规（须塞入 app 专属逻辑）、失败即无通用产出，且其唯一消费者（Figure 7）
早已被不可得的数据集卡死。根因是缺一个"止损/淘汰闸门"。本规则补上它。

现有纪律只有**准入**规则（"新增通用 API 必须有非-app 消费者才算通用"），
缺**对称的退出**规则。以下规则填补该缺口。

---

## 规则 G-1：Parity-with-App-Artifact 立项前置判定（Kill-Gate）

**定义。** "App-artifact parity 工作"= 任何以对齐某个 app/作者的**实现产物**为目标的工作，
包括但不限于：逐行 / 逐 hash / 内部数据流 / 中间状态 / 内部计数 / 选项专属输出 的字节或计数级对齐。

**前置判定（立项前必须回答，写入 call-for-review）：**

1. 该工作能否产出一个**带非-app 消费者**的通用能力？
   - 能：不属于 parity 工作，按正常通用 API 准入流程走。
   - 不能：进入下面第 2 条。
2. 达成 parity 是否**必须**编码 app/作者专属逻辑、常量或选项语义？
   - 是：**直接 fail-close，不进入实现**。理由：成功将违反"核心不含 app 逻辑"红线，
     失败则零通用产出——本质是"成功即违规、失败即白干"的无赢局。
3. 该 parity 的**唯一下游消费者**当前是否可达？
   - 不可达（例如所需数据集/图表已被独立 blocker 卡死）：**直接 fail-close，不进入实现**。
     即使 parity 完美达成也产不出可审成果。

> 三问中任一命中 fail-close，立项即被拦下。只有"能产出带非-app 消费者的通用能力"
> 才允许继续。

---

## 规则 G-2：进行中工作的连续无产出淘汰线

对已在进行的探索方向（非纯 bug 修复），设硬性淘汰线：

```text
连续 3 个目标未产出"可被非-app 消费者复用的通用能力"
→ 该方向默认 fail-close，须显式再论证方可继续
```

再论证的门槛与 G-1 第 1 条相同：**命名一个 app-neutral 能力 + 指出其非-app 消费者**。
论证不出 = 关闭。禁止以"下一个假设应该就对了"作为继续理由。

---

## 规则 G-3：进度用"通用能力"计量，而非"目标数"

- 每个探索目标的验收字段新增一项：`generic_capability_produced`（是/否 + 名称 + 非-app 消费者）。
- 该字段为"否"的目标**不计入项目进度**，只计入"探索成本"。
- 中期报告须并列两条数字：产出通用能力的目标数 / 纯探索成本目标数。
  防止"局部每个目标都成功、整体没推进真实目标"的错觉。

---

## 规则 G-4：父目标已 blocked，冻结其全部子目标

任一目标被独立 blocker 标记为不可达（如 exact 数据集不可得）后：

```text
以该目标为唯一下游的所有子目标，一并进入 frozen 状态，
不得继续投入实现，直至父 blocker 解除。
```

避免"父目标已死、仍在挖子目标"。

---

## 机器化检查（已接入）

Checker：`scripts/xhd_stop_loss_gate_check.py`
它扫描 goal 报告 / call-for-review 是否含"对齐 app 实现产物"信号
（hash parity / row identity / offload stream / full-cover / namespace reconciliation / `-lb` 等）；
一旦命中，就要求文档带 G-1 应答块，否则 fail-close（退出码 2）。

用法：

```text
py scripts/xhd_stop_loss_gate_check.py <goal_report_or_call_for_review.md> [...]
# 退出 0 = 无 parity 信号，或 parity 工作已正确 gated 且通过
# 退出 2 = 检出 parity 工作但未 gated / 应答判 fail-close
```

已验证：对 `xhd_comprehensive_midterm_status_after_goal5408`（满是 `-lb`/hash/offload 信号、
无 gate 字段）→ **BLOCKED**；对 `goal5127`（通用抽取）、`goal5211`（通用 early-break）→ PASS。
即：它会拦下当年的 `-lb` 线，同时放行真正的通用能力工作。

### 立项文档须内嵌的 G-1 应答块（register / call-for-review 各一份）

```text
gate_generic_capability_produced: true|false      # 是否产出通用能力
gate_non_app_consumer: <名称 或 none>             # 该能力的非-app 消费者
gate_requires_app_specific_logic: true|false       # 达成 parity 是否须编码 app 专属逻辑
gate_downstream_consumer_reachable: true|false      # 唯一下游消费者当前是否可达
```

判定：三个布尔中任一为 `generic=false` / `app_specific=true` / `reachable=false`，
或 `generic=true` 却 `non_app_consumer=none` → **fail-close，不进入实现**。

（若日后并入正式 preflight：把本 checker 作为一个 check 项加入
`scripts/goal5053_v2144_release_preflight.py` 的 checks 列表，
blocked 即整体 blocked，与 legacy-export 门同型。）

## 一句话总纲

> 有准入必有退出。任何以"对齐 app/作者实现产物"为目标的工作，
> 立项前先过 Kill-Gate（G-1）；进行中过淘汰线（G-2）；
> 进度按通用能力计（G-3）；父目标死则子目标冻结（G-4）。
> 判据始终是同一句：**它能否产出一个带非-app 消费者的通用能力？不能，就 fail-close。**
