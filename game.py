import re
import os
from asyncio import gather, get_event_loop, sleep

from aiohttp import ClientSession
from pyrogram import Client, filters, idle, compose
from Python_ARQ import ARQ
import requests
import random
from datetime import datetime, timedelta
import time
import atexit
import pytz
import threading
import asyncio
from pyrogram import filters
from pyrogram.types import ForceReply, Message, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, MessageEntity, ReplyKeyboardMarkup
from pyrogram.filters import command
from functions import (
    extract_user,
    extract_user_and_reason,
    time_converter,
)
from pyrogram.enums import MessageEntityType
#import telebot
#from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
#from telebot import TeleBot, types
from config import bot_token, bot_token2, bot_token3, group_id, group_id2, group_id3, admin_id, admin_id2, admin_id3, channel_id

#from pyromod import Client, Message, listen
from pyromod.exceptions import ListenerTimeout

is_config = os.path.exists("config.py")

if is_config:
    from config import *
else:
    from sample_config import *

Luna = Client(
    ":luna:",
    bot_token=bot_token,
)

bot_id = int(bot_token.split(":")[0])

bot = Client(
    ":taxu:",
    bot_token=bot_token2,
)

bot_id = int(bot_token.split(":")[0])


###############
luu_cau = {}
mo_game = {}
topdiem = {}

# Dictionary to store user bets
user_bets = {}
winner = {}

# Dictionary to store user balances
user_balance = {}

#########################
client = bot
bot_trangthai = {}
#################
user_state = {}
rut = {}
nap = {}
# Tạo từ điển lưu lịch sử cược và lịch sử rút tiền
# Tạo từ điển gitcodes
used_gitcodes = []
gitcode_amounts = {}
user_pending_gitcodes = {}
# Define a separate dictionary to track user game states
user_game_state = {}
# Dictionary to store user balances (user_id: balance)
user_balances = {}
# Dictionary to store user bets
####################################################################
# Add these variables for Gitcode handling
bot_FILE = "bot.txt"
# Function to create a Gitcode with a custom amount
def mo_bot(user_id):
    trangthai = "bot_game"
    if user_id in bot_trangthai:
        return
    if user_id not in bot_trangthai:
        bot_trangthai[user_id] = trangthai
        with open("bot.txt", "a") as f:
            f.write(f"{user_id} {trangthai}\n")
    

# Function to read Gitcodes from the file
def xem_bot():
    if os.path.exists("bot.txt"):
        with open("bot.txt", "r") as f:
            for line in f:
                user_id, trangthai  = line.strip().split()
                bot_trangthai[user_id] = trangthai

# Function to remove a used Gitcode
def xoa_grid(grid):
    with open(grid_FILE, "r") as f:
        lines = f.readlines()
    with open(grid_FILE, "w") as f:
        for line in lines:
            if not line.startswith(grid):
                f.write(line)


# Hàm để lưu tất cả số dư vào tệp văn bản
def save_balance_to_file():
    with open("id.txt", "w") as f:
        for user_id, balance in user_balance.items():
            f.write(f"{user_id} {balance}\n")

# Hàm để đọc số dư từ tệp văn bản và cập nhật vào từ điển user_balance
def load_balance_from_file():
    if os.path.exists("id.txt"):
        with open("id.txt", "r") as f:
            for line in f:
                user_id, balance_str = line.strip().split()
                balance = float(balance_str)
                if balance.is_integer():
                    balance = int(balance)
                user_balance[int(user_id)] = balance

def get_user_info(user_id):
  try:
    user = bot.get_chat(user_id)
    return user
  except Exception as e:
    print("Error fetching user info:", e)
    return None

#######################################################
load_balance_from_file()
# Function to send a dice and get its value
def send_dice(chat_id):
    response = requests.get(f'https://api.telegram.org/bot{bot_token}/sendDice?chat_id={chat_id}')
    #response = Luna.send_dice(chat_id, "🎲")
    if response.status_code == 200:
        data = response.json()
        if 'result' in data and 'dice' in data['result']:
            return data['result']['dice']['value']
    return None
    
# Hàm kiểm Tài/Xỉu
def calculate_tai_xiu(total_score):
  return "⚫️Tài" if 11 <= total_score <= 18 else "⚪️Xỉu"

@Luna.on_message(filters.command("tx"))
def start_taixiu(_, message: Message):
    xem_bot()
    chat_id = message.chat.id
    grid = chat_id
    if chat_id != group_id:
        return Luna.send_message(chat_id, "Vào nhóm t.me/sanhallwin để chơi GAME.")
    if len(mo_game) == 0:
        grtrangthai = 1
        game_timer(message, grid, grtrangthai)
        
    if len(mo_game) > 0 and mo_game[grid]['tthai'] == 2:
        return Luna.send_message(chat_id, "Đợi 10s để mở ván mới.")
        
    if len(mo_game) > 0 and mo_game[grid]['tthai'] == 1:
        total_bet_T = sum([user_bets[user_id]['T'] for user_id in user_bets])
        total_bet_X = sum([user_bets[user_id]['X'] for user_id in user_bets])
        nut = [
        [
            InlineKeyboardButton("Bot GAME", url="https://t.me/alltowin_bot?start=hi"),
            InlineKeyboardButton(" Bot Nạp - Rút", url="https://t.me/diemallwin_bot?start=hi"),
        ],
            [InlineKeyboardButton("Vào nhóm để chơi GAME", url="https://t.me/sanhallwin"),],]
        reply_markup = InlineKeyboardMarkup(nut)
        Luna.send_message(chat_id, f"Đang đợi đổ xúc xắc\n LƯU Ý : HÃY BẤM VÀO 2 NÚT BÊN DƯỚI, ĐỂ CÓ THỂ CHƠI GAME.", reply_markup=reply_markup)
        nut2 = [
        [
            InlineKeyboardButton("Soi cầu", url="https://t.me/kqtaixiu"),
            InlineKeyboardButton("Nạp - Rút", url="https://t.me/diemallwin_bot?start=hi"),
        ],]
        reply_markup2 = InlineKeyboardMarkup(nut2)
        Luna.send_message(group_id, f"""
┏ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
┣➤⚫️Tổng cược bên TÀI: {total_bet_T:,}đ
┣➤⚪️Tổng cược bên XỈU: {total_bet_X:,}đ
┗ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
""", reply_markup=reply_markup2)

    else: 
        mo_game.clear()

def game_timer(message, grid, grtrangthai):
    mo_game[grid] = {'tthai': 0}  # Initialize the user's bets if not already present
    mo_game[grid]['tthai'] += grtrangthai
    print(mo_game,1)
    nut = [
        [
            InlineKeyboardButton("Bot Nạp - Rút", url="https://t.me/diemallwin_bot?start=hi"),
            InlineKeyboardButton("Bot GAME", url="https://t.me/alltowin_bot?start=hi"),
        ],]
    reply_markup = InlineKeyboardMarkup(nut)
    text1 = Luna.send_message(group_id, "Bắt đầu ván mới! Có 90 giây để đặt cược\n LƯU Ý : HÃY BẤM VÀO 2 NÚT BÊN DƯỚI, ĐỂ CÓ THỂ CHƠI GAME.", reply_markup=reply_markup)
    time.sleep(30)
    text2 = Luna.send_message(group_id, "Còn 60s để đặt cược.")
    
    time.sleep(20)  # Wait for 120 seconds
    text3 = Luna.send_message(group_id, "Còn 40s để đặt cược.")
    Luna.delete_messages(grid, text2.id)

    time.sleep(30)  # Wait for 120 seconds
    text4 = Luna.send_message(group_id, "Còn 10s để đặt cược.")
    Luna.delete_messages(grid, text3.id)
    time.sleep(10)  # Wait for 120 seconds
    
    Luna.delete_messages(grid, text1.id)
    Luna.delete_messages(grid, text4.id)
    start_game(message, grid)

