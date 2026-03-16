"""
Hook: run_tests.py
触发时机: Agent 每轮操作结束（stop hook）
作用: 运行 pytest，如果测试失败则告知 Agent 去修复代码
"""
import subprocess
import json
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"],
    capture_output=True,
    text=True
)

print(result.stdout, file=sys.stderr)
print(result.stderr, file=sys.stderr)

if result.returncode != 0:
    # 测试失败：通过 followup_message 告知 Agent 需要修复
    print(json.dumps({
        "followup_message": (
            "Tests failed. Please fix the failing tests before proceeding.\n"
            f"pytest output:\n{result.stdout}\n{result.stderr}"
        )
    }))
else:
    # 测试通过：空输出，继续下一个 hook
    print(json.dumps({}))
