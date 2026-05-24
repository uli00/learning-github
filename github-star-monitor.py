#!/usr/bin/env python3
"""
GitHub Star 飙升监控脚本
扫描过去 24 小时内 Star 增长最快的 AI/Agent 相关项目
输出 Markdown 格式报告

原理：通过 GitHub Events API 获取最近的 Star 事件，
      统计每个仓库被 Star 的次数，得出"今日 Star 增量"排名。
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from collections import Counter

# --- 配置 ---

# AI 相关关键词（用于筛选项目）
AI_KEYWORDS = [
    "agent", "llm", "gpt", "mcp", "rag",
    "langchain", "claude", "anthropic", "openai",
    "copilot", "autogpt", "babyagi", "crewai",
    "dspy", "smolagents", "agno", "aider",
    "智能体", "大模型", "agentgpt", "llama",
    "vllm", "ollama", "huggingface", "transformers",
    "embedding", "inference", "finetune", "fine-tune",
    "skill", "tool-use", "function-calling",
    "workflow", "automation", "multi-agent", "multiagent",
    "chatbot", "generative", "diffusion",
]

# 排除关键词
EXCLUDE_KEYWORDS = [
    "crack", "hack", "cheat", "mod-menu",
    "keygen", "pirate", "torrent",
]

# 最低 Star 总数阈值
MIN_TOTAL_STARS = 10

# 最多抓取的事件页数（每页 100 条事件）
MAX_EVENT_PAGES = 5

# 最终报告的项目数量上限
MAX_REPOS = 20


def github_api_request(url):
    """调用 GitHub API，返回 JSON 数据"""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"API 请求失败: {url}\n错误: {e}")
        return None


def get_star_events():
    """获取最近的 Star 事件列表"""
    print("正在获取 Star 事件...")
    all_events = []
    
    for page in range(1, MAX_EVENT_PAGES + 1):
        url = f"https://api.github.com/events?per_page=100&page={page}"
        data = github_api_request(url)
        if not data:
            break
        
        # 只保留 Star 事件
        star_events = [e for e in data if e.get("type") == "WatchEvent"]
        all_events.extend(star_events)
        
        # 如果返回不足 100 条，说明到底了
        if len(data) < 100:
            break
        
        print(f"  第 {page} 页: {len(star_events)} 条 Star 事件")
    
    print(f"共获取到 {len(all_events)} 条 Star 事件")
    return all_events


def count_stars_per_repo(events):
    """统计每个仓库的 Star 增量"""
    counter = Counter()
    for event in events:
        repo_name = event.get("repo", {}).get("name", "")
        if repo_name:
            counter[repo_name] += 1
    return counter


def get_repo_info(repo_name):
    """获取仓库的详细信息"""
    url = f"https://api.github.com/repos/{repo_name}"
    return github_api_request(url)


def is_ai_related(repo_info):
    """判断项目是否与 AI 相关"""
    if not repo_info:
        return False
    
    name = (repo_info.get("name") or "").lower()
    desc = (repo_info.get("description") or "").lower()
    topics = [t.lower() for t in repo_info.get("topics", [])]
    all_text = f"{name} {desc} {' '.join(topics)}"
    
    # 排除黑名单
    for kw in EXCLUDE_KEYWORDS:
        if kw in all_text:
            return False
    
    # 匹配 AI 关键词
    for kw in AI_KEYWORDS:
        if kw in all_text:
            return True
    
    return False


def generate_report(repo_list):
    """生成 Markdown 格式报告"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    md = []
    md.append("# GitHub AI 项目每日 Star 增长监控报告")
    md.append(f"\n> 生成时间：{now}\n")
    md.append("---\n")
    
    if not repo_list:
        md.append("过去 24 小时未发现 Star 增长的 AI 相关项目。\n")
        return "\n".join(md)
    
    md.append(f"## 概况")
    md.append(f"本次扫描发现 **{len(repo_list)}** 个 AI 相关项目在过去 24 小时有 Star 增长\n")
    
    md.append("## 项目列表（按今日 Star 增量排序）\n")
    
    for i, item in enumerate(repo_list, 1):
        name = item["full_name"]
        desc = item.get("description") or "暂无描述"
        today_stars = item["today_stars"]
        total_stars = item.get("total_stars", 0)
        forks = item.get("forks_count", 0)
        lang = item.get("language") or "未标注"
        topics = item.get("topics", [])
        url = item.get("html_url", "")
        created = item.get("created_at", "")[:10]
        
        # 判断是否是新项目（30 天内创建）
        is_new = False
        try:
            created_date = datetime.strptime(created, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            is_new = (datetime.now(timezone.utc) - created_date).days <= 30
        except:
            pass
        
        new_tag = " 🆕" if is_new else ""
        
        md.append(f"### {i}. [{name}]({url}){new_tag}")
        if is_new:
            md.append(f"> **新项目！** 创建仅 {(datetime.now(timezone.utc) - created_date).days} 天")
        md.append(f"\n> {desc}\n")
        md.append(f"| 指标 | 值 |")
        md.append(f"|------|-----|")
        md.append(f"| 今日 Star | +{today_stars} |")
        md.append(f"| 总 Star | {total_stars:,} |")
        md.append(f"| Fork | {forks} |")
        md.append(f"| 语言 | {lang} |")
        if topics:
            md.append(f"| 标签 | {', '.join(topics[:5])} |")
        md.append("")
    
    md.append("---\n")
    md.append("*本报告由 GitHub API 自动生成，每日更新*\n")
    md.append("*🆕 标记表示 30 天内创建的新项目*")
    
    return "\n".join(md)


def main():
    print("=" * 50)
    print("GitHub AI 项目每日 Star 增长监控")
    print("=" * 50)
    
    # 1. 获取 Star 事件
    events = get_star_events()
    if not events:
        print("未获取到任何 Star 事件，退出。")
        return
    
    # 2. 统计每个仓库的 Star 增量
    star_counts = count_stars_per_repo(events)
    print(f"\n共 {len(star_counts)} 个仓库有 Star 增长")
    
    # 3. 获取热门仓库详情并筛选 AI 相关
    print("\n开始筛选 AI 相关项目...")
    ai_repos = []
    
    # 按今日 Star 增量降序排列
    for repo_name, count in star_counts.most_common():
        if count < 2:  # 至少 2 个 Star 才算有增长
            continue
        
        print(f"  检查: {repo_name} (+{count})")
        repo_info = get_repo_info(repo_name)
        
        if not repo_info:
            continue
        
        total_stars = repo_info.get("stargazers_count", 0)
        if total_stars < MIN_TOTAL_STARS:
            continue
        
        if is_ai_related(repo_info):
            ai_repos.append({
                "full_name": repo_name,
                "today_stars": count,
                "total_stars": total_stars,
                "forks_count": repo_info.get("forks_count", 0),
                "language": repo_info.get("language"),
                "topics": repo_info.get("topics", []),
                "html_url": repo_info.get("html_url", ""),
                "description": repo_info.get("description"),
                "created_at": repo_info.get("created_at", ""),
            })
            print(f"    ✓ AI 相关，加入报告")
        
        if len(ai_repos) >= MAX_REPOS:
            break
    
    print(f"\n筛选出 {len(ai_repos)} 个 AI 相关项目")
    
    # 4. 生成报告
    report = generate_report(ai_repos)
    
    # 5. 输出到文件
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"github-ai-daily-{today}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n报告已保存: {filename}")
    print("\n" + "=" * 50)
    print(report)


if __name__ == "__main__":
    main()
