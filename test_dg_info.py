#!/usr/bin/env python3
"""
测试DigitalOcean droplet管理功能的脚本
"""

import os
from main import (
    get_dg_info, 
    list_droplets, 
    find_droplet_by_name, 
    get_droplet_status, 
    power_on_droplet, 
    power_off_droplet, 
    shutdown_droplet, 
    reboot_droplet,
    get_droplet_actions,
    get_action_status,
    get_droplet_monitoring,
    delete_droplet_with_protection,
    get_droplet_deletion_policy,
    check_droplet_deletion_safety
)

def test_basic_functions():
    """测试基本功能"""
    
    print("=== DigitalOcean 基本功能测试 ===\n")
    
    # 检查环境变量
    do_token = os.getenv("DIGITALOCEAN_TOKEN")
    if not do_token:
        print("❌ 错误: 未设置DIGITALOCEAN_TOKEN环境变量")
        print("请设置您的DigitalOcean API令牌:")
        print("export DIGITALOCEAN_TOKEN=your_token_here")
        return
    
    print(f"✅ 找到DigitalOcean API令牌: {do_token[:10]}...")
    
    # 测试列出所有droplets
    print("\n🔍 测试列出所有droplets:")
    print("-" * 50)
    try:
        result = list_droplets()
        if result.get('error'):
            print(f"❌ 错误: {result.get('error')}")
        else:
            print(f"✅ 成功获取droplets列表")
            print(f"  总计droplets数量: {result.get('total_droplets', 0)}")
            
            droplets = result.get('droplets', [])
            for droplet in droplets[:3]:  # 只显示前3个
                print(f"  - ID: {droplet.get('id')}, 名称: {droplet.get('name')}, 状态: {droplet.get('status')}")
            
            if len(droplets) > 3:
                print(f"  ... 还有 {len(droplets) - 3} 个droplets")
                
    except Exception as e:
        print(f"❌ 测试列出droplets时发生异常: {str(e)}")

def test_droplet_operations():
    """测试droplet操作功能"""
    
    print("\n=== Droplet 操作功能测试 ===\n")
    
    # 获取用户输入的droplet ID或名称
    droplet_input = input("请输入要测试的droplet ID或名称 (回车跳过): ").strip()
    
    if not droplet_input:
        print("⏭️  跳过droplet操作测试")
        return
    
    droplet_id = None
    
    # 尝试将输入作为ID（数字）
    try:
        droplet_id = int(droplet_input)
        print(f"🎯 使用droplet ID: {droplet_id}")
    except ValueError:
        # 如果不是数字，则作为名称查找
        print(f"🔍 按名称查找droplet: {droplet_input}")
        try:
            result = find_droplet_by_name(droplet_input)
            if result.get('found') and result.get('droplets'):
                droplet = result['droplets'][0]  # 使用第一个匹配的droplet
                droplet_id = droplet.get('id')
                print(f"✅ 找到droplet: {droplet.get('name')} (ID: {droplet_id})")
            else:
                print(f"❌ 未找到名称为 '{droplet_input}' 的droplet")
                return
        except Exception as e:
            print(f"❌ 查找droplet时发生错误: {str(e)}")
            return
    
    if not droplet_id:
        print("❌ 无法确定droplet ID")
        return
    
    # 测试获取droplet状态
    print(f"\n📊 测试获取droplet状态 (ID: {droplet_id}):")
    print("-" * 50)
    try:
        result = get_droplet_status(droplet_id)
        if result.get('error'):
            print(f"❌ 错误: {result.get('error')}")
        else:
            print(f"✅ Droplet状态: {result.get('status')}")
            print(f"  名称: {result.get('name')}")
            print(f"  锁定状态: {result.get('locked')}")
            print(f"  规格: {result.get('size_slug')}")
            print(f"  区域: {result.get('region', {}).get('name')}")
    except Exception as e:
        print(f"❌ 获取droplet状态时发生异常: {str(e)}")
    
    # 测试获取操作历史
    print(f"\n📋 测试获取droplet操作历史 (ID: {droplet_id}):")
    print("-" * 50)
    try:
        result = get_droplet_actions(droplet_id)
        if result.get('error'):
            print(f"❌ 错误: {result.get('error')}")
        else:
            print(f"✅ 操作历史总数: {result.get('total_actions', 0)}")
            actions = result.get('actions', [])
            for action in actions[:5]:  # 只显示最近5个操作
                print(f"  - {action.get('type')}: {action.get('status')} ({action.get('started_at')})")
    except Exception as e:
        print(f"❌ 获取操作历史时发生异常: {str(e)}")
    
    # 询问是否要进行实际操作
    print(f"\n⚠️  注意: 以下操作会实际影响您的droplet!")
    perform_actions = input("是否要测试droplet操作功能？(y/N): ").strip().lower()
    
    if perform_actions in ['y', 'yes']:
        test_power_operations(droplet_id)
    else:
        print("⏭️  跳过droplet操作测试")

