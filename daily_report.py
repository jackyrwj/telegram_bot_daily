import asyncio
import os
import requests
import random
from datetime import datetime, timedelta
from telegram import Bot
from telegram.constants import ParseMode
import json

# --- 配置 ---
BOT_TOKEN = os.getenv('BOT_TOKEN', "8226079704:AAHuBWHZphave2xwU_A6ELI3M3IsZOfwZQ4")
CHAT_ID = os.getenv('CHAT_ID', "-1002587693096")
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')  # 可选：用于访问 GitHub API
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', '')  # 你的 GitHub 用户名

class DailyReportGenerator:
    def __init__(self):
        self.current_time = datetime.now()
        self.start_of_year = datetime(self.current_time.year, 1, 1)
        
    def get_time_stats(self):
        """获取时间统计信息"""
        # 计算今天是今年的第几天
        day_of_year = (self.current_time - self.start_of_year).days + 1
        total_days = 366 if self.current_time.year % 4 == 0 else 365
        
        # 计算年度进度百分比
        progress_percent = (day_of_year / total_days) * 100
        
        # 创建进度条
        filled_blocks = int(progress_percent / 5)  # 每5%一个块
        progress_bar = "█" * filled_blocks + "░" * (20 - filled_blocks)
        
        return {
            'wake_time': self.current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'day_of_year': day_of_year,
            'total_days': total_days,
            'progress_percent': round(progress_percent, 1),
            'progress_bar': progress_bar
        }
    
    async def get_github_activity(self):
        """获取 GitHub 活动信息"""
        if not GITHUB_USERNAME:
            return {"prs": [], "issues": [], "commits": []}
            
        try:
            headers = {}
            if GITHUB_TOKEN:
                headers['Authorization'] = f'token {GITHUB_TOKEN}'
            
            # 获取最近的事件
            events_url = f"https://api.github.com/users/{GITHUB_USERNAME}/events"
            response = requests.get(events_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return {"prs": [], "issues": [], "commits": []}
            
            events = response.json()
            yesterday = self.current_time - timedelta(days=1)
            
            github_activity = {"prs": [], "issues": [], "commits": []}
            
            for event in events[:20]:  # 只看最近20个事件
                event_date = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                if event_date.date() == yesterday.date():
                    if event['type'] == 'PullRequestEvent':
                        pr_info = {
                            'action': event['payload']['action'],
                            'title': event['payload']['pull_request']['title'],
                            'repo': event['repo']['name']
                        }
                        github_activity['prs'].append(pr_info)
                    elif event['type'] == 'IssuesEvent':
                        issue_info = {
                            'action': event['payload']['action'],
                            'title': event['payload']['issue']['title'],
                            'repo': event['repo']['name']
                        }
                        github_activity['issues'].append(issue_info)
                    elif event['type'] == 'PushEvent':
                        commits = event['payload']['commits']
                        for commit in commits:
                            commit_info = {
                                'message': commit['message'],
                                'repo': event['repo']['name']
                            }
                            github_activity['commits'].append(commit_info)
            
            return github_activity
            
        except Exception as e:
            print(f"获取 GitHub 活动失败: {e}")
            return {"prs": [], "issues": [], "commits": []}
    
    def get_running_stats(self):
        """获取跑步统计（示例数据，可以接入真实的运动 API）"""
        # 这里使用示例数据，你可以接入 Strava、Nike Run Club 等 API
        return {
            'yesterday': False,  # 昨天是否跑步
            'month_distance': round(random.uniform(40, 80), 1),  # 本月跑步距离
            'year_distance': round(random.uniform(800, 1200), 2),  # 今年跑步距离
        }
    
    def get_daily_poem(self):
        """获取每日诗词"""
        poems = [
            {"content": "携壶酌流霞，搴菊泛寒荣。", "author": "李白", "title": "九日龙山饮"},
            {"content": "山重水复疑无路，柳暗花明又一村。", "author": "陆游", "title": "游山西村"},
            {"content": "海内存知己，天涯若比邻。", "author": "王勃", "title": "送杜少府之任蜀州"},
            {"content": "落红不是无情物，化作春泥更护花。", "author": "龚自珍", "title": "己亥杂诗"},
            {"content": "会当凌绝顶，一览众山小。", "author": "杜甫", "title": "望岳"},
            {"content": "长风破浪会有时，直挂云帆济沧海。", "author": "李白", "title": "行路难"},
            {"content": "问君能有几多愁，恰似一江春水向东流。", "author": "李煜", "title": "虞美人"},
            {"content": "春花秋月何时了，往事知多少。", "author": "李煜", "title": "虞美人"},
            {"content": "但愿人长久，千里共婵娟。", "author": "苏轼", "title": "水调歌头"},
            {"content": "人生如梦，一尊还酹江月。", "author": "苏轼", "title": "念奴娇·赤壁怀古"},
        ]
        return random.choice(poems)
    
    async def generate_report(self):
        """生成完整的日报"""
        time_stats = self.get_time_stats()
        github_activity = await self.get_github_activity()
        running_stats = self.get_running_stats()
        poem = self.get_daily_poem()
        
        # 构建报告文本
        report = f"<b>📅 今日日报</b>\n\n"
        
        # 时间信息
        report += f"今天的起床时间是--{time_stats['wake_time']}。\n\n"
        report += "起床啦。\n\n"
        report += f"今天是今年的第 {time_stats['day_of_year']} 天。\n\n"
        report += f"<code>{time_stats['progress_bar']}</code> {time_stats['progress_percent']}% ({time_stats['day_of_year']}/{time_stats['total_days']})\n\n"
        
        # GitHub 活动
        report += "<b>📊 GitHub：</b>\n\n"
        if github_activity['prs'] or github_activity['issues'] or github_activity['commits']:
            for pr in github_activity['prs']:
                action_text = "创建了" if pr['action'] == 'opened' else "更新了"
                report += f"• {action_text} PR: {pr['title']} ({pr['repo']})\n"
            
            for issue in github_activity['issues']:
                action_text = "创建了" if issue['action'] == 'opened' else "更新了"
                report += f"• {action_text} Issue: {issue['title']} ({issue['repo']})\n"
            
            for commit in github_activity['commits'][:3]:  # 最多显示3个提交
                report += f"• 提交了: {commit['message'][:50]}... ({commit['repo']})\n"
        else:
            report += "• 昨天没有 GitHub 活动\n"
        
        report += "\n"
        
        # 跑步统计
        report += "<b>🏃 Run：</b>\n\n"
        if not running_stats['yesterday']:
            report += "• 昨天没跑\n"
        else:
            report += "• 昨天跑了步 ✅\n"
        
        report += f"• 本月跑了 {running_stats['month_distance']} 公里\n"
        report += f"• 今年跑了 {running_stats['year_distance']} 公里\n\n"
        
        # 每日诗词
        report += "<b>📜 今天的一句诗:</b>\n\n"
        report += f"<i>{poem['content']}</i>\n"
        report += f"—— {poem['author']}《{poem['title']}》"
        
        return report

async def send_daily_report():
    """发送日报"""
    bot = Bot(token=BOT_TOKEN)
    
    try:
        # 生成日报
        generator = DailyReportGenerator()
        report = await generator.generate_report()
        
        # 发送消息
        await bot.send_message(
            chat_id=CHAT_ID,
            text=report,
            parse_mode=ParseMode.HTML
        )
        
        print("✅ 日报发送成功！")
        
    except Exception as e:
        print(f"❌ 日报发送失败: {e}")
        # 发送错误通知
        try:
            error_msg = f"⚠️ 日报生成失败\n错误信息: {str(e)}"
            await bot.send_message(chat_id=CHAT_ID, text=error_msg)
        except:
            pass

if __name__ == '__main__':
    asyncio.run(send_daily_report())
