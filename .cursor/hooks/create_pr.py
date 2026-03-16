"""
Hook: create_pr.py
触发时机: auto_commit.py 之后执行
作用: 当 scratchpad.md 中标记 DONE 时，自动用 GitHub CLI 创建 PR
     需要提前执行: gh auth login
"""
import subprocess
import json
import sys
import os

SCRATCHPAD = ".cursor/scratchpad.md"


def is_task_done():
    """检查 scratchpad.md 中是否标记了 DONE"""
    if not os.path.exists(SCRATCHPAD):
        return False
    with open(SCRATCHPAD, "r", encoding="utf-8") as f:
        content = f.read()
    return "DONE" in content


def gh_available():
    """检查 gh CLI 是否已安装"""
    result = subprocess.run(
        ["gh", "--version"],
        capture_output=True, text=True
    )
    return result.returncode == 0


if not is_task_done():
    # 任务尚未完成，跳过 PR 创建
    print(json.dumps({}))
    sys.exit(0)

if not gh_available():
    print(json.dumps({
        "followup_message": (
            "GitHub CLI (gh) is not installed or not in PATH. "
            "Install it with: brew install gh (macOS) or https://cli.github.com/\n"
            "Then run: gh auth login"
        )
    }))
    sys.exit(0)

try:
    result = subprocess.run(
        [
            "gh", "pr", "create",
            "--title", "AutoML: model accuracy improved by AI agent",
            "--body", (
                "## Summary\n"
                "This PR was automatically created by the AutoML Agent.\n\n"
                "## Changes\n"
                "- Model type / hyperparameters tuned automatically\n"
                "- Accuracy target (>= 0.9) achieved\n\n"
                "## How to review\n"
                "1. Check `src/model.py` for model changes\n"
                "2. Run `python src/evaluate.py` to verify accuracy\n"
            ),
            "--head", "HEAD"
        ],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        pr_url = result.stdout.strip()
        print(json.dumps({
            "followup_message": f"PR created successfully: {pr_url}"
        }))
    else:
        print(json.dumps({
            "followup_message": (
                f"PR creation failed.\nError: {result.stderr}"
            )
        }))

except Exception as e:
    print(f"create_pr error: {e}", file=sys.stderr)
    print(json.dumps({}))