def test_power_operations(droplet_id):
    """测试电源操作功能"""
    
    print(f"\n⚡ 测试droplet电源操作 (ID: {droplet_id}):")
    print("-" * 50)
    
    # 获取当前状态
    status_result = get_droplet_status(droplet_id)
    current_status = status_result.get('status')
    print(f"当前状态: {current_status}")
    
    if current_status == "active":
        # 如果是活跃状态，测试重启
        print("🔄 测试重启droplet...")
        try:
            result = reboot_droplet(droplet_id)
            if result.get('error'):
                print(f"❌ 重启失败: {result.get('error')}")
            else:
                action_id = result.get('action', {}).get('id')
                print(f"✅ 重启操作已提交，操作ID: {action_id}")
                
                if action_id:
                    # 检查操作状态
                    print("⏳ 检查操作状态...")
                    status_result = get_action_status(action_id)
                    if not status_result.get('error'):
                        action_status = status_result.get('action', {}).get('status')
                        print(f"  操作状态: {action_status}")
        except Exception as e:
            print(f"❌ 重启操作异常: {str(e)}")
    
    elif current_status == "off":
        # 如果是关机状态，测试开机
        print("🟢 测试开启droplet...")
        try:
            result = power_on_droplet(droplet_id)
            if result.get('error'):
                print(f"❌ 开机失败: {result.get('error')}")
            else:
                action_id = result.get('action', {}).get('id')
                print(f"✅ 开机操作已提交，操作ID: {action_id}")
        except Exception as e:
            print(f"❌ 开机操作异常: {str(e)}")
    
    else:
        print(f"⚠️  Droplet当前状态为 '{current_status}'，跳过电源操作测试")

def test_monitoring():
    """测试监控功能"""
    
    print("\n=== Droplet 监控功能测试 ===\n")
    
    droplet_input = input("请输入要测试监控的droplet ID (回车跳过): ").strip()
    
    if not droplet_input:
        print("⏭️  跳过监控功能测试")
        return
    
    try:
        droplet_id = int(droplet_input)
    except ValueError:
        print("❌ 请输入有效的droplet ID")
        return
    
    print(f"📊 测试droplet监控功能 (ID: {droplet_id}):")
    print("-" * 50)
    
    try:
        result = get_droplet_monitoring(droplet_id)
        if result.get('error'):
            print(f"❌ 错误: {result.get('error')}")
        elif not result.get('monitoring_enabled'):
            print(f"⚠️  {result.get('message')}")
        else:
            print("✅ 监控功能已启用")
            metrics = result.get('metrics', {})
            
            for metric_type, metric_data in metrics.items():
                available = metric_data.get('available', False)
                status = "有数据" if available else "无数据"
                print(f"  {metric_type.upper()}: {status}")
            
            print(f"\n💡 {result.get('note')}")
    except Exception as e:
        print(f"❌ 测试监控功能时发生异常: {str(e)}")

def test_ip_lookup():
    """测试IP查找功能"""
    
    print("\n=== IP地址查找测试 ===\n")
    
    test_ip = input("请输入要查询的公网IP地址 (回车跳过): ").strip()
    
    if not test_ip:
        print("⏭️  跳过IP查找测试")
        return
    
    print(f"🔍 查找IP地址对应的droplet: {test_ip}")
    print("-" * 50)
    
    try:
        result = get_dg_info(test_ip)
        if result.get('error'):
            print(f"❌ 错误: {result.get('error')}")
        elif result.get('found'):
            print("✅ 找到匹配的droplet!")
            droplet_info = result.get('droplet_info', {})
            print(f"  名称: {droplet_info.get('name')}")
            print(f"  状态: {droplet_info.get('status')}")
            print(f"  ID: {droplet_info.get('id')}")
        else:
            print(f"❌ 未找到使用IP {test_ip} 的droplet")
    except Exception as e:
        print(f"❌ IP查找测试时发生异常: {str(e)}")

