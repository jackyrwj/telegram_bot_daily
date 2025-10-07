import asyncio
from telegram import Bot
from telegram.constants import ParseMode
import requests
import random
import os
from datetime import datetime

# --- 配置 ---
# 从环境变量获取配置，如果没有则使用默认值（本地开发用）
BOT_TOKEN = os.getenv('BOT_TOKEN', "8226079704:AAHuBWHZphave2xwU_A6ELI3M3IsZOfwZQ4")
YOUR_CHAT_ID = os.getenv('CHAT_ID', "-1002587693096")

# --- 获取古诗的函数（示例：使用本地数据）---
def get_daily_poem():
    # 实际项目中，您应该调用 API 或读取文件
    poems = [
        {"title": "静夜思", "author": "李白", "content": "床前明月光，疑是地上霜。举头望明月，低头思故乡。", "analysis": "此诗表达了诗人对故乡的深切思念。通过月光和低头动作来渲染思乡之情，情景交融。"},
        # ... 更多古诗
    ]
    return random.choice(poems)

# --- 测试 Bot 连接的函数 ---
async def test_bot():
    bot = Bot(token=BOT_TOKEN)
    try:
        # 获取 bot 信息
        bot_info = await bot.get_me()
        print(f"Bot 连接成功: {bot_info.first_name} (@{bot_info.username})")
        
        # 测试发送简单消息
        test_message = "🤖 Bot 测试消息"
        await bot.send_message(chat_id=YOUR_CHAT_ID, text=test_message)
        print("测试消息发送成功！")
        
    except Exception as e:
        print(f"Bot 测试失败: {e}")
        return False
    finally:
        # 不调用 close() 来避免 Flood control 问题
        pass
    return True

# --- 推送消息的主函数 ---
async def push_poem():
    # 1. 初始化 Bot
    bot = Bot(token=BOT_TOKEN)
    
    try:
        # 2. 获取古诗数据
        data = get_daily_poem()
        
        # 3. 格式化推送文本 (使用 HTML 格式而不是 Markdown，更可靠)
        message = (
            f"📜 <b>每日古诗词</b> ({datetime.now().strftime('%Y-%m-%d')})\n\n"
            f"<b>《{data['title']}》</b>\n"
            f"作者：{data['author']}\n\n"
            f"<i>{data['content']}</i>\n\n"
            f"<b>解析</b>\n"
            f"{data['analysis']}"
        )

        # 4. 发送消息
        await bot.send_message(
            chat_id=YOUR_CHAT_ID, 
            text=message, 
            parse_mode=ParseMode.HTML
        )
        print("✅ 推送成功！")
        
    except Exception as e:
        print(f"❌ 推送失败: {e}")
    finally:
        # 不调用 close() 来避免 Flood control 问题
        pass

if __name__ == '__main__':
    import sys
    
    # 如果传入 'test' 参数，则运行测试
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        asyncio.run(test_bot())
    else:
        asyncio.run(push_poem())