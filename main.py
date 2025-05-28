#!/usr/bin/env python3
"""
云服务器管理 MCP 服务器
支持多云平台：AWS、DigitalOcean、Vultr、阿里云
"""

import os
from mcp import server
from typing import Dict, Optional

# 导入各个云服务提供商
from providers.aws_provider import aws_provider
from providers.digitalocean_provider import digitalocean_provider
from providers.vultr_provider import vultr_provider
from providers.alibaba_provider import alibaba_provider

# 导入工具模块
from utils.ip_detection import detect_cloud_provider, get_cloud_provider_info
from utils.security import SecurityConfirmation, require_triple_confirmation

# 环境变量
IPINFO_API_TOKEN = os.getenv("IPINFO_API_TOKEN")

# 初始化MCP服务器
mcp = server.FastMCP("multi-cloud-manager")

# 云服务提供商映射
PROVIDERS = {
    'aws': aws_provider,
    'digitalocean': digitalocean_provider,
    'vultr': vultr_provider,
    'alibaba': alibaba_provider
}

@mcp.tool()
def get_instance_info(ip_address: str) -> Dict:
    """
    根据IP地址自动检测云服务提供商并获取实例信息
    
    Args:
        ip_address (str): 公网IP地址
        
    Returns:
        Dict: 实例信息，包含提供商信息和实例详情
    """
    # 检测云服务提供商
    provider_name = detect_cloud_provider(ip_address, IPINFO_API_TOKEN)
    provider_info = get_cloud_provider_info(provider_name)
    
    if provider_name == 'unknown':
        return {
            'error': '无法识别IP地址对应的云服务提供商',
            'ip_address': ip_address,
            'detected_provider': 'unknown',
            'suggestion': '请手动指定云服务提供商或检查IP地址是否正确'
        }
    
    # 获取对应的提供商
    provider = PROVIDERS.get(provider_name)
    if not provider:
        return {
            'error': f'不支持的云服务提供商: {provider_name}',
            'detected_provider': provider_name,
            'supported_providers': list(PROVIDERS.keys())
        }
    
    # 调用提供商的查询方法
    if provider_name == 'aws':
        result = provider.get_instance_by_ip(ip_address)
    elif provider_name == 'digitalocean':
        result = provider.get_droplet_by_ip(ip_address)
    elif provider_name == 'vultr':
        result = provider.get_instance_by_ip(ip_address)
    elif provider_name == 'alibaba':
        result = provider.get_instance_by_ip(ip_address)
    else:
        return {
            'error': f'提供商 {provider_name} 的查询方法未实现',
            'detected_provider': provider_name
        }
    
    # 添加检测信息到结果中
    result['detected_provider'] = provider_name
    result['provider_info'] = provider_info
    result['search_ip'] = ip_address
    
    return result

@mcp.tool()
def get_aws_instance_info(ip_address_or_id: str) -> Dict:
    """
    获取AWS EC2实例信息（只读）
    
    Args:
        ip_address_or_id (str): 公网IP地址或实例ID
        
    Returns:
        Dict: AWS实例信息
    """
    # 判断是IP地址还是实例ID
    if ip_address_or_id.startswith('i-'):
        return aws_provider.get_instance_by_id(ip_address_or_id)
    else:
        return aws_provider.get_instance_by_ip(ip_address_or_id)

@mcp.tool()
def get_aws_instance_storage_info(instance_id: str) -> Dict:
    """
    获取AWS EC2实例的存储详细信息
    
    Args:
        instance_id (str): EC2实例ID
        
    Returns:
        Dict: 存储信息，包括磁盘类型、IOPS、吞吐量等
    """
    return aws_provider.get_instance_storage_info(instance_id)

@mcp.tool()
def get_aws_instance_monitoring(instance_id: str, hours: int = 1) -> Dict:
    """
    获取AWS EC2实例的监控数据
    
    Args:
        instance_id (str): EC2实例ID
        hours (int): 获取过去多少小时的数据
        
    Returns:
        Dict: 监控数据
    """
    return aws_provider.get_instance_monitoring_data(instance_id, hours)

@mcp.tool()
def list_aws_instances() -> Dict:
    """
    列出所有AWS EC2实例
    
    Returns:
        Dict: AWS实例列表
    """
    return aws_provider.list_instances()

