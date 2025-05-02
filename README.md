# XidianZFW X电最废物平台操作库

这个库可以操作 `zfw.xidian.edu.cn`中的部分API，实现定制python脚本的快速开发。

## Quick-Start
可以用release里面的编译包。不相信NCC的多疑症患者们可以在根目录执行`python setup.py sdist bdist_wheel`来自己编译，之后再`pip install .\dist\xidian_zfw-x.x.x-py3-none-any.whl`安装即可。
引用时请使用`from xidian_zfw.api import XidianZFW`

## 后续优化点

- 产品顺序调整
- 无感知认证MAC添加和修改
- 账号密码修改
- 个人信息修改

## 优化注意部分

- 网站有特殊的反爬虫，我也稀里糊涂绕过的
- 属于深澜部署的系统，但是验证码有刷新bug。好好利用可以大幅提升登录成功率。

## 开源协议

- GPLv3， 我是极端分子
