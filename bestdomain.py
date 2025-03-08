import os
import requests

# # 从本地文件读取 IP 列表
# def get_ip_list(file_path):
#     with open(file_path, 'r') as f:
#         return [line.strip() for line in f if line.strip()]  # 读取文件并去除空行
def get_ip_list(file_path):
    if file_path.startswith("http"):  # 判断是否是 URL
        response = requests.get(file_path)
        response.raise_for_status()  # 确保请求成功
        return [line.strip() for line in response.text.splitlines() if line.strip()]
    else:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
# 获取 Cloudflare 域名信息
def get_cloudflare_zone(api_token):
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    response = requests.get('https://api.cloudflare.com/client/v4/zones', headers=headers)
    response.raise_for_status()
    zones = response.json().get('result', [])
    if not zones:
        raise Exception("No zones found")
    return zones[0]['id'], zones[0]['name']

# 删除指定子域名的现有 DNS 记录
def delete_existing_dns_records(api_token, zone_id, subdomain, domain):
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    record_name = domain if subdomain == '@' else f'{subdomain}.{domain}'
    while True:
        response = requests.get(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={record_name}', headers=headers)
        response.raise_for_status()
        records = response.json().get('result', [])
        if not records:
            break
        for record in records:
            delete_response = requests.delete(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record["id"]}', headers=headers)
            delete_response.raise_for_status()
            print(f"Del {subdomain}:{record['id']}")

# 更新 Cloudflare DNS 记录
def update_cloudflare_dns(ip_list, api_token, zone_id, subdomain, domain):
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    record_name = domain if subdomain == '@' else f'{subdomain}.{domain}'
    for ip in ip_list:
        data = {
            "type": "A",
            "name": record_name,
            "content": ip,
            "ttl": 1,
            "proxied": False
        }
        response = requests.post(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', json=data, headers=headers)
        if response.status_code == 200:
            print(f"Add {subdomain}:{ip}")
        else:
            print(f"Failed to add A record for IP {ip} to subdomain {subdomain}: {response.status_code} {response.text}")

if __name__ == "__main__":
    api_token = os.getenv('CF_API_TOKEN')  # 从环境变量获取 API 令牌
    
    # 子域名和对应的本地 IP 文件路径
    subdomain_ip_mapping = {
        #'bestcf': 'ip.txt',  # 使用第二份代码生成的 ip.txt 文件
        'api': 'https://raw.githubusercontent.com/Q-jun/Preferred-ip-acquisition/refs/heads/main/ip.txt',     # 示例中同样使用 ip.txt，也可以指定其他文件
        # 添加更多子域名和对应的文件路径
    }
    
    try:
        # 获取 Cloudflare 域名信息
        zone_id, domain = get_cloudflare_zone(api_token)
        
        for subdomain, file_path in subdomain_ip_mapping.items():
            # 从本地文件获取 IP 列表
            ip_list = get_ip_list(file_path)
            # 删除现有的 DNS 记录
            delete_existing_dns_records(api_token, zone_id, subdomain, domain)
            # 更新 Cloudflare DNS 记录
            update_cloudflare_dns(ip_list, api_token, zone_id, subdomain, domain)
            
    except Exception as e:
        print(f"Error: {e}")
