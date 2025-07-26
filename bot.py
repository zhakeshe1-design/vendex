import telebot
import requests
import html

BOT_TOKEN = '8202062736:AAE1OPYkJzfRxFpsF5D0gp3DiDs92ruHJxM'
API_TOKEN = '31349d8b-ff7d-4827-939e-22cc01f066ef'

bot = telebot.TeleBot(BOT_TOKEN)

user_last_number = {}

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        "Привет!\n\nДля поиска введи:\n<code>/check номер</code>\nПример: <code>/check 79001234567</code>",
        parse_mode="HTML"
    )

@bot.message_handler(commands=['check'])
def check_number(message):
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "Формат: <code>/check номер</code>", parse_mode="HTML")
            return

        number = args[1]
        user_last_number[message.chat.id] = number  # сақтау
        url = f"https://chaos-api.lol/check?number={number}&token={API_TOKEN}"
        res = requests.get(url).json()

        if not res.get("found"):
            bot.send_message(message.chat.id, f"По номеру <code>{number}</code> ничего не найдено.", parse_mode="HTML")
            return

        reply = f"Найдено: <b>{res['found']}</b> записей по номеру <code>{number}</code>\n\n"
        for entry in res['results']:
            db_name = html.escape(entry['database'])
            reply += f"База: <code>{db_name}</code>\n"
            for line in entry['data']:
                safe_line = html.escape(line)
                reply += f"{safe_line}\n"
            reply += "\n"

        for i in range(0, len(reply), 4000):
            bot.send_message(message.chat.id, reply[i:i+4000], parse_mode="HTML")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {html.escape(str(e))}", parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_search_query(message):
    query = message.text.strip().lower()
    if len(query) < 3:
        return

    number = user_last_number.get(message.chat.id, "79001234567")
    url = f"https://chaos-api.lol/check?number={number}&token={API_TOKEN}"

    try:
        res = requests.get(url).json()
        if not res.get("results"):
            bot.reply_to(message, "Данных нет.")
            return

        matches = []
        for entry in res["results"]:
            for line in entry["data"]:
                if query in line.lower():
                    matches.append((entry["database"], line))

        if not matches:
            bot.send_message(message.chat.id, "Совпадений не найдено.")
            return

        reply = f"Совпадения по: <b>{html.escape(query)}</b>\n\n"
        for db, line in matches:
            reply += f"База: <b>{html.escape(db)}</b>\n{html.escape(line)}\n\n"

        for i in range(0, len(reply), 4000):
            bot.send_message(message.chat.id, reply[i:i+4000], parse_mode="HTML")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при поиске: {html.escape(str(e))}", parse_mode="HTML")

print("Бот запущен...")
bot.polling()