@Luna.on_message(filters.command(["t", "x"]) & filters.text)
def handle_message(_, message: Message):
    #load_balance_from_file()
    chat_id = message.chat.id
    user_id = message.from_user.id
    #user_id = Luna.get_users(from_user).id
    grid = chat_id
    xem_bot()
    if chat_id != group_id:
        return Luna.send_message(chat_id, "Vào nhóm t.me/sanhallwin để chơi GAME.")
    if user_id not in bot_trangthai:
        nut = [
        [
            InlineKeyboardButton("Bot Nạp - Rút", url="https://t.me/diemallwin_bot?start=hi"),
            InlineKeyboardButton("Bot GAME", url="https://t.me/alltowin_bot?start=hi"),
        ],]
        reply_markup = InlineKeyboardMarkup(nut)
        return Luna.send_message(chat_id, "Lỗi!!! Vui lòng bấm vào cả 2 nút bên dưới và thử lại.", reply_markup=reply_markup)
    if len(mo_game) > 0 and mo_game[grid]['tthai'] == 2:
        return Luna.send_message(chat_id, "Đợi 10s để đặt cược ván tiếp theo.")
    
    # Check if the message is from the group chat
    if chat_id == group_id:
        # Check if the message is a valid bet
        if message.text and message.text.upper() in ['/T ALL', '/X ALL'] or (message.text and message.text.upper()[1] in ['T', 'X'] and message.text[3:].isdigit()): 
            ten_ncuoc = message.from_user#.mention#first_name
            bet_type = message.text.upper()[1]
            if message.text.upper() == '/T ALL' or message.text.upper() == '/X ALL':
                bet_amount = user_balance.get(user_id, 0)  # Use the entire balance
            else:
                bet_amount = int(message.text[3:])
            # Confirm the bet and check user balance
            confirm_bet(user_id, bet_type, bet_amount, ten_ncuoc, message)
        else:
            Luna.send_message(chat_id, "Lệnh không hợp lệ. Vui lòng tuân thủ theo quy tắc cược.")
    if len(mo_game) == 0:
            grtrangthai = 1
            grid = chat_id
            game_timer(message, grid, grtrangthai)

    
              

# Function to confirm the bet and check user balance
def confirm_bet(user_id, bet_type, bet_amount, ten_ncuoc, message):
    #load_balance_from_file()
    if bet_type == 'T':
        cua_cuoc = '⚫️Tài'
    else:
        cua_cuoc = '⚪️Xỉu'
    diemcuoc = f"{ten_ncuoc.mention} đã cược {cua_cuoc} {bet_amount:,} điểm."
    
    # Check if the user_id is present in user_balance dictionary
    if user_id in user_balance:
        if bet_amount <= 0:
            Luna.send_message(user_id, "Bạn không đủ điểm để đặt cược, vui lòng nạp điểm.")
        # Check user balance
        if user_balance[user_id] >= bet_amount:
            try:
                if user_id in user_bets:
                    user_bets[user_id][bet_type] += bet_amount  
                else:
                    user_bets[user_id] = {'T': 0, 'X': 0}  # Initialize the user's bets if not already present
                    user_bets[user_id][bet_type] += bet_amount
                user_balance[user_id] -= bet_amount
                text = f"""{diemcuoc} \nCược đã được chấp nhận."""
                balance = user_balance.get(user_id, 0)
                text += f"Còn {balance:,} điểm"
                request_message = f"""{diemcuoc} \nCược đã được chấp nhận."""
                #requests.get(f"https://api.telegram.org/bot{bot_token2}/sendMessage?chat_id={user_id}&text={request_message}")
                #requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={group_id2}&text={text}")
                print(user_id)
                Luna.send_message(user_id, request_message)
                Luna.send_message(group_id, request_message)
                Luna.send_message(group_id2, text)
                save_balance_to_file()
            except Exception as e:
                print("Error fetching user info:", e)
                Luna.send_message(group_id3, f"Lỗi:{e}")
                Luna.send_message(group_id, f"Lỗi:{ten_ncuoc.mention} chưa khởi động Bot @alltowin_bot, hãy khởi động bot và đặt cược lại.")
        else:
            Luna.send_message(group_id, "Không đủ số dư để đặt cược. Vui lòng kiểm tra lại số dư của bạn.")
    else:
        soicau = [
        [
            InlineKeyboardButton("Bot GAME", url="https://t.me/alltowin_bot"),
            InlineKeyboardButton(" Bot Nạp - Rút", url="https://t.me/diemallwin_bot"),
        ],]
        reply_markup = InlineKeyboardMarkup(soicau)
        Luna.send_message(group_id, f"Người chơi chưa khởi động Luna, vui lòng khởi động bot và thử lại. \nHÃY VÀO 2 BOT BÊN DƯỚI, KHỞI ĐỘNG BOT ĐỂ CÓ THỂ CHƠI GAME.", reply_markup=reply_markup)

# Function to start the dice game
def start_game(message, grid):
    #load_balance_from_file()
    grtrangthai2 = 1
    print(mo_game,2)
    mo_game[grid]['tthai'] += grtrangthai2
    print(mo_game,3)
    soicau = [
        [
            InlineKeyboardButton("Soi cầu", url="https://t.me/kqtaixiu"),
            InlineKeyboardButton("Nạp - Rút", url="https://t.me/diemallwin_bot?start=hi"),
        ],]
    reply_markup = InlineKeyboardMarkup(soicau)
    total_bet_T = sum([user_bets[user_id]['T'] for user_id in user_bets])
    total_bet_X = sum([user_bets[user_id]['X'] for user_id in user_bets])
    text = "Hết thời gian cược. Kết quả sẽ được công bố ngay sau đây.\n 💥 Bắt đầu tung XX 💥"
    text += f"""
┏ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
┣➤⚫️Tổng cược bên TÀI: {total_bet_T:,}đ
┣➤⚪️Tổng cược bên XỈU: {total_bet_X:,}đ
┗ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n
"""
    text4 = Luna.send_message(group_id, text)
    idtext4 = text4.id
    time.sleep(3)  # Simulating dice rolling
    
    result = [send_dice(group_id) for _ in range(3)]
    total_score = sum(result)
    kq = f"➤KẾT QUẢ XX: {' + '.join(str(x) for x in result)} = {total_score} điểm {calculate_tai_xiu(total_score)}\n"
    kq1 = f"➤KẾT QUẢ XX: {' + '.join(str(x) for x in result)} = {total_score} điểm {calculate_tai_xiu(total_score)}\n"
    ls_cau(result)
    Luna.send_message(channel_id, kq)
    # Determine the winner and calculate total winnings
    #tien_thang = 0
    total_win = 0
    for user_id in user_bets:
        if sum(result) >= 11 and user_bets[user_id]['T'] > 0:
            total_win += int(user_bets[user_id]['T'] * tile_thang)
            winner[user_id] = []
            winner[user_id] += [int(user_bets[user_id]['T'] * tile_thang)] 
            #tien_thang = user_bets[user_id]['T'] * tile_thang
            user_balance[user_id] += (int(user_bets[user_id]['T'] * tile_thang))

        elif sum(result) < 11 and user_bets[user_id]['X'] > 0:
            total_win += int(user_bets[user_id]['X'] * tile_thang)
            winner[user_id] = []
            winner[user_id] += [int(user_bets[user_id]['X'] * tile_thang)]
            #tien_thang = user_bets[user_id]['X'] * tile_thang
            user_balance[user_id] += (int(user_bets[user_id]['X'] * tile_thang))
            
    save_balance_to_file()        
    
    for user_id, diem in winner.items():
        balance = user_balance.get(user_id, 0)
        user_ids = Luna.get_users(user_id)
        user_id1 = message.from_user.id
        #user_id2 = message.from_user.first_name
        diem = diem[0]
        kq += f"""{user_ids.mention} thắng {diem:,} điểm.\n"""
        kq1 += f"""{user_ids.mention} thắng {diem:,} điểm.Có {balance:,} điểm\n"""
        #kq1 += f"{user_id1} có {balance:,} điểm"
        #requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={user_id}&text={kq1}")
        Luna.send_message(user_id, kq)
        
    kq += f"""
Tổng thắng: {total_win:,}đ
Tổng thua: {total_bet_T + total_bet_X - total_win:,}đ
    """  
    Luna.send_message(group_id, kq, reply_markup=reply_markup)
    Luna.send_message(group_id2, kq1)
    
    
    user_bets.clear()
    winner.clear()
    mo_game.clear()
    luu_cau.clear()
    time.sleep(10)
    Luna.delete_messages(group_id, idtext4)

