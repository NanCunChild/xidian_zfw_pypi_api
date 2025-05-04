
# 1.X电最废物平台操作库功能概述

- XidianZFW库可以实现对部分`zfw.xidian.edu.cn`中API的操纵，实现相关定制化Python脚本的快速开发。

## Quick-Start

- 可以用release里面的编译包。不相信NCC的多疑症患者们可以在根目录执行`python setup.py sdist bdist_wheel`来自己编译，之后再`pip install .\dist\xidian_zfw-x.x.x-py3-none-any.whl`安装即可。 引用时请使用`from xidian_zfw.api import XidianZFW`
# 2.安装该库

- 克隆该项目：

```
git clone https://github.com/NanCunChild/xidian_zfw_pypi_api     #在Git Bash中运行
```

- 注意，请确保你的Python版本至少为3.12，如不满足要求请自行安装对应版本。
- 在本地安装该库：

```
cd C:\example\to_your_directory_\xidian_zfw_pypi_api #1.转到项目的根目录下。  
pip install .                                        #2.开始安装。
```

# 3.函数调用指南

## 3.1 用户登录

函数体:

```
login(self,username,password) -> dict
```

输入参数：

| 参数名      | 类型  | 是否必填 | 内容说明 |
| -------- | --- | ---- | ---- |
| username | str | 是    | 用户名  |
| password | str | 是    | 密码   |

输出：

| 类型   | 内容说明     |
| ---- | -------- |
| dict | 登陆状态相关信息 |
结构（登录成功）：

```
{ 
  'status': str,            # 登陆状态
  'message': str,           # 附加信息 
  'plan_num': int,          # 套餐总数 
  'unicom_plan': bool,      # 是否有联通套餐
  'telecom_plan': bool,     # 是否有电信套餐
  'ip_pay': int,            # 付费IP数量 
  'ip_free': int            # 免费IP数量
  }
```

## 3.2 获取用户套餐信息

函数体：

```
get_plan_info(self, username, encrypted_password=None, validation_code=None) ->dict
```


| 参数名                | 类型  | 是否必填 | 内容说明           |
| ------------------ | --- | ---- | -------------- |
| username           | str | 是    | 用户名            |
| encrypted_password | str | 否    | 加密后的密码（登陆后可不传） |
| validation_code    | str | 否    | 验证码（登陆后可不传）    |

输出：

| 类型   | 内容说明 |
| ---- | ---- |
| dict | 套餐信息 |
输出结构：

```
{
  'username': str,                         # 用户名
  'realname': str,                         # 真实姓名
  'status': str,                           # 登录状态
  'wallet': float,                         # 电子钱包余额
  'plan_num': int,                         # 套餐数量
  'unicom_plan': bool,                     # 是否有联通套餐
  'telecom_plan': bool,                    # 是否有电信套餐
  'public_plan': bool,                     # 是否有因公套餐
  'special_plan': bool,                    # 是否有特殊套餐
  'ip_pay': int,                           # 付费IP数量
  'ip_free': int,                          # 免费IP数量
  'ip_pay_list': list(set),                # 付费IP列表
  'ip_free_list': list(set)                # 免费IP列表
}
```

## 3.3 获取无感知MAC认证状态及绑定的MAC地址列表

函数体：

```
get_mac_auth_info(self) -> dict
```

输入：无需手动输入

输出：

| 类型   | 内容说明                  |
| ---- | --------------------- |
| dict | 无感知MAC认证状态及绑定的MAC地址列表 |
输出结构：

```
{
  'status': str,                  # 状态
  'mac_auth_enabled': str,        # 验证无感知MAC认证开启
  'mac_list': list                # MAC地址列表
}
```

## 3.4 从CSV文件中读取用户名和密码并进行批量登录

函数体：

```
batch_login_from_file(self, file_path) 
```

输入参数：

| 参数名       | 类型  | 是否必填 | 说明      |
| --------- | --- | ---- | ------- |
| file_path | str | 是    | CSV文件路径 |
输出：

| 类型    | 说明     |
| ----- | ------ |
| CSV文件 | 用户名和密码 |

输出结构（示例）：

```
student_id,password,is_initial,plan_num,unicom_plan,telecom_plan,ip_free,ip_pay
2020114514,1234,True,2,True,False,5,3
2020114520,654321,False,0,False,False,0,0
```

# 4. 开源协议

- 本项目采用GNU 通用公共许可证版本 3（[GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)）


# 5. 对于想要贡献本项目的人的建议

## 后续优化点

- 产品顺序调整
- 无感知认证MAC添加和修改
- 账号密码修改
- 个人信息修改

## 优化注意部分

- 网站有特殊的反爬虫，我也稀里糊涂绕过的
- 属于深澜部署的系统，但是验证码有刷新bug。好好利用可以大幅提升登录成功率。

