---
description: 从 openspec/changes/<change-id>/ 生成可维护的 issues CSV 快照（唯一命名；不生成 issues/issues.csv）
argument-hint: "<change-id> [补充说明或文档路径...]"
---

你现在处于「OpenSpec Change → Issues CSV 模式」。

目标：把 `openspec/changes/<change-id>/` 文件夹（由 `/openspec:proposal` 生成的完整变更提案）转换为可落盘、可协作维护的 **唯一命名 issues CSV 快照**（`issues/<timestamp>-<change-id>.csv`），并确保该 CSV 可以作为代码的一部分提交到仓库中，用于长期追踪任务边界与状态。

> 核心原则：ISSUES CSV 是"会议落盘的任务边界合同"，不是 AI 自嗨文档。
> CSV 要能防止任务跑偏：每条必须明确 **做什么、怎么验收、怎么 review、用什么测试工具/MCP**。

---

## 一、输入与默认行为

### 1.1 主输入：OpenSpec Change

1. `$ARGUMENTS` 的**第一部分**是 `change-id`（可选）：
   - 若为空或未指定：默认选择 `openspec/changes/` 目录下**最新**的非 `archive/` 子目录。
   - 若指定：定位到 `openspec/changes/<change-id>/`。

2. 你必须读取该 change 文件夹下的**全部核心文件**（按顺序）：
   1. `proposal.md`（必须）：Why/What/Impact/Risks/Breaking Changes/Rollback
   2. `design.md`（可选但重要）：Constraints/Goals/Non-Goals/Decisions/Risks/Migration/Open Questions
   3. `tasks.md`（必须）：任务分解 + Dependencies + Validation Criteria
   4. `specs/*/spec.md`（可选但重要）：Requirements (SHALL) + Scenarios (WHEN/THEN)

### 1.2 补充输入（可选）

用户可以在 `$ARGUMENTS` 中追加**任意补充内容**，形式不限：

- **自然语言说明**：额外的背景、约束、优先级调整、特殊要求等
  - 示例：`add-l2-updater 这个任务需要在周五前完成，优先处理数据库相关的`
  - 作用：影响 priority 判断、notes 填充、任务理解

- **文档路径**：指向项目内的其他文档（PRD、会议记录、技术调研等）
  - 示例：`add-l2-updater plan/agent_refactor/Memory_Subgraph_Specification_V2.5.md`
  - 作用：作为额外的 refs 来源，补充 acceptance_criteria 或 review_requirements

- **混合形式**：自然语言 + 文档路径
  - 示例：`add-l2-updater 参考之前的设计 plan/agent_refactor/WorkTree_Plan.md 里面有依赖说明`

**处理规则**：
1. 如果补充内容看起来像文件路径（包含 `/` 或 `\` 且文件存在），读取该文件作为上下文
2. 其他内容作为自然语言理解，影响 CSV 生成时的判断
3. 补充文档中的信息可以进入 `refs` 和 `notes` 字段

### 1.3 错误处理

若找不到 change 文件夹或缺少 `proposal.md` / `tasks.md`：用 1–2 句话说明原因，并给出你需要的最小补充信息。

---

## 二、OpenSpec 文件全量信息提取

### 2.1 从 proposal.md 提取

| 节 | 提取内容 | CSV 字段映射 |
|---|---|---|
| `## Why` | 背景动机 | 理解上下文（不直接入 CSV） |
| `## What Changes` | 变更清单 | `description`（概括） |
| `## Impact → Affected Specs` | 影响的能力 | `refs`（指向 specs） |
| `## Impact → Affected Code` | 影响的代码目录 | `area` 推断 |
| `## Impact → Dependencies` | 外部依赖 | `notes`（阻塞条件） |
| `## Impact → Risk Assessment` | 风险表格 | `priority` 推断（High Impact → P0/P1） |
| `## Impact → Breaking Changes` | 破坏性变更表格 | **强制 priority = P0** |
| `## Impact → Rollback Strategy` | 回滚方案 | `review_regression_requirements` |

### 2.2 从 design.md 提取

| 节 | 提取内容 | CSV 字段映射 |
|---|---|---|
| `## Context → Constraints` | `P0:` 标记的约束 | **强制 priority = P0**；记入 `acceptance_criteria` |
| `## Goals / Non-Goals` | 范围边界 | 验证任务是否在范围内；Non-Goals 相关任务标记到 `notes` |
| `## Decisions` | 技术决策 | `refs`（指向决策）；`notes`（关键决策摘要） |
| `## Decisions → Alternatives` | 备选方案 | `review_initial_requirements`（为何不选其他方案） |
| `## Risks / Trade-offs` | 风险表格 | `review_regression_requirements`（Mitigation 策略） |
| `## Migration Plan` | 迁移步骤 | 验证任务顺序是否与迁移步骤一致 |
| `## Migration Plan → Rollback` | 回滚步骤 | `review_regression_requirements` |
| `## Open Questions` | 未解决问题 | `notes`（标记"待澄清"）；可能影响 `priority` |