@Luna.on_message(filters.command("diem"))
async def check_balance(_, message: Message):
    #load_balance_from_file()
    xem_bot()
    from_user = message.from_user#
    if len(message.text.split()) == 1 and not message.reply_to_message:
        if from_user.id not in user_balance:
            return Luna.send_message(message.chat.id, f"{from_user.mention} chưa khởi động bot. Vui lòng khởi động bot.")
        balance = user_balance.get(from_user.id, 0)
        await Luna.send_message(message.chat.id, f"👤 Số điểm của {from_user.mention} là {balance:,} điểm 💰")
        await Luna.send_message(group_id2, f"👤 Số điểm của {from_user.mention} là {balance:,} điểm 💰")
        return
    if len(message.text.split()) == 1 and message.reply_to_message: 
        user_id, username = await extract_user_and_reason(message)#
        user = await Luna.get_users(user_id)#
        if not user_id: #
            return await message.reply_text("không tìm thấy người này")
        if user_id not in user_balance:
            return Luna.send_message(message.chat.id, f"{user.mention} chưa khởi động bot. Vui lòng khởi động bot.")
        balance = user_balance.get(user_id, 0)
        await Luna.send_message(message.chat.id, f"👤 Số điểm của {user.mention} là {balance:,} điểm 💰")
        await Luna.send_message(group_id2, f"👤 Số điểm của {user.mention} là {balance:,} điểm 💰")
        return
    else:
        user_id, username = await extract_user_and_reason(message)#
        user = await Luna.get_users(user_id)#
        if not user_id: #
            return await message.reply_text("không tìm thấy người này")
        if user_id not in user_balance:
            return Luna.send_message(message.chat.id, f"{user.mention} chưa khởi động bot. Vui lòng khởi động bot.")
        balance = user_balance.get(user_id, 0)
        await Luna.send_message(message.chat.id, f"👤 Số điểm của {user.mention} là {balance:,} điểm 💰")
        await Luna.send_message(group_id2, f"👤 Số điểm của {user.mention} là {balance:,} điểm 💰")

def loai_cau(total_score):
  return "⚫️" if 11 <= total_score <= 18 else "⚪️"
    
def ls_cau(result):
    total_score = sum(result)
    cau = loai_cau(total_score)
    if cau not in luu_cau:
        luu_cau[cau] = []
        luu_cau[cau].append(cau)
    try:
        soicau_text = f"{cau}\n"
        with open("soicau.txt", "a", encoding='utf-8') as soicau_file:
            soicau_file.write(soicau_text)
    except Exception as e:
        print(f"Error saving history: {str(e)}")

@Luna.on_message(filters.command("soicau"))
def soicau_taixiu(_, message: Message):
    xem_bot()
    chat_id = message.chat.id
    #load_cau_from_file()
    soicau = [
        [
            InlineKeyboardButton("Soi cầu", url="https://t.me/kqtaixiu"),
            InlineKeyboardButton("Nạp - Rút", url="https://t.me/diemallwin_bot?start=hi"),
        ],]
    reply_markup = InlineKeyboardMarkup(soicau)
    with open("soicau.txt", "r", encoding='utf-8') as f:
        lines = f.read().splitlines()[-1:-11:-1]
        scau = f"10 lần cầu gần nhất:\n"
        for line in lines:
            cau = line.strip().split()
            cau1 = cau[0]
            cau2 = "".join(reversed(cau1))
            scau += f"""{cau2}<-"""
        Luna.send_message(chat_id, scau, reply_markup=reply_markup)

@Luna.on_message(filters.command("start"))
def show_main_menu(_, message: Message):
    user_id = message.from_user.id
    #load_balance_from_file()
    if user_id not in bot_trangthai and filters.private:
        mo_bot(user_id)
        print(bot_trangthai)
  # Check if the user is already in the user_balance dictionary
    xem_bot()
    if user_id not in user_balance:
        user_balance[user_id] = 0  # Set initial balance to 0 for new users
        save_balance_to_file()  # Save user balances to the text file
    nut = [
        [
            InlineKeyboardButton("Soi cầu", url="https://t.me/kqtaixiu"),
            InlineKeyboardButton("Bot Nạp - Rút", url="https://t.me/diemallwin_bot?start=hi"),
        ],
        [
            InlineKeyboardButton("Bot GAME", url="https://t.me/alltowin_bot?start=hi"),
            InlineKeyboardButton("Vào nhóm để chơi GAME", url="https://t.me/sanhallwin"),
        ],]
    reply_markup = InlineKeyboardMarkup(nut)
  # Send a message with a photo link
    photo_url = "https://github.com/tmq247/taxu2/blob/main/photo_2023-12-14_21-31-58.jpg?raw=true"
    caption = """
<code>𝐒ả𝐧𝐡 𝐀𝐋𝐋 𝐖𝐈𝐍</code>
        
<b>♨️Open 15-12 ♨️</b>

🤝 <strong>Nơi hội tụ các chiến thần tài-xỉu</strong> 🎁

⚡️ <b>Tỉ lệ thắng cược 1.95</b> 💸

🔰 <b>Nạp-rút uy tín, chất lượng</b> 👌

🆘 <b>100% xanh chín</b> ✅

⚠️ <b>Tuyệt đối không gian lận chỉnh cầu</b> ❗️

📎 <b> https://t.me/sanhallwin</b> 

<b> LƯU Ý : HÃY BẤM VÀO 2 NÚT BÊN DƯỚI, ĐỂ CÓ THỂ CHƠI GAME<b>
"""
    Luna.send_photo(message.chat.id,
                 photo_url,
                 caption=caption,
                 reply_markup=reply_markup)

@Luna.on_message(filters.command("hdan"))
def soicau_taixiu(_, message: Message):
    chat_id = message.chat.id
    text = f"""
Hướng dẫn sử dụng lệnh của bot
/tx :mở game tài xỉu
/t điểm :đặt cửa tài với số điểm muốn cược
/x điểm: đặt cửa xỉu với số điểm muốn cược
/diem :để xem điểm hiện có
/soicau :để soi cầu
/tangdiem [id người nhận] số điểm muốn tặng :để tặng điểm cho người khác (bạn có thể trả lời tin nhắn của người muốn tặng để nhập lệnh tặng và số điểm muốn tặng) .Lưu ý :phí tặng 5%.
/nap :để nạp điểm
/rut :để rút điểm
/code code của bạn :để nhận điểm bằng code

LƯU Ý: BẤM VÀO 2 NÚT BÊN DƯỚI ĐỂ CHƠI GAME.
"""
    nut = [
        [
            InlineKeyboardButton("Bot Nạp - Rút", url="https://t.me/diemallwin_bot?start=hi"),
            InlineKeyboardButton("Bot GAME", url="https://t.me/alltowin_bot?start=hi"),
        ],]
    reply_markup = InlineKeyboardMarkup(nut)
    Luna.send_message(message.chat.id, text, reply_markup=reply_markup)

