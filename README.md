# AutoML Agent — 用 Cursor AI 自动优化机器学习模型

> 一个完整、可运行的 AutoML Dev Agent 示例，演示如何结合 **Cursor Skill + Hooks + GitHub MCP** 构建一个能自主改代码、训练模型、调参、提交 Git、创建 PR 的智能体。

---

## 目录

- [项目简介](#项目简介)
- [目录结构](#目录结构)
- [快速开始](#快速开始)
- [核心概念详解](#核心概念详解)
  - [SKILL.md — Agent 的知识库](#skillmd--agent-的知识库)
  - [Hooks — 自动化流水线](#hooks--自动化流水线)
  - [Scratchpad — Agent 状态管理](#scratchpad--agent-状态管理)
- [每个文件说明](#每个文件说明)
- [Agent 执行流程](#agent-执行流程)
- [Hook 详细说明](#hook-详细说明)
- [进阶扩展](#进阶扩展)
- [常见问题](#常见问题)

---

## 项目简介

这个项目展示了一个 **AutoML Agent** 的完整设计，目标能力：

| 能力 | 实现方式 |
|------|---------|
| 自动写/修改模型代码 | Cursor Agent + SKILL.md 引导 |
| 自动训练模型 | `train_model.py` hook |
| 自动调参 | Agent 读取 accuracy 反馈后修改代码 |
| 自动运行测试 | `run_tests.py` hook |
| 自动提交 Git | `auto_commit.py` hook |
| 自动创建 PR | `create_pr.py` hook + GitHub CLI |

**技术栈：** Python · scikit-learn · pytest · GitHub CLI · Cursor Hooks

---

## 目录结构

```
automl-agent/
│
├─ src/
│  ├─ model.py          # 模型定义 + 数据加载
│  ├─ train.py          # 训练入口
│  └─ evaluate.py       # 评估脚本（输出 accuracy）
│
├─ tests/
│  └─ test_model.py     # 单元测试
│
├─ data/
│  └─ sample.csv        # 示例分类数据
│
├─ .cursor/
│  ├─ hooks.json        # Hook 注册配置（告诉 Cursor 何时运行哪些脚本）
│  ├─ scratchpad.md     # Agent 状态记录（迭代日志、当前目标）
│  └─ hooks/
│      ├─ pre_run_check.py   # Start Hook：运行前环境及依赖检查
│      ├─ format_code.py    # Stop Hook 1：代码格式化 (ruff) - 演示主动修改代码
│      ├─ security_scan.py  # Stop Hook 2：静态安全检查 (bandit)
│      ├─ run_tests.py      # Stop Hook 3：运行 pytest
│      ├─ train_model.py    # Stop Hook 4：自动训练
│      ├─ check_metrics.py  # Stop Hook 5：评估 accuracy 并给 Agent 反馈
│      ├─ check_model_size.py # Stop Hook 6：资源约束检查（文件大小限制）
│      ├─ auto_commit.py    # Stop Hook 7：自动 git commit
│      └─ create_pr.py      # Stop Hook 8：自动创建 GitHub PR
│
├─ SKILL.md             # Agent 技能文档（优化策略、工作流）
├─ requirements.txt
└─ README.md
```

---

## 快速开始

### 1. 环境准备与依赖安装（推荐使用 `uv`）

通过 [uv](https://github.com/astral-sh/uv) 创建极速虚拟环境，大大加快 Agent 自动化过程中的包管理和格式化速度：

```bash
# 安装 uv (如果系统尚未安装)
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows: 
.venv\Scripts\activate
# macOS/Linux: 
# source .venv/bin/activate

# 极速安装依赖
uv pip install -r requirements.txt
```

### 2. 初始化 Git 仓库（Hooks 中的 commit/PR 需要）

```bash
cd automl-agent
git init
git add .
git commit -m "initial commit"
```

### 3. 连接 GitHub（可选，用于自动创建 PR）

```bash
# 安装 GitHub CLI
# macOS:
brew install gh
# Windows: https://cli.github.com/

# 登录
gh auth login

# 关联远程仓库
git remote add origin https://github.com/your-username/automl-agent.git
git push -u origin main
```

### 4. 手动验证流程

```bash
# 运行测试
pytest tests/ -q

# 训练模型
python src/train.py

# 评估模型
python src/evaluate.py
```

### 5. 在 Cursor 中启动 Agent

在 Cursor 聊天框输入：

```
@SKILL.md 请帮我自动优化模型，使 accuracy 达到 0.9 以上。
```

Agent 会自动进入优化循环，每轮结束后 Hooks 自动执行。

---

## 核心概念详解

### SKILL.md — Agent 的知识库

`SKILL.md` 是 Cursor Agent 的**专业知识文档**，等同于给 Agent 一份"操作手册"。

**作用：**
- 定义任务目标（accuracy >= 0.9）
- 定义 Agent Personas（状态机）：指导 Agent 在 Data Engineer 和 Model Tuner 等不同角色之间切换
- 规定工作流（读 scratchpad → 判断 Persona → 改代码 → 看结果 → 循环）
- 提供具体的优化策略（换模型、调参、特征工程）
- 指定文件地图，让 Agent 知道该改哪些文件

**使用方式：**
```
# 在 Cursor 聊天框中通过 @ 引用
@SKILL.md 开始自动优化任务
```

Agent 会读取 SKILL.md 的全部内容，并严格按照其中的 Workflow 执行。

---

### Hooks — 自动化流水线

Hooks 是 Cursor 在 **Agent 开始和完成每轮操作时自动运行的脚本**，配置在 `.cursor/hooks.json`。

#### Hook 执行时机

```
Agent 开始工作
        ↓
  [start hook 触发]
        ↓
pre_run_check.py  → 验证数据集和依赖环境是否就绪，不通过则中断
        ↓
Agent 完成一轮修改
        ↓
  [stop hook 触发]
        ↓
format_code.py    → 使用 ruff 自动格式化代码（主动修改）
        ↓
security_scan.py  → 使用 bandit 进行静态安全检查，不通过则要求修复
        ↓
run_tests.py      → 运行单元测试，如果失败，发送 followup_message 给 Agent
        ↓
train_model.py    → 如果失败，发送 followup_message 给 Agent
        ↓
check_metrics.py  → 解析 accuracy，发送反馈给 Agent
        ↓
check_model_size.py → 检查模型大小约束，超限则退回修改
        ↓
auto_commit.py    → git add + commit
        ↓
create_pr.py      → 检测到 DONE 时创建 PR
```

#### Hook 通信协议

每个 Hook 脚本必须在 **stdout** 输出一个 JSON 对象：

```python
# 正常情况（不打断 Agent）
print(json.dumps({}))

# 需要 Agent 处理（Agent 会收到这条消息并继续工作）
print(json.dumps({
    "followup_message": "Tests failed. Fix the failing tests."
}))
```

> **关键**：`followup_message` 会被 Cursor 注入给 Agent 作为下一轮的输入，驱动 Agent 自动修复问题。

#### .cursor/hooks.json 配置

```json
{
  "version": 1,
  "hooks": {
    "start": [
      { "command": "python .cursor/hooks/pre_run_check.py" }
    ],
    "stop": [
      { "command": "python .cursor/hooks/format_code.py" },
      { "command": "python .cursor/hooks/security_scan.py" },
      { "command": "python .cursor/hooks/run_tests.py" },
      { "command": "python .cursor/hooks/train_model.py" },
      { "command": "python .cursor/hooks/check_metrics.py" },
      { "command": "python .cursor/hooks/check_model_size.py" },
      { "command": "python .cursor/hooks/auto_commit.py" },
      { "command": "python .cursor/hooks/create_pr.py" }
    ]
  }
}
```

- `"start"` 键表示在 Agent **开始工作前** 触发
- `"stop"` 键表示在 Agent **停止（完成一轮）** 时触发
- 钩子内部命令**按顺序**执行
- 工作目录是项目根目录

---

### Scratchpad — Agent 状态管理

`.cursor/scratchpad.md` 是 Agent 的**状态记录文件**，相当于 Agent 的"工作日记"。

**用途：**
- 记录每次迭代的结果（模型类型、参数、accuracy）
- 标记任务是否完成（`DONE` 标志被 `create_pr.py` 检测）
- 让 Agent 跨轮次保持上下文

**Agent 应该在每轮结束时更新这个文件：**

```markdown
| 1 | LogisticRegression | C=1.0      | 0.62 | baseline       |
| 2 | RandomForest       | n=100      | 0.82 | better model   |
| 3 | RandomForest       | n=200      | 0.92 | target reached |

## Final Status
`DONE`
```

当 `scratchpad.md` 中出现 `DONE` 时，`create_pr.py` 会自动触发 PR 创建。

---

## 每个文件说明

### `src/model.py`

```python
def load_data(path="data/sample.csv"):
    # 读取 CSV，返回特征 X 和标签 y

def build_model(model_type="logistic", C=1.0, n_estimators=100):
    # 支持两种模型：LogisticRegression / RandomForestClassifier
    # Agent 调参的核心目标就是修改这里的参数
```

Agent 在优化时主要修改这个文件：
- 切换 `model_type`
- 调整 `C`、`n_estimators` 等超参数
- 在 `load_data()` 中添加特征工程

---

### `src/train.py`

训练入口，保存模型到 `model.joblib`：

```bash
python src/train.py
```

由 `train_model.py` hook 自动调用，不需要手动执行。

---

### `src/evaluate.py`

评估模型，**必须输出格式为 `accuracy: X.XXXX`**（check_metrics.py 用正则解析这个值）：

```bash
python src/evaluate.py
# 输出：accuracy: 0.9167
```

---

### `tests/test_model.py`

4 个单元测试：
1. 逻辑回归模型可以创建
2. 随机森林模型可以创建
3. 数据加载返回正确列
4. 模型可以完成拟合和预测

每轮 Hook 先跑这些测试，失败则阻断流程并要求 Agent 修复。

---

## Agent 执行流程

```
用户: @SKILL.md 优化模型，目标 accuracy >= 0.9
         │
         ▼
   Agent 读取 SKILL.md
   Agent 读取 scratchpad.md（了解当前状态）
         │
         ▼
   Agent 修改 src/model.py
   （例如：改为 RandomForestClassifier）
         │
         ▼
   Agent 完成本轮操作（stop 触发）
         │
    ┌────▼────────────────────────────────┐
    │         Hooks 自动执行               │
    │  1. pytest → 通过 ✓                 │
    │  2. python src/train.py → 成功 ✓    │
    │  3. python src/evaluate.py          │
    │     accuracy: 0.82                  │
    │     → followup: "0.82 < 0.9, 继续" │
    │  4. git commit                      │
    │  5. scratchpad 无 DONE, 跳过 PR     │
    └────┬────────────────────────────────┘
         │
         ▼
   Agent 收到 followup_message
   继续修改代码（调参 n_estimators=200）
         │
         ▼
   第 N 轮... accuracy = 0.92 ✓
         │
    ┌────▼────────────────────────────────┐
    │  check_metrics: "达到目标，更新     │
    │  scratchpad 为 DONE"               │
    └────┬────────────────────────────────┘
         │
         ▼
   Agent 更新 scratchpad.md: Final Status = DONE
         │
         ▼
   create_pr.py 检测到 DONE → gh pr create
         │
         ▼
         PR URL 返回给 Agent，任务结束
```

---

## Hook 详细说明

### Hook 1: `pre_run_check.py`

| 项目 | 说明 |
|------|------|
| 触发时机 | Agent 开始工作前（start hook） |
| 行为 | 检查数据文件和依赖环境（`pandas`, `sklearn`）是否就绪 |
| 作用 | 避免因为基础环境没配置好导致 Agent 浪费大量时间和 token 去排查环境问题 |

### Hook 2: `format_code.py`

| 项目 | 说明 |
|------|------|
| 触发时机 | 每轮 stop 后第一个执行 |
| 命令 | `ruff format src/ tests/` |
| 作用 | 自动使用 Ruff 格式化代码，减轻 Agent 对格式细节的关注 |

### Hook 3: `security_scan.py`

| 项目 | 说明 |
|------|------|
| 触发时机 | 格式化代码之后执行 |
| 命令 | `bandit -r src/ -q` |
| 失败 | 输出 `{"followup_message": "Security Scan Failed..."}` |
| 作用 | 进行静态代码安全检查，确保不会引入常见漏洞，如果有漏洞立即强制 Agent 修复 |

### Hook 4: `run_tests.py`

| 项目 | 说明 |
|------|------|
| 触发时机 | 安全检查通过后执行 |
| 命令 | `pytest tests/ -q --tb=short` |
| 成功 | 输出 `{}` |
| 失败 | 输出 `{"followup_message": "Tests failed..."}` |
| 作用 | 充当安全门，防止坏代码进入训练环节 |

### Hook 5: `train_model.py`

| 项目 | 说明 |
|------|------|
| 触发时机 | run_tests 通过后 |
| 命令 | `python src/train.py` |
| 成功 | 生成/更新 `model.joblib` |
| 失败 | 告知 Agent 修复训练脚本 |
| 作用 | 确保每轮代码变更后模型都重新训练 |

### Hook 6: `check_metrics.py`

| 项目 | 说明 |
|------|------|
| 触发时机 | train_model 完成后 |
| 命令 | `python src/evaluate.py` |
| 解析 | 正则 `accuracy:\s*([0-9.]+)` |
| accuracy < 0.9 | 返回改进建议给 Agent |
| accuracy >= 0.9 | 通知 Agent 任务完成 |
| 作用 | **这是 AutoML 循环的核心驱动器** |

### Hook 7: `check_model_size.py`

| 项目 | 说明 |
|------|------|
| 触发时机 | check_metrics 之后 |
| 行为 | 检查 `model.joblib` 文件大小 |
| 失败 | 超出 1.0MB 时要求 Agent 简化模型 |
| 作用 | 模拟生产环境的资源约束，增加 Agent 任务的现实挑战性 |

### Hook 8: `auto_commit.py`

| 项目 | 说明 |
|------|------|
| 触发时机 | 检查完模型大小之后 |
| 行为 | `git add . && git commit -m "AI: improve model [时间戳]"` |
| 安全设计 | 非 git 仓库 / 无改动时静默跳过，不报错 |
| 作用 | 每次改进都有记录，可以 git log 回溯 |

### Hook 9: `create_pr.py`

| 项目 | 说明 |
|------|------|
| 触发时机 | auto_commit 之后 |
| 前提条件 | scratchpad.md 中含有 `DONE` |
| 依赖 | GitHub CLI (`gh`) 已安装并已 `gh auth login` |
| 行为 | `gh pr create --title ... --body ...` |
| 作用 | 任务完成后自动提交 PR，无需人工干预 |

---

## 进阶扩展

### 自动调参（GridSearchCV）

在 `src/train.py` 中加入：

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    "n_estimators": [50, 100, 200, 500],
    "max_depth": [None, 3, 5, 10]
}
gs = GridSearchCV(model, param_grid, cv=3, n_jobs=-1)
gs.fit(X, y)
model = gs.best_estimator_
print("Best params:", gs.best_params_)
```

### 自动特征工程

在 `src/model.py` 的 `load_data()` 中：

```python
df["x1_x2"] = df["x1"] * df["x2"]     # 交叉特征
df["x1_sq"] = df["x1"] ** 2            # 多项式特征
df["x2_sq"] = df["x2"] ** 2
X = df[["x1", "x2", "x1_x2", "x1_sq", "x2_sq"]]
```

### 实验记录

在 `check_metrics.py` 中追加写入 `experiments.json`：

```python
import json
from datetime import datetime

record = {
    "timestamp": datetime.now().isoformat(),
    "accuracy": acc,
    "model": "RandomForest"
}
with open("experiments.json", "a") as f:
    f.write(json.dumps(record) + "\n")
```

---

## 常见问题

**Q: Hook 没有触发？**  
A: 确认 `.cursor/hooks.json` 的格式正确，且 Cursor 版本支持 Hooks 功能。

**Q: `evaluate.py` 报错 `model.joblib not found`？**  
A: 先手动运行 `python src/train.py` 生成模型文件。

**Q: `create_pr.py` 提示 gh not found？**  
A: 需要安装 [GitHub CLI](https://cli.github.com/) 并执行 `gh auth login`。

**Q: pytest 找不到 src 模块？**  
A: `tests/test_model.py` 已经通过 `sys.path.insert` 处理，确保从项目根目录运行 `pytest`。

**Q: accuracy 始终是 0.0？**  
A: 检查当前目录是否是项目根目录（`automl-agent/`），`data/sample.csv` 路径必须相对于根目录。

---

## 学习要点总结

| 概念 | 文件 | 核心作用 |
|------|------|---------|
| **Skill** | `SKILL.md` | 给 Agent 提供领域知识和工作流指引 |
| **Hook 配置** | `.cursor/hooks.json` | 注册自动化脚本，定义触发时机 |
| **Hook 脚本** | `.cursor/hooks/*.py` | 实现自动化步骤，通过 `followup_message` 与 Agent 通信 |
| **Scratchpad** | `.cursor/scratchpad.md` | Agent 的跨轮状态记忆，也作为信号（DONE）触发 PR |
| **MCP/CLI** | `gh` 命令 | 与外部系统（GitHub）集成 |

---

*This project is a learning example for building AI Dev Agents with Cursor.*
