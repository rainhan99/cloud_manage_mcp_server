#!/usr/bin/env python3
"""
IP地址检测工具模块
用于根据IP地址自动识别云服务提供商
"""

import os
import requests
from typing import Dict, Optional

def get_isp_by_ip(ip_address: str, ipinfo_token: Optional[str] = None) -> Dict[str, str]:
    """
    根据IP地址获取ISP信息
    
    Args:
        ip_address (str): 要查询的IP地址
        ipinfo_token (str, optional): IPInfo API令牌
        
    Returns:
        Dict[str, str]: 包含ISP信息的字典
    """
    try:
        # 使用IPInfo API查询
        if ipinfo_token:
            headers = {'Authorization': f'Bearer {ipinfo_token}'}
            response = requests.get(f'https://ipinfo.io/{ip_address}', headers=headers, timeout=10)
        else:
            response = requests.get(f'https://ipinfo.io/{ip_address}', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'org': data.get('org', ''),
                'hostname': data.get('hostname', ''),
                'country': data.get('country', ''),
                'region': data.get('region', ''),
                'city': data.get('city', ''),
                'loc': data.get('loc', ''),
                'postal': data.get('postal', ''),
                'timezone': data.get('timezone', '')
            }
    except Exception as e:
        print(f"查询IP信息时发生错误: {str(e)}")
    
    return {'org': 'Unknown', 'hostname': ''}

def detect_cloud_provider(ip_address: str, ipinfo_token: Optional[str] = None) -> str:
    """
    检测IP地址属于哪个云服务提供商
    
    Args:
        ip_address (str): 要检测的IP地址
        ipinfo_token (str, optional): IPInfo API令牌
        
    Returns:
        str: 云服务提供商名称 ('aws', 'digitalocean', 'vultr', 'alibaba', 'unknown')
    """
    isp_info = get_isp_by_ip(ip_address, ipinfo_token)
    org = isp_info.get('org', '').lower()
    hostname = isp_info.get('hostname', '').lower()
    
    # DigitalOcean检测
    if any(keyword in org for keyword in ['digitalocean', 'digital ocean']):
        return 'digitalocean'
    if 'digitalocean' in hostname:
        return 'digitalocean'
    
    # AWS检测
    if any(keyword in org for keyword in ['amazon', 'aws', 'amazon web services']):
        return 'aws'
    if any(keyword in hostname for keyword in ['amazonaws', 'aws', 'amazon']):
        return 'aws'
    
    # Vultr检测
    if 'vultr' in org:
        return 'vultr'
    if 'vultr' in hostname:
        return 'vultr'
    
    # 阿里云检测
    if any(keyword in org for keyword in ['alibaba', 'aliyun', 'alicloud']):
        return 'alibaba'
    if any(keyword in hostname for keyword in ['aliyun', 'alibaba', 'alicloud']):
        return 'alibaba'
    
    return 'unknown'

def get_cloud_provider_info(provider: str) -> Dict[str, str]:
    """
    获取云服务提供商的基本信息
    
    Args:
        provider (str): 提供商名称
        
    Returns:
        Dict[str, str]: 提供商信息
    """
    providers = {
        'aws': {
            'name': 'Amazon Web Services',
            'description': 'AWS EC2实例',
            'permissions': '只允许查询实例信息',
            'supported_operations': ['查询实例信息', '查看磁盘信息', '查看网络信息']
        },
        'digitalocean': {
            'name': 'DigitalOcean',
            'description': 'DigitalOcean Droplets',
            'permissions': '允许查询、开关机、重启',
            'supported_operations': ['查询实例信息', '开关机', '重启', '查看监控数据']
        },
        'vultr': {
            'name': 'Vultr',
            'description': 'Vultr云服务器',
            'permissions': '允许查询、开关机、重启',
            'supported_operations': ['查询实例信息', '开关机', '重启', '查看系统状态']
        },
        'alibaba': {
            'name': '阿里云',
            'description': '阿里云ECS实例',
            'permissions': '允许查询、开关机、重启',
            'supported_operations': ['查询实例信息', '开关机', '重启', '查看监控数据']
        },
        'unknown': {
            'name': '未知提供商',
            'description': '无法识别的云服务提供商',
            'permissions': '无可用操作',
            'supported_operations': []
        }
    }
    
    return providers.get(provider, providers['unknown']) 