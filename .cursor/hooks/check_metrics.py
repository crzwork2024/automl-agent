"""
Hook: check_metrics.py
触发时机: train_model.py 完成后执行
作用: 评估模型 accuracy，
      - accuracy < 0.9 → 要求 Agent 继续优化
      - accuracy >= 0.9 → 通知 Agent 任务完成，更新 scratchpad
"""
import subprocess
import json
import re
import sys

TARGET_ACCURACY = 0.99

result = subprocess.run(
    [sys.executable, "src/evaluate.py"],
    capture_output=True,
    text=True
)

output = result.stdout
print(output, file=sys.stderr)

match = re.search(r"accuracy:\s*([0-9.]+)", output)

if not match:
    print(json.dumps({
        "followup_message": (
            "Could not parse accuracy from evaluate.py output. "
            "Make sure evaluate.py prints 'accuracy: <value>'.\n"
            f"Output was:\n{output}"
        )
    }))
    sys.exit(0)

acc = float(match.group(1))

if acc < TARGET_ACCURACY:
    print(json.dumps({
        "followup_message": (
            f"Current accuracy is {acc:.4f}, which is below the target of {TARGET_ACCURACY}. "
            "Please improve the model. Suggestions:\n"
            "1. Try RandomForestClassifier instead of LogisticRegression\n"
            "2. Tune hyperparameters (C, n_estimators, max_depth)\n"
            "3. Add feature engineering in src/model.py\n"
            "Update .cursor/scratchpad.md with your iteration results."
        )
    }))
else:
    print(json.dumps({
        "followup_message": (
            f"Model meets the accuracy target! accuracy={acc:.4f} >= {TARGET_ACCURACY}. "
            "Please update .cursor/scratchpad.md: set Final Status to DONE."
        )
    }))
