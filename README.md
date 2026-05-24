# 我的github学习仓库

这是我学习 GitHub 的练习项目，从零开始。

## 学习记录

- [x] 学会了创建第一个仓库
- [x] 学会上传文件
- [x] 学会 GitHub API
- [ ] 学会用 Git 命令行


## 学习笔记1

今天开始学习 GitHub，了解了以下概念：
- Repository = 项目文件夹
- Star = 点赞收藏
- Fork = 复制项目
- README = 项目说明

## 学习笔记2

GitHub 提供了官方 API，可以用程序方式获取数据，不用手动打开网页。

**官方文档地址：** https://docs.github.com/en/rest

**最简单的例子 — 获取一个仓库的信息：**

### 输入命令

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

### 输出结果

仓库名称: uli00/learning-github
描述: 从零开始学习github使用直到成为大神（嘿嘿嘿～）
Star 数量: 0
Fork 数量: 0
创建时间: 2026-05-24T03:10:56Z
最后更新: 2026-05-24T03:20:35Z

### 这个命令做了什么：

1、curl -s "..." — 用程序访问 GitHub API，拿到原始 JSON 数据
2、| python3 -c "..." — 把 JSON 数据解析成字典，打印出你关心的字段

接口	用途
GET /repos/{owner}/{repo}	获取某个仓库的详细信息
GET /search/repositories	搜索仓库（按 Star、语言、时间等筛选）
GET /repos/{owner}/{repo}/stargazers	获取点了 Star 的用户列表

