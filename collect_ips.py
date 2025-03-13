import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表
urls = [
    'https://ip.164746.xyz/ipTop10.html',
    'https://cf.090227.xyz/',
    'https://www.wetest.vip/page/cloudflare/address_v4.html'
]

# 正则表达式用于匹配IP地址（限制每个段为0-255）
ip_pattern = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
# 正则表达式用于匹配速度
speed_pattern = r'(\d+\.\d+|\d+)MB/s'

# 检查并删除已有ip.txt文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 创建文件存储IP地址
with open('ip.txt', 'w') as file:
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if url == 'https://ip.164746.xyz/ipTop10.html':
                page_text = soup.get_text()
                ip_matches = re.findall(ip_pattern, page_text)
                for ip in ip_matches:
                    file.write(ip + '\n')
                print(f"从 {url} 提取: {ip_matches}")
                
            elif url == 'https://cf.090227.xyz/':
                # 查找表格行并过滤速度大于0的IP
                elements = soup.find_all('tr')
                for element in elements:
                    element_text = element.get_text()
                    ip_matches = re.findall(ip_pattern, element_text)
                    speed_matches = re.findall(speed_pattern, element_text)
                    
                    if ip_matches and speed_matches:
                        # 确保IP和速度一一对应
                        ip = ip_matches[0]  # 取第一个匹配的IP
                        speed = float(speed_matches[0].replace('MB/s', ''))
                        if speed > 0.00:
                            # 验证IP是否有效
                            valid_ip = True
                            for octet in ip.split('.'):
                                if not (0 <= int(octet) <= 255):
                                    valid_ip = False
                                    break
                            if valid_ip:
                                file.write(ip + '\n')
                                print(f"从 {url} 提取: {ip} (速度: {speed}MB/s)")
            
            elif url == 'https://www.wetest.vip/page/cloudflare/address_v4.html':
                elements = soup.find_all('tr')
                for element in elements:
                    element_text = element.get_text()
                    ip_matches = re.findall(ip_pattern, element_text)
                    if ip_matches:
                        ip = ip_matches[0]
                        file.write(ip + '\n')
                        print(f"从 {url} 提取: {ip}")
        
        except requests.exceptions.RequestException as e:
            print(f"无法访问 {url}: {e}")
            continue

print('符合条件的IP地址已保存到ip.txt文件中。')
