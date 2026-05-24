#!/usr/bin/env python3
"""
GitHub Star 飙升监控脚本
扫描 Star 增长最快的 AI/Agent 相关项目，输出 Markdown 报告

运行模式：
  python3 github-star-monitor.py collect   → 采集 Star 事件，追加到数据文件
  python3 github-star-monitor.py report    → 基于今日采集数据生成报告
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from collections import Counter

# --- 配置 ---

# AI 相关关键词
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

# 最低 Star 总数阈值（成熟项目）
MIN_TOTAL_STARS = 10

# 新项目阈值（总 Star 小于此数的项目会被纳入跟踪）
NEW_PROJECT_THRESHOLD = 100

# 新项目上报阈值（跟踪期间增长超过此数就上报告）
NEW_PROJECT_REPORT_THRESHOLD = 50

# 新项目跟踪天数
NEW_PROJECT_TRACK_DAYS = 7

# 最多抓取的事件页数
MAX_EVENT_PAGES = 5

# 最终报告的项目数量上限
MAX_REPOS = 20

# 数据目录
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "star-data")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def get_today_file():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return os.path.join(DATA_DIR, f"stars-{today}.jsonl")


def get_new_projects_file():
    return os.path.join(DATA_DIR, "new-projects.json")


def github_api_request(url):
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"API 请求失败: {url}\n错误: {e}")
        return None


def load_new_projects():
    """加载新项目跟踪列表"""
    filepath = get_new_projects_file()
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_new_projects(data):
    """保存新项目跟踪列表"""
    filepath = get_new_projects_file()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def collect_star_events():
    """采集 Star 事件，追加到今日数据文件 + 更新新项目跟踪"""
    print(f"[采集] 正在获取 Star 事件...")
    ensure_data_dir()
    
    all_events = []
    for page in range(1, MAX_EVENT_PAGES + 1):
        url = f"https://api.github.com/events?per_page=100&page={page}"
        data = github_api_request(url)
        if not data:
            break
        
        star_events = [e for e in data if e.get("type") == "WatchEvent"]
        all_events.extend(star_events)
        
        if len(data) < 100:
            break
    
    print(f"[采集] 获取到 {len(all_events)} 条 Star 事件")
    
    # 统计本轮 repo 计数
    counter = Counter()
    for event in all_events:
        repo_name = event.get("repo", {}).get("name", "")
        if repo_name:
            counter[repo_name] += 1
    
    # 追加到今日数据文件
    today_file = get_today_file()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    existing = {}
    if os.path.exists(today_file):
        with open(today_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    record = json.loads(line)
                    existing[record["repo"]] = record["count"]
    
    for repo, count in counter.items():
        if repo in existing:
            existing[repo] += count
        else:
            existing[repo] = count
    
    with open(today_file, "w", encoding="utf-8") as f:
        for repo, count in existing.items():
            f.write(json.dumps({"repo": repo, "count": count, "updated": now}) + "\n")
    
    print(f"[采集] 数据已追加到 {today_file}")
    print(f"[采集] 今日共 {len(existing)} 个仓库有 Star 增长")
    
    # --- 新项目跟踪 ---
    print("[采集] 检查新项目...")
    new_projects = load_new_projects()
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    for repo_name, count in counter.items():
        if repo_name in new_projects:
            # 已跟踪的项目，更新今日数据
            if today_str not in new_projects[repo_name]["daily"]:
                new_projects[repo_name]["daily"][today_str] = 0
            new_projects[repo_name]["daily"][today_str] += count
            new_projects[repo_name]["last_updated"] = now
            print(f"  已跟踪: {repo_name} (+{count})")
        else:
            # 未跟踪的项目，检查是否是新项目
            repo_info = get_repo_info(repo_name)
            if not repo_info:
                continue
            
            total_stars = repo_info.get("stargazers_count", 0)
            if total_stars < NEW_PROJECT_THRESHOLD and is_ai_related(repo_info):
                new_projects[repo_name] = {
                    "full_name": repo_name,
                    "description": repo_info.get("description", ""),
                    "html_url": repo_info.get("html_url", ""),
                    "first_seen": today_str,
                    "initial_stars": total_stars,
                    "language": repo_info.get("language", ""),
                    "topics": repo_info.get("topics", []),
                    "daily": {today_str: count},
                    "last_updated": now,
                    "reported": False,
                }
                print(f"  🆕 发现新项目: {repo_name} (总Star={total_stars})")
    
    # 清理过期项目（超过跟踪天数的移除）
    cutoff_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=NEW_PROJECT_TRACK_DAYS)).strftime("%Y-%m-%d")
    
    expired = []
    for repo_name, info in new_projects.items():
        if info["first_seen"] < cutoff:
            # 检查是否达到上报阈值
            total_growth = sum(info["daily"].values())
            if total_growth >= NEW_PROJECT_REPORT_THRESHOLD and not info["reported"]:
                info["reported"] = True
                print(f"  📢 达到上报阈值: {repo_name} (7天增长 {total_growth} Star)")
            expired.append(repo_name)
    
    for repo in expired:
        del new_projects[repo]
    
    save_new_projects(new_projects)
    print(f"[采集] 当前跟踪中的新项目: {len(new_projects)} 个")


def is_ai_related(repo_info):
    if not repo_info:
        return False
    
    name = (repo_info.get("name") or "").lower()
    desc = (repo_info.get("description") or "").lower()
    topics = [t.lower() for t in repo_info.get("topics", [])]
    all_text = f"{name} {desc} {' '.join(topics)}"
    
    for kw in EXCLUDE_KEYWORDS:
        if kw in all_text:
            return False
    
    for kw in AI_KEYWORDS:
        if kw in all_text:
            return True
    
    return False


def get_repo_info(repo_name):
    url = f"https://api.github.com/repos/{repo_name}"
    return github_api_request(url)


def generate_report():
    """生成报告：成熟项目 + 新项目跟踪"""
    today_file = get_today_file()
    
    if not os.path.exists(today_file):
        print(f"[报告] 今日数据文件不存在: {today_file}")
        print("[报告] 请先运行 collect 模式采集数据")
        return
    
    # 读取今日数据
    repo_counts = {}
    with open(today_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                record = json.loads(line)
                repo_counts[record["repo"]] = record["count"]
    
    print(f"[报告] 今日共 {len(repo_counts)} 个仓库有 Star 增长")
    
    # --- 筛选成熟 AI 项目 ---
    print("[报告] 开始筛选成熟 AI 项目...")
    sorted_repos = sorted(repo_counts.items(), key=lambda x: x[1], reverse=True)
    
    mature_repos = []
    for repo_name, count in sorted_repos:
        if count < 2:
            continue
        
        repo_info = get_repo_info(repo_name)
        if not repo_info:
            continue
        
        total_stars = repo_info.get("stargazers_count", 0)
        if total_stars < MIN_TOTAL_STARS or total_stars >= NEW_PROJECT_THRESHOLD:
            pass  # 成熟项目
        else:
            continue  # 新项目在新项目跟踪里处理
        
        if total_stars < MIN_TOTAL_STARS:
            continue
        
        if is_ai_related(repo_info):
            mature_repos.append({
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
            print(f"  ✓ {repo_name} (+{count})")
        
        if len(mature_repos) >= MAX_REPOS:
            break
    
    print(f"[报告] 筛选出 {len(mature_repos)} 个成熟 AI 项目")
    
    # --- 新项目跟踪报告 ---
    new_projects = load_new_projects()
    alert_projects = []
    tracking_projects = []
    
    for repo_name, info in new_projects.items():
        total_growth = sum(info["daily"].values())
        days_tracking = info.get("first_seen", "")
        
        proj = {
            "name": repo_name,
            "description": info.get("description", ""),
            "url": info.get("html_url", ""),
            "initial_stars": info.get("initial_stars", 0),
            "growth": total_growth,
            "daily": info["daily"],
            "first_seen": days_tracking,
        }
        
        if total_growth >= NEW_PROJECT_REPORT_THRESHOLD or info.get("reported"):
            alert_projects.append(proj)
        else:
            tracking_projects.append(proj)
    
    # --- 生成 Markdown ---
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    collect_times = []
    with open(today_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                record = json.loads(line)
                collect_times.append(record.get("updated", ""))
    last_update = max(collect_times) if collect_times else "未知"
    
    md = []
    md.append("# GitHub AI 项目每日 Star 增长监控报告")
    md.append(f"\n> 生成时间：{now}")
    md.append(f"> 数据采集截至：{last_update}\n")
    md.append("---\n")
    
    # === 第一部分：成熟项目 ===
    md.append("## 一、成熟 AI 项目（Star 增长排行）\n")
    
    if mature_repos:
        md.append(f"共 **{len(mature_repos)}** 个项目\n")
        md.append("| 排名 | 项目 | 今日 +Star | 总 Star | 语言 |")
        md.append("|------|------|-----------|---------|------|")
        for i, item in enumerate(mature_repos, 1):
            name = item["full_name"]
            url = item["html_url"]
            today_stars = item["today_stars"]
            total_stars = item["total_stars"]
            lang = item.get("language") or "未标注"
            md.append(f"| {i} | [{name}]({url}) | +{today_stars} | {total_stars:,} | {lang} |")
        md.append("")
        
        # 详细卡片
        md.append("### 详细项目信息\n")
        for i, item in enumerate(mature_repos, 1):
            name = item["full_name"]
            desc = item.get("description") or "暂无描述"
            url = item["html_url"]
            
            # 判断是否是新项目
            is_new = False
            try:
                created_date = datetime.strptime(item["created_at"][:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                is_new = (datetime.now(timezone.utc) - created_date).days <= 30
            except:
                pass
            
            new_tag = " 🆕" if is_new else ""
            md.append(f"**{i}. [{name}]({url})**{new_tag}")
            if is_new:
                created_date = datetime.strptime(item["created_at"][:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                days_old = (datetime.now(timezone.utc) - created_date).days
                md.append(f"> **新项目！** 创建 {days_old} 天")
            md.append(f"\n> {desc}\n")
            md.append(f"| 指标 | 值 |")
            md.append(f"|------|-----|")
            md.append(f"| 今日 Star | +{item['today_stars']} |")
            md.append(f"| 总 Star | {item['total_stars']:,} |")
            md.append(f"| Fork | {item['forks_count']} |")
            if item.get("topics"):
                md.append(f"| 标签 | {', '.join(item['topics'][:5])} |")
            md.append("")
    else:
        md.append("今日无符合条件的成熟 AI 项目。\n")
    
    # === 第二部分：新潜力项目 ===
    md.append("---\n")
    md.append("## 二、新潜力项目跟踪（总 Star < 100，持续观察 7 天）\n")
    
    if alert_projects or tracking_projects:
        # 达到阈值的项目
        if alert_projects:
            md.append(f"### ⚠️ 达到上报阈值的项目（7天增长 > {NEW_PROJECT_REPORT_THRESHOLD} Star）\n")
            for proj in alert_projects:
                md.append(f"**[{proj['name']}]({proj['url']})**")
                md.append(f"> {proj.get('description', '暂无描述')}")
                md.append(f"- 初始 Star: {proj['initial_stars']} | 跟踪期增长: +{proj['growth']}")
                daily_str = " | ".join([f"{d}: +{c}" for d, c in sorted(proj["daily"].items())])
                md.append(f"- 每日增长: {daily_str}")
                md.append("")
        
        # 正在跟踪中的项目
        if tracking_projects:
            md.append(f"### 正在跟踪中的项目（尚未达到阈值）\n")
            md.append("| 项目 | 初始Star | 跟踪期增长 | 发现日期 |")
            md.append("|------|---------|-----------|---------|")
            for proj in tracking_projects:
                md.append(f"| [{proj['name']}]({proj['url']}) | {proj['initial_stars']} | +{proj['growth']} | {proj['first_seen']} |")
            md.append("")
            md.append(f"> 阈值规则：7 天内增长超过 {NEW_PROJECT_REPORT_THRESHOLD} Star 时自动上报")
    else:
        md.append("暂无跟踪中的新项目。\n")
    
    md.append("\n---\n")
    md.append("*本报告由 GitHub API 自动生成，每 4 小时采集一次数据，每日生成报告*\n")
    md.append("*🆕 标记表示 30 天内创建的新项目*")
    
    report_text = "\n".join(md)
    
    # 输出到文件
    filename = f"github-ai-daily-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print(f"\n[报告] 报告已保存: {filepath}")
    print("\n" + "=" * 50)
    print(report_text)
    
    return report_text


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 github-star-monitor.py collect   → 采集 Star 事件 + 跟踪新项目")
        print("  python3 github-star-monitor.py report    → 生成今日报告")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == "collect":
        collect_star_events()
    elif mode == "report":
        generate_report()
    else:
        print(f"未知模式: {mode}")
        print("请用 collect 或 report")
        sys.exit(1)


if __name__ == "__main__":
    main()
