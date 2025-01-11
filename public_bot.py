import telebot
import sqlite3
import random
import string

# Bot token
TOKEN = "7479437712:AAFKmI9jF5P9OSYkL8FvdkLg1PKhHih54jI"
bot = telebot.TeleBot(TOKEN)

# Generate a secure random password
def generate_password():
    while True:
        password = ''.join(random.choices(
            string.ascii_letters + string.digits + "!@#$%^&*", k=9))
        if (any(c.isupper() for c in password) and
                any(c.islower() for c in password) and
                any(c.isdigit() for c in password)):
            return password

# Command: Start
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Login", "New User")
    bot.send_message(message.chat.id, "Welcome! Choose an option:", reply_markup=markup)

# New User Registration
@bot.message_handler(func=lambda msg: msg.text == "New User")
def new_user(message):
    bot.send_message(message.chat.id, "Enter your registration code:")
    bot.register_next_step_handler(message, validate_code)

def validate_code(message):
    code = message.text
    conn = sqlite3.connect('telegram_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM codes WHERE code=?", (code,))
    data = cursor.fetchone()
    if data:
        link = data[0]
        bot.send_message(message.chat.id, "Code verified! Now, set your username:")
        bot.register_next_step_handler(message, set_username, code, link)
    else:
        bot.send_message(message.chat.id, "Invalid code! Please check with the seller.")
    conn.close()

def set_username(message, code, link):
    username = message.text
    conn = sqlite3.connect('telegram_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        bot.send_message(message.chat.id, "Username already exists! Try another.")
        bot.register_next_step_handler(message, set_username, code, link)
    else:
        password = generate_password()
        cursor.execute("INSERT INTO users (username, password, registration_code, access_count) VALUES (?, ?, ?, 0)",
                       (username, password, code))
        conn.commit()
        bot.send_message(message.chat.id, f"Registration successful!\nYour Username: {username}\nYour Password: {password}\nYou can access your link up to 9 times.")
        conn.close()

# Login
@bot.message_handler(func=lambda msg: msg.text == "Login")
def login(message):
    bot.send_message(message.chat.id, "Enter your username:")
    bot.register_next_step_handler(message, validate_login)

def validate_login(message):
    username = message.text
    conn = sqlite3.connect('telegram_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password, registration_code, access_count FROM users WHERE username=?", (username,))
    data = cursor.fetchone()
    if data:
        password, code, access_count = data
        bot.send_message(message.chat.id, "Enter your password:")
        bot.register_next_step_handler(message, verify_password, username, password, code, access_count)
    else:
        bot.send_message(message.chat.id, "Invalid username! Try again.")
    conn.close()

def verify_password(message, username, password, code, access_count):
    if message.text == password:
        if access_count < 9:
            conn = sqlite3.connect('telegram_system.db')
            cursor = conn.cursor()
            cursor.execute("SELECT link FROM codes WHERE code=?", (code,))
            link = cursor.fetchone()[0]
            cursor.execute("UPDATE users SET access_count = access_count + 1 WHERE username=?", (username,))
            conn.commit()
            bot.send_message(message.chat.id, f"Access granted! Here is your link: {link}\nYou have {9 - (access_count + 1)} accesses left.")
            conn.close()
        else:
            bot.send_message(message.chat.id, "Access limit reached! Contact the seller.")
            conn = sqlite3.connect('telegram_system.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            conn.close()
    else:
        bot.send_message(message.chat.id, "Invalid password! Try again.")

# Notify the admin about the user
from private_bot import notify_admin
notify_admin(username, link)

bot.polling()