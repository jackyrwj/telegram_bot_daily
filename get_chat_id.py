#!/usr/bin/env python3
"""
获取你的 Telegram Chat ID 的辅助脚本
使用方法：
1. 在 Telegram 中搜索你的 Bot 并发送 /start
2. 运行这个脚本来获取你的 Chat ID
"""

import asyncio
import os
from telegram import Bot

BOT_TOKEN = os.getenv('BOT_TOKEN', "8226079704:AAHuBWHZphave2xwU_A6ELI3M3IsZOfwZQ4")

async def get_updates():
    bot = Bot(token=BOT_TOKEN)
    
    try:
        print("正在获取最近的消息...")
        updates = await bot.get_updates()
        
        if not updates:
            print("❌ 没有找到任何消息！")
            print("请先在 Telegram 中：")
            print("1. 搜索你的 Bot: @Daily_report_robot")
            print("2. 点击 'START' 或发送 /start")
            print("3. 然后重新运行这个脚本")
            return
        
        print(f"✅ 找到 {len(updates)} 条消息")
        print("\n最近的对话:")
        print("-" * 50)
        
        for update in updates[-5:]:  # 显示最近5条消息
            if update.message:
                chat_id = update.message.chat.id
                username = update.message.from_user.username or "无用户名"
                first_name = update.message.from_user.first_name or "无姓名"
                text = update.message.text or "[非文本消息]"
                
                print(f"Chat ID: {chat_id}")
                print(f"用户: {first_name} (@{username})")
                print(f"消息: {text}")
                print(f"时间: {update.message.date}")
                print("-" * 30)
        
        # 获取最新消息的 Chat ID
        latest_chat_id = updates[-1].message.chat.id
        print(f"\n🎯 推荐使用的 Chat ID: {latest_chat_id}")
        print(f"请将 push.py 中的 YOUR_CHAT_ID 修改为: \"{latest_chat_id}\"")
        
    except Exception as e:
        print(f"❌ 获取消息失败: {e}")
    finally:
        # 不调用 close() 来避免 Flood control 问题
        pass

if __name__ == '__main__':
    asyncio.run(get_updates())
