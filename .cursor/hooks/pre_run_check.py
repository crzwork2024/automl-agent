"""
Hook: pre_run_check.py
触发时机: start hook (Agent 开始操作前执行)
作用: 验证前置条件，例如数据文件是否存在、虚拟环境是否激活，
      如果条件不满足，可以提前向 Agent 注入 `followup_message` 提供环境建议，或者要求 Agent 创建文件。
"""
import os
import json
import sys

# 检查数据文件是否存在
if not os.path.exists("data/sample.csv"):
    print(json.dumps({
        "followup_message": (
            "Environment Check: `data/sample.csv` is missing! "
            "Please create it first before attempting to train any models."
        )
    }))
    sys.exit(0)

# 检查系统环境中是否有关键依赖
try:
    import pandas
    import sklearn
except ImportError:
    print(json.dumps({
        "followup_message": (
            "Environment Check: Missing dependencies. "
            "It looks like pandas or scikit-learn is not installed. "
            "Did you forget to activate the virtual environment or run `uv pip install -r requirements.txt`?"
        )
    }))
    sys.exit(0)

# 所有检查通过
print(json.dumps({}))
