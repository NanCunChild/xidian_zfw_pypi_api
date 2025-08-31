# tests/test_api.py

import pytest
from xidian_zfw.api import XidianZFW

def test_class_instantiation():
    """
    测试 XidianZFW 类是否可以被成功实例化，
    这同时也会测试 ONNX 模型是否能被正确加载。
    """
    try:
        _ = XidianZFW()
    except Exception as e:
        pytest.fail(f"实例化 XidianZFW 类失败，错误: {e}")

def test_placeholder():
    # pytest喜欢找测试，那就让它测测这个。之后再添加别的。
    assert 1 == 1