@mcp.tool()
def get_digitalocean_droplet_info(ip_address_or_id: str) -> Dict:
    """
    获取DigitalOcean Droplet信息
    
    Args:
        ip_address_or_id (str): 公网IP地址或Droplet ID
        
    Returns:
        Dict: Droplet信息
    """
    # 判断是IP地址还是Droplet ID
    if ip_address_or_id.isdigit():
        return digitalocean_provider.get_droplet_by_id(int(ip_address_or_id))
    else:
        return digitalocean_provider.get_droplet_by_ip(ip_address_or_id)

@mcp.tool()
def power_on_digitalocean_droplet(
    droplet_id: int, 
    ip_confirmation: str = "", 
    name_confirmation: str = "", 
    operation_confirmation: str = ""
) -> Dict:
    """
    开启DigitalOcean Droplet（需要三次确认）
    
    Args:
        droplet_id (int): Droplet ID
        ip_confirmation (str): 确认IP地址
        name_confirmation (str): 确认Droplet名称
        operation_confirmation (str): 确认操作类型（输入"开机"或"power_on"）
        
    Returns:
        Dict: 操作结果或确认要求
    """
    return digitalocean_provider.power_on_droplet(
        droplet_id, ip_confirmation, name_confirmation, operation_confirmation
    )

@mcp.tool()
def power_off_digitalocean_droplet(
    droplet_id: int, 
    ip_confirmation: str = "", 
    name_confirmation: str = "", 
    operation_confirmation: str = ""
) -> Dict:
    """
    强制关闭DigitalOcean Droplet（需要三次确认）
    """
    return digitalocean_provider.power_off_droplet(
        droplet_id, ip_confirmation, name_confirmation, operation_confirmation
    )

@mcp.tool()
def shutdown_digitalocean_droplet(
    droplet_id: int, 
    ip_confirmation: str = "", 
    name_confirmation: str = "", 
    operation_confirmation: str = ""
) -> Dict:
    """
    优雅关闭DigitalOcean Droplet（需要三次确认）
    """
    return digitalocean_provider.shutdown_droplet(
        droplet_id, ip_confirmation, name_confirmation, operation_confirmation
    )

@mcp.tool()
def reboot_digitalocean_droplet(
    droplet_id: int, 
    ip_confirmation: str = "", 
    name_confirmation: str = "", 
    operation_confirmation: str = ""
) -> Dict:
    """
    重启DigitalOcean Droplet（需要三次确认）
    """
    return digitalocean_provider.reboot_droplet(
        droplet_id, ip_confirmation, name_confirmation, operation_confirmation
    )

@mcp.tool()
def list_digitalocean_droplets() -> Dict:
    """
    列出所有DigitalOcean Droplets
    """
    return digitalocean_provider.list_droplets()

@mcp.tool()
def get_digitalocean_droplet_monitoring(droplet_id: int) -> Dict:
    """
    获取DigitalOcean Droplet监控信息
    """
    return digitalocean_provider.get_droplet_monitoring(droplet_id)

@mcp.tool()
def get_digitalocean_droplet_actions(droplet_id: int) -> Dict:
    """
    获取DigitalOcean Droplet操作历史
    """
    return digitalocean_provider.get_droplet_actions(droplet_id)

@mcp.tool()
def get_vultr_instance_info(ip_address_or_id: str) -> Dict:
    """
    获取Vultr实例信息
    
    Args:
        ip_address_or_id (str): 公网IP地址或实例ID
        
    Returns:
        Dict: Vultr实例信息
    """
    # Vultr实例ID通常是UUID格式
    if '-' in ip_address_or_id and len(ip_address_or_id) > 20:
        return vultr_provider.get_instance_by_id(ip_address_or_id)
    else:
        return vultr_provider.get_instance_by_ip(ip_address_or_id)

@mcp.tool()
def power_on_vultr_instance(
    instance_id: str, 
    ip_confirmation: str = "", 
    name_confirmation: str = "", 
    operation_confirmation: str = ""
) -> Dict:
    """
    开启Vultr实例（需要三次确认）
    """
    return vultr_provider.power_on_instance(
        instance_id, ip_confirmation, name_confirmation, operation_confirmation
    )

