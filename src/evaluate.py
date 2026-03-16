import sys
import os
import joblib
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from model import load_data


def evaluate():
    """
    加载已保存的模型，在验证数据上评估并打印 accuracy。

    Returns:
        float: accuracy 分数
    """
    if not os.path.exists("model.joblib"):
        print("accuracy: 0.0")
        return 0.0

    model = joblib.load("model.joblib")
    X, y = load_data()
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=42)
    
    pred = model.predict(X_val)
    acc = accuracy_score(y_val, pred)

    print(f"accuracy: {acc:.4f}")
    print(classification_report(y_val, pred))

    return acc


if __name__ == "__main__":
    evaluate()