@Luna.on_message(filters.command("listdiem"))
def listdiem(_, message: Message):
    #chat_id = message.chat.id
    with open("id.txt", "r") as f:
        a = f.read()
        Luna.send_message(group_id2, f"{a}")

@Luna.on_message(filters.command("topdiem"))
def top_diem(_, message: Message):
    #load_balance_from_file()
    chat_id = message.chat.id
    if chat_id == group_id2 or group_id3:
        with open("id.txt", "r", encoding='utf-8') as f:
            lines = f.read().splitlines()
            top = f"Top 10 điểm cao nhất:\n"
            for line in lines:
                user_id, diem_str = line.strip().split()
                diem = float(diem_str)
                diem = int(diem)
                if diem > 0:
                    topdiem[user_id] = diem
                    #topdiem += {user_id}
                    #topdiem += {diem}
                    #user_id, diem = topdiem.get()
                        
                    #user_id, diem = topdiem.split()
                    td = sorted(topdiem, key=diem)
                    top += f"""{td}\n"""
                    #topdiem[int(user_id)] += (int(diem))
                    # = "/n".join(reversed(diem))
        
                
            Luna.send_message(chat_id, top)
        #for user_id, balance in user_balance.items():
            #topdiem = []
            #topdiem += [user_id], [balance]
        #Luna.send_message(group_id2, f"{topdiem}")

@Luna.on_message(filters.command("listdata"))
def list(_, message: Message):
    chat_id = message.chat.id
    if chat_id == group_id2 or group_id3:
        ls = f"luu_cau: {luu_cau}"
        ls += f"mo_game: {mo_game}"
        ls += f"topdiem: {topdiem}"
        ls += f"user_bets: {user_bets}"
        ls += f"winner: {winner}"
        ls += f"user_balance: {user_balance}"
        ls += f"bot_trangthai: {bot_trangthai}"
        Luna.send_message(chat_id, ls)

@Luna.on_message(filters.command("xoalist"))
def list(_, message: Message):
    chat_id = message.chat.id
    if chat_id == group_id2 or group_id3:
        luu_cau.clear()
        mo_game.clear()
        topdiem.clear()
        user_bets.clear()
        winner.clear()
        user_balance.clear()
        bot_trangthai.clear()
        Luna.send_message(chat_id, "Đã clear data")


################################

#@Luna.on_message(filters.command("tangdiem"))
async def chuyentien_money(_, message: Message):
    from_user = message.from_user.id
    #load_balance_from_file()
    if len(message.text.split()) != 3 or len(message.text.split()) != 2 :
        if len(message.text.split()) == 3:
            user_id, amount = await extract_user_and_reason(message)
            user = await Luna.get_users(user_id)
            from_user1 = message.from_user.mention
            #lenh, user_id, amount = message.text.split(" ", 3)
            if amount.isdigit():
                if not user_id:
                    return await message.reply_text("không tìm thấy người này")
                #if user_id not in user_balance:
                    #user_balance[user_id] = 0
                #if await deduct_balance(from_user, user_id, amount, message):
                amount = int(amount)
                #await message.reply_text(f"{from_user1} đã tặng {user.mention} {int(amount*0.95):,}đ. Phí tặng điểm là 5%")
                await Luna.send_message(user_id, f"Bạn đã nhận được {int(amount*0.95):,}đ được tặng từ {from_user1}, id người dùng là: {from_user}.")
                #await Luna.send_message(group_id3, f"{from_user1} đã tặng {user.mention} {int(amount*0.95):,}đ. ID người tặng là: {from_user}.")
                return
            else:
                return await message.reply(text)
        
        #if and message.text[2:].isdigit():
        if len(message.text.split()) == 2 and message.reply_to_message:
            user_id, amount = await extract_user_and_reason(message)
            #lenh, amount = message.text.split(" ", 2)
            if amount.isdigit():
                user = await Luna.get_users(user_id)
                if not user_id:
                    return await message.reply_text("không tìm thấy người này")
                #if user_id not in user_balance:
                    #user_balance[user_id] = 0
                #if await deduct_balance(from_user, user_id, amount, message):
                amount = int(amount)
                from_user1 = message.from_user.mention
                #await message.reply_text(f"{from_user1} đã tặng {user.mention} {int(amount*0.95):,}đ. Phí tặng điểm là 5%")
                await Luna.send_message(user_id, f"Bạn đã nhận được {int(amount*0.95):,}đ được tặng từ {from_user1}, id người dùng là: {from_user}.")
                #await Luna.send_message(group_id3, f"{from_user1} đã tặng {user.mention} {int(amount*0.95):,}đ, id người tặng là: {from_user}.")
                return
            
            else:
                return
        
        else:
            return

    else:
        return

#################################
# Add these variables for Gitcode handling
GITCODE_FILE = "gitcode.txt"
# Function to create a Gitcode with a custom amount
def create_gitcode(amount):
    gitcode = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
    gitcode_amounts[gitcode] = amount
    with open(GITCODE_FILE, "a") as f:
        f.write(f"{gitcode}:{amount}\n")
    return gitcode

# Function to read Gitcodes from the file
def read_gitcodes():
    if not os.path.exists(GITCODE_FILE):
        return
    with open(GITCODE_FILE, "r") as f:
        for line in f:
            gitcode, amount = line.strip().split(":")
            gitcode_amounts[gitcode] = int(amount)

# Function to remove a used Gitcode
def remove_gitcode(gitcode):
    with open(GITCODE_FILE, "r") as f:
        lines = f.readlines()
    with open(GITCODE_FILE, "w") as f:
        for line in lines:
            if not line.startswith(gitcode):
                f.write(line)


@bot.on_message(filters.command("taocode"))
async def create_gitcode_handler(_, message: Message):
    if message.from_user.id not in admin:
      return await message.reply_text("Bạn không có quyền thực hiện lệnh này.")
    if len(message.text.split()) != 2:
      return await message.reply_text("Vui lòng nhập số tiền cho giftcode.Ví dụ: /regcode 1000")
    lenh, amount = message.text.split(" ", 2)
    try:
      val = int(amount)
      await process_gitcode_amount(message, amount)
    except ValueError:
      return await message.reply_text("Số tiền cho giftcode phải là số nguyên.")

async def process_gitcode_amount(message, amount):
    try:
        amount = int(amount)
        formatted_amount = "{:,.0f}".format(amount).replace(".", ",")
        gitcode = create_gitcode(amount)
        await message.reply_text(f"Đã tạo giftcode thành công. Giftcode của bạn là: {gitcode} ({formatted_amount} điểm).")
    except ValueError:
        await message.reply_text("Số điểm không hợp lệ.")

@bot.on_message(filters.command("code"))
async def naptien_gitcode(_, message: Message):
    read_gitcodes()
    user_id = message.from_user.id
    if user_id not in user_balance:
        user_balance[user_id] = 0
    if len(message.text.split()) != 2:
       return await message.reply_text("Nhập Code bằng lệnh /code [dấu cách] code của bạn \n➡️VD: /code ABCD") 
    if len(message.text.split()) == 2:
      user_id = message.from_user.id
      lenh, gitcode = message.text.split()
      if gitcode in gitcode_amounts:
        await process_naptien_gitcode(user_id, gitcode, message)
      else:
          await message.reply_text("Giftcode không hợp lệ hoặc đã được sử dụng.")
    
