import re
import os
from asyncio import gather, get_event_loop, sleep

from aiohttp import ClientSession
from pyrogram import Client, filters, idle
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
from pyrogram.types import  Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.filters import command
from functions import (
    extract_user,
    extract_user_and_reason,
    time_converter,
)
#from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telebot.util import quick_markup
#from keyboard import ikb
#from pykeyboard import InlineKeyboard
import telebot
#from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telebot import TeleBot, types


is_config = os.path.exists("config.py")

if is_config:
    from config import *
else:
    from sample_config import *

bot = Client(
    ":memory:",
    bot_token=bot_token,
    api_id=api_id,
    api_hash=api_hash,
)

bot_id = int(bot_token.split(":")[0])

###############
luu_cau = {}
#cau = {}
mo_game = {}
grtrangthai = {}

# Dictionary to store user bets
user_bets = {}
winner = {}
winner2 = {}

# Dictionary to store user balances
user_balance = {}

# Variable to store the group chat ID
group_chat_id = -1002121532989
channel_id = -1002067584440

# Winning coefficient
winning_coefficient = 1.95

#########################
# Tạo từ điển gitcodes
used_gitcodes = []
grid_trangthai = {}
user_pending_gitcodes = {}

# Add these variables for Gitcode handling
grid_FILE = "grid.txt"
# Function to create a Gitcode with a custom amount
def tao_grid(chat_id):
    th = '1'
    trangthai = int(th)
    grid = chat_id
    grid_trangthai[grid] = trangthai
    with open(grid_FILE, "a") as f:
        f.write(f"{grid}:{trangthai}\n")
    return grid

# Function to read Gitcodes from the file
def xem_grid():
    if not os.path.exists(grid_FILE):
        return
    with open(grid_FILE, "r") as f:
        for line in f:
            grid, trangthai = line.strip().split(":")
            grid_trangthai[grid] = int(trangthai)

# Function to remove a used Gitcode
def xoa_grid(grid):
    with open(grid_FILE, "r") as f:
        lines = f.readlines()
    with open(grid_FILE, "w") as f:
        for line in lines:
            if not line.startswith(grid):
                f.write(line)



#######################################################


# Function to send a dice and get its value
def send_dice(chat_id):
    response = requests.get(f'https://api.telegram.org/bot{bot_token}/sendDice?chat_id={chat_id}')
    if response.status_code == 200:
        data = response.json()
        if 'result' in data and 'dice' in data['result']:
            return data['result']['dice']['value']
    return None


# Hàm kiểm Tài/Xỉu
def calculate_tai_xiu(total_score):
  return "Tài" if 11 <= total_score <= 18 else "Xỉu"

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



admin_user_id = 6337933296 or 6630692765 or 5838967403 or 6050066066



# Function to confirm the bet and check user balance
def confirm_bet(user_id, bet_type, bet_amount, ten_ncuoc, message):
    load_balance_from_file()
    mention =  bot.get_users(user_id).mention
    user_id = message.from_user.id
    if bet_type == 'T':
        cua_cuoc = '⚫️Tài'
    else:
        cua_cuoc = '⚪️Xỉu'
    diemcuoc = f"{ten_ncuoc} đã cược {cua_cuoc} {bet_amount} điểm"
    
    #time.sleep(3)
    #await diemcuoc.delete()
    
    # Check if the user_id is present in user_balance dictionary
    if user_id in user_balance:
        # Check user balance
        if user_balance[user_id] >= bet_amount:
            user_bets[user_id] = {'T': 0, 'X': 0}  # Initialize the user's bets if not already present
            for user_id in user_bets.items():
                user_id, bet_type, tiencuoc = user_bets
                bot.send_message(group_chat_id, f"{user_id} {bet_type} {tiencuoc}")
                tongtiencuoc = sum(tiencuoc + bet_amount)
                bot.send_message(group_chat_id, f"{user_id} {bet_type} {tongtiencuoc}")
                
                
            user_bets[user_id][bet_type] += bet_amount
            user_balance[user_id] -= bet_amount
            
            bot.send_message(user_id, f"{diemcuoc} \n Cược đã được chấp nhận.")
            bot.send_message(group_chat_id, f"{diemcuoc} \n Cược đã được chấp nhận.")

        else:
            bot.send_message(group_chat_id, "Không đủ số dư để đặt cược. Vui lòng kiểm tra lại số dư của bạn.")
    else:
        bot.send_message(group_chat_id, "Người chơi không có trong danh sách. Hãy thử lại.")
    # Load user balances from the file
    save_balance_to_file()
    load_balance_from_file()