def test_deletion_protection():
    """测试删除保护功能"""
    
    print("\n=== Droplet 删除保护功能测试 ===\n")
    
    # 测试删除策略
    print("🔒 测试删除策略:")
    print("-" * 50)
    try:
        policy_result = get_droplet_deletion_policy()
        
        print("📋 当前删除策略:")
        deletion_policy = policy_result.get('deletion_policy', {})
        print(f"  启用状态: {'✅ 已启用' if deletion_policy.get('enabled') else '❌ 已禁用'}")
        print(f"  保护级别: {deletion_policy.get('protection_level')}")
        print(f"  当前状态: {deletion_policy.get('current_status')}")
        
        print(f"\n🛡️  安全检查项目:")
        for i, check in enumerate(deletion_policy.get('safety_checks', []), 1):
            print(f"  {i}. {check}")
        
        print(f"\n🏷️  保护标签:")
        protected_tags = deletion_policy.get('protected_tags', [])
        print(f"  {', '.join(protected_tags)}")
        
        security_info = policy_result.get('security_info', {})
        print(f"\n💡 安全理念: {security_info.get('philosophy')}")
        print(f"📚 建议: {security_info.get('recommendation')}")
        
    except Exception as e:
        print(f"❌ 测试删除策略时发生异常: {str(e)}")
    
    # 测试删除保护
    droplet_input = input("\n请输入要测试删除安全性的droplet ID (回车跳过): ").strip()
    
    if not droplet_input:
        print("⏭️  跳过删除安全性测试")
        return
    
    try:
        droplet_id = int(droplet_input)
    except ValueError:
        print("❌ 请输入有效的droplet ID")
        return
    
    # 测试安全检查
    print(f"\n🔍 测试droplet删除安全性 (ID: {droplet_id}):")
    print("-" * 50)
    try:
        safety_result = check_droplet_deletion_safety(droplet_id)
        
        if safety_result.get('error'):
            print(f"❌ 错误: {safety_result.get('error')}")
        else:
            print(f"📦 Droplet: {safety_result.get('droplet_name')}")
            print(f"🔒 总体安全等级: {safety_result.get('overall_safety')}")
            print(f"📊 安全状态: {safety_result.get('safety_level')}")
            
            # 显示安全检查结果
            print(f"\n✅ 安全检查结果:")
            safety_checks = safety_result.get('safety_checks', [])
            for check in safety_checks:
                status_icon = {"PASS": "✅", "WARNING": "⚠️", "BLOCKED": "❌"}.get(check['status'], "❓")
                print(f"  {status_icon} {check['check']}: {check['message']}")
            
            # 显示警告
            warnings = safety_result.get('warnings', [])
            if warnings:
                print(f"\n⚠️  警告信息:")
                for warning in warnings:
                    print(f"  - {warning}")
            
            # 显示统计
            summary = safety_result.get('summary', {})
            print(f"\n📊 检查统计:")
            print(f"  总计: {summary.get('total_checks')}")
            print(f"  通过: {summary.get('passed')}")
            print(f"  警告: {summary.get('warnings')}")
            print(f"  阻止: {summary.get('blocked')}")
            
            print(f"\n💡 {safety_result.get('note')}")
            
    except Exception as e:
        print(f"❌ 测试删除安全性时发生异常: {str(e)}")
    
    # 测试实际删除操作（应该被阻止）
    print(f"\n🚫 测试删除操作 (应该被保护机制阻止):")
    print("-" * 50)
    
    # 测试不带确认码的删除
    print("1. 测试不带确认码的删除:")
    try:
        result = delete_droplet_with_protection(droplet_id)
        
        if result.get('error'):
            print(f"   ✅ 正确阻止: {result.get('error')}")
            security_info = result.get('security_info', {})
            if security_info:
                print(f"   🔒 保护级别: {security_info.get('protection_level')}")
                print(f"   📝 原因: {security_info.get('reason')}")
        else:
            print(f"   ❌ 意外成功: {result}")
            
    except Exception as e:
        print(f"   ❌ 测试异常: {str(e)}")
    
    # 测试带错误确认码的删除
    print("\n2. 测试带错误确认码的删除:")
    try:
        result = delete_droplet_with_protection(droplet_id, "WRONG_CODE")
        
        if result.get('error'):
            print(f"   ✅ 正确阻止: {result.get('error')}")
            required = result.get('required_confirmation')
            if required:
                print(f"   📝 需要的确认码: {required}")
        else:
            print(f"   ❌ 意外成功: {result}")
            
    except Exception as e:
        print(f"   ❌ 测试异常: {str(e)}")
    
    # 测试带正确确认码的删除（仍应被其他保护机制阻止）
    print("\n3. 测试带正确确认码的删除 (仍应被保护):")
    try:
        result = delete_droplet_with_protection(droplet_id, "CONFIRM_DELETE_DROPLET")
        
        if result.get('error'):
            print(f"   ✅ 正确阻止: {result.get('error')}")
            
            # 显示详细的安全信息
            if result.get('droplet_info'):
                droplet_info = result['droplet_info']
                print(f"   📦 目标droplet: {droplet_info.get('name')} (状态: {droplet_info.get('status')})")
            
            if result.get('security_note'):
                print(f"   🔒 安全说明: {result.get('security_note')}")
            
            # 显示替代操作
            alternatives = result.get('alternative_actions', [])
            if alternatives:
                print(f"   💡 替代操作:")
                for alt in alternatives:
                    print(f"     - {alt}")
                    
        else:
            print(f"   ❌ 意外成功: {result}")
            
    except Exception as e:
        print(f"   ❌ 测试异常: {str(e)}")
    
    print(f"\n✅ 删除保护测试完成!")
    print("💡 所有删除操作都应该被安全机制正确阻止")

if __name__ == "__main__":
    print("🚀 DigitalOcean Droplet 管理功能测试")
    print("=" * 60)
    
    # 基本功能测试
    test_basic_functions()
    
    # Droplet操作测试
    test_droplet_operations()
    
    # 监控功能测试
    test_monitoring()
    
    # 删除保护功能测试
    test_deletion_protection()
    
    # IP查找测试
    test_ip_lookup()
    
    print("\n✅ 所有测试完成!")
    print("\n💡 提示:")
    print("- 确保在测试前设置了正确的DIGITALOCEAN_TOKEN环境变量")
    print("- 监控功能需要在droplet上启用监控选项")
    print("- 实际操作会影响您的droplet，请谨慎使用")
    print("- 删除功能被安全机制保护，防止意外删除重要服务器") 