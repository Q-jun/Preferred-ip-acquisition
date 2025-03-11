import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urljoin

# 目标URL列表
urls = [
    'https://ip.164746.xyz/ipTop10/',  # 注意URL末尾可能不需要.html
    'https://cf.090227.xyz/'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
# 正则表达式用于匹配速度 (例如 28.46MB/s)
speed_pattern = r'(\d+\.\d+|\d+)MB/s'

# 请求头，模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 检查并创建ip.txt文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 创建一个文件来存储IP地址
try:
    with open('ip.txt', 'w', encoding='utf-8') as file:
        for url in urls:
            try:
                # 发送HTTP请求获取网页内容，增加headers和更长的超时时间
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # 确保正确的字符编码
                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, 'html.parser')
                
                if 'ip.164746.xyz' in url:
                    # 对于ipTop10页面，使用更灵活的提取方式
                    page_text = soup.get_text(separator=' ')  # 使用空格分隔文本
                    ip_matches = re.findall(ip_pattern, page_text)
                    
                    # 验证IP地址的有效性
                    valid_ips = []
                    for ip in ip_matches:
                        parts = ip.split('.')
                        if all(0 <= int(part) <= 255 for part in parts):
                            valid_ips.append(ip)
                            file.write(ip + '\n')
                    
                    if valid_ips:
                        print(f"Extracted from {url}: {valid_ips}")
                    else:
                        print(f"No valid IPs found in {url}")
                
                elif 'cf.090227.xyz' in url:
                    # 处理cf网站的逻辑保持不变
                    elements = soup.find_all('tr')
                    for element in elements:
                        element_text = element.get_text()
                        ip_matches = re.findall(ip_pattern, element_text)
                        speed_matches = re.findall(speed_pattern, element_text)
                        
                        if ip_matches and speed_matches:
                            ip = ip_matches[0]
                            speed = float(speed_matches[0].replace('MB/s', ''))
                            
                            if speed > 0.00:
                                file.write(ip + '\n')
                                print(f"Extracted from {url}: {ip} (speed: {speed}MB/s)")
            
            except requests.exceptions.RequestException as e:
                print(f"Failed to access {url}: {e}")
                continue
                
except IOError as e:
    print(f"Failed to write to file: {e}")

print('符合条件的IP地址已保存到ip.txt文件中。')