# Function to start the dice game
def start_game(message):
    load_balance_from_file()
    soicau = [
        [
            InlineKeyboardButton("Soi cầu", url="https://t.me/kqtaixiu"),
            InlineKeyboardButton("Nạp - Rút", url="https://t.me/testtaixiu1bot"),
        ],]
    reply_markup = InlineKeyboardMarkup(soicau)
    total_bet_T = sum([user_bets[user_id]['T'] for user_id in user_bets])
    total_bet_X = sum([user_bets[user_id]['X'] for user_id in user_bets])
    text4 = bot.send_message(group_chat_id, f"""
┏ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
┣➤⚫️Tổng cược bên TÀI: {total_bet_T}đ
┣➤⚪️Tổng cược bên XỈU: {total_bet_X}đ
┗ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
""")
    idtext4 = text4.id
    text5 = bot.send_message(group_chat_id, "Hết thời gian cược. Kết quả sẽ được công bố ngay sau đây.\n 💥 Bắt đầu tung XX 💥")
    #bot.send_message(group_chat_id, "")
    idtext5 = text5.id

    time.sleep(3)  # Simulating dice rolling

    result = [send_dice(group_chat_id) for _ in range(3)]
    total_score = sum(result)
    time.sleep(3)

    bot.send_message(group_chat_id, f"➤KẾT QUẢ XX: {' + '.join(str(x) for x in result)} = {total_score} điểm {calculate_tai_xiu(total_score)}")
    ls_cau(result)
    

    # Determine the winner and calculate total winnings
    tien_thang = 0
    total_win = 0
    for user_id in user_bets:
        if sum(result) >= 11 and user_bets[user_id]['T'] > 0:
            total_win += user_bets[user_id]['T'] * winning_coefficient
            winner[user_id] = []
            winner[user_id] += [user_bets[user_id]['T'] * winning_coefficient] 
            tien_thang = user_bets[user_id]['T'] * winning_coefficient

        elif sum(result) < 11 and user_bets[user_id]['X'] > 0:
            total_win += user_bets[user_id]['X'] * winning_coefficient
            winner[user_id] = []
            winner[user_id] += [user_bets[user_id]['X'] * winning_coefficient]
            tien_thang = user_bets[user_id]['T'] * winning_coefficient

    # Update user balances based on the game result
    for user_id in user_bets:
        if sum(result) >= 11 and user_bets[user_id]['T'] > 0:
            user_balance[user_id] += tien_thang 
        elif sum(result) < 11 and user_bets[user_id]['X'] > 0:
            user_balance[user_id] += tien_thang

    #bot.send_message(group_chat_id, f"{winner}")#######
    for user_id, diem in winner.items():
        user_ids =  bot.get_users(user_id).mention
        time.sleep(3)

        bot.send_message(group_chat_id, f"{user_ids} thắng {diem} điểm \n", time.sleep(1))#######

    # Save updated balances to the file
    save_balance_to_file()
    load_balance_from_file()
    
    mo_game.clear()
    time.sleep(3)

    text7 = bot.send_message(group_chat_id, f"""
Tổng thắng: {total_win}đ
Tổng thua: {total_bet_T + total_bet_X}đ
""", reply_markup=reply_markup)
    bot.send_message(channel_id, f"➤KẾT QUẢ XX: {' + '.join(str(x) for x in result)} = {total_score} điểm {calculate_tai_xiu(total_score)}")
    bot.delete_messages(group_chat_id, idtext4)
    bot.delete_messages(group_chat_id, idtext5)
    # Clear user bets
    user_bets.clear()
    winner.clear()


# Function to handle the game timing
def game_timer(message, grid, grtrangthai):
    mo_game[grid] = {'trangthai': 0}  # Initialize the user's bets if not already present
    mo_game[grid]['trangthai'] += grtrangthai
    text1 = bot.send_message(group_chat_id, "Bắt đầu ván mới! Có 45s để đặt cược.")
    time.sleep(15)
    text2 = bot.send_message(group_chat_id, "Còn 30s để đặt cược.")
    
    time.sleep(20)  # Wait for 120 seconds
    text3 = bot.send_message(group_chat_id, "Còn 10s để đặt cược.")
    bot.delete_messages(grid, text2.id)
    
    time.sleep(10)  # Wait for 120 seconds
    
    bot.delete_messages(grid, text1.id)
    bot.delete_messages(grid, text3.id)
    start_game(message)
        

# Function to handle user messages
@bot.on_message(filters.command(["t", "x"]) & filters.text)
def handle_message(_, message: Message):
    load_balance_from_file()
    chat_id = message.chat.id
    grid = chat_id
    # Check if the message is from the group chat
    if chat_id == group_chat_id:
        # Check if the message is a valid bet
        if message.text and message.text.upper() in ['/T ALL', '/X ALL'] or (message.text and message.text.upper()[1] in ['T', 'X'] and message.text[3:].isdigit()): 
            user_id = message.from_user.id
            ten_ncuoc = message.from_user.first_name
            bet_type = message.text.upper()[1]
            if message.text.upper() == '/T ALL' or message.text.upper() == '/X ALL':
                bet_amount = user_balance.get(user_id, 0)  # Use the entire balance
            else:
                bet_amount = int(message.text[3:])

            # Confirm the bet and check user balance
            confirm_bet(user_id, bet_type, bet_amount, ten_ncuoc, message)
            
        else:
            bot.send_message(chat_id, "Lệnh không hợp lệ. Vui lòng tuân thủ theo quy tắc cược.")
    if len(mo_game) == 0:
            grtrangthai = 1
            game_timer(message, grid, grtrangthai)


