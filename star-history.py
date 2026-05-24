#!/usr/bin/env python3
"""
Star 历史记录工具
记录指定项目列表的每日 Star 数量，生成增长曲线数据
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "star-data")
HISTORY_FILE = os.path.join(DATA_DIR, "star-history.json")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def github_api_request(url):
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"API 请求失败: {url}\n错误: {e}")
        return None


def get_star_count(repo_name):
    """获取项目的当前 Star 数"""
    data = github_api_request(f"https://api.github.com/repos/{repo_name}")
    if data:
        return data.get("stargazers_count", 0)
    return None


def record_today(watch_list):
    """记录今日 Star 数据"""
    ensure_data_dir()
    history = load_history()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    print(f"[记录] 今日: {today}")
    print(f"[记录] 共跟踪 {len(watch_list)} 个项目\n")
    
    new_records = 0
    for repo in watch_list:
        stars = get_star_count(repo)
        if stars is None:
            print(f"  ✗ {repo} - 获取失败")
            continue
        
        if repo not in history:
            history[repo] = {"name": repo, "records": {}}
        
        history[repo]["records"][today] = stars
        new_records += 1
        print(f"  ✓ {repo} - {stars:,} Star")
    
    save_history(history)
    print(f"\n[记录] 完成！更新了 {new_records} 个项目的数据")
    print(f"[记录] 数据文件: {HISTORY_FILE}")


def add_project(repo_name, watch_list=None):
    """添加新项目到关注列表"""
    wl_file = os.path.join(DATA_DIR, "watch-list.json")
    if watch_list is None:
        if os.path.exists(wl_file):
            with open(wl_file, "r", encoding="utf-8") as f:
                watch_list = json.load(f)
        else:
            watch_list = []
    
    if repo_name in watch_list:
        print(f"{repo_name} 已在关注列表中")
        return watch_list
    
    # 验证项目是否存在
    stars = get_star_count(repo_name)
    if stars is None:
        print(f"✗ 项目 {repo_name} 不存在或无法访问")
        return watch_list
    
    watch_list.append(repo_name)
    with open(wl_file, "w", encoding="utf-8") as f:
        json.dump(watch_list, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 已添加 {repo_name} (当前 Star: {stars:,})")
    return watch_list


def list_projects():
    """列出所有关注的项目"""
    wl_file = os.path.join(DATA_DIR, "watch-list.json")
    if not os.path.exists(wl_file):
        print("暂无关注的项目")
        return
    
    with open(wl_file, "r", encoding="utf-8") as f:
        watch_list = json.load(f)
    
    history = load_history()
    print(f"当前关注 {len(watch_list)} 个项目:\n")
    
    for repo in watch_list:
        stars = get_star_count(repo)
        recorded = history.get(repo, {}).get("records", {})
        first_record = min(recorded.keys()) if recorded else "未开始记录"
        last_stars = recorded[max(recorded.keys())] if recorded else "-"
        
        print(f"  {repo}")
        print(f"    当前: {stars:,} | 首次记录: {first_record} | 上次记录: {last_stars}")


def generate_chart():
    """从历史数据生成 Star 增长曲线/赛跑图"""
    history = load_history()
    if not history:
        print("暂无历史数据，先用 record 命令记录几天")
        return
    
    wl_file = os.path.join(DATA_DIR, "watch-list.json")
    if not os.path.exists(wl_file):
        print("暂无关注的项目")
        return
    
    with open(wl_file, "r", encoding="utf-8") as f:
        watch_list = json.load(f)
    
    # 收集所有日期
    all_dates = set()
    for repo in watch_list:
        if repo in history:
            all_dates.update(history[repo].get("records", {}).keys())
    
    all_dates = sorted(all_dates)
    if not all_dates:
        print("暂无记录数据，先用 record 命令记录")
        return
    
    print(f"[数据] {len(all_dates)} 个日期: {all_dates[0]} ~ {all_dates[-1]}")
    print(f"[数据] {len(watch_list)} 个项目\n")
    
    # 转换为 bar-race-viz 格式的 JSON
    # 按最新日期的 Star 数排序，取前 10
    latest_date = all_dates[-1]
    repo_latest = []
    for repo in watch_list:
        records = history.get(repo, {}).get("records", {})
        if latest_date in records:
            repo_latest.append((repo, records[latest_date]))
    
    repo_latest.sort(key=lambda x: x[1], reverse=True)
    top_repos = repo_latest[:10]
    
    # 构建 JSON
    viz_data = {
        "meta": {
            "title": "GitHub AI 项目 Star 增长排行",
            "subtitle": f"{all_dates[0]} 至 {all_dates[-1]}",
            "unit": "Star",
            "source": "GitHub API",
            "note": "数据每日自动采集"
        },
        "platforms": []
    }
    
    icons = ["🚀", "⭐", "🔥", "💡", "🤖", "🧠", "⚡", "🎯", "🌟", "🔮"]
    for i, (repo, _) in enumerate(top_repos):
        records = history[repo].get("records", {})
        # 转为字符串 key
        str_records = {str(k): v for k, v in records.items()}
        
        viz_data["platforms"].append({
            "id": repo.replace("/", "-"),
            "name": repo,
            "icon": icons[i % len(icons)],
            "data": str_records
        })
    
    # 保存 JSON
    viz_json_file = os.path.join(DATA_DIR, "star-race-data.json")
    with open(viz_json_file, "w", encoding="utf-8") as f:
        json.dump(viz_data, f, indent=2, ensure_ascii=False)
    
    print(f"[数据] 已保存可视化数据: {viz_json_file}")
    
    # 调用 bar-race-viz 生成脚本
    skill_dir = os.path.expanduser("~/.qoderwork/skills/bar-race-viz/scripts")
    generate_script = os.path.join(skill_dir, "generate_viz.py")
    output_html = os.path.join(DATA_DIR, "star-race-viz.html")
    
    if not os.path.exists(generate_script):
        print(f"\n⚠ 未找到 bar-race-viz 生成脚本: {generate_script}")
        print("  请先安装 bar-race-viz skill")
        return
    
    import subprocess
    cmd = ["python3", generate_script, viz_json_file, output_html, "--type", "line"]
    print(f"\n[生成] 正在创建折线赛跑图...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ 折线赛跑图已生成: {output_html}")
        print(f"   打开查看: open {output_html}")
    else:
        print(f"❌ 生成失败:")
        print(result.stderr)
        print(result.stdout)


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 star-history.py record          → 记录今日 Star 数据")
        print("  python3 star-history.py add <repo>       → 添加项目到关注列表")
        print("  python3 star-history.py list             → 列出所有关注的项目")
        print("  python3 star-history.py generate-chart   → 生成 Star 增长曲线图")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == "record":
        wl_file = os.path.join(DATA_DIR, "watch-list.json")
        if not os.path.exists(wl_file):
            print("暂无关注的项目，先用 add 命令添加项目")
            sys.exit(1)
        with open(wl_file, "r", encoding="utf-8") as f:
            watch_list = json.load(f)
        record_today(watch_list)
    
    elif mode == "add":
        if len(sys.argv) < 3:
            print("请提供项目名称，如: python3 star-history.py add uli00/learning-github")
            sys.exit(1)
        add_project(sys.argv[2])
    
    elif mode == "list":
        list_projects()
    
    elif mode == "generate-chart":
        print("生成 Star 增长曲线图...")
        generate_chart()
    
    else:
        print(f"未知模式: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
