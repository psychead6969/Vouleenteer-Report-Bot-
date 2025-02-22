from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import json
import datetime

# Load or Initialize Data
try:
    with open("reports.json", "r") as file:
        user_reports = json.load(file)
except FileNotFoundError:
    user_reports = {}

# Admin IDs (Replace with actual Telegram Admin IDs)
ADMIN_IDS = [123456789, 987654321]

# Password
PASSWORD = "Titan@psychead"

# Multi-language support
LANGUAGES = {
    "en": {
        "select_lang": "🌍 Select your language:",
        "welcome": "👋 Hello {}, welcome to the Titan Volunteer Report Bot!\n📅 Submit your daily report to secure your contributions.",
        "password_prompt": "🔑 Enter Password:\n💡 You can find it in Titan International Department or ask your country mod.",
        "incorrect_password": "❌ Incorrect password! Try again.",
        "role_prompt": "✅ Correct Password! Choose your role:",
        "volunteer_menu": "👷 Volunteer Menu:",
        "submit_report": "⌛ Enter your working hours (e.g., 3h 20m):",
        "already_reported": "⚠️ You have already submitted a report today!",
        "job_prompt": "📝 What jobs have you done today? Describe briefly:",
        "extra_work": "📌 Any extra activities?",
        "extra_prompt": "✅ Extra Activity Selected: {}\n📎 Provide link/details:",
        "report_submitted": "✅ Report Submitted!\n📌 Come back tomorrow to submit again.",
        "admin_menu": "🛠 Admin Menu:",
        "not_admin": "❌ You are not an admin.",
        "all_reports": "📊 All Reports:\n",
        "no_reports": "No reports found.",
        "points_prompt": "📌 Select Role for Point Calculation:",
        "points_calculated": "📈 Points Calculation:\n",
        "reports_deleted": "🗑 All reports deleted!",
    },
    "cn": {
        "select_lang": "🌍 选择你的语言:",
        "welcome": "👋 你好 {}，欢迎来到 Titan 志愿者报告机器人！\n📅 提交您的每日报告以确保您的贡献。",
        "password_prompt": "🔑 输入密码:\n💡 你可以在 Titan International Department 找到密码，或询问你的国家管理员。",
        "incorrect_password": "❌ 密码错误！请再试一次。",
        "role_prompt": "✅ 密码正确！请选择您的角色:",
        "volunteer_menu": "👷 志愿者菜单:",
        "submit_report": "⌛ 请输入您的工作时间 (例如: 3h 20m):",
        "already_reported": "⚠️ 您今天已经提交了报告！",
        "job_prompt": "📝 今天你做了什么工作？请简要描述:",
        "extra_work": "📌 任何额外活动？",
        "extra_prompt": "✅ 选择的额外活动: {}\n📎 提供链接/详细信息:",
        "report_submitted": "✅ 报告已提交！\n📌 明天再来提交。",
        "admin_menu": "🛠 管理菜单:",
        "not_admin": "❌ 你不是管理员。",
        "all_reports": "📊 所有报告:\n",
        "no_reports": "未找到报告。",
        "points_prompt": "📌 选择角色进行积分计算:",
        "points_calculated": "📈 积分计算:\n",
        "reports_deleted": "🗑 所有报告已删除！",
    },
}

# Start Command
def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
                 InlineKeyboardButton("🇨🇳 中文", callback_data="lang_cn")]]
    update.message.reply_text("🌍 Select your language | 选择你的语言:", reply_markup=InlineKeyboardMarkup(keyboard))

# Language Selection
def set_language(update: Update, context: CallbackContext):
    query = update.callback_query
    lang_code = query.data.split("_")[1]
    context.user_data["language"] = lang_code
    lang = LANGUAGES[lang_code]

    first_name = query.from_user.first_name
    query.edit_message_text(lang["welcome"].format(first_name))
    
    keyboard = [[InlineKeyboardButton("👷 Volunteer", callback_data="volunteer"),
                 InlineKeyboardButton("👮 Admin", callback_data="admin")]]
    query.message.reply_text(lang["role_prompt"], reply_markup=InlineKeyboardMarkup(keyboard))

# Role Selection
def check_role(update: Update, context: CallbackContext):
    query = update.callback_query
    lang = LANGUAGES[context.user_data["language"]]

    if query.data == "volunteer":
        volunteer_menu(update, context)
    elif query.data == "admin":
        if query.from_user.id not in ADMIN_IDS:
            query.message.reply_text(lang["not_admin"])
        else:
            admin_menu(update, context)

# Volunteer Menu
def volunteer_menu(update: Update, context: CallbackContext):
    lang = LANGUAGES[context.user_data["language"]]
    keyboard = [[InlineKeyboardButton("📩 Submit Report", callback_data="submit_report")]]
    update.callback_query.message.reply_text(lang["volunteer_menu"], reply_markup=InlineKeyboardMarkup(keyboard))

# Submit Report
def submit_report(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    today = str(datetime.date.today())
    lang = LANGUAGES[context.user_data["language"]]

    if user_id in user_reports and user_reports[user_id].get("date") == today:
        update.callback_query.message.reply_text(lang["already_reported"])
        return

    update.callback_query.message.reply_text(lang["submit_report"])
    context.user_data["step"] = "working_hours"

def receive_hours(update: Update, context: CallbackContext):
    if context.user_data.get("step") != "working_hours":
        return
    
    context.user_data["working_hours"] = update.message.text
    lang = LANGUAGES[context.user_data["language"]]
    update.message.reply_text(lang["job_prompt"])
    context.user_data["step"] = "job_description"

def receive_job_description(update: Update, context: CallbackContext):
    context.user_data["job_description"] = update.message.text
    lang = LANGUAGES[context.user_data["language"]]
    keyboard = [[InlineKeyboardButton("📹 Video", callback_data="extra_video"),
                 InlineKeyboardButton("🐞 Bug", callback_data="extra_bug")]]
    update.message.reply_text(lang["extra_work"], reply_markup=InlineKeyboardMarkup(keyboard))
    context.user_data["step"] = "extra_work"

def receive_extra_details(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    today = str(datetime.date.today())
    lang = LANGUAGES[context.user_data["language"]]

    user_reports[user_id] = {
        "date": today,
        "name": update.message.from_user.first_name,
        "working_hours": context.user_data["working_hours"],
        "job_description": context.user_data["job_description"],
    }

    with open("reports.json", "w") as file:
        json.dump(user_reports, file)

    update.message.reply_text(lang["report_submitted"])
    context.user_data.clear()

# Telegram Bot Setup
updater = Updater("")
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(set_language, pattern="lang_"))
dp.add_handler(CallbackQueryHandler(check_role, pattern="volunteer|admin"))
dp.add_handler(CallbackQueryHandler(submit_report, pattern="submit_report"))
dp.add_handler(MessageHandler(Filters.text, receive_hours))

updater.start_polling()
