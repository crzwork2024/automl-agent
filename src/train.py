import sys
import os
import joblib

# 确保在 automl-agent/ 根目录执行时，src/ 可被 import
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from model import load_data, build_model


def train(model_type="random_forest", C=1.0, n_estimators=100):
    """
    训练模型并将其保存到 model.joblib。

    Args:
        model_type: 模型类型，"logistic" 或 "random_forest"
        C: 逻辑回归正则化参数
        n_estimators: 随机森林树数量
    """
    X, y = load_data()
    model = build_model(model_type=model_type, C=C, n_estimators=n_estimators)
    model.fit(X, y)
    joblib.dump(model, "model.joblib")
    print(f"Training complete | model_type={model_type} C={C} n_estimators={n_estimators}")


if __name__ == "__main__":
    train()