@mcp.tool()
def power_off_vultr_instance(
    instance_id: str, 
    ip_confirmation: str = "", 
    name_confirmation: str = "", 
    operation_confirmation: str = ""
) -> Dict:
    """
    强制关闭Vultr实例（需要三次确认）
    """
    return vultr_provider.power_off_instance(
        instance_id, ip_confirmation, name_confirmation, operation_confirmation
    )

@mcp.tool()
def reboot_vultr_instance(
    instance_id: str, 
    ip_confirmation: str = "", 
    name_confirmation: str = "", 
    operation_confirmation: str = ""
) -> Dict:
    """
    重启Vultr实例（需要三次确认）
    """
    return vultr_provider.reboot_instance(
        instance_id, ip_confirmation, name_confirmation, operation_confirmation
    )

@mcp.tool()
def list_vultr_instances() -> Dict:
    """
    列出所有Vultr实例
    """
    return vultr_provider.list_instances()

@mcp.tool()
def get_vultr_instance_bandwidth(instance_id: str) -> Dict:
    """
    获取Vultr实例带宽使用情况
    """
    return vultr_provider.get_instance_bandwidth(instance_id)

@mcp.tool()
def get_alibaba_instance_info(ip_address_or_id: str) -> Dict:
    """
    获取阿里云ECS实例信息
    
    Args:
        ip_address_or_id (str): 公网IP地址或实例ID
        
    Returns:
        Dict: 阿里云实例信息
    """
    # 阿里云实例ID通常以i-开头
    if ip_address_or_id.startswith('i-'):
        return alibaba_provider.get_instance_by_id(ip_address_or_id)
    else:
        return alibaba_provider.get_instance_by_ip(ip_address_or_id)

@mcp.tool()
def power_on_alibaba_instance(
    instance_id: str, 
    ip_confirmation: str = "", 
    name_confirmation: str = "", 
    operation_confirmation: str = ""
) -> Dict:
    """
    启动阿里云ECS实例（需要三次确认）
    """
    return alibaba_provider.power_on_instance(
        instance_id, ip_confirmation, name_confirmation, operation_confirmation
    )

@mcp.tool()
def power_off_alibaba_instance(
    instance_id: str, 
    ip_confirmation: str = "", 
    name_confirmation: str = "", 
    operation_confirmation: str = ""
) -> Dict:
    """
    强制停止阿里云ECS实例（需要三次确认）
    """
    return alibaba_provider.power_off_instance(
        instance_id, ip_confirmation, name_confirmation, operation_confirmation
    )

@mcp.tool()
def reboot_alibaba_instance(
    instance_id: str, 
    ip_confirmation: str = "", 
    name_confirmation: str = "", 
    operation_confirmation: str = ""
) -> Dict:
    """
    重启阿里云ECS实例（需要三次确认）
    """
    return alibaba_provider.reboot_instance(
        instance_id, ip_confirmation, name_confirmation, operation_confirmation
    )

@mcp.tool()
def list_alibaba_instances() -> Dict:
    """
    列出所有阿里云ECS实例
    """
    return alibaba_provider.list_instances()

@mcp.tool()
def get_alibaba_instance_monitoring(instance_id: str) -> Dict:
    """
    获取阿里云ECS实例监控信息
    """
    return alibaba_provider.get_instance_monitoring(instance_id)

@mcp.tool()
def get_supported_providers() -> Dict:
    """
    获取支持的云服务提供商列表
    
    Returns:
        Dict: 支持的云服务提供商信息
    """
    providers_status = {}
    
    for provider_name, provider in PROVIDERS.items():
        provider_info = get_cloud_provider_info(provider_name)
        providers_status[provider_name] = {
            'name': provider_info['name'],
            'description': provider_info['description'],
            'permissions': provider_info['permissions'],
            'supported_operations': provider_info['supported_operations'],
            'available': getattr(provider, 'available', False),
            'error': getattr(provider, 'error', None) if not getattr(provider, 'available', False) else None
        }
    
    return {
        'total_providers': len(PROVIDERS),
        'providers': providers_status,
        'ip_detection_available': bool(IPINFO_API_TOKEN),
        'security_features': [
            '三次确认机制（IP、名称、操作类型）',
            'AWS只读权限',
            '其他平台禁止删除操作',
            '智能安全检查'
        ]
    }

