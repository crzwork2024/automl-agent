import sys
import os
import joblib
from sklearn.metrics import accuracy_score, classification_report

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from model import load_data


def evaluate():
    """
    加载已保存的模型，在训练数据上评估并打印 accuracy。

    Returns:
        float: accuracy 分数
    """
    if not os.path.exists("model.joblib"):
        print("accuracy: 0.0")
        return 0.0

    model = joblib.load("model.joblib")
    X, y = load_data()
    pred = model.predict(X)
    acc = accuracy_score(y, pred)

    print(f"accuracy: {acc:.4f}")
    print(classification_report(y, pred))

    return acc


if __name__ == "__main__":
    evaluate()
