# 我的github学习仓库

这是我学习 GitHub 的练习项目，从零开始。

## 学习记录

- [x] 学会了创建第一个仓库
- [x] 学会在网页上编辑和上传文件
- [x] 了解 GitHub API 的基本用法
- [ ] 学会 Git 命令行操作（clone / add / commit / push）
- [ ] 编写 Star 收集脚本

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

**官方文档地址：** [https://docs.github.com/en/rest]

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
print('最后更新:', data.get('updated_at'))"
```

**输出结果**

```仓库名称: uli00/learning-github
描述: 从零开始学习github使用直到成为大神（嘿嘿嘿～）
Star 数量: 0
Fork 数量: 0
创建时间: 2026-05-24T03:10:56Z
最后更新: 2026-05-24T03:20:35Z
```

**这个命令做了什么？**

- 1、```curl -s "..."``` — 用程序访问 GitHub API，拿到原始 JSON 数据
- 2、```| python3 -c "..."``` — 把 JSON 数据解析成字典，打印出你关心的字段

**通俗理解：** 就像你打开一个网页看仓库信息，只不过 API 让程序替你"看"，而且速度更快、可以批量处理。

**常用接口速查：**

| 接口 | 用途 |
|------|---------|
|```GET /repos/{owner}/{repo}```| 获取某个仓库的详细信息 |
|```GET /search/repositories``` | 搜索仓库（按 Star、语言、时间等筛选） |
|```GET /repos/{owner}/{repo}/stargazers``` | 获取点了 Star 的用户列表 |

