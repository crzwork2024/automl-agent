import sys
import os

# 将项目根目录加入路径，使 src/ 下的模块可被导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from model import build_model, load_data


def test_model_creation_logistic():
    """测试逻辑回归模型能正常创建"""
    model = build_model(model_type="logistic", C=1.0)
    assert model is not None


def test_model_creation_random_forest():
    """测试随机森林模型能正常创建"""
    model = build_model(model_type="random_forest", n_estimators=50)
    assert model is not None


def test_data_loading():
    """测试数据加载返回正确的列"""
    X, y = load_data()
    assert "x1" in X.columns
    assert "x2" in X.columns
    assert len(X) == len(y)


def test_model_fit():
    """测试模型能在示例数据上完成训练"""
    X, y = load_data()
    model = build_model()
    model.fit(X, y)
    preds = model.predict(X)
    assert len(preds) == len(y)
