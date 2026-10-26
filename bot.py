import telebot
from telebot import types
import requests

TOKEN = '8708639454:AAHeYbnnaKwp8X-mACK9yeCnl-5CkPah2KU'
ADMIN_ID = 8938159425
URL = "https://gntoxiukufrrvmpgmksi.supabase.co/rest/v1/profiles"
KEY = "sb_secret_yc5CaF393DDzeI7DdnyjxA_6ChphlK1"

bot = telebot.TeleBot(TOKEN)
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

def get_user(t_id):
    r = requests.get(f"{URL}?telegram_id=eq.{t_id}", headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        return data[0] if data else None
    return None

def get_all():
    r = requests.get(f"{URL}?select=telegram_id,first_name", headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        return data if isinstance(data, list) else []
    return []

@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id != ADMIN_ID: 
        return bot.send_message(m.chat.id, "Доступ запрещен")
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("Пользователи", callback_data="select_user"), types.InlineKeyboardButton("Рассылка", callback_data="broadcast"))
    bot.send_message(m.chat.id, "Админ-панель YouXGram", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "select_user")
def show_users(c):
    if c.from_user.id != ADMIN_ID: return
    r = requests.get(f"{URL}?select=telegram_id,first_name", headers=HEADERS)
    if r.status_code != 200:
        return bot.edit_message_text(f"Ошибка базы: {r.text}", c.message.chat.id, c.message.message_id)
    
    users = r.json()
    if not isinstance(users, list):
        return bot.edit_message_text(f"Странный ответ базы: {users}", c.message.chat.id, c.message.message_id)
        
    if not users: 
        return bot.edit_message_text("В базе нет пользователей", c.message.chat.id, c.message.message_id)
        
    markup = types.InlineKeyboardMarkup(row_width=1)
    for u in users:
        f_name = u.get('first_name') or "Без имени"
        t_id = u.get('telegram_id')
        if t_id:
            markup.add(types.InlineKeyboardButton(f"{f_name} ({t_id})", callback_data=f"user_{t_id}"))
    
    markup.add(types.InlineKeyboardButton("Назад", callback_data="back_to_main"))
    bot.edit_message_text("Выбери пользователя:", c.message.chat.id, c.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("user_"))
def user_menu(c):
    if c.from_user.id != ADMIN_ID: return
    t_id = c.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("Звезды", callback_data=f"act_stars_{t_id}"), types.InlineKeyboardButton("Ранг", callback_data=f"act_rank_{t_id}"), types.InlineKeyboardButton("Подарок", callback_data=f"act_gift_{t_id}"), types.InlineKeyboardButton("Привилегии", callback_data=f"act_priv_{t_id}"), types.InlineKeyboardButton("Инфо", callback_data=f"act_info_{t_id}"), types.InlineKeyboardButton("Бан", callback_data=f"act_ban_{t_id}"), types.InlineKeyboardButton("Назад", callback_data="select_user"))
    bot.edit_message_text(f"Пользователь: {t_id}\nЧто делаем?", c.message.chat.id, c.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("act_stars_"))
def ask_stars(c):
    if c.from_user.id != ADMIN_ID: return
    t_id = c.data.split("_")[2]
    msg = bot.send_message(c.message.chat.id, f"Сколько звезд выдать {t_id}?")
    bot.register_next_step_handler(msg, process_stars, t_id)

def process_stars(m, t_id):
    try:
        amount = int(m.text)
        user = get_user(t_id)
        if user:
            new_s = user.get('stars', 0) + amount
            requests.patch(f"{URL}?telegram_id=eq.{t_id}", headers=HEADERS, json={"stars": new_s})
            bot.send_message(m.chat.id, f"Выдано {amount} звезд")
    except: bot.send_message(m.chat.id, "Ошибка")