async def process_naptien_gitcode(user_id, gitcode, message):
    #load_balance_from_file()
    if gitcode in gitcode_amounts:
        amount = gitcode_amounts[gitcode]
        # Check if the user's balance exists in the dictionary, initialize it if not
        if user_id not in user_balance:
            user_balance[user_id] = 0
            #save_balance_to_file()
        user_balance[user_id] += amount
        remove_gitcode(gitcode)
        del gitcode_amounts[gitcode]
        await message.reply_text(f"Nhập Giftcode Thành Công!\nSố điểm của bạn là: {user_balance[user_id]:,}đ.\n💹Chúc Bạn May Mắn Nhé💖")
        # Sử dụng phương thức send_message để gửi thông báo vào nhóm
        await bot.send_message(group_id3, f"""
Người chơi {message.from_user.mention} 
User: {user_id}
Đã Nạp: {amount:,}đ bằng Giftcode.""")
        # Save the updated balance to the file
        #save_balance_to_file()
        #load_balance_from_file()
    else:
        await message.reply_text("Giftcode không hợp lệ hoặc đã được sử dụng.")



############################################
# Hàm xử lý chuyển tiền và cập nhật số dư của cả người gửi và người được chuyển
async def deduct_balance(from_user, user_id, amount, message):
    amount = int(amount)
    if from_user not in user_balance or int(user_balance[from_user]) < amount:
      return await message.reply_text("Bạn không có đủ số điểm để tặng người này.")
    if amount <= 0 or int(user_balance[from_user]) < amount:
        return await message.reply_text("Bạn không có đủ số điểm để tặng người này.")
    # Trừ số tiền từ số dư của người gửi và cộng cho người được chuyển
    user_balance[from_user] -= amount
    user_balance[user_id] += int(amount*0.95)

    # Lưu số dư vào tệp văn bản
    save_balance_to_file()
    load_balance_from_file()
    return True
    

@bot.on_message(filters.command("tangdiem"))
async def chuyentien_money(_, message: Message):
    from_user = message.from_user.id
    text = f"""
Để tặng điểm của mình cho người chơi khác bằng 2 cách:
Cách 1:Trả lời người muốn tặng điểm bằng lệnh /tangdiem [dấu cách] số điểm.
Cách 2:Trả lời người muốn tặng điểm rồi nhập /id để lấy ID rồi nhập lệnh 
/tangdiem [dấu cách] ID vừa lấy [dấu cách] số điểm.
VD: /tangdiem 987654321 10000.
Phí tặng điểm là 5%."""
    load_balance_from_file()
    if len(message.text.split()) != 3 or len(message.text.split()) != 2 :
        if len(message.text.split()) == 3:
            user_id, amount = await extract_user_and_reason(message)
            user = await bot.get_users(user_id)
            from_user1 = message.from_user.mention
            #lenh, user_id, amount = message.text.split(" ", 3)
            if amount.isdigit():
                if not user_id:
                    return await message.reply_text("không tìm thấy người này")
                if user_id not in user_balance:
                    user_balance[user_id] = 0
                if await deduct_balance(from_user, user_id, amount, message):
                    amount = int(amount)
                    await bot.send_message(user_id, f"Bạn đã nhận được {int(amount*0.95):,}đ được tặng từ {from_user1}, id người dùng là: {from_user}.")
                    await message.reply_text(f"{from_user1} đã tặng {user.mention} {int(amount*0.95):,}đ. Phí tặng điểm là 5%")
                    await bot.send_message(group_id3, f"{from_user1} đã tặng {user.mention} {int(amount*0.95):,}đ. ID người tặng là: {from_user}.")
                    return
            else:
                return await message.reply(text)
        
        #if and message.text[2:].isdigit():
        if len(message.text.split()) == 2 and message.reply_to_message:
            user_id, amount = await extract_user_and_reason(message)
            #lenh, amount = message.text.split(" ", 2)
            if amount.isdigit():
                user = await bot.get_users(user_id)
                if not user_id:
                    return await message.reply_text("không tìm thấy người này")
                if user_id not in user_balance:
                    user_balance[user_id] = 0
                if await deduct_balance(from_user, user_id, amount, message):
                    amount = int(amount)
                    from_user1 = message.from_user.mention
                    await message.reply_text(f"{from_user1} đã tặng {user.mention} {int(amount*0.95):,}đ. Phí tặng điểm là 5%")
                    await bot.send_message(user_id, f"Bạn đã nhận được {int(amount*0.95):,}đ được tặng từ {from_user1}, id người dùng là: {from_user}.")
                    await bot.send_message(group_id3, f"{from_user1} đã tặng {user.mention} {int(amount*0.95):,}đ, id người tặng là: {from_user}.")
                    return
            
            else:
                return await message.reply(text)
        
        else:
            return await message.reply(text)

    else:
        return await message.reply(text)
#################################################


@bot.on_message(filters.command("cdiem"))
async def set_balance_cong(_, message: Message):
  load_balance_from_file()
  from_user = message.from_user.id
  if from_user not in admin:
      return await message.reply_text("Bạn không có quyền sử dụng lệnh này.")
  if len(message.text.split()) != 3:
      return await message.reply_text("⏲Nhập id và số điểm muốn cộng 🪤 \n🚬(ví dụ: /cdiem 12345 1000 )🎚")
  #lenh, user_id, diem = message.text.split()
  #user = bot.get_users(user_id)
  user_id, diem = await extract_user_and_reason(message)
  user = await bot.get_users(user_id)
  if not user_id:
      return await message.reply_text("không tìm thấy người này")
  if user_id not in user_balance:
      user_balance[user_id] = 0
      #return await message.reply_text("Người dùng này chưa khởi động bot.")
  elif diem.isdigit():
      await update_balance_cong(diem, user_id, message)
  else:
      return await message.reply_text("⏲Nhập id và số điểm muốn cộng🪤 \n🚬(ví dụ: /cdiem 12345 1000)🎚")
      #await update_balance(diem, user_id, message)
   
    
async def update_balance_cong(diem, user_id, message):
  chat_id = message.chat.id
  user = await bot.get_users(user_id)
  if user_id in user_balance and diem.isdigit():
    balance_change = int(diem)
    current_balance = user_balance.get(user_id, 0)
    new_balance = current_balance + balance_change
    user_balance[user_id] = new_balance
    save_balance_to_file()
    load_balance_from_file()
    notification_message = f"""
🫥Bạn Đã Nạp Điểm Thành Công🤖
🫂Số Điểm Hiện Tại: {new_balance:,} điểm🐥
🐝Chúc Bạn Chơi Game Vui Vẻ🐳
""" 
    text2 = f"""
🫥{user.mention} Đã Nạp Điểm Thành Công🤖
🫥ID {user_id}
🫂Số Điểm Cũ: {new_balance-balance_change:,} điểm🐥
🫂Số Điểm Hiện Tại: {new_balance:,} điểm🐥"""
    text = f"""🔥Chúc mừng {user.mention} đã bơm máu thành công⚡️⚡️"""
    await bot.send_message(user_id, notification_message)
    await bot.send_message(group_id3, text2)
    await bot.send_message(group_id2, text2)
    await bot.send_message(group_id, text)
      
  else:
    await message.reply_text("Vui lòng nhập một số điểm hợp lệ.⏲Nhập id và số điểm muốn cộng🪤 \n🚬(ví dụ: /cdiem 12345 1000)🎚")


@bot.on_message(filters.command("tdiem"))
async def set_balance_tru(_, message: Message):
  load_balance_from_file()
  from_user = message.from_user.id
  if from_user not in admin:
      return await message.reply_text("Bạn không có quyền sử dụng lệnh này.")
  if len(message.text.split()) != 3:
      return await message.reply_text("⏲Nhập id và số điểm muốn trừ🪤 \n🚬(ví dụ: /tdiem 12345 1000)🎚)🎚")
  user_id, diem = await extract_user_and_reason(message)
  user = await bot.get_users(user_id)
  if not user_id:
      return await message.reply_text("không tìm thấy người này")
  if user_id not in user_balance:
      user_balance[user_id] = 0
  if diem.isdigit():
      await update_balance_tru(diem, user_id, message)
  else:
      return await message.reply_text("⏲Nhập id và số điểm muốn trừ🪤 \n🚬(ví dụ: /tdiem 12345 1000)🎚")
      #await update_balance(diem, user_id, message)
   
    
