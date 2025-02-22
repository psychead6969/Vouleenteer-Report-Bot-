import json
import os
from datetime import datetime, date
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler
)
--------------------------

Configuration and Globals

--------------------------

TOKEN = "7796539888:AAGAtFvOJgx-4YFQsWWLL6eliUQOEj2CcMw"  # Replace with your bot token DATA_FILE = "reports.json"

Pre-approved admin Telegram user IDs

ADMIN_IDS = [123456789, 6733652838]  # Replace with actual admin IDs

Make sure data file exists

if not os.path.exists(DATA_FILE): with open(DATA_FILE, "w") as file: json.dump({}, file)

def load_data(): with open(DATA_FILE, "r") as file: return json.load(file)

def save_data(data): with open(DATA_FILE, "w") as file: json.dump(data, file, indent=4)

--------------------------

Conversation States

--------------------------

LANG_SELECT, PASSWORD, ROLE_SELECT, VOL_ACTION, REPORT_HOURS, REPORT_JOBS, REPORT_EXTRA, REPORT_EXTRA_DETAILS, ADMIN_ACTION, ADMIN_VIEW_USER, ADMIN_CALC, ADMIN_GETDATA, ADMIN_DELETE = range(13)

--------------------------

Language Dictionaries

--------------------------

MESSAGES = { "en": { "welcome": "Welcome {first_name} to the Titan volunteer report bot. The bot records your daily reports—please submit your report daily to secure your contributions towards Titan network.", "password_prompt": "Please enter the password. (You can find it in Titan international department or ask your country mod.)", "password_incorrect": "Incorrect password. Please try again.", "role_prompt": "Please select your role:", "role_volunteer": "Volunteer", "role_admin": "Admin", "vol_menu": "Hi {first_name}, please choose an option:", "vol_what_can_i_do": "What can I do?", "vol_submit_report": "Submit Report", "what_can_i_do_text": ( "📣 To all international volunteers – The TITAN warriors\n\n" "🔥 Wish you a productive and successful day at work!\n\n" "1️⃣ User Support:\n" "⭐ Respond to user messages promptly.\n" "⚠️ Report negative messages and ban violators.\n" "🌐 Assist with troubleshooting.\n\n" "2️⃣ Bug Collection:\n" "🚨 Report all bugs found by users; tag the admins.\n" "🛡 Participate in testing new versions.\n\n" "3️⃣ Content Development:\n" "✍️ Create content related to DEPIN and Titan Network.\n" "🏅 Earn extra points for high-quality content.\n\n" "4️⃣ Contact Local KOLs:\n" "🤝 Engage with key influencers in your area.\n" "🎯 Earn additional points for valuable collaborations.\n\n" "5️⃣ Send Daily Reports:\n" "👨‍💻 Submit your daily work report and confirm extra points." ), "enter_hours": "Please enter your working hours for today (e.g., '2 30' for 2 hours 30 minutes):", "enter_jobs": "Please briefly describe what jobs you have completed today:", "choose_extra": "Select any extra activity you did today:", "extra_options": ["Video Creation", "Bug Collection", "Article Writing", "Other", "None"], "enter_extra_details": "Please provide details or a link for your extra activity:", "report_submitted": "Your report has been submitted:\n{report}\nCome back tomorrow to submit your report again.", "report_already": "You have already submitted a report for today.", "admin_menu": "Hello Admin {first_name}, please choose an admin option:", "admin_view": "View Reports (by user)", "admin_calc": "Calculate Points", "admin_getdata": "Get Data List", "admin_delete": "Delete All Data", "enter_user_for_view": "Please enter the Telegram user ID of the user to view reports:", "no_reports": "No reports found for that user.", "report_list": "Reports for user {user}:\n{reports}", "enter_hours_for_calc": "Please enter the total working hours (in minutes) to calculate points:", "choose_role_for_calc": "Select the role for coefficient calculation:", "coeff_options": ["Volunteer (10)", "Pioneer (15)", "Mod (20)"], "points_result": "Calculated points: {points}", "data_list": "All Users Data:\n{data}", "data_deleted": "All report data has been deleted.", "invalid_input": "Invalid input, please try again.", "not_admin": "Sorry, you are not authorized to use admin features." }, "zh": { "welcome": "欢迎 {first_name} 使用 Titan 志愿者日报机器人。该机器人会记录您的每日报告——请务必每天提交报告，以确保您在 Titan 网络中的贡献。", "password_prompt": "请输入密码。（您可以在 Titan 国际部门找到，或询问您的国家管理员。）", "password_incorrect": "密码错误，请重试。", "role_prompt": "请选择您的角色：", "role_volunteer": "志愿者", "role_admin": "管理员", "vol_menu": "嗨 {first_name}，请选择一个选项：", "vol_what_can_i_do": "我可以做什么？", "vol_submit_report": "提交报告", "what_can_i_do_text": ( "📣 致所有国际志愿者 —— TITAN 勇士们\n\n" "🔥 祝您工作顺利、成果丰硕！\n\n" "1️⃣ 用户支持：\n" "⭐ 及时回复用户消息。\n" "⚠️ 举报负面消息，并封禁违规用户。\n" "🌐 协助解决用户遇到的问题。\n\n" "2️⃣ Bug 收集：\n" "🚨 收集用户反馈的所有 bug，并@管理员。\n" "🛡 参与新版本测试，发现 bug 可获奖励积分。\n\n" "3️⃣ 内容开发：\n" "✍️ 创作与 DEPIN 和 Titan 网络相关的内容。\n" "🏅 优质内容可获得额外积分。\n\n" "4️⃣ 联系本地 KOL：\n" "🤝 主动联系您所在地区的意见领袖，推广 Titan 网络。\n" "🎯 有价值的合作可获得额外积分。\n\n" "5️⃣ 提交日报：\n" "👨‍💻 提交您的每日工作报告，并确认额外积分。" ), "enter_hours": "请输入您今天的工作时长（例如，输入“2 30”代表2小时30分钟）：", "enter_jobs": "请简要描述您今天完成的工作内容：", "choose_extra": "请选择今天额外完成的任务：", "extra_options": ["视频制作", "Bug 收集", "文章编写", "其他", "无"], "enter_extra_details": "请提供额外任务的详细说明或链接：", "report_submitted": "您的报告已提交：\n{report}\n请明天再来提交新的报告。", "report_already": "您今天的报告已提交。", "admin_menu": "管理员 {first_name}，请选择一个管理选项：", "admin_view": "查看报告（按用户）", "admin_calc": "计算积分", "admin_getdata": "获取用户数据列表", "admin_delete": "删除所有数据", "enter_user_for_view": "请输入要查看报告的用户的 Telegram ID：", "no_reports": "未找到该用户的报告。", "report_list": "用户 {user} 的报告：\n{reports}", "enter_hours_for_calc": "请输入总工作时长（以分钟为单位）以计算积分：", "choose_role_for_calc": "请选择用于计算系数的角色：", "coeff_options": ["志愿者 (10)", "先锋 (15)", "管理员 (20)"], "points_result": "计算得到的积分：{points}", "data_list": "所有用户数据：\n{data}", "data_deleted": "所有报告数据已删除。", "invalid_input": "输入无效，请重试。", "not_admin": "抱歉，您无权使用管理员功能。" } }

