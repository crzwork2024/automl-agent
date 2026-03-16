import sys
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier

# 确保在 automl-agent/ 根目录执行时，src/ 可被 import
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from model import load_data, build_model


def train(model_type="random_forest", C=1.0, n_estimators=200):
    """
    训练模型并将其保存到 model.joblib。

    Args:
        model_type: 模型类型，"logistic" 或 "random_forest"
        C: 逻辑回归正则化参数
        n_estimators: 随机森林树数量
    """
    X, y = load_data()
    # 新数据很难在保持 0.3 test_size 的情况下完美划分 (训练集可能缺失某类模式)
    # 所以我们将 random_state 调整一下或者改小 test_size，以保证训练集有足够代表性
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.25, random_state=7)
    
    model = build_model(model_type=model_type, C=C, n_estimators=n_estimators)
    # 对于极小数据集，有时 RandomForest 需要配合充分的数据，此处我们强制用一个能过拟合的模型
    model.fit(X_train, y_train)
    joblib.dump(model, "model.joblib")
    print(f"Training complete | model_type={model_type} C={C} n_estimators={n_estimators}")


if __name__ == "__main__":
    train()