async def update_balance_tru(diem, user_id, message):
  chat_id = message.chat.id
  user = await bot.get_users(user_id)
  if user_id in user_balance and diem.isdigit():
    balance_change = int(diem)
    current_balance = user_balance.get(user_id, 0)
    if current_balance <= 0 :
        return await bot.send_message(group_id3, f"{user.mention} không đủ điểm để trừ")
    if current_balance < balance_change:
        return await bot.send_message(group_id3, f"{user.mention} không đủ điểm để trừ")
    new_balance = current_balance - balance_change
    user_balance[user_id] = new_balance
    #save_balance_to_file()
    #load_balance_from_file()
    #notification_message = f"""
#🫥{user_ids.mention} Đã Nạp Điểm Thành Công🤖
#🫥ID {user_id}
#🫂Số Điểm Hiện Tại: {new_balance:,} điểm🐥
#🐝Chúc Bạn Chơi Game Vui Vẻ🐳""" 
    text2 = f"""
🫥Đã Trừ Điểm {user.mention} Thành Công🤖
🫥ID {user_id}
🫂Số Điểm Cũ: {new_balance+balance_change:,} điểm🐥
🫂Số Điểm Hiện Tại: {new_balance:,} điểm🐥"""
    #text = f"""🔥Chúc mừng {user_ids.mention} đã bơm máu thành công⚡️⚡️"""
    #await bot.send_message(user_id, notification_message)
    await bot.send_message(group_id3, text2)
    #await bot.send_message(group_id, text)
      
  else:
    await message.reply_text("Vui lòng nhập một số điểm hợp lệ.⏲Nhập id và số điểm muốn trừ🪤 \n🚬(ví dụ: /tdiem 12345 1000)🎚)🎚")
########################################################

@bot.on_message(filters.command("start"))
async def show_main_menu(_, message: Message):
    user_id = message.from_user.id
    if user_id not in user_balance:
        user_balance[user_id] = 0  # Set initial balance to 0 for new users
        save_balance_to_file()  # Save user balances to the text file
    nut = [
        [
            InlineKeyboardButton("Bot GAME", url="https://t.me/alltowin_bot?start=hi"),
            InlineKeyboardButton("Vào nhóm để chơi GAME", url="https://t.me/sanhallwin"),
        ],
        [
            InlineKeyboardButton("Soi cầu", url="https://t.me/kqtaixiu"),
            InlineKeyboardButton("Nạp - Rút", url="https://t.me/diemallwin_bot?start=hi"),
        ],]
    reply_markup = InlineKeyboardMarkup(nut)
    photo_url = "https://github.com/tmq247/taxu2/blob/main/photo_2023-12-14_21-31-58.jpg?raw=true"
    caption = """
<code>𝐒ả𝐧𝐡 𝐀𝐋𝐋 𝐖𝐈𝐍</code>
        
<b>♨️Open 15-12 ♨️</b>

🤝 <strong>Nơi hội tụ các chiến thần tài-xỉu</strong> 🎁

⚡️ <b>Tỉ lệ thắng cược 1.95</b> 💸

🔰 <b>Nạp-rút uy tín, chất lượng</b> 👌

🆘 <b>100% xanh chín</b> ✅

⚠️ <b>Tuyệt đối không gian lận chỉnh cầu</b> ❗️

📎 <b> https://t.me/sanhallwin</b> 

LƯU Ý: BẤM VÀO NÚT bot GAME VÀ NÚT vào nhóm bên dưới để chơi GAME
"""
    await bot.send_photo(message.chat.id,
                 photo_url,
                 caption=caption,
                 reply_markup=reply_markup)
#####################################################

@bot.on_message(filters.command("diem"))
async def check_balance(_, message: Message):
  load_balance_from_file()
  user_id = message.from_user.id
  balance = user_balance.get(user_id, 0)
  await bot.send_message(user_id, f"""
👤 Tên tài khoản: {message.from_user.mention}
💳 ID Tài khoản: {user_id}
💰 Số dư của bạn: {balance:,} đ
        """)

client = bot
@bot.on_message(filters.command("rut"))
async def withdraw_balance(_, message: Message):
  chat_id = message.chat.id
  user_id = message.from_user.id
  rut[user_id] = "withdraw_method"
  user_game_state.pop(user_id, None)  # Clear game state to avoid conflicts

  ruttien = [[InlineKeyboardButton("Rút qua ngân hàng", callback_data="_bank")]]
   #[[InlineKeyboardButton("Rút qua MoMo", callback_data="_momo")]
  markup = InlineKeyboardMarkup(ruttien)
    # Tạo bàn phím cho phương thức rút
  if chat_id == group_id:
    await bot.send_message(chat_id, "Vui lòng nhắn tin riêng với bot")
  await bot.send_message(user_id, "Chọn phương thức rút điểm:", reply_markup=markup)

#rut momo
@bot.on_callback_query(filters.regex("_momo"))
async def handle_withdrawal_method_selection_momo(_, callback_query):
  user_id = callback_query.from_user.id
  
  if filters.regex("_momo"):
    rut[user_id] = "momo_account"
    await bot.send_message(user_id, "Nhập số MoMo của bạn:")
    rutdiem = await client.listen(user_id=user_id)
    await process_account_inforut(_, rutdiem, user_id)
    
  #await bot.answer_callback_query(callback_query.id, "Bạn đã chọn phương thức rút điểm.")

#rut bank
@bot.on_callback_query(filters.regex("_bank"))
async def handle_withdrawal_method_selection_bank(_, callback_query):
    user_id = callback_query.from_user.id
    rut[user_id] = "bank_account"
    await bot.send_message(
          user_id, """
Nhập thông tin tài khoản ngân hàng của bạn:
STK + MÃ NGÂN HÀNG
VD: 0987654321 VCB 
TÊN NGÂN HÀNG - MÃ NGÂN HÀNG
📌 Vietcombank => VCB
📌 BIDV => BIDV 
📌 Vietinbank => VTB
📌 Techcombank => TCB
📌 MB Bank => MBB 
📌 Agribank => AGR 
📌 TienPhong Bank => TPB
📌 SHB bank => SHB
📌 ACB => ACB 
📌 Maritime Bank => MSB
📌 VIB => VIB
📌 Sacombank => STB
📌 VP Bank => VPB
📌 SeaBank => SEAB
📌 Shinhan bank Việt Nam => SHBVN
📌 Eximbank => EIB 
📌 KienLong Bank => KLB 
📌 Dong A Bank => DAB 
📌 HD Bank => HDB 
📌 LienVietPostBank => LPB 
📌 VietBank => VBB
📌 ABBANK => ABB 
📌 PG Bank => PGB
📌 PVComBank => PVC
📌 Bac A Bank => BAB 
📌 Sai Gon Commercial Bank => SCB
📌 BanVietBank => VCCB 
📌 Saigonbank => SGB
📌 Bao Viet Bank => BVB  
📌 Orient Commercial Bank => OCB 

⚠️ Lưu ý: ❌ Không hỗ trợ hoàn tiền nếu bạn nhập sai thông tin Tài khoản. 
❗️ Rút min 50K
  """)
    rutdiem = await client.listen(user_id=user_id)
    await process_account_inforut(_, rutdiem, user_id)

    #await bot.answer_callback_query(callback_query.id, "Bạn đã chọn phương thức rút điểm.")


        
