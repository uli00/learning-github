# 我的 GitHub 学习仓库

> 从零开始学习 GitHub，记录每一步。如果你是小白，可以跟着我的节奏一起学。

## 学习目标

最终目标：创建一个每日定时收集 GitHub Star 暴涨项目的技能。

## 学习进度

- [x] 学会了创建第一个仓库
- [x] 学会在网页上编辑和上传文件
- [x] 了解 GitHub API 的基本用法
- [x] 学会 Git 命令行操作（clone / add / commit / push）
- [ ] 编写 Star 收集脚本
- [ ] 设置每日定时任务
- [ ] 生成每日 Star 报告
- [ ] （进阶）制作 Star 增长动画

---

## 学习笔记

### 一、基础概念

| 概念 | 通俗理解 |
|------|---------|
| **Repository（仓库）** | 就是一个项目的文件夹，里面可以放代码、文档、图片等 |
| **Star** | 相当于点赞收藏，Star 越多说明项目越火 |
| **Fork** | 把别人的项目复制一份到自己账号下，可以在副本上随意修改 |
| **Pull Request（PR）** | 你在 Fork 的项目里改了代码后，请求原作者合并你的修改 |
| **README.md** | 项目的"门面"，别人打开仓库第一眼看到的说明文档 |
| **Markdown** | GitHub 上写文档的通用格式，用简单的符号实现加粗、标题、列表等 |

### 二、Markdown 快速入门

```markdown
# 大标题
## 中标题
### 小标题

**加粗文字**
*斜体文字*

- 列表项 1
- 列表项 2

[链接文字](https://example.com)
![图片描述](图片链接)
```

### 三、GitHub 快速入门

GitHub 提供了官方 API，可以用程序方式获取数据，不用手动打开网页。

