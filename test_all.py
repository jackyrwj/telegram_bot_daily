#!/usr/bin/env python3
"""
测试脚本 - 验证所有功能
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(__file__))

async def test_basic_bot():
    """测试基本的 Bot 连接"""
    print("🤖 测试 Bot 连接...")
    try:
        from telegram import Bot
        
        bot_token = os.getenv('BOT_TOKEN', "8226079704:AAHuBWHZphave2xwU_A6ELI3M3IsZOfwZQ4")
        bot = Bot(token=bot_token)
        
        bot_info = await bot.get_me()
        print(f"✅ Bot 连接成功: {bot_info.first_name} (@{bot_info.username})")
        return True
        
    except Exception as e:
        print(f"❌ Bot 连接失败: {e}")
        return False

def test_config_file():
    """测试配置文件"""
    print("\n📁 测试配置文件...")
    
    try:
        config_path = 'config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ 配置文件读取成功")
            print(f"   GitHub 用户名: {config.get('github', {}).get('username', '未设置')}")
            print(f"   本月跑步: {config.get('running', {}).get('month_distance', 0)} km")
            return True
        else:
            print("⚠️ 配置文件不存在，将使用默认配置")
            return True
            
    except Exception as e:
        print(f"❌ 配置文件错误: {e}")
        return False

async def test_github_api():
    """测试 GitHub API"""
    print("\n📊 测试 GitHub API...")
    
    try:
        import requests
        
        username = os.getenv('GH_USERNAME', '')
        if not username:
            # 尝试从配置文件读取
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    username = config.get('github', {}).get('username', '')
            except:
                pass
        
        if not username:
            print("⚠️ 未设置 GitHub 用户名，跳过测试")
            return True
        
        headers = {'User-Agent': 'Daily-Report-Bot'}
        github_token = os.getenv('GITHUB_TOKEN', '')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        url = f"https://api.github.com/users/{username}/events"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            events = response.json()
            print(f"✅ GitHub API 连接成功，获取到 {len(events)} 个事件")
            return True
        else:
            print(f"⚠️ GitHub API 返回状态码: {response.status_code}")
            if response.status_code == 403:
                print("   可能是 API 限制，建议设置 GITHUB_TOKEN")
            return True
            
    except Exception as e:
        print(f"❌ GitHub API 测试失败: {e}")
        return False

async def test_report_generation():
    """测试报告生成"""
    print("\n📋 测试报告生成...")
    
    try:
        from advanced_report import DailyReportGenerator
        
        generator = DailyReportGenerator()
        report = await generator.generate_report()
        
        if report and len(report) > 100:
            print("✅ 报告生成成功")
            print(f"   报告长度: {len(report)} 字符")
            
            # 显示报告预览
            preview = report.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '').replace('<code>', '').replace('</code>', '')
            lines = preview.split('\n')[:10]
            print("   报告预览:")
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            if len(preview.split('\n')) > 10:
                print("   ...")
            
            return True
        else:
            print("❌ 报告生成失败或内容为空")
            return False
            
    except Exception as e:
        print(f"❌ 报告生成测试失败: {e}")
        return False

async def test_send_report():
    """测试发送报告（可选）"""
    print("\n📤 测试发送报告...")
    
    chat_id = os.getenv('CHAT_ID', '')
    if not chat_id:
        print("⚠️ 未设置 CHAT_ID，跳过发送测试")
        return True
    
    response = input("是否发送测试报告到 Telegram？(y/N): ").strip().lower()
    if response == 'y':
        try:
            from advanced_report import send_daily_report
            await send_daily_report()
            print("✅ 测试报告发送成功")
            return True
        except Exception as e:
            print(f"❌ 发送测试失败: {e}")
            return False
    else:
        print("⏭️ 跳过发送测试")
        return True

async def main():
    """主测试函数"""
    print("🧪 Telegram 日报机器人 - 功能测试")
    print("=" * 50)
    
    test_results = []
    
    # 基本连接测试
    result1 = await test_basic_bot()
    test_results.append(("Bot 连接", result1))
    
    # 配置文件测试
    result2 = test_config_file()
    test_results.append(("配置文件", result2))
    
    # GitHub API 测试
    result3 = await test_github_api()
    test_results.append(("GitHub API", result3))
    
    # 报告生成测试
    result4 = await test_report_generation()
    test_results.append(("报告生成", result4))
    
    # 发送测试（可选）
    result5 = await test_send_report()
    test_results.append(("发送测试", result5))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    total = 0
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
        total += 1
    
    print(f"\n🎯 测试完成: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 所有测试通过！机器人已准备就绪。")
    else:
        print("⚠️ 部分测试失败，请检查配置和网络连接。")
    
    print("\n💡 接下来你可以:")
    print("   1. 运行 'python update_config.py' 更新配置")
    print("   2. 运行 'python advanced_report.py' 发送完整日报")
    print("   3. 推送代码到 GitHub 启用自动化")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试已中断")
