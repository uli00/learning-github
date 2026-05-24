#!/usr/bin/env python3
"""
GitHub Star 飙升监控脚本

运行模式：
  python3 github-star-monitor.py collect-mature  → 采集成熟项目 Star 事件（每4小时，Events API）
  python3 github-star-monitor.py collect-new      → 采集新创建项目（每天一次，Search API）
  python3 github-star-monitor.py report           → 合并两类数据生成报告
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from collections import Counter

# --- 配置 ---

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

EXCLUDE_KEYWORDS = [
    "crack", "hack", "cheat", "mod-menu",
    "keygen", "pirate", "torrent",
]

MIN_TOTAL_STARS = 50       # 成熟项目最低 Star
NEW_PROJECT_MAX_STARS = 50 # 新项目最高 Star
NEW_PROJECT_REPORT_THRESHOLD = 30  # 7天增长上报阈值
NEW_PROJECT_TRACK_DAYS = 7
MAX_EVENT_PAGES = 5
MAX_REPOS = 20

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


def get_repo_readme(repo_name):
    """获取项目的 README 内容（用于深度分析）"""
    url = f"https://api.github.com/repos/{repo_name}/readme"
    data = github_api_request(url)
    if data and "content" in data:
        import base64
        content = data["content"].replace("\n", "")
        try:
            return base64.b64decode(content).decode("utf-8", errors="ignore")
        except:
            pass
    return ""


def analyze_project(readme_text):
    """从 README 文本中提炼项目关键信息"""
    if not readme_text:
        return {
            "one_liner": "暂无详细信息",
            "key_features": [],
            "tech_stack": "未知",
            "use_case": "需进一步评估",
        }
    
    # 提取前 2000 字符分析
    text = readme_text[:2000].lower()
    
    # 一句话简介（取第一段有意义的纯文字）
    lines = readme_text.split("\n")
    one_liner = ""
    for line in lines:
        line = line.strip().strip("#").strip()
        # 跳过图片标签、空行、HTML标签
        if not line or line.startswith("![") or line.startswith("<") or len(line) < 10:
            continue
        one_liner = line[:150]
        break
    
    if not one_liner:
        one_liner = "暂无详细描述"
    
    # 技术栈识别
    tech_keywords = {
        "Python": ["python", "pip", "requirements.txt"],
        "TypeScript/Node.js": ["typescript", "node", "npm", "tsconfig"],
        "Rust": ["rust", "cargo", "cargo.toml"],
        "Go": ["golang", "go.mod", "go.sum"],
        "Java": ["java", "maven", "gradle", "pom.xml"],
        "React": ["react", "jsx", "tsx"],
        "Vue": ["vue", "vite"],
        "Docker": ["docker", "dockerfile", "docker-compose"],
    }
    
    detected_tech = []
    for tech, keywords in tech_keywords.items():
        if any(kw in text for kw in keywords):
            detected_tech.append(tech)
    
    tech_stack = ", ".join(detected_tech) if detected_tech else "未知"
    
    # 关键特性提取（寻找 Features、特性、功能等段落）
    key_features = []
    in_features = False
    for line in lines[:100]:  # 只看前100行
        stripped = line.strip()
        if any(kw in stripped.lower() for kw in ["feature", "特性", "功能", "highlights", "capabilit"]):
            in_features = True
            continue
        if in_features and stripped.startswith("-") or stripped.startswith("*"):
            feature = stripped[1:].strip()
            if feature and len(feature) < 200:
                key_features.append(feature[:120])
            if len(key_features) >= 5:
                break
        elif in_features and (stripped.startswith("##") or stripped.startswith("#")):
            break
    
    # 适用场景判断
    use_case_keywords = {
        "AI Agent/智能体": ["agent", "autonomous", "自主", "智能体", "task planning"],
        "代码辅助": ["code", "programming", "coding", "refactor", "代码"],
        "数据分析": ["data analysis", "analytics", "dashboard", "可视化"],
        "自动化工作流": ["workflow", "automation", "自动化", "pipeline"],
        "对话/聊天机器人": ["chat", "chatbot", "对话", "conversation"],
        "MCP/工具调用": ["mcp", "tool use", "function calling", "tool calling"],
        "知识管理/RAG": ["rag", "knowledge", "retrieval", "knowledge base", "知识"],
        "技能/插件系统": ["skill", "plugin", "extension", "技能", "插件"],
    }
    
    matched_scenarios = []
    for scenario, keywords in use_case_keywords.items():
        if any(kw in text for kw in keywords):
            matched_scenarios.append(scenario)
    
    use_case = ", ".join(matched_scenarios) if matched_scenarios else "需进一步评估"
    
    return {
        "one_liner": one_liner,
        "key_features": key_features[:5],
        "tech_stack": tech_stack,
        "use_case": use_case,
    }


def _load_new_projects():
    filepath = get_new_projects_file()
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_new_projects(data):
    filepath = get_new_projects_file()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# === 模式1：采集成熟项目 Star 事件（Events API） ===

def collect_mature():
    """采集 Star 事件，追加到今日数据文件"""
    print(f"[成熟采集] 正在获取 Star 事件...")
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

    print(f"[成熟采集] 获取到 {len(all_events)} 条 Star 事件")

    counter = Counter()
    for event in all_events:
        repo_name = event.get("repo", {}).get("name", "")
        if repo_name:
            counter[repo_name] += 1

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

    print(f"[成熟采集] 数据已追加到 {today_file}")
    print(f"[成熟采集] 今日共 {len(existing)} 个仓库有 Star 增长")


# === 模式2：采集新创建项目（Search API） ===

def collect_new():
    """搜索过去 1 天新创建的 AI 项目，加入跟踪列表"""
    print(f"[新项目采集] 搜索新创建的 AI 项目...")
    ensure_data_dir()

    since = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    query = f"created:>{since} stars:<{NEW_PROJECT_MAX_STARS}"
    encoded_query = urllib.parse.quote(query)
    url = (
        f"https://api.github.com/search/repositories"
        f"?q={encoded_query}&sort=stars&order=desc&per_page=50"
    )

    data = github_api_request(url)
    if not data:
        print("[新项目采集] API 请求失败")
        return

    items = data.get("items", [])
    print(f"[新项目采集] 找到 {len(items)} 个新创建的仓库")

    new_projects = _load_new_projects()
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    found = 0

    for repo in items:
        repo_name = repo.get("full_name", "")
        total_stars = repo.get("stargazers_count", 0)

        if repo_name in new_projects:
            continue

        if total_stars < NEW_PROJECT_MAX_STARS and is_ai_related(repo):
            new_projects[repo_name] = {
                "full_name": repo_name,
                "description": repo.get("description", ""),
                "html_url": repo.get("html_url", ""),
                "first_seen": today_str,
                "initial_stars": total_stars,
                "language": repo.get("language", ""),
                "topics": repo.get("topics", []),
                "daily": {today_str: total_stars},
                "last_updated": now,
                "reported": False,
            }
            found += 1
            print(f"  🆕 {repo_name} (Star={total_stars})")

    # 清理过期
    cutoff = (datetime.now(timezone.utc) - timedelta(days=NEW_PROJECT_TRACK_DAYS)).strftime("%Y-%m-%d")
    expired = []
    for repo_name, info in new_projects.items():
        if info["first_seen"] < cutoff:
            total_growth = sum(info["daily"].values())
            if total_growth >= NEW_PROJECT_REPORT_THRESHOLD and not info["reported"]:
                info["reported"] = True
                print(f"  📢 达到上报阈值: {repo_name}")
            expired.append(repo_name)

    for repo in expired:
        del new_projects[repo]

    _save_new_projects(new_projects)
    print(f"[新项目采集] 新发现 {found} 个，当前跟踪中: {len(new_projects)} 个")


# === 模式3：生成报告 ===

def generate_report():
    """合并成熟项目和新项目数据，生成完整报告"""
    today_file = get_today_file()

    # 读取成熟项目数据
    repo_counts = {}
    if os.path.exists(today_file):
        with open(today_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    record = json.loads(line)
                    repo_counts[record["repo"]] = record["count"]

    print(f"[报告] 今日 {len(repo_counts)} 个仓库有 Star 增长")
    print("[报告] 筛选成熟 AI 项目...")

    sorted_repos = sorted(repo_counts.items(), key=lambda x: x[1], reverse=True)
    mature_repos = []

    for repo_name, count in sorted_repos:
        if count < 2:
            continue

        repo_info = get_repo_info(repo_name)
        if not repo_info:
            continue

        total_stars = repo_info.get("stargazers_count", 0)
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

    # 读取新项目数据
    new_projects = _load_new_projects()
    alert_projects = []
    tracking_projects = []

    for repo_name, info in new_projects.items():
        total_growth = sum(info["daily"].values())
        proj = {
            "name": repo_name,
            "description": info.get("description", ""),
            "url": info.get("html_url", ""),
            "initial_stars": info.get("initial_stars", 0),
            "growth": total_growth,
            "daily": info["daily"],
            "first_seen": info.get("first_seen", ""),
            "language": info.get("language", ""),
            "topics": info.get("topics", []),
        }
        if total_growth >= NEW_PROJECT_REPORT_THRESHOLD or info.get("reported"):
            alert_projects.append(proj)
        else:
            tracking_projects.append(proj)

    # 生成 Markdown
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    last_update = "未知"
    if os.path.exists(today_file):
        with open(today_file, "r", encoding="utf-8") as f:
            times = []
            for line in f:
                line = line.strip()
                if line:
                    times.append(json.loads(line).get("updated", ""))
            if times:
                last_update = max(times)

    md = []
    md.append("# GitHub AI 项目每日 Star 增长监控报告")
    md.append(f"\n> 生成时间：{now}")
    md.append(f"> 数据采集截至：{last_update}\n")
    md.append("---\n")

    # 成熟项目
    md.append("## 一、成熟 AI 项目（Star 增长排行）\n")
    if mature_repos:
        md.append(f"共 **{len(mature_repos)}** 个项目\n")
        for i, item in enumerate(mature_repos, 1):
            name = item["full_name"]
            url = item["html_url"]
            desc = item.get("description") or "暂无描述"
            today_stars = item["today_stars"]
            total_stars = item["total_stars"]
            forks = item["forks_count"]
            lang = item.get("language") or "未标注"
            topics = item.get("topics", [])

            is_new = False
            days_old = 999
            try:
                cd = datetime.strptime(item["created_at"][:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                days_old = (datetime.now(timezone.utc) - cd).days
                is_new = days_old <= 30
            except:
                pass

            new_tag = " 🆕" if is_new else ""
            
            # 抓取 README 做深度分析
            print(f"  正在分析 {name}...")
            readme = get_repo_readme(name)
            analysis = analyze_project(readme)
            
            md.append(f"### {i}. [{name}]({url}){new_tag}")
            if is_new:
                md.append(f"> **新项目！** 创建 {days_old} 天")
            md.append("")
            md.append(f"**一句话简介：** {analysis['one_liner']}")
            md.append("")
            md.append(f"**适用场景：** {analysis['use_case']}")
            md.append("")
            md.append(f"**技术栈：** {analysis['tech_stack']}")
            md.append("")
            
            if analysis["key_features"]:
                md.append("**核心功能：**")
                for feat in analysis["key_features"]:
                    md.append(f"- {feat}")
                md.append("")
            
            # 搬迁建议
            if analysis["use_case"] != "需进一步评估":
                md.append(f"**💡 可借鉴方向：** {analysis['use_case']}")
                md.append("")
            
            md.append(f"| 指标 | 值 |")
            md.append(f"|------|-----|")
            md.append(f"| 今日 Star | +{today_stars} |")
            md.append(f"| 总 Star | {total_stars:,} |")
            md.append(f"| Fork | {forks} |")
            md.append(f"| 语言 | {lang} |")
            if topics:
                md.append(f"| 标签 | {', '.join(topics[:5])} |")
            md.append("")
    else:
        md.append("今日无符合条件的成熟 AI 项目。\n")

    # 新项目
    md.append("---\n")
    md.append("## 二、新潜力项目跟踪（总 Star < 50，持续观察 7 天）\n")

    if alert_projects or tracking_projects:
        if alert_projects:
            md.append(f"### ⚠️ 达到上报阈值（7天增长 > {NEW_PROJECT_REPORT_THRESHOLD} Star）\n")
            for proj in alert_projects:
                md.append(f"**[{proj['name']}]({proj['url']})**")
                # 深度分析
                readme = get_repo_readme(proj["name"])
                analysis = analyze_project(readme)
                md.append(f"> **简介：** {analysis['one_liner']}")
                md.append(f"> **适用场景：** {analysis['use_case']} | **技术栈：** {analysis['tech_stack']}")
                md.append(f"- 初始 Star: {proj['initial_stars']} | 跟踪期增长: +{proj['growth']}")
                daily_str = " | ".join([f"{d}: +{c}" for d, c in sorted(proj["daily"].items())])
                md.append(f"- 每日增长: {daily_str}")
                if analysis["use_case"] != "需进一步评估":
                    md.append(f"- **💡 可借鉴方向：** {analysis['use_case']}")
                md.append("")

        if tracking_projects:
            md.append("### 正在跟踪中（未达阈值）\n")
            md.append("| 项目 | 初始Star | 跟踪期增长 | 发现日期 |")
            md.append("|------|---------|-----------|---------|")
            for proj in tracking_projects:
                md.append(f"| [{proj['name']}]({proj['url']}) | {proj['initial_stars']} | +{proj['growth']} | {proj['first_seen']} |")
            md.append("")
            md.append(f"> 阈值：7 天内增长超过 {NEW_PROJECT_REPORT_THRESHOLD} Star 时自动上报")
    else:
        md.append("暂无跟踪中的新项目。\n")

    md.append("\n---\n")
    md.append("*本报告由 GitHub API 自动生成*\n")
    md.append("*成熟项目数据：每 4 小时采集 Star 事件*\n")
    md.append("*新项目数据：每日扫描新创建仓库*\n")
    md.append("*🆕 标记表示 30 天内创建的新项目*")

    report_text = "\n".join(md)

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
        print("  python3 github-star-monitor.py collect-mature  → 采集成熟项目 Star 事件（每4小时）")
        print("  python3 github-star-monitor.py collect-new      → 采集新创建项目（每天一次）")
        print("  python3 github-star-monitor.py report           → 合并生成报告")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "collect-mature":
        collect_mature()
    elif mode == "collect-new":
        collect_new()
    elif mode == "report":
        generate_report()
    else:
        print(f"未知模式: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