### 2.3 从 tasks.md 提取

| 结构 | 提取内容 | CSV 字段映射 |
|---|---|---|
| `## N. Section (WT2-0X)` | Phase + 任务组编号 | `phase`；`id` 前缀（如 `WT2-01`） |
| `### N.M Subsection` | 任务单元标题 | `title` |
| `- [ ] N.M.X Task...` | 具体任务项 | `description`（概括多个 checkbox） |
| `## Dependencies` | 依赖关系 | `notes`（"Blocked by: ..."）；影响 `priority` |
| `## Validation Criteria` | 验证命令 | **直接作为 `acceptance_criteria`** |

### 2.4 从 specs/*/spec.md 提取

| 结构 | 提取内容 | CSV 字段映射 |
|---|---|---|
| `### Requirement: Name` | 需求标题 | 关联到对应任务的 `refs` |
| `The system SHALL...` | 规范性语句 | `acceptance_criteria`（SHALL 语句本身就是验收标准） |
| `#### Scenario: Name` | 场景标题 | 关联到 `acceptance_criteria` |
| `- **WHEN** ... - **THEN** ...` | 测试条件 | `acceptance_criteria`（WHEN→THEN 格式） |
| `## ADDED/MODIFIED/REMOVED` | 变更类型 | 影响 `test_mcp` 选择（MODIFIED 需要回归测试） |

---

## 三、Priority 智能推断规则

按以下优先级顺序确定 `priority` 字段：

| 优先级 | 触发条件 | 来源 |
|---|---|---|
| **P0** | 任务关联 `P0:` 约束 | design.md Context → Constraints |
| **P0** | 任务涉及 Breaking Changes | proposal.md Impact → Breaking Changes |
| **P0** | tasks.md 中标记 `**Priority**: Critical` | tasks.md 任务描述 |
| **P1** | 任务被多个其他任务依赖 | tasks.md Dependencies 图 |
| **P1** | 任务涉及 High Impact 风险 | design.md Risks / proposal.md Risk Assessment |
| **P1** | tasks.md 中标记 `**Priority**: High` | tasks.md 任务描述 |
| **P2** | 默认值 | 无特殊标记 |
| **降级** | 任务有 Open Questions 未解决 | design.md Open Questions |
| **降级** | 任务被其他任务阻塞 | tasks.md Dependencies "Blocked by" |

---

## 四、Acceptance Criteria 构建规则

按以下顺序组合 `acceptance_criteria`：

1. **首选**：`specs/*/spec.md` 中对应 Requirement 的 Scenario（WHEN→THEN 格式）
2. **补充**：`specs/*/spec.md` 中的 SHALL 语句（规范性验收标准）
3. **补充**：`design.md` 中的 P0 Constraints
4. **补充**：`tasks.md` 底部的 Validation Criteria（如 `pytest ...` 命令）
5. **格式**：每条标准用分号分隔，末尾附 `ref: file:line`

**示例**：
```
"WHEN duplicate job enqueued → THEN INSERT ignored; SHALL provide idempotency; ref: specs/l2-updater-service/spec.md:26; validate: pytest backend/tests/..."
```

---

## 五、Review Requirements 构建规则

### review_initial_requirements（开发中 Review）

来源优先级：
1. `design.md` Decisions → Alternatives（"为何不用 X 方案"）
2. `proposal.md` Impact → Risk Assessment（开发时需关注的风险点）
3. 通用要点：兼容性、日志、错误处理、边界条件

### review_regression_requirements（回归 Review）

来源优先级：
1. `design.md` Risks → Mitigation 策略
2. `design.md` Migration Plan → Rollback 步骤
3. `proposal.md` Rollback Strategy
4. `specs/*.md` 中的 MODIFIED Requirements（需要回归验证）
5. 通用要点：故障注入、并发、性能基线

---

## 六、CSV Schema（固定表头）

```
id,priority,phase,area,title,description,acceptance_criteria,test_mcp,review_initial_requirements,review_regression_requirements,dev_state,review_initial_state,review_regression_state,git_state,owner,refs,notes
```

### 字段填写规范