**官方文档地址：** [GitHub REST API 文档](https://docs.github.com/en/rest)

**最简单的例子 — 获取一个仓库的信息：**

**输入命令**

```bash
curl -s "https://api.github.com/repos/uli00/learning-github" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('仓库名称:', data.get('full_name'))
print('描述:', data.get('description') or '无')
print('Star 数量:', data.get('stargazers_count'))
print('Fork 数量:', data.get('forks_count'))
print('创建时间:', data.get('created_at'))
print('最后更新:', data.get('updated_at'))
"
```

**输出结果**

```
仓库名称: uli00/learning-github
描述: 从零开始学习github使用直到成为大神（嘿嘿嘿～）
Star 数量: 0
Fork 数量: 0
创建时间: 2026-05-24T03:10:56Z
最后更新: 2026-05-24T03:20:35Z
```

**这个命令做了什么？**

1. `curl -s "..."` — 用程序访问 GitHub API，拿到原始 JSON 数据
2. `| python3 -c "..."` — 把 JSON 数据解析成字典，打印出你关心的字段

**通俗理解：** 就像你打开一个网页看仓库信息，只不过 API 让程序替你"看"，而且速度更快、可以批量处理。

**常用接口速查：**

| 接口 | 用途 |
|------|------|
| `GET /repos/{owner}/{repo}` | 获取某个仓库的详细信息 |
| `GET /search/repositories` | 搜索仓库（按 Star、语言、时间等筛选） |
| `GET /repos/{owner}/{repo}/stargazers` | 获取点了 Star 的用户列表 |

### 四、Git 命令行基础

Git 是管理代码版本的工具，命令行是最常用的操作方式。

**前置配置（只需做一次）：**

```bash
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱"
```

**1. 克隆仓库到本地**

```bash
git clone https://github.com/uli00/learning-github.git
```

这会在当前目录创建一个 `learning-github` 文件夹，把 GitHub 上的整个仓库下载下来。

**2. 查看当前状态**

```bash
git status
```

工作区干净时的输出：

```
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

有新文件未跟踪时的输出：

```
Untracked files:
  (use "git add <file>..." to include in what will be committed)
    notes.md
nothing added to commit but untracked files present (use "git add" to track)
```

**3. 把文件加入暂存区**

```bash
git add notes.md
```

执行后再看 `git status`，会显示 `Changes to be committed: new file: notes.md`。`git add` 的作用是告诉 Git："这个文件我要提交，先放到暂存区。"

**4. 提交更改**

```bash
git commit -m "添加 Git 学习笔记"
```

`-m` 后面是提交说明，描述这次改了什么。每次 commit 都会生成一个唯一的哈希值。

**5. 配置 push 认证（首次推送前必须完成）**

GitHub 已经不支持密码推送，首次 `git push` 前需要完成认证。最简单的方式是安装 GitHub CLI：

```bash
brew install gh
gh auth login
```

按提示操作：
- 选择 **GitHub.com**
- 选择 **HTTPS**
- 选择 **Login with a web browser**，在浏览器里授权
- 当提示 `Authenticate Git with your GitHub credentials? (Y/n)` 时，输入 **Y** 回车

授权完成后，以后执行 `git push` 就不用输密码了。

**6. 推送到 GitHub**

```bash
git push
```

**日常使用总结：**

| 命令 | 作用 |
|------|------|
| `git clone <url>` | 从 GitHub 下载仓库到本地 |
| `git status` | 查看当前状态 |
| `git add <文件>` | 把文件加入暂存区 |
| `git commit -m "说明"` | 提交更改，附带说明文字 |
| `git push` | 推送到 GitHub 上 |

### 五、Git 进阶：分支与合并

#### 查看和创建分支

```bash
git branch
```

输出中 `*` 标记当前所在分支。创建新分支：

```bash
git branch 分支名
```

**重要：新分支会包含当前分支上的全部文件。** 从 main 创建分支时，main 上的一切都会自动"拷贝"过来，不需要手动操作。

#### 切换分支

```bash
git checkout 分支名
```

创建并切换到新分支（一步完成）：

```bash
git checkout -b 分支名
```

#### 合并分支

切回 main 后，把某个分支的改动合并过来：

```bash
git checkout main
git merge 分支名
```

如果两个分支没有修改同一处，Git 会 Fast-forward（快进）自动合并。

#### 分支在真实项目中的工作流

| 分支 | 用途 |
|------|------|
| `main` | 稳定版，随时可以发布 |
| `feature-xxx` | 开发新功能，不影响主线 |
| `bugfix-xxx` | 修复 bug，完成后合并回 main |

典型流程：
1. 从 main 创建功能分支 `git checkout -b feature-新功能`
2. 在功能分支上开发、提交
3. 完成后切回 main `git checkout main`
4. 合并功能分支 `git merge feature-新功能`
5. 删除已合并的分支 `git branch -d feature-新功能`（可选）

#### 解决合并冲突

当两个分支修改了同一文件的同一处，Git 无法自动决定保留谁，就会报冲突：

```
CONFLICT (content): Merge conflict in 文件名
Automatic merge failed; fix conflicts and then commit the result.
```

冲突文件的格式：

```
<<<<<<< HEAD
main 分支的内容
=======
另一个分支的内容
>>>>>>> 分支名
```

**解决步骤：**

1. 打开冲突文件，找到 `<<<<<<<`、`=======`、`>>>>>>>` 标记
2. 编辑文件，删除标记，保留你想要的内容（可以两个都保留，也可以只选一个）
3. 保存文件
4. `git add 文件名` — 标记冲突已解决
5. `git commit -m "解决合并冲突"` — 完成合并

**如果不想合并了，可以取消：**

```bash
git merge --abort
```

### 六、其他常用命令

| 命令 | 作用 |
|------|------|
| `git pull` | 拉取远程更新并合并到本地 |
| `git log --oneline` | 简洁查看提交历史 |
| `git diff` | 查看未提交的改动 |
| `git diff HEAD~1` | 查看最近一次提交前后的差异 |
| `.gitignore` | 文件，列出需要 Git 忽略的文件（如 `.DS_Store`、`*.pyc`、`.env`） |

---

### 七、SkillOpt 源码学习（微软 Agent 技能自动优化框架）

> 仓库地址：https://github.com/microsoft/SkillOpt
> 论文：https://arxiv.org/abs/2605.23904
> 核心思想：**训练过程（procedure），而非模型权重（weights）**

#### 7.1 一句话理解 SkillOpt

SkillOpt 把 Agent 的"技能文档"（一份自然语言写成的操作指南 .md 文件）当作可训练的"参数"，通过类似深度学习训练循环的方式自动迭代优化这份文档，而 Agent 使用的 LLM 模型本身完全不动（冻结）。

打个比方：传统做法是训练大脑（微调模型权重），SkillOpt 的做法是给大脑写一本越来越好的操作手册。

#### 7.2 核心概念：与深度学习的类比

| 深度学习概念 | SkillOpt 对应 | 说明 |
|---|---|---|
| 模型权重 | 技能文档 (skill.md) | 被优化的对象 |
| 前向传播 | Rollout（执行任务） | 用当前技能跑一批任务，记录结果 |
| 反向传播 | Reflect（反思分析） | 分析成功/失败的轨迹，找出改进点 |
| 梯度聚合 | Aggregate（合并补丁） | 把多个分析结果合并成一份统一的修改方案 |
| 梯度裁剪 | Select（排序选择） | 只保留最重要的 N 个修改（文本学习率） |
| 参数更新 | Update（应用编辑） | 把修改应用到技能文档 |
| 验证集评估 | Gate（验证门） | 在留出集上验证，只有分数提升才接受修改 |
| 学习率 | edit_budget（编辑预算） | 每步最多做几条修改，防止大改破坏好的规则 |
| 慢速学习/EMA | Slow Update（慢更新） | 每个 epoch 结束后做跨 epoch 的纵向对比总结 |

#### 7.3 仓库目录结构

```
SkillOpt/
├── skillopt/              # 核心库（论文训练循环）
│   ├── engine/trainer.py  # 训练主循环（最重要的文件，~2400行）
│   ├── optimizer/         # 优化器模块
│   │   ├── clip.py        # "梯度裁剪"：编辑排序与选择
│   │   ├── skill.py       # 编辑应用（append/insert/replace/delete）
│   │   ├── rewrite.py     # 全量重写模式
│   │   ├── slow_update.py # 慢更新（epoch 级纵向反思）
│   │   ├── meta_skill.py  # 优化器元记忆（跨 epoch 经验）
│   │   ├── scheduler.py   # 学习率调度（constant/linear/cosine）
│   │   └── skill_aware.py # 技能感知反思（附录笔记机制）
│   ├── gradient/          # "梯度"计算
│   │   ├── reflect.py     # 反思引擎：minibatch 轨迹分析
│   │   └── aggregate.py   # 聚合引擎：层次化补丁合并
│   ├── evaluation/
│   │   └── gate.py        # 验证门：accept/reject 决策
│   ├── envs/              # 环境适配器（6个 benchmark）
│   │   ├── base.py        # 抽象基类 EnvAdapter
│   │   ├── alfworld/      # 家务机器人环境
│   │   ├── searchqa/      # 搜索问答
│   │   ├── spreadsheetbench/  # Excel 操作
│   │   ├── livemathematicianbench/  # 数学推理
│   │   ├── docvqa/        # 文档视觉问答
│   │   └── officeqa/      # Office 文档问答
│   ├── model/             # LLM 后端
│   │   ├── common.py      # 统一的 chat_optimizer / chat_target 接口
│   │   ├── azure_openai.py
│   │   ├── claude_backend.py
│   │   ├── codex_backend.py
│   │   ├── qwen_backend.py
│   │   └── minimax_backend.py
│   ├── prompts/           # Prompt 模板（.md 文件）
│   │   ├── analyst_error.md    # 失败分析师 prompt
│   │   ├── analyst_success.md  # 成功分析师 prompt
│   │   ├── ranking.md          # 编辑排序 prompt
│   │   ├── merge_*.md          # 合并阶段 prompts
│   │   ├── slow_update.md      # 慢更新 prompt
│   │   └── meta_skill.md       # 元技能 prompt
│   ├── config.py          # YAML 配置加载（支持继承）
│   └── types.py           # 数据结构定义（Edit/Patch/RolloutResult 等）
├── skillopt_sleep/        # Sleep 模式（部署后夜间学习）
├── plugins/               # 插件（Claude Code / Codex / Copilot）
├── ckpt/                  # 训练产出示例（best_skill.md）
├── configs/               # YAML 配置文件
├── data/                  # 数据集 train/val/test 分割
├── scripts/               # 训练入口脚本
│   └── train.py           # 主入口
└── tests/                 # 单元测试
```

#### 7.4 六阶段训练流水线（核心循环）

每一步（step）执行以下 6 个阶段：

```
① Rollout → ② Reflect → ③ Aggregate → ④ Select → ⑤ Update → ⑥ Evaluate
  (执行)      (反思)       (聚合)         (选择)      (更新)      (验证)
```

**① Rollout（执行任务）**
- 用当前 skill.md + 目标 LLM 去跑一批训练任务
- 每个任务产生一条轨迹（对话记录、工具调用、最终得分）
- 返回 `hard`（0/1 是否完全正确）和 `soft`（部分分数）

**② Reflect（反思分析）**
- 把 Rollout 结果按成功/失败分成两组
- 每组再分成多个 minibatch（类似小批量 SGD）
- 对每个 minibatch 调用优化器 LLM 分析轨迹，产出修改建议（Patch）
- 失败分析师找"系统性错误模式"，成功分析师找"值得固化的好模式"
- 关键：多个 minibatch 可以**并行**执行（ThreadPoolExecutor）

**③ Aggregate（聚合补丁）**
- 把所有 minibatch 产出的 Patch 合并为一份
- 采用**层次化合并**：先合并失败类 Patch，再合并成功类，最后两者合一
- 合并时失败补丁优先级高于成功补丁
- 同一层级的合并也可以并行

**④ Select（排序选择 = 梯度裁剪）**
- 如果合并后的编辑数超过预算 L（edit_budget），调用优化器 LLM 排序
- 按"系统性影响 > 互补性 > 通用性 > 可操作性"排序
- 只保留前 L 个最重要的编辑
- 这就是"文本学习率"——防止一步改太多把好的规则覆盖掉

**⑤ Update（应用编辑）**
- 按顺序把编辑应用到 skill.md：
  - `append`：在文档末尾追加（在保护区之前）
  - `insert_after`：在指定位置后插入
  - `replace`：替换指定文本
  - `delete`：删除指定文本
- **保护区机制**：`<!-- SLOW_UPDATE_START -->` 和 `<!-- SLOW_UPDATE_END -->` 之间的内容不能被常规编辑修改

**⑥ Evaluate（验证门）**
- 在留出验证集（valid_seen）上跑候选技能
- 与当前技能对比：
  - 分数 > 当前 → 接受（accept）
  - 分数 > 历史最高 → 接受并标记为新最佳（accept_new_best）
  - 分数 ≤ 当前 → 拒绝（reject），回退到当前技能
- 被拒绝的编辑会记录到 step_buffer，下一步的分析时可以看到，避免重蹈覆辙

#### 7.5 三个关键的稳定机制

**1. 文本学习率（Edit Budget）**
- 每步最多做 L 条修改（默认 L=4）
- 可选调度器：constant（固定）/ linear（线性衰减）/ cosine（余弦衰减）
- 防止"大改"把已经有效的规则覆盖掉

**2. 被拒绝编辑缓冲（Rejected Buffer / Step Buffer）**
- 每步结束后，把失败模式和被拒绝的编辑记录下来
- 下一步反思时作为上下文传入："这些改法试过了没用，别再试了"
- 类似人类 debug 时记住"这个方法不行"

**3. 慢更新（Slow Update）+ 元技能（Meta Skill）**
- **慢更新**：每个 epoch 结束后，对比上一个 epoch 和当前 epoch 在同一批样本上的表现
  - 分类为：improved（进步）、regressed（退步）、persistent_fail（一直失败）、stable_success（一直成功）
  - 优化器分析这些纵向变化，写入技能文档的保护区（SLOW_UPDATE 区）
  - 保护区内的内容只有慢更新能修改，常规编辑碰不到
- **元技能**：优化器自己的"记忆"
  - 不改技能文档，而是记住"哪些编辑策略有效/无效"
  - 在后续步骤中作为上下文注入，提升优化器决策质量

#### 7.6 数据类型流转

整个流水线用一套统一的数据类贯穿：

```python
# 一条编辑操作
Edit(op="append|insert_after|replace|delete", content="...", target="...")

# 一组编辑 + 推理说明
Patch(edits=[Edit, ...], reasoning="为什么要做这些修改")

# 一个任务的执行结果
RolloutResult(id="task_001", hard=0, soft=0.3, n_turns=5, fail_reason="...")

# 分析师的原始输出
RawPatch(patch=Patch, source_type="failure|success", batch_size=8)

# 慢更新的结果
SlowUpdateResult(reasoning="...", slow_update_content="...", action="accept")

# 验证门的结果
GateResult(action="accept_new_best", current_skill="...", best_score=0.85)
```

#### 7.7 环境适配器模式

SkillOpt 用 `EnvAdapter` 抽象基类支持不同 benchmark，每个环境需要实现：

| 方法 | 作用 |
|------|------|
| `setup(cfg)` | 一次性初始化 |
| `build_train_env(batch_size, seed)` | 构建训练环境 |
| `build_eval_env(env_num, split, seed)` | 构建评估环境 |
| `rollout(env, skill, out_dir)` | 执行一批任务，返回结果列表 |
| `reflect(results, skill, out_dir)` | 分析轨迹，返回补丁列表 |
| `get_task_types()` | 返回任务类型列表 |

Prompt 有两级优先级：环境专属 prompt > 通用默认 prompt。

#### 7.8 SkillOpt-Sleep（部署后夜间学习）

Sleep 是论文代码之外的实用延伸，用于部署后的持续学习。流程：

```
harvest（收割会话记录）→ mine（挖掘重复任务）→ replay（离线重放）
→ consolidate（反思+编辑+验证门）→ stage（暂存提案）→ adopt（用户确认后采纳）
```

与训练循环的区别：
- 数据源不是 benchmark 而是用户的真实使用记录
- 同时优化技能（skill.md）和记忆（CLAUDE.md）
- 有人工确认环节（staging → adopt），不是全自动
- 已为 Claude Code、Codex、Copilot 三个 Agent 写了插件

#### 7.9 训练产出示例

看 `ckpt/alfworld/gpt5.5_skill.md`，这是一份经过训练的 ALFWorld 技能文档：
- 开头是 Overview + Task Types 表格（任务分类和关键步骤）
- 中间是 General Principles（通用原则，如"分解任务""系统探索""立即抓取"）
- 然后是 Common Mistakes to Avoid（常见错误规避）
- 再往后是越来越细化的搜索循环恢复策略
- 末尾的 `<!-- SLOW_UPDATE_START -->` 区域是慢更新写入的纵向经验

可以看到：初始技能可能只有基本规则，经过训练后，文档会自动积累大量针对失败模式的细化规则，比如"搜索账本过滤器""目的地-来源锁定"等——这些都是从失败轨迹中自动学到的。

#### 7.10 对我的启发

1. **技能是可以自动优化的**：不需要人手动改 prompt/skill，只要有评估标准就能自动迭代
2. **"训练过程不训练模型"**：LLM 冻结不变，只优化给 LLM 看的指导文档
3. **验证门是安全阀**：每次修改都经过验证集测试，不合格就回退，保证技能只升不降
4. **两种学习速度**：快更新（每步）修具体问题，慢更新（每 epoch）做全局反思
5. **可迁移性**：优化好的 skill.md 可以直接给不同模型用，不需要重新训练
6. **与悟空/SkillAtlas 的关联**：悟空的技能体系理论上也可以用类似方法自动优化——用 eval run 结果驱动技能迭代
