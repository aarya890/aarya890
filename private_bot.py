import telebot
import sqlite3

# Bot token
TOKEN = "7302209243:AAFR4Zc-tQe9WHO6MpR8Z6BkXKP5GqWmNp0"
bot = telebot.TeleBot(TOKEN)

# Command: Start
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Add Registration Code", "View All Codes")
    markup.row("View User Logs")
    bot.send_message(message.chat.id, "Welcome, Admin! Choose an option:", reply_markup=markup)

# Add Registration Code
@bot.message_handler(func=lambda msg: msg.text == "Add Registration Code")
def add_code(message):
    bot.send_message(message.chat.id, "Enter the registration code:")
    bot.register_next_step_handler(message, get_code)

def get_code(message):
    code = message.text
    bot.send_message(message.chat.id, "Enter the link associated with this code:")
    bot.register_next_step_handler(message, save_code, code)

def save_code(message, code):
    link = message.text
    conn = sqlite3.connect('telegram_system.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO codes (code, link) VALUES (?, ?)", (code, link))
        conn.commit()
        bot.send_message(message.chat.id, f"Registration code '{code}' added successfully with the link: {link}")
    except sqlite3.IntegrityError:
        bot.send_message(message.chat.id, "This code already exists! Try a different code.")
    conn.close()

# View All Codes
@bot.message_handler(func=lambda msg: msg.text == "View All Codes")
def view_codes(message):
    conn = sqlite3.connect('telegram_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT code, link FROM codes")
    data = cursor.fetchall()
    if data:
        codes_list = "\n".join([f"Code: {code}, Link: {link}" for code, link in data])
        bot.send_message(message.chat.id, f"Here are all active codes:\n{codes_list}")
    else:
        bot.send_message(message.chat.id, "No registration codes found.")
    conn.close()

# View User Logs
@bot.message_handler(func=lambda msg: msg.text == "View User Logs")
def view_logs(message):
    conn = sqlite3.connect('telegram_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, registration_code, access_count FROM users")
    data = cursor.fetchall()
    if data:
        logs_list = "\n".join([f"User: {username}, Code: {code}, Accesses: {access_count}" for username, code, access_count in data])
        bot.send_message(message.chat.id, f"User Logs:\n{logs_list}")
    else:
        bot.send_message(message.chat.id, "No user activity found.")
    conn.close()

# Notify Admin When User Completes Limit
def notify_admin(username, link):
    message = f"🚨 User '{username}' has accessed the link 9 times and has been removed.\nLink: {link}"
   7103674778, message)  # Replace ADMIN_CHAT_ID with your Telegram ID.

bot.polling()