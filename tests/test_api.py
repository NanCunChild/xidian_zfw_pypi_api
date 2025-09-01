import os
import pytest
from xidian_zfw.api import XidianZFW

# --- 测试 1：一个简单的占位/初始化测试 ---
def test_class_instantiation():
    """
    测试 XidianZFW 类是否可以被成功实例化，
    这同时也会测试 ONNX 模型是否能被正确加载。
    """
    try:
        _ = XidianZFW()
    except Exception as e:
        pytest.fail(f"实例化 XidianZFW 类失败，错误: {e}")

# --- 测试 2：需要登录的集成测试 ---

# 检查是否设置了用于测试的用户名和密码环境变量
credentials_are_set = 'XDZFW_USERNAME' in os.environ and 'XDZFW_PASSWORD' in os.environ

@pytest.mark.skipif(not credentials_are_set, reason="未在环境变量中设置测试凭据 (XD_USERNAME, XD_PASSWORD)")
def test_login_and_modify_profile():
    """
    一个完整的集成测试：
    1. 使用环境变量中的凭据登录。
    2. 尝试修改个人资料。
    3. 验证两个操作都返回成功状态。
    """
    # 1. 从环境变量获取凭据
    username = os.environ['XDZFW_USERNAME']
    password = os.environ['XDZFW_PASSWORD']

    # 2. 实例化并登录
    client = XidianZFW()
    print(f"正在使用用户 '{username}' 尝试登录...")
    login_result = client.login(username, password)
    
    # 断言登录必须成功，否则测试失败
    assert login_result.get('status') == 'success', f"登录失败: {login_result.get('message')}"
    print("登录成功！")

    # 3. 尝试修改个人资料
    # 为了避免每次都真的修改，我们可以传入 None，或者传入和当前值一样的值
    # 这里为了演示，我们传入一个测试值
    print("正在尝试修改个人资料...")
    modify_result = client.modify_profile(email="test@example.com")

    # 断言修改操作返回成功
    assert modify_result.get('status') == 'success', f"修改个人资料失败: {modify_result.get('message')}"
    print("修改个人资料接口调用成功！")