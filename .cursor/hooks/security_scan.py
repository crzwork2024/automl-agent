"""
Hook: security_scan.py
触发时机: stop hook
作用: 演示如何使用 Bandit 进行静态安全检查，
     如果 Agent 引入了不安全的做法（如硬编码密码、使用危险函数），
     此 Hook 会立刻截断流程并要求 Agent 修复代码。
"""
import subprocess
import json
import sys

# 尝试运行 bandit 检查 src 目录
try:
    result = subprocess.run(
        [sys.executable, "-m", "bandit", "-r", "src/", "-q"],
        capture_output=True,
        text=True
    )
except FileNotFoundError:
    # 如果 bandit 没安装，建议 Agent 安装（或者跳过）
    print(json.dumps({
        "followup_message": "Security warning: bandit is not installed. Please add it to requirements.txt and install."
    }))
    sys.exit(0)

# 如果安全扫描发现问题
if result.returncode != 0:
    print(json.dumps({
        "followup_message": (
            "Security Scan Failed! 🚨\n"
            "Bandit found potential security issues in your code:\n"
            f"{result.stdout}\n"
            "Please fix the reported vulnerabilities before continuing."
        )
    }))
else:
    print(json.dumps({}))