| 字段 | 格式 | 来源 |
|---|---|---|
| `id` | `<TASK-GROUP>-<seq>`（如 `WT2-01-01`） | tasks.md `## N. Section (WT2-0X)` |
| `priority` | `P0\|P1\|P2` | 见「三、Priority 智能推断规则」 |
| `phase` | `1\|2\|3...` | tasks.md `## N.` 中的 N |
| `area` | `backend\|frontend\|both\|infra` | proposal.md Affected Code |
| `title` | 一句话标题 | tasks.md `### N.M` 标题 |
| `description` | 1-2 句边界说明 | tasks.md checkbox 概括 |
| `acceptance_criteria` | 见「四」 | specs + design.constraints + validation |
| `test_mcp` | 见「七」 | 根据 area + 任务性质推断 |
| `review_initial_requirements` | 见「五」 | design.decisions + risks |
| `review_regression_requirements` | 见「五」 | design.risks + rollback |
| `dev_state` | `未开始` | 默认 |
| `review_initial_state` | `未开始` | 默认 |
| `review_regression_state` | `未开始` | 默认 |
| `git_state` | `未提交` | 默认 |
| `owner` | 留空 | 会议分配 |
| `refs` | `file:line; file:line` | 指向 openspec 各文件 |
| `notes` | 自由备注 | Open Questions / Dependencies / 关键决策 |

---

## 七、测试执行器 / MCP 指定

| test_mcp | 适用场景 | 触发条件 |
|---|---|---|
| `AUTOSERVER` | 后端单测/接口测试 | area=backend |
| `AUTOFRONTEND` | 前端组件测试 | area=frontend |
| `AUTOE2E` | 端到端联调 | area=both 或涉及多服务 |
| `CONTRACT` | Schema/契约验证 | 任务涉及 adapter/schema/API 契约 |
| `MIGRATION` | 数据迁移验证 | 任务涉及 Alembic/数据迁移 |
| `MANUAL` | 需人工验证 | 涉及 UI/UX 体验或无法自动化 |

---

## 八、状态字段（枚举，禁止百分比）

| 字段 | 允许值 | 默认 |
|---|---|---|
| `dev_state` | `未开始\|进行中\|已完成` | `未开始` |
| `review_initial_state` | `未开始\|进行中\|已完成` | `未开始` |
| `review_regression_state` | `未开始\|进行中\|已完成` | `未开始` |
| `git_state` | `未提交\|已提交` | `未提交` |

---

## 九、任务拆分规则

1. **默认粒度**：`### N.M` 级别 → 一条 issues
2. **允许合并**：若某个 `### N.M` 下只有 1-2 个简单 checkbox，可与相邻合并
3. **允许拆分**：若某个 `### N.M` 包含明显独立的多项工作，可拆分
4. **建议规模**：5–30 行最易维护

---

## 十、文件命名与编码

1. 目录：确保 `issues/` 存在
2. 文件名：`issues/YYYY-MM-DD_HH-mm-ss-<change-id>.csv`
3. 禁止：不要创建 `issues/issues.csv`
4. 编码：**UTF-8 with BOM**（Excel 友好）
5. 转义：所有字段用双引号包裹，内部 `"` 用 `""` 转义

---

## 十一、执行步骤

1. **定位输入**：根据 `$ARGUMENTS` 或默认规则定位 openspec change 文件夹
2. **全量读取**：
   - `proposal.md` → 提取 Breaking Changes / Risk Assessment / Rollback
   - `design.md` → 提取 P0 Constraints / Decisions / Risks / Open Questions
   - `tasks.md` → 提取任务结构 + Dependencies + Validation Criteria
   - `specs/*/spec.md` → 提取 Requirements + Scenarios
3. **构建任务映射**：
   - 从 tasks.md 提取 phase 和任务单元
   - 关联 specs 中的对应 Requirement（通过关键词匹配）
   - 应用 Priority 推断规则
4. **生成 CSV 行**：按照字段规范填充
5. **写入文件**：UTF-8 BOM 编码
6. **校验**：
   - `Import-Csv` 验证可解析
   - 检查状态字段枚举
   - 检查 `refs` 非空

---

## 十二、对话内输出格式

```
**生成完成**
- 快照路径：`issues/YYYY-MM-DD_HH-mm-ss-<change-id>.csv`
- 来源 change：`openspec/changes/<change-id>/`
- 行数统计：N 条 issues
- P0 任务：M 条（涉及 Breaking Changes / P0 Constraints）
- 注意事项：（如有 Open Questions 影响的任务）
- 下一步：`/issues_csv_execute issues/YYYY-MM-DD_HH-mm-ss-<change-id>.csv`
```

若无法写文件：输出完整 CSV 代码块 + 目标路径 + 编码要求。
