"""
Hook: format_code.py
触发时机: 每轮 stop 后最先执行
作用: 使用 ruff 自动修复并格式化代码
学习点: 演示 Hook 不仅仅能做只读检查，还可以主动修改 Agent 编写的代码，修正潜在的格式或 lint 问题。
"""
import subprocess
import json
import sys

try:
    # 尝试运行 ruff check --fix (自动修复 lint 问题)
    subprocess.run(
        ["uv", "run", "ruff", "check", "--fix", "src/", "tests/"],
        capture_output=True,
        check=False
    )
    
    # 尝试运行 ruff format (代码格式化)
    subprocess.run(
        ["uv", "run", "ruff", "format", "src/", "tests/"],
        capture_output=True,
        check=False
    )
    
    # 因为这是静默修复，我们不需要中断 Agent，返回空 json
    print(json.dumps({}))
    
except Exception as e:
    # 如果系统没有安装 ruff/uv 或执行出错，静默忽略以保证主流程不中断
    print(json.dumps({}))