@mcp.tool()
def check_provider_availability(provider_name: str) -> Dict:
    """
    检查特定云服务提供商的可用性
    
    Args:
        provider_name (str): 提供商名称 ('aws', 'digitalocean', 'vultr', 'alibaba')
        
    Returns:
        Dict: 提供商可用性信息
    """
    if provider_name not in PROVIDERS:
        return {
            'error': f'不支持的提供商: {provider_name}',
            'supported_providers': list(PROVIDERS.keys())
        }
    
    provider = PROVIDERS[provider_name]
    provider_info = get_cloud_provider_info(provider_name)
    
    # 检查必要的环境变量
    required_env_vars = {
        'aws': ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'],
        'digitalocean': ['DIGITALOCEAN_TOKEN'],
        'vultr': ['VULTR_API_KEY'],
        'alibaba': ['ALIBABA_CLOUD_ACCESS_KEY_ID', 'ALIBABA_CLOUD_ACCESS_KEY_SECRET']
    }
    
    env_status = {}
    if provider_name in required_env_vars:
        for env_var in required_env_vars[provider_name]:
            env_status[env_var] = bool(os.getenv(env_var))
    
    return {
        'provider': provider_name,
        'provider_info': provider_info,
        'available': getattr(provider, 'available', False),
        'error': getattr(provider, 'error', None),
        'environment_variables': env_status,
        'all_env_vars_set': all(env_status.values()) if env_status else False
    }

@mcp.tool()
def get_system_status() -> Dict:
    """
    获取整个系统的状态概览
    
    Returns:
        Dict: 系统状态信息
    """
    provider_status = {}
    available_count = 0
    
    for provider_name, provider in PROVIDERS.items():
        is_available = getattr(provider, 'available', False)
        provider_status[provider_name] = {
            'available': is_available,
            'error': getattr(provider, 'error', None) if not is_available else None
        }
        if is_available:
            available_count += 1
    
    return {
        'system_status': 'operational' if available_count > 0 else 'limited',
        'total_providers': len(PROVIDERS),
        'available_providers': available_count,
        'provider_status': provider_status,
        'ip_detection_enabled': bool(IPINFO_API_TOKEN),
        'security_features_enabled': True,
        'version': '2.0.0',
        'capabilities': {
            'aws': '只读查询',
            'digitalocean': '查询和电源管理',
            'vultr': '查询和电源管理', 
            'alibaba': '查询和电源管理'
        }
    }

def main():
    """主函数"""
    print("🚀 多云服务器管理系统启动中...")
    print("=" * 60)
    
    # 检查各提供商状态
    provider_status = {}
    for name, provider in PROVIDERS.items():
        status = "✅ 可用" if getattr(provider, 'available', False) else "❌ 不可用"
        error = getattr(provider, 'error', '')
        provider_status[name] = f"{status} {f'({error})' if error else ''}"
        print(f"{name.upper():>12}: {provider_status[name]}")
    
    print(f"{'IP检测':>12}: {'✅ 可用' if IPINFO_API_TOKEN else '❌ 未配置'}")
    print("=" * 60)
    
    available_count = sum(1 for provider in PROVIDERS.values() if getattr(provider, 'available', False))
    print(f"系统状态: {available_count}/{len(PROVIDERS)} 个提供商可用")
    
    if available_count == 0:
        print("\n⚠️  警告: 没有可用的云服务提供商！")
        print("请检查环境变量配置:")
        print("- AWS: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("- DigitalOcean: DIGITALOCEAN_TOKEN")
        print("- Vultr: VULTR_API_KEY")
        print("- 阿里云: ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    
    print("\n💡 系统特性:")
    print("- 🔍 智能IP检测和提供商路由")
    print("- 🛡️  三重确认安全机制")
    print("- 🔒 AWS只读权限")
    print("- ⛔ 禁止删除操作")
    print("- 🌐 多云平台统一管理")
    
    print("\n✅ 多云服务器管理系统已就绪！")

if __name__ == "__main__":
    main()
