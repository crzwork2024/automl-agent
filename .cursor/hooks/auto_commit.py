"""
Hook: auto_commit.py
触发时机: check_metrics.py 之后执行
作用: 将本轮所有改动自动 git add + commit
     如果 git 没有初始化或没有改动，静默跳过
"""
import subprocess
import json
import sys
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

try:
    # 检查是否是 git 仓库
    check = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True
    )
    if check.returncode != 0:
        print(json.dumps({}))
        sys.exit(0)

    # 检查是否有改动
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    )
    if not status.stdout.strip():
        # 没有改动，跳过
        print(json.dumps({}))
        sys.exit(0)

    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"AI: improve model [{timestamp}]"],
        check=True
    )
    subprocess.run(["git", "push"], check=True)
    print(json.dumps({}))

except Exception as e:
    # commit 失败不阻断流程，静默处理
    print(f"auto_commit warning: {e}", file=sys.stderr)
    print(json.dumps({}))
