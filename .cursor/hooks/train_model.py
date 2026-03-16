"""
Hook: train_model.py
触发时机: run_tests.py 通过后执行
作用: 自动重新训练模型，确保 model.joblib 始终是最新代码的结果
"""
import subprocess
import json
import sys

result = subprocess.run(
    [sys.executable, "src/train.py"],
    capture_output=True,
    text=True
)

print(result.stdout, file=sys.stderr)
print(result.stderr, file=sys.stderr)

if result.returncode != 0:
    print(json.dumps({
        "followup_message": (
            "Training failed. Please fix the training script (src/train.py).\n"
            f"Error output:\n{result.stderr}"
        )
    }))
else:
    print(json.dumps({}))
