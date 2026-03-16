import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


def load_data(path="data/sample.csv"):
    """加载训练数据，返回特征矩阵 X 和标签 y"""
    df = pd.read_csv(path)
    X = df[["x1", "x2"]]
    y = df["label"]
    return X, y


def build_model(model_type="logistic", C=1.0, n_estimators=100):
    """
    构建分类模型。

    Args:
        model_type: "logistic" 使用逻辑回归，"random_forest" 使用随机森林
        C: 逻辑回归正则化参数（值越大正则化越弱）
        n_estimators: 随机森林树的数量
    """
    if model_type == "random_forest":
        return RandomForestClassifier(n_estimators=n_estimators, random_state=42)
    return LogisticRegression(C=C, max_iter=1000)
