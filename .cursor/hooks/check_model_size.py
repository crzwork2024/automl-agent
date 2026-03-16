"""
Hook: check_model_size.py
触发时机: check_metrics 之后
作用: 检查模型文件 model.joblib 的大小，如果超过限制则打回。
学习点: 演示如何使用 Hook 实施非功能性约束 (Non-functional Constraints)。
       例如，Agent 为了提高 accuracy 可能会把 RandomForest 的 n_estimators 设为 10000，
       这会导致模型体积过大。通过这层约束，强制 Agent 在 accuracy 和 资源占用 之间做 trade-off。
"""
import os
import json
import sys

# 限制模型大小最大为 1.0 MB
MAX_SIZE_MB = 1.0
MODEL_PATH = "model.joblib"

if os.path.exists(MODEL_PATH):
    size_bytes = os.path.getsize(MODEL_PATH)
    size_mb = size_bytes / (1024 * 1024)
    
    if size_mb > MAX_SIZE_MB:
        print(json.dumps({
            "followup_message": (
                f"Resource Constraint Violation: The trained model is {size_mb:.2f} MB, "
                f"which exceeds the maximum allowed size of {MAX_SIZE_MB} MB. "
                "Please simplify the model to reduce its size. "
                "For example: decrease `n_estimators`, reduce `max_depth`, or try a simpler algorithm."
            )
        }))
        sys.exit(0)

# 通过检查
print(json.dumps({}))