--------------------------

Helper Functions

--------------------------

def get_message(context: CallbackContext, key: str) -> str: lang = context.user_data.get("lang", "en") return MESSAGES[lang][key]

def get_extra_options(context: CallbackContext): lang = context.user_data.get("lang", "en") return MESSAGES[lang]["extra_options"]

--------------------------

Command and Conversation Handlers

--------------------------

def start(update: Update, context: CallbackContext) -> int: # Ask for language selection keyboard = [ [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"), InlineKeyboardButton("中文 🇨🇳", callback_data="lang_zh")] ] update.message.reply_text("Please select your language / 请选择语言:", reply_markup=InlineKeyboardMarkup(keyboard)) return LANG_SELECT

def language_select(update: Update, context: CallbackContext) -> int: query = update.callback_query query.answer() lang = "en" if query.data == "lang_en" else "zh" context.user_data["lang"] = lang

# Proceed to ask for password
query.edit_message_text(text=MESSAGES[lang]["password_prompt"])
return PASSWORD

def password_input(update: Update, context: CallbackContext) -> int: user_pass = update.message.text.strip() lang = context.user_data.get("lang", "en") if user_pass != "Titan@psychead": update.message.reply_text(MESSAGES[lang]["password_incorrect"]) return PASSWORD # Password correct, now greet the user and ask for role selection first_name = update.effective_user.first_name welcome_text = MESSAGES[lang]["welcome"].format(first_name=first_name) update.message.reply_text(welcome_text) # Role selection buttons keyboard = [ [InlineKeyboardButton(MESSAGES[lang]["role_volunteer"], callback_data="role_volunteer")], [InlineKeyboardButton(MESSAGES[lang]["role_admin"], callback_data="role_admin")] ] update.message.reply_text(MESSAGES[lang]["role_prompt"], reply_markup=InlineKeyboardMarkup(keyboard)) return ROLE_SELECT

