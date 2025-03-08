import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表
urls = ['https://ip.164746.xyz/ipTop10.html', 
        'https://cf.090227.xyz'
        ]

# 正则表达式用于匹配IP地址
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 正则表达式用于匹配速度 (例如 23.21MB/s)
speed_pattern = r'(\d+\.\d+|\d+)MB/s'

# 检查ip.txt文件是否存在,如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 创建一个文件来存储IP地址
with open('ip.txt', 'w') as file:
    for url in urls:
        # 发送HTTP请求获取网页内容
        response = requests.get(url)
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 根据网站的不同结构找到包含IP地址的元素
        if url == 'https://ip.164746.xyz/ipTop10.html':
            elements = soup.find_all('tr')
        elif url == 'https://cf.090227.xyz':
            elements = soup.find_all('tr')
        else:
            elements = soup.find_all('li')
        
        # 遍历所有元素,查找IP地址和速度
        for element in elements:
            element_text = element.get_text()  # 获取元素文本
            ip_matches = re.findall(ip_pattern, element_text)  # 查找IP地址
            speed_matches = re.findall(speed_pattern, element_text)  # 查找速度
            
            # 确保找到IP地址和速度
            if ip_matches and speed_matches:
                ip = ip_matches[0]  # 假设每行只有一个IP地址
                speed = float(speed_matches[0].replace('MB/s', ''))  # 将速度转换为浮点数
                
                # 只保存速度大于0.00MB/s的IP地址
                if speed > 0.00:
                    file.write(ip + '\n')

print('IP地址已保存到ip.txt文件中（仅包含速度大于0.00MB/s的IP）。')