#@bot.on_message(filters.reply & rut in ["momo_account"] or ["bank_account"])
async def process_account_inforut(_, rutdiem, user_id):
  if user_id in rut and rut in ["momo_account"] or ["bank_account"]:
    try:
      account_info = rutdiem.text
      #user_id = message.from_user.id

      if rut[user_id] == "momo_account":
        rut[user_id] = (account_info, "withdraw_amount_momo")
        await bot.send_message(user_id, """
❗️Nhập số tiền bạn muốn rút qua MoMo💮
🚫VD: 50000 - 50000000🚮
              """)
        diemrut = await client.listen(user_id=user_id)
        await process_withdraw_amountrut(diemrut, user_id)
      elif rut[user_id] == "bank_account":
        rut[user_id] = (account_info, "withdraw_amount_bank")
        await bot.send_message(user_id, """
❗️Nhập số tiền bạn muốn rút qua ngân hàng💮
🚫VD: 50000 - 50000000🚮
              """)
        diemrut = await client.listen(user_id=user_id)
        await process_withdraw_amountrut(diemrut, user_id)
    except ValueError:
        pass
  

#@bot.on_message(filters.text & rut in ["withdraw_amount_momo"] or ["withdraw_amount_bank"])
async def process_withdraw_amountrut(diemrut, user_id):
  load_balance_from_file()
  if user_id in rut and rut[user_id][1] in ["withdraw_amount_momo"] or ["withdraw_amount_bank"]:
    user = await bot.get_users(user_id)
    if diemrut.text.isdigit():
      account_info, withdraw_amount_type = rut[user_id]
      withdraw_amount = int(diemrut.text)
      user_balance_value = user_balance.get(user_id, 0)
      if withdraw_amount < 50000:
        await bot.send_message(user_id, 
            """
🖇 Số điểm rút phải lớn hơn hoặc bằng 50,000 đồng.🗳
              """)
        del rut[user_id]
        return

      if withdraw_amount > user_balance_value:
        await bot.send_message(user_id,
            """
🌀Số điểm rút của bạn không đủ💳
🪫Vui Lòng 🔎Chơi Tiếp🔍 Để Có Thêm Điểm💎
              """)
        del rut[user_id]
        return

      # Trừ số tiền từ số dư của người chơi
      user_balance_value -= withdraw_amount
      user_balance[user_id] = user_balance_value

      with open("id.txt", "r") as f:
        lines = f.readlines()

      with open("id.txt", "w") as f:
        for line in lines:
          user_id_str, balance_str = line.strip().split()
          if int(user_id_str) == user_id:
            balance = int(balance_str)
            if withdraw_amount <= balance:
              balance -= withdraw_amount
              f.write(f"{user_id} {balance}\n")
            else:
              await bot.send_message(user_id, "Số dư không đủ để rút điểm.")
        else:
            f.write(line)

      formatted_balance = "{:,.0f} đ".format(user_balance_value)
      account_type = "MoMo" if withdraw_amount_type == "withdraw_amount_momo" else "ngân hàng"
      await bot.send_message(user_id,
          f"""
⏺Lệnh rút: {withdraw_amount:,} VNĐ🔚
✅Của bạn về {account_type}: {account_info} đang chờ hệ thống xử lý🔚
☢️Số điểm khi chưa rút: {user_balance_value+withdraw_amount:,}
              """)

      request_message = f"""
➤Tên Người Rút: {user.mention} 
➤ID Người Rút: {user.id} 
➤Yêu Cầu Rút: {withdraw_amount:,} VNĐ 
➤Về {account_type}: {account_info}
          """
      requests.get(f"https://api.telegram.org/bot{bot_token3}/sendMessage?chat_id={admin_id}&text={request_message}")
      requests.get(f"https://api.telegram.org/bot{bot_token3}/sendMessage?chat_id={admin_id2}&text={request_message}")
      requests.get(f"https://api.telegram.org/bot{bot_token3}/sendMessage?chat_id={admin_id3}&text={request_message}")
      await bot.send_message(group_id3, request_message)
      await bot.send_message(group_id2, f"{user.mention} đã rút {withdraw_amount:,}đ ,còn {formatted_balance}đ.")

      del rut[user_id]
      load_balance_from_file() 
      time.sleep(10)
      user_notification = f"""
📬 Rút điểm thành công!
⏺ Số điểm rút: {withdraw_amount:,} VNĐ
📈 Số điểm còn lại: {formatted_balance}
💵 sẽ đc chuyển trong vòng 15 phút. Xin cảm ơn!!!
          """
      await bot.send_message(user_id, user_notification)
      await bot.send_message(group_id, f"""{user.mention} đã rút điểm thành công. Xin chúc mừng🥳🥳🥳 (yêu cầu sẽ được sử lý trong vòng 15 phút )""")
    else:
      await bot.send_message(user_id, "Lỗi!!! Vui lòng thử lại.")
  else:
    await bot.send_message(user_id, "Lỗi!!! Vui lòng thử lại.")



####################################

# Hàm nạp tiền tài khoản
@bot.on_message(filters.command("nap"))
async def napwithdraw_balance(_, message: Message):
  chat_id = message.chat.id
  user_id = message.from_user.id
  nap[user_id] = "napwithdraw_method"
  user_game_state.pop(user_id, None)  # Clear game state to avoid conflicts

  naptien = [[InlineKeyboardButton("Nạp qua MoMo", callback_data="_napmomo")],
  [InlineKeyboardButton("Nạp qua ngân hàng", callback_data="_napbank")]]
  markup = InlineKeyboardMarkup(naptien)
   # Tạo bàn phím cho phương thức rút
  if chat_id == group_id:
    await bot.send_message(chat_id,
                   "Vui lòng nhắn tin riêng với bot")
  await bot.send_message(user_id,
                   "Chọn phương thức nạp điểm:",
                   reply_markup=markup)
  
@bot.on_callback_query(filters.regex("_napmomo"))
async def naphandle_withdrawal_method_selectionmomo(_, callback_query):
  user_id = callback_query.from_user.id

  if filters.regex("_napmomo"):
    nap[user_id] = "napmomo_account"
    await bot.send_message(user_id, "Nhập số MoMo của bạn:")
    napdiem = await client.listen(user_id=user_id)
    await process_account_info_nap(_, napdiem, user_id)
  #await bot.answer_callback_query(callback_query.id, "Bạn đã chọn phương thức nạp điểm.")

@bot.on_callback_query(filters.regex("_napbank"))
async def naphandle_withdrawal_method_selectionbank(_, callback_query):
    user_id = callback_query.from_user.id
    nap[user_id] = "napbank_account"
    await bot.send_message(
        user_id, """***
Nhập thông tin tài khoản ngân hàng của bạn:
STK + MÃ NGÂN HÀNG
VD: 0987654321 VCB
 TÊN NGÂN HÀNG - MÃ NGÂN HÀNG
📌 Vietcombank => VCB
📌 BIDV => BIDV 
📌 Vietinbank => VTB
📌 Techcombank => TCB
📌 MB Bank => MBB 
📌 Agribank => AGR 
📌 TienPhong Bank => TPB
📌 SHB bank => SHB
📌 ACB => ACB 
📌 Maritime Bank => MSB
📌 VIB => VIB
📌 Sacombank => STB
📌 VP Bank => VPB
📌 SeaBank => SEAB
📌 Shinhan bank Việt Nam => SHBVN
📌 Eximbank => EIB 
📌 KienLong Bank => KLB 
📌 Dong A Bank => DAB 
📌 HD Bank => HDB 
📌 LienVietPostBank => LPB 
📌 VietBank => VBB
📌 ABBANK => ABB 
📌 PG Bank => PGB
📌 PVComBank => PVC
📌 Bac A Bank => BAB 
📌 Sai Gon Commercial Bank => SCB
📌 BanVietBank => VCCB 
📌 Saigonbank => SGB
📌 Bao Viet Bank => BVB  
📌 Orient Commercial Bank => OCB 

⚠️ Lưu ý: ❌ Không hỗ trợ hoàn tiền nếu bạn nhập sai thông tin Tài khoản. 
❗️ Nạp min 10K
***""")
    napdiem = await client.listen(user_id=user_id)
    await process_account_info_nap(_, napdiem, user_id)

  #await bot.answer_callback_query(callback_query.id, "Bạn đã chọn phương thức nạp điểm.")


