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

**5. 推送到 GitHub**

```bash
git push
```

**push 认证问题：** GitHub 已经不支持密码推送。最简单的解决方案：

```bash
brew install gh
gh auth login
```

选择 GitHub.com → HTTPS → Login with a web browser，在浏览器里授权后，以后 `git push` 就不用输密码了。

**日常使用总结：**

| 命令 | 作用 |
|------|------|
| `git clone <url>` | 从 GitHub 下载仓库到本地 |
| `git status` | 查看当前状态 |
| `git add <文件>` | 把文件加入暂存区 |
| `git commit -m "说明"` | 提交更改，附带说明文字 |
| `git push` | 推送到 GitHub 上 |
