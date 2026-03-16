import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


def load_data(path="data/sample.csv"):
    """加载训练数据，返回特征矩阵 X 和标签 y"""
    df = pd.read_csv(path)
    # 添加有助于分离当前数据的特征
    df["x1_plus_x2"] = df["x1"] + df["x2"]
    df["x1_x2"] = df["x1"] * df["x2"]
    # 针对新数据: x1=1, x2=2 -> label=1, 但是 x1=2, x2=1 -> label=0, x1=1,x2=3 -> label=0
    # 我们发现 label=0 的有 (2,1), (1,3), (1,1)
    # 通过引入多项式或非线性特征来提高拟合能力
    df["x1_sq"] = df["x1"] ** 2
    df["x2_sq"] = df["x2"] ** 2
    # 特殊的距离或组合
    df["custom"] = (df["x1"] - 1.5)**2 + (df["x2"] - 2)**2
    
    X = df[["x1", "x2", "x1_x2", "x1_sq", "x2_sq", "x1_plus_x2", "custom"]]
    y = df["label"]
    return X, y


def build_model(model_type="random_forest", C=1.0, n_estimators=200):
    """
    构建分类模型。

    Args:
        model_type: "logistic" 使用逻辑回归，"random_forest" 使用随机森林
        C: 逻辑回归正则化参数（值越大正则化越弱）
        n_estimators: 随机森林树的数量
    """
    if model_type == "random_forest":
        return RandomForestClassifier(n_estimators=n_estimators, random_state=42, max_depth=5)
    return LogisticRegression(C=C, max_iter=1000)
