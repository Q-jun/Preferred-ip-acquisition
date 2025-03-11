import os
import requests

def get_ip_list(file_path):
    """ 从本地文件或 URL 读取 IP 列表 """
    try:
        if file_path.startswith("http"):
            response = requests.get(file_path, timeout=10)
            response.raise_for_status()
            return [line.strip() for line in response.text.splitlines() if line.strip()]
        else:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading IP list from {file_path}: {e}")
        return []

def get_cloudflare_zone(api_token):
    """ 获取 Cloudflare Zone ID 和主域名 """
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

def get_existing_dns_records(api_token, zone_id, subdomain, domain):
    """ 获取 Cloudflare 现有 DNS 记录 """
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    record_name = domain if subdomain == '@' else f'{subdomain}.{domain}'
    
    response = requests.get(
        f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={record_name}',
        headers=headers
    )
    response.raise_for_status()
    records = response.json().get('result', [])
    
    return {record["content"]: record["id"] for record in records}

def update_cloudflare_dns(ip_list, api_token, zone_id, subdomain, domain):
    """ 更新 Cloudflare DNS 记录，仅添加新的 IP，删除旧的 IP """
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    record_name = domain if subdomain == '@' else f'{subdomain}.{domain}'
    
    # 获取当前 DNS 记录
    existing_records = get_existing_dns_records(api_token, zone_id, subdomain, domain)
    existing_ips = set(existing_records.keys())
    new_ips = set(ip_list)

    # 需要删除的 IP
    to_delete = existing_ips - new_ips
    # 需要新增的 IP
    to_add = new_ips - existing_ips

    # 删除不需要的 IP 记录
    for ip in to_delete:
        record_id = existing_records[ip]
        delete_response = requests.delete(
            f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}',
            headers=headers
        )
        if delete_response.status_code == 200:
            print(f"[DEL] {subdomain}: {ip}")
        else:
            print(f"[DEL FAIL] {subdomain}: {ip} - {delete_response.text}")

    # 添加新的 IP 记录
    for ip in to_add:
        data = {
            "type": "A",
            "name": record_name,
            "content": ip,
            "ttl": 1,
            "proxied": False
        }
        add_response = requests.post(
            f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records',
            json=data,
            headers=headers
        )
        if add_response.status_code == 200:
            print(f"[ADD] {subdomain}: {ip}")
        else:
            print(f"[ADD FAIL] {subdomain}: {ip} - {add_response.text}")

if __name__ == "__main__":
    api_token = os.getenv('CF_API_TOKEN')  # 从环境变量获取 API 令牌

    # 子域名和对应的 IP 文件路径
    subdomain_ip_mapping = {
        'api': 'https://raw.githubusercontent.com/Q-jun/Preferred-ip-acquisition/refs/heads/main/ip.txt',
    }

    try:
        # 获取 Cloudflare 域名信息
        zone_id, domain = get_cloudflare_zone(api_token)

        for subdomain, file_path in subdomain_ip_mapping.items():
            # 获取 IP 列表
            ip_list = get_ip_list(file_path)
            if not ip_list:
                print(f"[SKIP] No IPs found for {subdomain}, skipping update.")
                continue

            # 更新 Cloudflare DNS 记录
            update_cloudflare_dns(ip_list, api_token, zone_id, subdomain, domain)

    except Exception as e:
        print(f"[ERROR] {e}")
