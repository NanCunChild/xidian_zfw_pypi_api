from time import sleep
import requests
import pandas as pd
from bs4 import BeautifulSoup
import bs4
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
from PIL import Image
from io import BytesIO
import ddddocr
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
from collections import Counter
import os
import onnxruntime

if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

class XidianZFW:
    def __init__(self):
        os.environ['ORT_TENSORRT_LOG_LEVEL'] = '3'  # 只显示错误信息
        os.environ['ORT_TENSORRT_FP16_ENABLE'] = '1'
        
        sess_options = onnxruntime.SessionOptions()
        sess_options.log_severity_level = 3
        self.ocr = ddddocr.DdddOcr()
        self.session = self._create_session_with_retries()
        self.cookies = None
        self.csrf_token = None
        self.public_key = None
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
        })

    def _create_session_with_retries(self, retries=3, backoff_factor=0.3):
        """创建一个带重试策略的会话"""
        session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session

    def _is_valid_ip(self, ip_address):
        """检查字符串是否为有效的 IPv4 地址"""
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        match = re.match(pattern, ip_address)
        return bool(match)

    def _encrypt_password(self, password, public_key_str):
        """使用RSA公钥加密密码"""
        public_key = RSA.importKey(public_key_str)
        cipher = PKCS1_v1_5.new(public_key)
        encrypted_password = cipher.encrypt(password.encode('utf-8'))
        return base64.b64encode(encrypted_password).decode('utf-8')

    def _get_login_page(self):
        """获取登录页面以提取公钥和CSRF token"""
        url = 'https://zfw.xidian.edu.cn/'
        response = self.session.get(url)
        response.raise_for_status()

        # 解析HTML以获取public key和csrf token
        soup = BeautifulSoup(response.text, 'html.parser')
        self.csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
        self.public_key = soup.find('input', {'id': 'public'})['value']

        # 获取cookies
        self.cookies = response.cookies.get_dict()

    def _get_captcha_image(self):
        """从服务器获取验证码图片"""
        url = 'https://zfw.xidian.edu.cn/site/captcha'
        response = self.session.get(url, cookies=self.cookies)
        response.raise_for_status()
        return response.content

    def _recognize_captcha(self, image):
        """使用 ddddocr 识别验证码"""
        result = self.ocr.classification(image)
        return result

    def login(self, username, password):
        """
        使用用户名和密码进行登录（含验证码重试机制）
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            dict: 包含登录状态及相关信息
        """
        for attempt in range(3):
            try:
                # 创建独立会话防止状态污染
                temp_session = self._create_session_with_retries()
                temp_session.headers.update(self.session.headers)

                # 获取登录页面信息
                login_page_response = temp_session.get('https://zfw.xidian.edu.cn/')
                soup = BeautifulSoup(login_page_response.text, 'html.parser')
                csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
                public_key = soup.find('input', {'id': 'public'})['value']
                cookies = login_page_response.cookies.get_dict()

                # 获取新验证码
                captcha_response = temp_session.get('https://zfw.xidian.edu.cn/site/captcha', cookies=cookies)
                captcha_image = captcha_response.content

                validation_code = self._recognize_captcha(captcha_image)

                # 密码加密处理
                encrypted_pwd = self._encrypt_password(password, public_key)

                # 构建登录请求
                login_response = temp_session.post(
                    'https://zfw.xidian.edu.cn/site/validate-user',
                    headers={
                        'X-CSRF-Token': csrf_token,
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    cookies=cookies,
                    data={
                        'LoginForm[username]': username,
                        'LoginForm[password]': encrypted_pwd,
                        'LoginForm[verifyCode]': validation_code,
                    }
                )
                login_data = login_response.json()

                # 处理登录结果
                if login_data.get("message") == "success":
                    # 登录成功同步会话状态
                    self.session = temp_session
                    self.cookies = cookies
                    self.csrf_token = csrf_token
                    self.public_key = public_key
                    return self._handle_success_login(username, encrypted_pwd, validation_code)
                
                # 验证码错误特殊处理
                if "验证码" in login_data.get("message", ""):
                    print(f"Attempt {attempt+1}: 验证码错误，刷新重试...")
                    continue
                    
                # 其他错误立即返回
                return {
                    'status': 'error',
                    'message': login_data.get("message", "未知错误")
                }

            except Exception as e:
                print(f"Attempt {attempt+1} 发生异常: {str(e)}")
                if attempt == 2:
                    return {'status': 'error', 'message': f"登录失败: {str(e)}"}

        return {'status': 'error', 'message': '三次尝试均失败'}

    def _handle_success_login(self, username, encrypted_pwd, validation_code):
        """处理成功登录后的信息获取"""
        plan_info = self.get_plan_info(username, encrypted_pwd, validation_code)
        return {
            'status': 'success',
            'message': '登录成功',
            'plan_num': plan_info['plan_num'],
            'unicom_plan': plan_info['unicom_plan'],
            'telecom_plan': plan_info['telecom_plan'],
            'ip_pay': plan_info['ip_pay'],
            'ip_free': plan_info['ip_free']
        }

    def get_plan_info(self, username, encrypted_password=None, validation_code=None):
        """
        获取用户套餐信息
        
        Args:
            username (str): 用户名
            encrypted_password (str, optional): 加密后的密码，如果已登录可不传
            validation_code (str, optional): 验证码，如果已登录可不传
            
        Returns:
            dict: 包含套餐数量、运营商信息和IP信息的字典
        """
        url = 'https://zfw.xidian.edu.cn/'
        
        if encrypted_password and validation_code:
            data = {
                '_csrf-8800': self.csrf_token,
                'LoginForm[username]': username,
                'LoginForm[password]': encrypted_password,
                'LoginForm[smsCode]': "",
                'LoginForm[verifyCode]': validation_code
            }
            response = self.session.post(url, data=data)
        else:
            response = self.session.get(url)
            
        response.raise_for_status()
        return self._parse_html(response.text)

    def _parse_html(self, html):
        """解析HTML获取套餐信息、IP信息和用户信息"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 解析用户信息
        user_info = self._parse_user_info(soup)
        
        # 解析套餐信息
        plan_info = self._parse_plan_info(soup)
        
        # 解析IP信息
        ip_info = self._parse_ip_info(soup)

        return {
            **user_info,
            **plan_info,
            **ip_info
        }

    def _parse_user_info(self, soup):
        """解析用户基本信息"""
        user_panel = soup.find("div", class_="query-user")
        info = {
            'username': '',
            'realname': '',
            'status': '',
            'wallet': 0.0
        }

        if user_panel:
            items = user_panel.find_all("li", class_="list-group-item")
            for item in items:
                label = item.find("label", class_="list-group-label")
                if not label:
                    continue
                
                label_text = label.get_text(strip=True)
                value = label.next_sibling
                
                # 处理特殊状态按钮
                if label_text == "状态":
                    status_btn = item.find("a", class_="btn")
                    if status_btn:
                        info['status'] = status_btn.get_text(strip=True)
                    continue
                
                # 处理数字类型的电子钱包
                if label_text == "电子钱包":
                    try:
                        info['wallet'] = float(value.strip())
                    except (ValueError, AttributeError):
                        pass
                    continue
                
                # 处理普通文本信息
                if isinstance(value, bs4.element.NavigableString):
                    text = value.strip()
                    if label_text == "用户名":
                        info['username'] = text
                    elif label_text == "姓名":
                        info['realname'] = text

        return info

    def _parse_plan_info(self, soup):
        """解析套餐信息"""
        plan_num = 0
        unicom_plan = False
        telecom_plan = False
        public_plan = False
        special_plan = False
        
        table = soup.find("table", class_="kv-grid-table")
        if table:
            tbody = table.find("tbody")
            if tbody:
                for tr in tbody.find_all("tr"):
                    plan_num += 1
                    text = tr.get_text()
                    if "联通" in text:
                        unicom_plan = True
                    elif "电信" in text:
                        telecom_plan = True
                    elif "因公" in text:
                        public_plan = True
                    else:
                        special_plan = True
        
        return {
            'plan_num': plan_num,
            'unicom_plan': unicom_plan,
            'telecom_plan': telecom_plan,
            'public_plan': public_plan,
            'special_plan': special_plan
        }

    def _parse_ip_info(self, soup):
        """解析IP信息"""
        ip_free_set = set()
        ip_pay_set = set()
        
        table = soup.find("table", class_="table-striped")
        if table:
            tbody = table.find("tbody")
            if tbody:
                for tr in tbody.find_all("tr"):
                    ip = ""
                    is_pay = False
                    for td in tr.find_all("td"):
                        text = td.get_text(strip=True)
                        if self._is_valid_ip(text):
                            ip = text
                        elif "电信" in text or "联通" in text or "移动" in text:
                            is_pay = True
                    if ip:
                        (ip_pay_set if is_pay else ip_free_set).add(ip)
        
        return {
            'ip_pay': len(ip_pay_set),
            'ip_free': len(ip_free_set),
            'ip_pay_list': list(ip_pay_set),
            'ip_free_list': list(ip_free_set)
        }

    def _handle_success_login(self, username, encrypted_pwd, validation_code):
        """处理成功登录后的信息获取"""
        plan_info = self.get_plan_info(username, encrypted_pwd, validation_code)
        return {
            'status': 'success',
            'message': '登录成功',
            'username': plan_info.get('username', ''),
            'realname': plan_info.get('realname', ''),
            'user_status': plan_info.get('status', ''),
            'wallet': plan_info.get('wallet', 0.0),
            'plan_num': plan_info['plan_num'],
            'unicom_plan': plan_info['unicom_plan'],
            'telecom_plan': plan_info['telecom_plan'],
            'ip_pay': plan_info['ip_pay'],
            'ip_free': plan_info['ip_free']
        }
        
    def get_mac_auth_info(self):
        """获取无感知MAC认证状态及绑定的MAC地址列表"""
        try:
            url = 'https://zfw.xidian.edu.cn/user/mac-auth'
            headers = {'Referer': url}
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {'status': 'error', 'message': f'请求失败: {str(e)}', 'mac_auth_enabled': False, 'mac_list': []}

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找状态div
        status_div = soup.find('div', class_='kv-panel-before')
        if not status_div:
            return {'status': 'error', 'message': '未找到状态信息', 'mac_auth_enabled': False, 'mac_list': []}

        status_text = None
        for element in status_div:
            if isinstance(element, bs4.element.NavigableString):
                text = element.strip()
                if "无感知认证" in text:
                    # 定位相邻的span标签
                    next_sibling = element.next_sibling
                    while next_sibling and not isinstance(next_sibling, bs4.element.Tag):
                        next_sibling = next_sibling.next_sibling
                    if next_sibling and next_sibling.name == 'span':
                        status_text = next_sibling.get_text(strip=True)
                    break

        if not status_text:
            return {'status': 'error', 'message': '未找到状态值', 'mac_auth_enabled': False, 'mac_list': []}

        # 验证状态有效性
        if status_text not in ['开启', '关闭']:
            return {'status': 'error', 'message': f'非法状态值: {status_text}', 'mac_auth_enabled': False, 'mac_list': []}

        # 解析MAC地址表格
        mac_list = []
        if status_text == '开启':
            table = soup.find('table', class_='kv-grid-table table table-hover table-bordered kv-table-wrap')
            if not table:
                return {'status': 'error', 'message': '未找到MAC表格', 'mac_auth_enabled': True, 'mac_list': []}
            
            tbody = table.find('tbody')
            if tbody:
                for row in tbody.find_all('tr'):
                    tds = row.find_all('td')
                    if len(tds) >= 2:
                        mac = tds[1].get_text(strip=True)
                        mac_list.append(mac)

        return {
            'status': 'success',
            'mac_auth_enabled': status_text == '开启',
            'mac_list': mac_list
        }

    def batch_login_from_file(self, file_path):
        """
        从CSV文件中读取用户名和密码并进行批量登录
        
        Args:
            file_path (str): CSV文件路径
            
        Returns:
            pd.DataFrame: 更新后的数据框
        """
        df = pd.read_csv(file_path)
        # 找到第一个is_initial为空的索引
        start_index = df[df['is_initial'].isnull()].index.min()
        
        # 如果没有找到需要处理的行，返回
        if pd.isna(start_index):
            print("所有用户已处理完毕，无需继续。")
            return df

        for index, row in df.iterrows():
            if index < start_index:
                continue
                
            username = row.get('student_id')
            password = row.get('password')
            password = password.zfill(6)
            
            for _ in range(3):
                sleep(0.2)
                self.session.close()
                self.session = self._create_session_with_retries()
                
                result = self.login(username, password)
                
                if result['status'] == "success":
                    df.at[index, 'is_initial'] = "True"
                    df.at[index, 'plan_num'] = result['plan_num']
                    df.at[index, 'unicom_plan'] = result['unicom_plan']
                    df.at[index, 'telecom_plan'] = result['telecom_plan']
                    df.at[index, 'ip_free'] = result['ip_free']
                    df.at[index, 'ip_pay'] = result['ip_pay']
                    break
                else:
                    if "用户名或密码错误" in result['message']:
                        df.at[index, 'is_initial'] = "False"
                        break
                    elif "验证码错误" in result['message']:
                        df.at[index, 'is_initial'] = "Unknown"
                        continue
                    else:
                        break

            # 每处理一个用户就保存一次结果
            df.to_csv(file_path, index=False)
            print(f"Progress saved after {index + 1} attempts.")

        df.to_csv(file_path, index=False)
        print("Final results saved.")
        return df