def role_select(update: Update, context: CallbackContext) -> int: query = update.callback_query query.answer() role = query.data lang = context.user_data.get("lang", "en") context.user_data["role"] = role

if role == "role_admin":
    # Check if user is an admin
    if update.effective_user.id not in ADMIN_IDS:
        query.edit_message_text(MESSAGES[lang]["not_admin"])
        return ConversationHandler.END
    # Admin Menu
    keyboard = [
        [InlineKeyboardButton(MESSAGES[lang]["admin_view"], callback_data="admin_view")],
        [InlineKeyboardButton(MESSAGES[lang]["admin_calc"], callback_data="admin_calc")],
        [InlineKeyboardButton(MESSAGES[lang]["admin_getdata"], callback_data="admin_getdata")],
        [InlineKeyboardButton(MESSAGES[lang]["admin_delete"], callback_data="admin_delete")]
    ]
    query.edit_message_text(MESSAGES[lang]["admin_menu"].format(first_name=update.effective_user.first_name),
                            reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_ACTION
else:
    # Volunteer Menu
    keyboard = [
        [InlineKeyboardButton(MESSAGES[lang]["vol_what_can_i_do"], callback_data="vol_what_can_i_do")],
        [InlineKeyboardButton(MESSAGES[lang]["vol_submit_report"], callback_data="vol_submit_report")]
    ]
    query.edit_message_text(MESSAGES[lang]["vol_menu"].format(first_name=update.effective_user.first_name),
                            reply_markup=InlineKeyboardMarkup(keyboard))
    return VOL_ACTION

---------- Volunteer Handlers ----------

def volunteer_action(update: Update, context: CallbackContext) -> int: query = update.callback_query query.answer() lang = context.user_data.get("lang", "en") action = query.data

if action == "vol_what_can_i_do":
    # Send what-can-I-do text
    query.edit_message_text(MESSAGES[lang]["what_can_i_do_text"])
    # Show volunteer menu again
    keyboard = [
        [InlineKeyboardButton(MESSAGES[lang]["vol_what_can_i_do"], callback_data="vol_what_can_i_do")],
        [InlineKeyboardButton(MESSAGES[lang]["vol_submit_report"], callback_data="vol_submit_report")]
    ]
    query.message.reply_text(MESSAGES[lang]["vol_menu"].format(first_name=update.effective_user.first_name),
                               reply_markup=InlineKeyboardMarkup(keyboard))
    return VOL_ACTION

elif action == "vol_submit_report":
    # Check if a report for today already exists
    data = load_data()
    uid = str(update.effective_user.id)
    today = date.today().isoformat()
    if uid in data and today in data[uid]:
        query.edit_message_text(MESSAGES[lang]["report_already"])
        return ConversationHandler.END
    query.edit_message_text(MESSAGES[lang]["enter_hours"])
    return REPORT_HOURS

def report_hours(update: Update, context: CallbackContext) -> int: lang = context.user_data.get("lang", "en") text = update.message.text.strip() try: parts = text.split() if len(parts) != 2: raise ValueError hours = int(parts[0]) minutes = int(parts[1]) total_minutes = hours * 60 + minutes context.user_data["working_minutes"] = total_minutes except Exception: update.message.reply_text(MESSAGES[lang]["invalid_input"]) return REPORT_HOURS

update.message.reply_text(MESSAGES[lang]["enter_jobs"])
return REPORT_JOBS

def report_jobs(update: Update, context: CallbackContext) -> int: lang = context.user_data.get("lang", "en") context.user_data["jobs"] = update.message.text.strip() # Ask for extra activity using inline buttons extra_options = get_extra_options(context) keyboard = [[InlineKeyboardButton(option, callback_data=option)] for option in extra_options] update.message.reply_text(MESSAGES[lang]["choose_extra"], reply_markup=InlineKeyboardMarkup(keyboard)) return REPORT_EXTRA

def report_extra(update: Update, context: CallbackContext) -> int: query = update.callback_query query.answer() lang = context.user_data.get("lang", "en") extra_choice = query.data context.user_data["extra"] = extra_choice if extra_choice.lower() in ["none", "无"]: # No extra details needed, finish report return finish_report(update, context) else: query.edit_message_text(MESSAGES[lang]["enter_extra_details"]) return REPORT_EXTRA_DETAILS

def report_extra_details(update: Update, context: CallbackContext) -> int: context.user_data["extra_details"] = update.message.text.strip() return finish_report(update, context)

def finish_report(update: Update, context: CallbackContext) -> int: lang = context.user_data.get("lang", "en") uid = str(update.effective_user.id) today = date.today().isoformat() first_name = update.effective_user.first_name working_minutes = context.user_data.get("working_minutes", 0) jobs = context.user_data.get("jobs", "") extra = context.user_data.get("extra", "") extra_details = context.user_data.get("extra_details", "")

# Create report text
hours = working_minutes // 60
minutes = working_minutes % 60
report_text = (f"Name: {first_name}\nDate: {today}\nWorking Hours: {hours}h {minutes}m\n"
               f"Jobs: {jobs}\nExtra Activity: {extra}")
if extra.lower() not in ["none", "无"] and extra_details:
    report_text += f"\nExtra Details: {extra_details}"

# Save report in JSON
data = load_data()
if uid not in data:
    data[uid] = {}
data[uid][today] = {
    "first_name": first_name,
    "working_minutes": working_minutes,
    "jobs": jobs,
    "extra": extra,
    "extra_details": extra_details,
    "timestamp": datetime.now().isoformat()
}
save_data(data)

update.message.reply_text(MESSAGES[lang]["report_submitted"].format(report=report_text))
return ConversationHandler.END

---------- Admin Handlers ----------

def admin_action(update: Update, context: CallbackContext) -> int: query = update.callback_query query.answer() lang = context.user_data.get("lang", "en") action = query.data

if action == "admin_view":
    query.edit_message_text(MESSAGES[lang]["enter_user_for_view"])
    return ADMIN_VIEW_USER
elif action == "admin_calc":
    query.edit_message_text(MESSAGES[lang]["enter_hours_for_calc"])
    return ADMIN_CALC
elif action == "admin_getdata":
    data = load_data()
    # Aggregate data: list each user's total working minutes and calculated points assuming volunteer coefficient (10)
    result = ""
    for uid, reports in data.items():
        total_minutes = sum(report["working_minutes"] for report in reports.values())
        total_hours = total_minutes / 60
        points = total_hours * 10  # default volunteer coefficient
        first_name = list(reports.values())[0].get("first_name", "Unknown")
        result += f"{first_name} (ID: {uid}): {total_hours:.2f} hrs, {points:.2f} pts\n"
    if not result:
        result = MESSAGES[lang]["no_reports"]
    query.edit_message_text(MESSAGES[lang]["data_list"].format(data=result))
    return ConversationHandler.END
elif action == "admin_delete":
    # Delete all data
    save_data({})
    query.edit_message_text(MESSAGES[lang]["data_deleted"])
    return ConversationHandler.END
else:
    query.edit_message_text(MESSAGES[lang]["invalid_input"])
    return ADMIN_ACTION

def admin_view_user(update: Update, context: CallbackContext) -> int: lang = context.user_data.get("lang", "en") user_id = update.message.text.strip() data = load_data() if user_id not in data: update.message.reply_text(MESSAGES[lang]["no_reports"]) return ConversationHandler.END else: report_lines = "" for report_date, report in data[user_id].items(): hours = report["working_minutes"] // 60 minutes = report["working_minutes"] % 60 report_lines += f"Date: {report_date} - {report['first_name']} worked {hours}h {minutes}m, Jobs: {report['jobs']}\n" update.message.reply_text(MESSAGES[lang]["report_list"].format(user=user_id, reports=report_lines)) return ConversationHandler.END

def admin_calc(update: Update, context: CallbackContext) -> int: lang = context.user_data.get("lang", "en") try: total_minutes = int(update.message.text.strip()) except Exception: update.message.reply_text(MESSAGES[lang]["invalid_input"]) return ADMIN_CALC context.user_data["calc_minutes"] = total_minutes # Ask for coefficient selection keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in MESSAGES[lang]["coeff_options"]] update.message.reply_text(MESSAGES[lang]["choose_role_for_calc"], reply_markup=InlineKeyboardMarkup(keyboard)) return ADMIN_ACTION  # reuse ADMIN_ACTION to capture coefficient callback

def admin_coeff_choice(update: Update, context: CallbackContext) -> int: query = update.callback_query query.answer() lang = context.user_data.get("lang", "en") choice = query.data coeff = 10  # default for volunteer if "Pioneer" in choice or "先锋" in choice: coeff = 15 elif "Mod" in choice or "管理员" in choice: coeff = 20 total_minutes = context.user_data.get("calc_minutes", 0) total_hours = total_minutes / 60 points = total_hours * coeff query.edit_message_text(MESSAGES[lang]["points_result"].format(points=points)) return ConversationHandler.END

---------- Cancel Handler ----------

def cancel(update: Update, context: CallbackContext) -> int: update.message.reply_text('Cancelled.', reply_markup=ReplyKeyboardRemove()) return ConversationHandler.END

--------------------------

Main Function

--------------------------

def main(): updater = Updater(TOKEN, use_context=True) dispatcher = updater.dispatcher

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        LANG_SELECT: [CallbackQueryHandler(language_select)],
        PASSWORD: [MessageHandler(Filters.text & ~Filters.command, password_input)],
        ROLE_SELECT: [CallbackQueryHandler(role_select)],
        VOL_ACTION: [CallbackQueryHandler(volunteer_action)],
        REPORT_HOURS: [MessageHandler(Filters.text & ~Filters.command, report_hours)],
        REPORT_JOBS: [MessageHandler(Filters.text & ~Filters.command, report_jobs)],
        REPORT_EXTRA: [CallbackQueryHandler(report_extra)],
        REPORT_EXTRA_DETAILS: [MessageHandler(Filters.text & ~Filters.command, report_extra_details)],
        ADMIN_ACTION: [
            CallbackQueryHandler(admin_action),
            CallbackQueryHandler(admin_coeff_

Give it full like this