#@bot.on_callback_query(filters.text & nap in ["napmomo_account", "napbank_account"])
async def process_account_info_nap(_, napdiem, user_id):
  try:
    account_info = napdiem.text
    #user_id = message.from_user.id

    if nap[user_id] == "napmomo_account":
      nap[user_id] = (account_info, "withdraw_amount_napmomo")
      await bot.send_message(user_id,
          """
❗️Nhập số điểm bạn muốn nạp qua MoMo💮
🚫VD: 10000 - 50000000🚮
            """)
      diemnap = await client.listen(user_id=user_id)
      await process_withdraw_amountnap(diemnap, user_id)
    elif nap[user_id] == "napbank_account":
      nap[user_id] = (account_info, "withdraw_amount_napbank")
      await bot.send_message(user_id,
          """
❗️Nhập số điểm bạn muốn nạp qua ngân hàng💮
🚫VD: 10000 - 50000000🚮
            """)
      diemnap = await client.listen(user_id=user_id)
      await process_withdraw_amountnap(diemnap, user_id)
  except ValueError:
    pass


#@bot.on_message(nap in ["withdraw_amount_napmomo", "withdraw_amount_napbank"])
async def process_withdraw_amountnap(diemnap, user_id):
  load_balance_from_file()
  if user_id in nap and nap[user_id][1] in ["withdraw_amount_napmomo", "withdraw_amount_napbank"]:
    user = await bot.get_users(user_id)
    if diemnap.text.isdigit():
      account_info, withdraw_amount_type = nap[user_id]
      withdraw_amount = int(diemnap.text)
      #user_id = message.from_user.id
      user_balance_value = user_balance.get(user_id, 0)

      if withdraw_amount < 10000:
        await bot.send_message(user_id,
            """
🖇 Số điểm nạp phải lớn hơn hoặc bằng 10,000 đồng.🗳
              """)
        del nap[user_id]
        return

      formatted_balance = "{:,.0f} đ".format(user_balance_value)

      account_type = "MoMo" if withdraw_amount_type == "withdraw_amount_napmomo" else "ngân hàng"
      await bot.send_message(user_id,
          f"""
⏺Lệnh nạp: {withdraw_amount:,} VNĐ🔚
✅Của bạn từ {account_type}: {account_info} đang chờ hệ thống check🔚
☢️Số điểm trước khi nạp của bạn: {formatted_balance}
              """)
      napmomo_account = "108002189644"
      photo_link = "https://github.com/tmq247/taxu2/blob/main/photo_2023-12-08_03-22-58.jpg?raw=true"
      caption = f"""
🏧Phương Thức Nạp Bank🏧
💰 Ngân hàng PVCOM 💰
🔊Tài Khoản: {napmomo_account}🔚

🔊Nội Dung: napdiem_{user.id} 🔚

🔊Min Nạp: 10.000k Min Rút: 100.000k
🔊Min Nạp: 10.000 - 3.000.000🔚
🔊Vui lòng ghi đúng nội dung nạp điểm.🔚
🔊Vui lòng chụp lại bill.🔚
🔊Không Hỗ Trợ Lỗi Nội Dung.🔚
🔊NẠP NHANH BẰNG MÃ QR PHÍA BÊN DƯỚI NHÉ 🔚
      """
      await bot.send_message(user_id, caption)
      await bot.send_photo(user_id, photo_link)

      request_message = f"""
➤Tên Người Nạp: {user.mention} 
➤ID Người Nạp: {user.id}
➤Yêu Cầu Nạp: {withdraw_amount:,} VNĐ ( {withdraw_amount} )
➤Từ {account_type}: {account_info}
          """
      requests.get(f"https://api.telegram.org/bot{bot_token3}/sendMessage?chat_id={admin_id}&text={request_message}")
      requests.get(f"https://api.telegram.org/bot{bot_token3}/sendMessage?chat_id={admin_id2}&text={request_message}")
      requests.get(f"https://api.telegram.org/bot{bot_token3}/sendMessage?chat_id={admin_id3}&text={request_message}")
      await bot.send_message(group_id3, request_message)

      del nap[user_id]
    else:
      await bot.send_message(user_id, "Lỗi!!! Vui lòng thử lại.")
  else:
    await bot.send_message(user_id, "Lỗi!!! Vui lòng thử lại.")

##############################################

@bot.on_message(filters.command("listdata"))
async def list(_, message: Message):
    chat_id = message.chat.id
    if chat_id == group_id2 or group_id3:
        ls = f"user_state: {user_state}"
        ls += f"rut: {rut}"
        ls += f"nap: {nap}"
        ls += f"user_balance: {user_balance}"
        ls += f"user_bet_history: {user_bet_history}"
        ls += f"user_withdraw_history: {user_withdraw_history}"
        ls += f"napuser_withdraw_history: {napuser_withdraw_history}"
        ls += f"used_gitcodes: {used_gitcodes}"
        ls += f"gitcode_amounts: {gitcode_amounts}"
        ls += f"user_pending_gitcodes: {user_pending_gitcodes}"
        ls += f"user_game_state: {user_game_state}"
        ls += f"user_balances: {user_balances}"
        ls += f"user_bets: {user_bets}"
        await bot.send_message(chat_id, ls)

@bot.on_message(filters.command("xoalist"))
async def list(_, message: Message):
    chat_id = message.chat.id
    if chat_id == group_id2 or group_id3:
        user_state.clear()
        rut.clear()
        nap.clear()
        user_balance.clear()
        user_bet_history.clear()
        user_withdraw_history.clear()
        napuser_withdraw_history.clear()
        used_gitcodes.clear()
        gitcode_amounts.clear()
        user_pending_gitcodes.clear()
        user_game_state.clear()
        user_balances.clear()
        user_bets.clear()
        await bot.send_message(chat_id, "Đã clear data")

###################################



#######################################################
def on_exit():
  save_balance_to_file()

# Xử lý khi bot bị tắt hoặc lỗi
atexit.register(save_balance_to_file)

#@Luna.on_message(filters.command("tatbotgame"))
#@atexit.register
#async def dong(_, message: Message):
    #chat_id = message.chat.id
    #save_balance_to_file()
    #await Luna.send_message(chat_id, "Tắt Bot Game")
                                          
        
######################################################
async def main():
    apps = (bot, Luna)
    await compose(apps)
    #Luna.start()
    print(
        """
-----------------
| Luna khởi động! |
-----------------
"""
    )
  #await bot.start()
    print(
        """
-----------------
| Taxu khởi động! |
-----------------
""")
    await Luna.send_message(group_id3, "Bot Game đã mở")
    await bot.send_message(group_id3, "bot Điểm đã mở")
    user_state.clear()
    rut.clear()
    nap.clear()
    used_gitcodes.clear()
    gitcode_amounts.clear()
    user_pending_gitcodes.clear()
    user_game_state.clear()
    user_bets.clear()
    
    luu_cau.clear()
    mo_game.clear()
    topdiem.clear()
    user_bets.clear()
    winner.clear()
    
    await idle()


loop = get_event_loop()
loop.run_until_complete(main())