@bot.callback_query_handler(func=lambda c: c.data.startswith("act_rank_"))
def ask_rank(c):
    if c.from_user.id != ADMIN_ID: return
    t_id = c.data.split("_")[2]
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(types.InlineKeyboardButton("Dev", callback_data=f"setrank_dev_{t_id}"), types.InlineKeyboardButton("Admin", callback_data=f"setrank_admin_{t_id}"), types.InlineKeyboardButton("Стажер", callback_data=f"setrank_trainee_{t_id}"))
    bot.send_message(c.message.chat.id, f"Выбери ранг:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("setrank_"))
def process_rank(c):
    if c.from_user.id != ADMIN_ID: return
    _, r_name, t_id = c.data.split("_")
    requests.patch(f"{URL}?telegram_id=eq.{t_id}", headers=HEADERS, json={"rank": r_name})
    bot.edit_message_text(f"Выдан ранг {r_name}", c.message.chat.id, c.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("act_gift_"))
def ask_gift(c):
    if c.from_user.id != ADMIN_ID: return
    t_id = c.data.split("_")[2]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("Мишка", callback_data=f"setgift_bear_{t_id}"), types.InlineKeyboardButton("Роза", callback_data=f"setgift_rose_{t_id}"), types.InlineKeyboardButton("Корона", callback_data=f"setgift_crown_{t_id}"), types.InlineKeyboardButton("Алмаз", callback_data=f"setgift_diamond_{t_id}"))
    bot.send_message(c.message.chat.id, "Выбери подарок:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("setgift_"))
def process_gift(c):
    if c.from_user.id != ADMIN_ID: return
    _, g_name, t_id = c.data.split("_")
    user = get_user(t_id)
    if user:
        gifts = user.get('gifts') or []
        gifts.append(g_name)
        requests.patch(f"{URL}?telegram_id=eq.{t_id}", headers=HEADERS, json={"gifts": gifts})
        bot.edit_message_text(f"Подарок {g_name} отправлен!", c.message.chat.id, c.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("act_priv_"))
def ask_priv(c):
    if c.from_user.id != ADMIN_ID: return
    t_id = c.data.split("_")[2]
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(types.InlineKeyboardButton("VIP", callback_data=f"setpriv_vip_{t_id}"), types.InlineKeyboardButton("Premium", callback_data=f"setpriv_premium_{t_id}"), types.InlineKeyboardButton("Бета", callback_data=f"setpriv_beta_{t_id}"))
    bot.send_message(c.message.chat.id, "Выбери привилегию:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("setpriv_"))
def process_priv(c):
    if c.from_user.id != ADMIN_ID: return
    _, p_name, t_id = c.data.split("_")
    user = get_user(t_id)
    if user:
        privs = user.get('privileges') or []
        if p_name not in privs:
            privs.append(p_name)
            requests.patch(f"{URL}?telegram_id=eq.{t_id}", headers=HEADERS, json={"privileges": privs})
            bot.edit_message_text(f"Привилегия {p_name} выдана!", c.message.chat.id, c.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("act_info_"))
def show_info(c):
    if c.from_user.id != ADMIN_ID: return
    t_id = c.data.split("_")[2]
    user = get_user(t_id)
    if user:
        txt = f"Имя: {user.get('first_name')}\nID: {user.get('telegram_id')}\nЗвезды: {user.get('stars',0)}\nРанг: {user.get('rank','trainee')}\nПривилегии: {', '.join(user.get('privileges') or ['Нет'])}\nПодарки: {', '.join(user.get('gifts') or ['Нет'])}\nБан: {'Да' if user.get('is_banned') else 'Нет'}"
        bot.send_message(c.message.chat.id, txt)

@bot.callback_query_handler(func=lambda c: c.data.startswith("act_ban_"))
def toggle_ban(c):
    if c.from_user.id != ADMIN_ID: return
    t_id = c.data.split("_")[2]
    user = get_user(t_id)
    if user:
        new_b = not user.get('is_banned', False)
        requests.patch(f"{URL}?telegram_id=eq.{t_id}", headers=HEADERS, json={"is_banned": new_b})
        bot.edit_message_text(f"Пользователь {t_id}: {'ЗАБАНЕН' if new_b else 'РАЗБАНЕН'}", c.message.chat.id, c.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data == "broadcast")
def start_bcast(c):
    if c.from_user.id != ADMIN_ID: return
    msg = bot.send_message(c.message.chat.id, "Введи текст для рассылки:")
    bot.register_next_step_handler(msg, process_bcast)

def process_bcast(m):
    if m.from_user.id != ADMIN_ID: return
    users = get_all()
    count = 0
    for u in users:
        try:
            bot.send_message(u['telegram_id'], f"Объявление: {m.text}")
            count += 1
        except: pass
    bot.send_message(m.chat.id, f"Рассылка: {count} чел.")

@bot.callback_query_handler(func=lambda c: c.data == "back_to_main")
def back_to_main(c):
    if c.from_user.id != ADMIN_ID: return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("Пользователи", callback_data="select_user"), types.InlineKeyboardButton("Рассылка", callback_data="broadcast"))
    bot.edit_message_text("Админ-панель YouXGram", c.message.chat.id, c.message.message_id, reply_markup=markup)

print("Бот запущен...")
bot.infinity_polling()
