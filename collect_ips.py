import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表
urls = [
    'https://ip.164746.xyz/ipTop10.html',
    'https://cf.090227.xyz'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
# 正则表达式用于匹配速度 (例如 28.46MB/s)
speed_pattern = r'(\d+\.\d+|\d+)MB/s'

# 检查ip.txt文件是否存在，如果存在则删除
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 创建一个文件来存储IP地址
with open('ip.txt', 'w') as file:
    for url in urls:
        try:
            # 发送HTTP请求获取网页内容，设置超时时间为10秒
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if url == 'https://ip.164746.xyz/ipTop10.html':
                # 对于 ipTop10.html，直接提取所有IP地址
                page_text = soup.get_text()  # 获取页面全部文本
                ip_matches = re.findall(ip_pattern, page_text)
                
                # 写入所有找到的IP地址
                for ip in ip_matches:
                    file.write(ip + '\n')
                print(f"Extracted from {url}: {ip_matches}")
                
            elif url == 'https://cf.090227.xyz/':
                # 对于 cf.090227.xyz，查找表格行并过滤速度大于0的IP
                elements = soup.find_all('tr')
                for element in elements:
                    element_text = element.get_text()
                    ip_matches = re.findall(ip_pattern, element_text)
                    speed_matches = re.findall(speed_pattern, element_text)
                    
                    # 确保找到IP和速度
                    if ip_matches and speed_matches:
                        ip = ip_matches[0]  # 假设每行只有一个IP
                        speed = float(speed_matches[0].replace('MB/s', ''))  # 转换为浮点数
                        
                        # 只保存速度大于0的IP
                        if speed > 0.00:
                            file.write(ip + '\n')
                            print(f"Extracted from {url}: {ip} (speed: {speed}MB/s)")
        
        except requests.exceptions.RequestException as e:
            print(f"Failed to access {url}: {e}")
            continue

print('符合条件的IP地址已保存到ip.txt文件中。')
