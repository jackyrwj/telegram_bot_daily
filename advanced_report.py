import asyncio
import os
import requests
import random
import json
from datetime import datetime, timedelta
from telegram import Bot
from telegram.constants import ParseMode

# --- 配置 ---
BOT_TOKEN = os.getenv('BOT_TOKEN', "8226079704:AAHuBWHZphave2xwU_A6ELI3M3IsZOfwZQ4")
CHAT_ID = os.getenv('CHAT_ID', "-1002587693096")
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', '')

class DailyReportGenerator:
    def __init__(self):
        self.current_time = datetime.now()
        self.start_of_year = datetime(self.current_time.year, 1, 1)
        self.config = self.load_config()
        
    def load_config(self):
        """加载配置文件"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，返回默认配置
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
                    "username": GITHUB_USERNAME
                },
                "wake_time": {
                    "target": "06:00",
                    "actual": "06:00:00"
                }
            }
        
    def get_time_stats(self):
        """获取时间统计信息"""
        day_of_year = (self.current_time - self.start_of_year).days + 1
        total_days = 366 if self.current_time.year % 4 == 0 else 365
        progress_percent = (day_of_year / total_days) * 100
        
        # 创建进度条 (20个字符)
        filled_blocks = int(progress_percent / 5)
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
        username = GITHUB_USERNAME or self.config.get('github', {}).get('username', '')
        
        if not username:
            return {"prs": [], "issues": [], "commits": [], "stars": 0}
            
        try:
            headers = {'User-Agent': 'Daily-Report-Bot'}
            if GITHUB_TOKEN:
                headers['Authorization'] = f'token {GITHUB_TOKEN}'
            
            # 获取用户事件
            events_url = f"https://api.github.com/users/{username}/events"
            response = requests.get(events_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"GitHub API 返回状态码: {response.status_code}")
                return {"prs": [], "issues": [], "commits": [], "error": True}
            
            events = response.json()
            yesterday = self.current_time - timedelta(days=1)
            
            github_activity = {"prs": [], "issues": [], "commits": []}
            
            for event in events[:30]:  # 检查最近30个事件
                event_date = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                
                # 检查是否是昨天的活动
                if event_date.date() == yesterday.date():
                    if event['type'] == 'PullRequestEvent' and event['payload']['action'] in ['opened', 'closed']:
                        pr_info = {
                            'action': '创建了' if event['payload']['action'] == 'opened' else '合并了',
                            'title': event['payload']['pull_request']['title'],
                            'repo': event['repo']['name'],
                            'url': event['payload']['pull_request']['html_url']
                        }
                        github_activity['prs'].append(pr_info)
                        
                    elif event['type'] == 'IssuesEvent' and event['payload']['action'] == 'opened':
                        issue_info = {
                            'action': '创建了',
                            'title': event['payload']['issue']['title'],
                            'repo': event['repo']['name'],
                            'url': event['payload']['issue']['html_url']
                        }
                        github_activity['issues'].append(issue_info)
                        
                    elif event['type'] == 'PushEvent':
                        commits = event['payload']['commits']
                        for commit in commits[:2]:  # 最多2个提交
                            commit_info = {
                                'message': commit['message'].split('\n')[0][:60],  # 只取第一行，限制长度
                                'repo': event['repo']['name']
                            }
                            github_activity['commits'].append(commit_info)
            
            return github_activity
            
        except Exception as e:
            print(f"获取 GitHub 活动失败: {e}")
            return {"prs": [], "issues": [], "commits": [], "error": True}
    
    def get_running_stats(self):
        """获取跑步统计"""
        running_config = self.config.get('running', {})
        
        # 检查昨天是否跑步
        last_run = running_config.get('last_run_date', '2025-01-01')
        yesterday = (self.current_time - timedelta(days=1)).strftime('%Y-%m-%d')
        ran_yesterday = last_run == yesterday
        
        return {
            'yesterday': ran_yesterday,
            'month_distance': running_config.get('month_distance', 0),
            'year_distance': running_config.get('year_distance', 0),
            'monthly_goal': running_config.get('monthly_goal', 80),
            'yearly_goal': running_config.get('yearly_goal', 1000)
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
            {"content": "采菊东篱下，悠然见南山。", "author": "陶渊明", "title": "饮酒"},
            {"content": "不畏浮云遮望眼，自缘身在最高层。", "author": "王安石", "title": "登飞来峰"},
            {"content": "千里莺啼绿映红，水村山郭酒旗风。", "author": "杜牧", "title": "江南春"},
            {"content": "停车坐爱枫林晚，霜叶红于二月花。", "author": "杜牧", "title": "山行"},
        ]
        return random.choice(poems)
    
    async def generate_report(self):
        """生成完整的日报"""
        time_stats = self.get_time_stats()
        github_activity = await self.get_github_activity()
        running_stats = self.get_running_stats()
        poem = self.get_daily_poem()
        
        # 构建报告文本
        report = f"<b>📅 每日报告</b>\n\n"
        
        # 时间信息
        report += f"今天的起床时间是--{time_stats['wake_time']}。\n\n"
        report += "起床啦。\n\n"
        report += f"今天是今年的第 {time_stats['day_of_year']} 天。\n\n"
        report += f"<code>{time_stats['progress_bar']}</code> {time_stats['progress_percent']}% ({time_stats['day_of_year']}/{time_stats['total_days']})\n\n"
        
        # GitHub 活动
        report += "<b>GitHub：</b>\n\n"
        has_activity = False
        
        for pr in github_activity.get('prs', []):
            report += f"• {pr['action']} PR: {pr['title']} ({pr['repo']})\n"
            has_activity = True
        
        for issue in github_activity.get('issues', []):
            report += f"• {issue['action']} Issue: {issue['title']} ({issue['repo']})\n"
            has_activity = True
        
        for commit in github_activity.get('commits', []):
            report += f"• 提交了: {commit['message']} ({commit['repo']})\n"
            has_activity = True
        
        if not has_activity:
            if github_activity.get('error'):
                report += "• GitHub 数据获取失败\n"
            else:
                report += "• 昨天没有 GitHub 活动\n"
        
        report += "\n"
        
        # 跑步统计
        report += "<b>Run：</b>\n\n"
        if running_stats['yesterday']:
            report += "• 昨天跑了步 ✅\n"
        else:
            report += "• 昨天没跑\n"
        
        report += f"• 本月跑了 {running_stats['month_distance']} 公里\n"
        report += f"• 今年跑了 {running_stats['year_distance']} 公里\n\n"
        
        # 每日诗词
        report += "<b>今天的一句诗:</b>\n\n"
        report += f"<i>{poem['content']}</i>\n"
        if poem.get('author') and poem.get('title'):
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
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
        print("✅ 日报发送成功！")
        
    except Exception as e:
        print(f"❌ 日报发送失败: {e}")
        # 发送简化的错误通知
        try:
            error_msg = f"⚠️ 日报生成失败\n\n错误: {str(e)[:100]}"
            await bot.send_message(chat_id=CHAT_ID, text=error_msg)
        except:
            print("连错误通知都发送失败了")

# 兼容性：保持原有的简单推送功能
async def push_poem():
    """推送简单的古诗（向后兼容）"""
    await send_daily_report()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'simple':
        # python advanced_report.py simple - 发送简单版本
        asyncio.run(push_poem())
    else:
        # python advanced_report.py - 发送完整日报
        asyncio.run(send_daily_report())
