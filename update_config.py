#!/usr/bin/env python3
"""
配置更新脚本
用于更新运动数据和其他配置信息
"""

import json
import os
from datetime import datetime

def load_config():
    """加载当前配置"""
    config_path = 'config.json'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "running": {
                "month_distance": 0,
                "year_distance": 0,
                "last_run_date": "2025-01-01",
                "weekly_goal": 20,
                "monthly_goal": 80,
                "yearly_goal": 1000
            },
            "github": {
                "username": ""
            },
            "wake_time": {
                "target": "06:00",
                "actual": "06:00:00"
            }
        }

def save_config(config):
    """保存配置"""
    config_path = 'config.json'
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"✅ 配置已保存到 {config_path}")

def update_running_data():
    """更新跑步数据"""
    config = load_config()
    
    print("🏃 更新跑步数据")
    print("=" * 30)
    
    # 显示当前数据
    running = config['running']
    print(f"当前本月距离: {running['month_distance']} km")
    print(f"当前本年距离: {running['year_distance']} km") 
    print(f"上次跑步日期: {running['last_run_date']}")
    print()
    
    # 更新数据
    try:
        month_dist = input(f"输入本月跑步距离 (当前: {running['month_distance']} km): ").strip()
        if month_dist:
            running['month_distance'] = float(month_dist)
        
        year_dist = input(f"输入本年跑步距离 (当前: {running['year_distance']} km): ").strip()
        if year_dist:
            running['year_distance'] = float(year_dist)
        
        last_run = input(f"输入最后跑步日期 YYYY-MM-DD (当前: {running['last_run_date']}): ").strip()
        if last_run:
            # 验证日期格式
            datetime.strptime(last_run, '%Y-%m-%d')
            running['last_run_date'] = last_run
        
        config['running'] = running
        save_config(config)
        
    except ValueError as e:
        print(f"❌ 输入格式错误: {e}")
    except KeyboardInterrupt:
        print("\n操作已取消")

def update_github_username():
    """更新 GitHub 用户名"""
    config = load_config()
    
    print("📊 更新 GitHub 配置")
    print("=" * 30)
    
    current_username = config.get('github', {}).get('username', '')
    print(f"当前 GitHub 用户名: {current_username}")
    
    new_username = input("输入 GitHub 用户名: ").strip()
    if new_username:
        if 'github' not in config:
            config['github'] = {}
        config['github']['username'] = new_username
        save_config(config)

def show_current_config():
    """显示当前配置"""
    config = load_config()
    
    print("📋 当前配置")
    print("=" * 30)
    print(json.dumps(config, ensure_ascii=False, indent=2))

def main():
    """主菜单"""
    while True:
        print("\n🔧 配置管理工具")
        print("=" * 30)
        print("1. 更新跑步数据")
        print("2. 更新 GitHub 用户名")
        print("3. 显示当前配置")
        print("4. 退出")
        
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == '1':
            update_running_data()
        elif choice == '2':
            update_github_username()
        elif choice == '3':
            show_current_config()
        elif choice == '4':
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重试")

if __name__ == '__main__':
    main()