# Load user balances from the file
load_balance_from_file()

@bot.on_message(filters.command("diem"))
async def check_balance(_, message):
    load_balance_from_file()
    if message.reply_to_message:
        user_id = await extract_user(message)
        balance = user_balance.get(user_id, 0)
        mention = (await bot.get_users(user_id)).mention
        await bot.send_message(message.chat.id, f"👤 Số điểm của {mention} là {balance:,} điểm 💰")

    else:
        user_id = message.from_user.id
        balance = user_balance.get(user_id, 0)
        mention = (await bot.get_users(user_id)).mention
        await bot.send_message(message.chat.id, f"👤 Số điểm của {message.from_user.mention} là {balance:,} điểm 💰")


@bot.on_message(filters.command("tx"))
def start_taixiu(_, message):
    
    grtrangthai = int('1')
    chat_id = message.chat.id
    grid = chat_id
    if len(mo_game) == 0:
        grtrangthai = 1
        grid = chat_id
        #bot.send_message(chat_id, f"Bắt đầu ván mới")
        game_timer(message, grid, grtrangthai)
        
    else:
        
        total_bet_T = sum([user_bets[user_id]['T'] for user_id in user_bets])
        total_bet_X = sum([user_bets[user_id]['X'] for user_id in user_bets])
        bot.send_message(chat_id, f"Đang đợi đổ xúc xắc")
        soicau = [
        [
            InlineKeyboardButton("Soi cầu", url="https://t.me/kqtaixiu"),
            InlineKeyboardButton("Nạp - Rút", url="https://t.me/testtaixiu1bot"),
        ],]
        reply_markup = InlineKeyboardMarkup(soicau)
        bot.send_message(group_chat_id, f"""
┏ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
┣➤⚫️Tổng cược bên TÀI: {total_bet_T}đ
┣➤⚪️Tổng cược bên XỈU: {total_bet_X}đ
┗ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
""", reply_markup=reply_markup)



def loai_cau(total_score):
  return "Tài" if 11 <= total_score <= 18 else "Xỉu"
    

def ls_cau(result):
    total_score = sum(result)
    cau = loai_cau(total_score)
    if cau not in luu_cau:
        luu_cau[cau] = []
        luu_cau[cau].append(cau)
    
    # Automatically save the history to "kiemtraxs.txt"
    try:
        soicau_text = f"{cau}\n"

        # Define the encoding as 'utf-8' when opening the file
        with open("soicau.txt", "a", encoding='utf-8') as soicau_file: #, encoding='utf-8'ASCII
            soicau_file.write(soicau_text)
    except Exception as e:
        # Handle any potential errors, e.g., by logging them
        print(f"Error saving history: {str(e)}")

def load_cau_from_file():
    if os.path.exists("soicau.txt"):
        with open("soicau.txt", "r") as f:
            for line in f:
                cau_str = line.strip().split()
                cau = str(cau_str)
                luu_cau[cau] = [cau]

@bot.on_message(filters.command("delsc"))
async def delsoicau(_, message):
    chat_id = message.chat.id
    luu_cau.clear()

@bot.on_message(filters.command("soicau"))
async def show_game_options(_, message):
    chat_id = message.chat.id
    load_cau_from_file()
    #bot.send_message(chat_id, f"Soi cầu")
        
    soicau = [
        [
            InlineKeyboardButton("Soi cầu", url="https://t.me/kqtaixiu"),
            InlineKeyboardButton("Nạp - Rút", url="https://t.me/testtaixiu1bot"),
        ],]
    reply_markup = InlineKeyboardMarkup(soicau)
    await bot.send_message(chat_id, "Soi cầu", reply_markup=reply_markup)
    for scau, cau in reversed(luu_cau.items()):
        await bot.send_message(chat_id, f"{scau}")

def soi_cau():
    soicau = [
        [
            InlineKeyboardButton("Soi cầu", url="https://t.me/kqtaixiu"),
            InlineKeyboardButton("Nạp - Rút", url="https://t.me/testtaixiu1bot"),
        ],]
    reply_markup = InlineKeyboardMarkup(soicau)
##########################



async def main():


    await bot.start()
    print(
        """
-----------------
| Luna Started! |
-----------------
"""
    )
    await idle()


loop = get_event_loop()
loop.run_until_complete(main())
