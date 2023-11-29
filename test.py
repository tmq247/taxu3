import telebot
import requests
import random
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
import time
import atexit
from telebot import TeleBot, types
import pytz
import threading

# Thay thế giá trị dưới đây bằng token của bot Telegram của bạn
API_KEY = '6757521267:AAE5IHnHoESuOPViTNOJsxrYMlit6jtgbwQ'
# Khởi tạo bot
bot = telebot.TeleBot(API_KEY, parse_mode=None)
# Dùng trạng thái (state) để theo dõi quá trình cược
user_state = {}
# Dùng từ điển để lưu số dư của người dùng
user_balance = {}
# Tạo từ điển lưu lịch sử cược và lịch sử rút tiền
user_bet_history = {}
user_withdraw_history = {}
# Tạo từ điển gitcodes
used_gitcodes = []
gitcode_amounts = {}
user_pending_gitcodes = {}
# Define a separate dictionary to track user game states
user_game_state = {}
# Dictionary to store user balances (user_id: balance)
user_balances = {}
# Dictionary to store user bets
user_bets = {}  # {user_id: {"bet_type": "", "amount": 0, "chosen_number": ""}}
# Inside your message handler function
vietnam_timezone = pytz.timezone(
    'Asia/Ho_Chi_Minh')  # Define the Vietnam timezone
# Get the current time in Vietnam timezone
current_time_vietnam = datetime.now(
    tz=vietnam_timezone).strftime("%Y-%m-%d %H:%M:%S")
group_chat_id2 = "-1002121532989"  # Replace with your second group chat ID
# Định nghĩa id của nhóm mà bạn muốn gửi thông báo
group_chat_id = '-1002121532989'
def get_user_info(user_id):
  try:
    user = bot.get_chat(user_id)
    return user
  except telebot.apihelper.ApiException as e:
    print("Error fetching user info:", e)
    return None


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


# Gọi hàm load_balance_from_file khi chương trình chạy để tải số dư từ tệp
load_balance_from_file()


# Hàm xử lý khi bot bị tắt hoặc lỗi, để lưu số dư vào tệp id.txt trước khi thoát
def on_exit():
  save_balance_to_file()


# Xử lý khi bot bị tắt hoặc lỗi
atexit.register(save_balance_to_file)

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

# Read Gitcodes from the file
read_gitcodes()

# Define the admin's user ID
admin_user_id = 6337933296 or 6630692765 or 5838967403 or 6050066066  # Replace with the actual admin user ID

@bot.message_handler(commands=['regcode'])
def create_gitcode_handler(message):
    # Check if the user is the admin
    if message.from_user.id == admin_user_id:
        bot.reply_to(message, "Vui lòng nhập số tiền cho gitcode:")
        bot.register_next_step_handler(message, process_gitcode_amount)
    else:
        bot.reply_to(message, "Bạn không có quyền thực hiện lệnh này.")

def process_gitcode_amount(message):
    try:
        amount = int(message.text)
        formatted_amount = "{:,.0f}".format(amount).replace(".", ",")
        gitcode = create_gitcode(amount)
        bot.reply_to(message, f"Đã tạo gitcode thành công. Gitcode của bạn là: {gitcode} ({formatted_amount} đồng).")
    except ValueError:
        bot.reply_to(message, "Số tiền không hợp lệ.")

@bot.message_handler(func=lambda message: message.text.lower() == 'code')
def naptien_gitcode(message):
    bot.reply_to(message, "Bạn Đã Chọn Nhập Code\nBạn Hãy Nhập Code\n➡️VD: ABCD")
    bot.register_next_step_handler(message, process_naptien_gitcode)

def process_naptien_gitcode(message):
    load_balance_from_file()
    gitcode = message.text
    user_id = message.from_user.id  # Get the user's ID
    if gitcode in gitcode_amounts:
        amount = gitcode_amounts[gitcode]

        # Check if the user's balance exists in the dictionary, initialize it if not
        if user_id not in user_balance:
            user_balance[user_id] = 0

        user_balance[user_id] += amount
        remove_gitcode(gitcode)
        del gitcode_amounts[gitcode]
        bot.reply_to(message, f"Gitcode Thành Công!\nSố dư của bạn là: {user_balance[user_id]:,}đ.\n💹Chúc Bạn May Mắn Nhé💖")
        
        # Sử dụng phương thức send_message để gửi thông báo vào nhóm
        bot.send_message(group_chat_id, f"""
Người chơi {message.from_user.first_name} 
User: {user_id}
Đã Nạp: {amount:,}đ bằng Gitcode.""")
        # Save the updated balance to the file
        save_balance_to_file()
        load_balance_from_file()
    else:
        bot.reply_to(message, "Gitcode không hợp lệ hoặc đã được sử dụng.")





# Hàm xử lý chuyển tiền và cập nhật số dư của cả người gửi và người được chuyển
def deduct_balance(sender_id, recipient_id, amount):
    # Kiểm tra xem cả sender_id và recipient_id có tồn tại trong user_balance không
    if sender_id not in user_balance or recipient_id not in user_balance:
        return False

    # Kiểm tra xem số tiền cần chuyển có lớn hơn 0 và không vượt quá số dư của người gửi
    if amount <= 0 or user_balance[sender_id] < amount:
        return False

    # Trừ số tiền từ số dư của người gửi và cộng cho người được chuyển
    user_balance[sender_id] -= amount
    user_balance[recipient_id] += amount

    # Lưu số dư vào tệp văn bản
    save_balance_to_file()

    return True


@bot.message_handler(commands=['tangdiem'])
def chuyentien_money(message):
    load_balance_from_file()
    try:
        # Parse thông tin người dùng và số tiền từ tin nhắn
        user_id, amount = map(int, message.text.split()[1:3])

        # Kiểm tra xem người gửi có đủ số dư để thực hiện chuyển khoản không
        sender_id = message.from_user.id
        sender_name = message.from_user.first_name  # Lấy tên của người gửi

        if sender_id not in user_balance or user_balance[sender_id] < amount:
            bot.reply_to(message, "Bạn không có đủ số dư để chuyển khoản này.")
            return

        # Thực hiện chuyển khoản và thông báo kết quả
        if deduct_balance(sender_id, user_id, amount):
            recipient_name = bot.get_chat(user_id).first_name  # Lấy tên của người được chuyển
            bot.reply_to(message, f"Chuyển khoản thành công! {amount:,} chuyển đến người dùng {recipient_name}.")
            bot.send_message(user_id, f"Bạn đã nhận được {amount:,}đ được chuyển từ {sender_name}, id người dùng là: {sender_id}.")
        else:
            bot.reply_to(message, "Không hợp lệ. Sử dụng /chuyentien <user_id> <số tiền>")
    except Exception as e:
        bot.reply_to(message, """
Tạo lệnh để chuyển tiền của mình cho ID người chơi khác:
    
/chuyentien [dấu cách] ID nhận tiền [dấu cách] số tiền
    
VD: /chuyentien 987654321 10000""")


@bot.message_handler(commands=["cdiem"])
def set_balance(msg):
  if msg.from_user.id == 6337933296 or 6630692765 or 5838967403 or 6050066066:
    bot.reply_to(msg, """
🔭Nhập user ID của thành viên🔨
        """)
    user_state[msg.from_user.id] = "set_user_id"
  else:
    bot.reply_to(msg, "Bạn không có quyền sử dụng lệnh này.")


@bot.message_handler(func=lambda message: message.from_user.id in user_state
                     and user_state[message.from_user.id] == "set_user_id")
def set_user_balance(msg):
  try:
    user_id = int(msg.text)
    bot.reply_to(
        msg, """
⏲Nhập số tiền muốn cộng hoặc trừ🪤 
🚬(ví dụ: +1000 hoặc -1000)🎚
🫡 Kèm Nội Dung 👊🏽
        """)
    user_state[msg.from_user.id] = (user_id, "setbalance")
  except ValueError:
    bot.reply_to(msg, "Vui lòng nhập một user ID hợp lệ.")


@bot.message_handler(func=lambda message: message.from_user.id in user_state
                     and user_state[message.from_user.id][1] == "setbalance")
def update_balance(msg):
  load_balance_from_file()
  try:
    user_input = msg.text.split()
    if len(user_input) < 2:
      bot.reply_to(msg, "Vui lòng nhập số tiền và nội dung cần kèm")
      return

    balance_change = int(user_input[0])
    user_id, _ = user_state[msg.from_user.id]
    current_balance = user_balance.get(user_id, 0)
    new_balance = current_balance + balance_change
    user_balance[user_id] = new_balance
    del user_state[msg.from_user.id]
    save_balance_to_file()
    load_balance_from_file()

    # Lấy nội dung từ tin nhắn của người chơi
    user_message = " ".join(user_input[1:])
    # Gửi thông báo cập nhật thành công cho người chơi kèm theo nội dung
    notification_message = f"""
🫥Bạn Đã Nạp Tiền Thành Công🤖
🫂SD Hiện Tại: {new_balance:,}đ🐥
👾Nội Dung: {user_message} 🫶🏽
🐝Chúc Bạn Chơi Game Vui Vẻ🐳
"""
    bot.send_message(user_id, notification_message)

    # Gửi thông báo đến nhóm về việc có người chơi đặt cược
    group_chat_id = -1002121532989  # Thay thế bằng ID thực sự của nhóm chat
    bot.send_message(chat_id=group_chat_id, text=notification_message
                     )  # Sử dụng notification_message thay cho result_message
  except ValueError:
    bot.reply_to(msg, "Vui lòng nhập một số tiền hợp lệ.")




# Hàm hiển thị menu chính
@bot.message_handler(commands=["start"])
def show_main_menu(msg):
  user_id = msg.from_user.id

  # Check if the user is already in the user_balance dictionary
  if user_id not in user_balance:
    user_balance[user_id] = 0  # Set initial balance to 0 for new users
    save_balance_to_file()  # Save user balances to the text file

  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  rows = [
      ["👤 Tài Khoản", "🎲 Soi cầu"],
      ["💸 Rút Tiền", "💵 Nạp Tiền"],
      ["📈 Lịch Sử Cược", "📊 Lịch Sử Rút"],
      ["📤Chuyển Tiền📪", "🫧Nhập CODE💶"],
  ]

  for row in rows:
    markup.row(*[types.KeyboardButton(button_text) for button_text in row])

  # Send a message with a photo link
  photo_url = "https://gamebaidoithuong.zone/wp-content/uploads/2021/12/game-bai-doi-thuong-gamebaidoithuongzone-3.jpg"
  caption = """
<b>Chào Mừng Bạn Đã Đến Với Sân Chơi Giải Trí</b>
      <code>GAME TAXU</code>
<b>Game Xanh Chính Nói Không Với Chỉnh Cầu</b>

👉 <strong>Cách chơi đơn giản, tiện lợi</strong> 🎁

👉 <b>Nạp rút nhanh chóng, đa dạng hình thức</b> 💸

👉 <b>Có Nhiều Phần Quà Dành Cho Người Chơi Mới</b> 🤝

👉 <b>Đua top thật hăng, nhận quà cực căng</b> 💍

👉 <b>An toàn, bảo mật tuyệt đối</b> 🏆

⚠️ <b>Chú ý đề phòng lừa đảo, Chúng Tôi Không inbox Trước</b> ⚠️
"""
  bot.send_photo(msg.chat.id,
                 photo_url,
                 caption=caption,
                 reply_markup=markup,
                 parse_mode='HTML')


# Hàm xử lý khi người dùng chọn nút
@bot.message_handler(func=lambda message: message.text == "👤 Tài Khoản")
#@bot.message_handler(commands=["diem"])
def handle_check_balance_button(msg):
  load_balance_from_file()
  check_balance(msg)

@bot.message_handler(func=lambda message: message.text == "💸 Rút Tiền")
def handle_withdraw_balance_button(msg):
  withdraw_balance(msg)

@bot.message_handler(func=lambda message: message.text == "🎲 Soi cầu")
def handle_game_list_button(msg):
  show_game_options(msg)

@bot.message_handler(func=lambda message: message.text == "💵 Nạp Tiền")
def handle_deposit_button(msg):
  napwithdraw_balance(msg)

@bot.message_handler(func=lambda message: message.text == "📈 Lịch Sử Cược")
def handle_bet_history_button(msg):
  show_bet_history(msg)

@bot.message_handler(func=lambda message: message.text == "📊 Lịch Sử Rút")
def handle_withdraw_history_button(msg):
  show_withdraw_history(msg)

@bot.message_handler(func=lambda message: message.text == "📤Chuyển Tiền📪")
def handle_chuyentien_money_button(msg):
    chuyentien_money(msg)

@bot.message_handler(func=lambda message: message.text == "🫧Nhập CODE💶")
def handle_naptien_gitcode_button(msg):
    naptien_gitcode(msg)

def show_game_options(msg):
   bot.send_message(msg.chat.id, "Vào @kqtaixiu để xem lịch sử cầu")
   
# Hàm kiểm tra số dư
def check_balance(msg):
  user_id = msg.from_user.id
  balance = user_balance.get(user_id, 0)
  #photo_link = "https://scontent.fdad1-4.fna.fbcdn.net/v/t39.30808-6/374564260_311252494902338_4501893302206805342_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=49d041&_nc_ohc=ypCR3gJKO84AX8vBaGO&_nc_oc=AQkV2yigf-t0BVkyWvCT0B1QFbLFdXx-cDg9Lal65LdSPI_AvgJdmKKS0ZpvItzfP3rlfqLxFP3pFitVvMbCHjGI&_nc_ht=scontent.fdad1-4.fna&oh=00_AfCW5YKUPRq6IRYMDCqhbPKQYFlUoIbVsuCjDAmzsr50VA&oe=64F55781"  # Thay thế bằng đường dẫn URL của hình ảnh
  #bot.send_photo(msg.chat.id,
  #               photo_link,
  #               caption=f"""
#👤 <b>Tên tài khoản</b>: <code>{msg.from_user.first_name}</code>
#💳 <b>ID Tài khoản</b>: <code>{msg.from_user.id}</code>
#💰 <b>Số dư của bạn</b>: {balance:,} đ
#        """,
#                 parse_mode='HTML')
  bot.send_message(msg.chat.id, f"""
👤 Tên tài khoản: {msg.from_user.first_name}
💳 ID Tài khoản: {msg.from_user.id}
💰 Số dư của bạn: {balance:,} đ
        """)


#hàm rút tiền
def create_withdraw_method_keyboard():
  markup = InlineKeyboardMarkup()
  momo_button = InlineKeyboardButton("Rút qua MoMo", callback_data="momo")
  bank_button = InlineKeyboardButton("Rút qua ngân hàng", callback_data="bank")
  markup.row(momo_button, bank_button)  # Đặt cả hai nút trên cùng một hàng
  return markup


# Hàm rút tiền tài khoản
def withdraw_balance(msg):
  chat_id = msg.chat.id
  user_id = msg.from_user.id
  user_state[user_id] = "withdraw_method"
  user_game_state.pop(user_id, None)  # Clear game state to avoid conflicts

  reply_markup = create_withdraw_method_keyboard(
  )  # Tạo bàn phím cho phương thức rút
  bot.send_message(chat_id,
                   "Vui lòng nhắn tin riêng với bot")
  bot.send_message(user_id,
                   "Chọn phương thức rút tiền:",
                   reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda call: call.data in ["momo", "bank"])
def handle_withdrawal_method_selection(call):
  user_id = call.from_user.id

  if call.data == "momo":
    user_state[user_id] = "momo_account"
    bot.send_message(user_id, "Nhập số MoMo của bạn:")
  elif call.data == "bank":
    user_state[user_id] = "bank_account"
    bot.send_message(
        user_id, """
Nhập thông tin tài khoản ngân hàng của bạn:
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

  bot.answer_callback_query(call.id, "Bạn đã chọn phương thức rút tiền.")


@bot.message_handler(
    func=lambda message: message.from_user.id in user_state and user_state[
        message.from_user.id] in ["momo_account", "bank_account"])
def process_account_info(msg):
  try:
    account_info = msg.text
    user_id = msg.from_user.id

    if user_state[user_id] == "momo_account":
      user_state[user_id] = (account_info, "withdraw_amount_momo")
      bot.reply_to(
          msg, """
❗️Nhập số tiền bạn muốn rút qua MoMo💮
🚫VD: 50.000 - 50.000.000🚮
            """)
    elif user_state[user_id] == "bank_account":
      user_state[user_id] = (account_info, "withdraw_amount_bank")
      bot.reply_to(
          msg, """
❗️Nhập số tiền bạn muốn rút qua ngân hàng💮
🚫VD: 50.000 - 50.000.000🚮
            """)

  except ValueError:
    pass


@bot.message_handler(func=lambda message: message.from_user.id in user_state
                     and user_state[message.from_user.id][1] in
                     ["withdraw_amount_momo", "withdraw_amount_bank"])
def process_withdraw_amount(msg):
  try:
    account_info, withdraw_amount_type = user_state[msg.from_user.id]
    withdraw_amount = int(msg.text)
    user_id = msg.from_user.id
    user_balance_value = user_balance.get(user_id, 0)

    if withdraw_amount < 50000:
      bot.reply_to(
          msg, """
🖇 Số tiền rút phải lớn hơn hoặc bằng 50,000 đồng.🗳
            """)
      del user_state[user_id]
      return

    if withdraw_amount > user_balance_value:
      bot.reply_to(
          msg, """
🌀Số dư của bạn không đủ💳
🪫Vui Lòng 🔎/naptiep🔍 Có Số Dư Mới💎
            """)
      del user_state[user_id]
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
            bot.reply_to(msg, "Số dư không đủ để rút số tiền này.")
        else:
          f.write(line)

    formatted_balance = "{:,.0f} đ".format(user_balance_value)
    account_type = "MoMo" if withdraw_amount_type == "withdraw_amount_momo" else "ngân hàng"
    bot.reply_to(
        msg, f"""
⏺Lệnh rút: {withdraw_amount:,} VNĐ🔚
✅Của bạn về {account_type}: {account_info} được hệ thống check🔚
☢️Số tiền còn lại của bạn: {formatted_balance}
            """)

    request_message = f"""
➤Tên Người Rút: {msg.from_user.first_name} 
➤Yêu Cầu Rút: {withdraw_amount:,} VNĐ 
➤Về {account_type}: {account_info}
        """
    another_bot_token = "6755926001:AAGD0Gc9xMomJgnfhwjeIENF9XO0reeST1o"
    another_bot_chat_id = "6337933296"
    requests.get(
        f"https://api.telegram.org/bot{another_bot_token}/sendMessage?chat_id={another_bot_chat_id}&text={request_message}"
    )

    del user_state[user_id]

    user_withdraw_history.setdefault(user_id, []).append(
        (account_info, withdraw_amount))
    time.sleep(10)
    user_notification = f"""
📬 Rút tiền thành công!
⏺ Số tiền rút: {withdraw_amount:,} VNĐ
📈 Số dư còn lại: {formatted_balance}
        """
    bot.send_message(user_id, user_notification)

  except ValueError:
    pass



# Hàm lệnh nạp tiền
def deposit_info(msg):
  user_id = msg.from_user.id
  momo_account = "034xxxxxx"
  username = msg.from_user.username or msg.from_user.first_name

  photo_link = "https://scontent.fdad1-3.fna.fbcdn.net/v/t39.30808-6/368953112_304417105585877_8104665371433145272_n.jpg?_nc_cat=104&ccb=1-7&_nc_sid=730e14&_nc_ohc=9tNmHpvwO7UAX97Ml6f&_nc_ht=scontent.fdad1-3.fna&oh=00_AfDCHSKEY4xF2TL3e4YhEjvP0kh4uVR_4cEPa_GyN5hzXA&oe=64E49255"  # Replace with the actual image link

  # Creating the caption
  caption = f"""
🏧<b>Phương Thức Nạp Bank</b>🏧
💰<b>MB BANK _ MOMO</b>💰
🔊Tài Khoản: <code>{momo_account}</code>🔚
🔊Nội Dung: <code>naptien_{msg.from_user.id}</code>🔚
🔊<b>Min Nạp: 10.000k Min Rút: 100.000k</b>
🔊<b>Min Nạp: 10.000 - 3.000.000</b>🔚
🔊<b>Vui lòng ghi đúng nội dung tiền vào 5s.</b>🔚
🔊<b>Không Hỗ Trợ Lỗi Nội Dung.</b>🔚
🔊<b>NẠP NHANH QR PHÍA BÊN DƯỚI NHÉ</b> 🔚
    """

  # Sending the caption and photo
  bot.send_message(msg.chat.id, caption, parse_mode='HTML')
  bot.send_photo(msg.chat.id, photo_link)


##############################

#@bot.message_handler(commands=["sc"])
def show_game_options(msg):
   chat_id = msg.chat.id
   bot.send_message(chat_id, "Soi cầu", reply_markup=soi_cau())

def soi_cau():
  markup = InlineKeyboardMarkup()
  momo_button = InlineKeyboardButton("Soi cầu", url="https://t.me/kqtaixiu")
  bank_button = InlineKeyboardButton("Nạp - Rút", url="https://t.me/testtaixiu1bot")
  markup.row(momo_button, bank_button)  # Đặt cả hai nút trên cùng một hàng
  return markup

#hàm rút tiền
def napcreate_withdraw_method_keyboard():
  markup = InlineKeyboardMarkup()
  momo_button = InlineKeyboardButton("Nạp qua MoMo", callback_data="nạp momo")
  bank_button = InlineKeyboardButton("Nạp qua ngân hàng", callback_data="nạp bank")
  markup.row(momo_button, bank_button)  # Đặt cả hai nút trên cùng một hàng
  return markup


# Hàm rút tiền tài khoản
def napwithdraw_balance(msg):
  chat_id = msg.chat.id
  user_id = msg.from_user.id
  user_state[user_id] = "napwithdraw_method"
  user_game_state.pop(user_id, None)  # Clear game state to avoid conflicts

  reply_markup = napcreate_withdraw_method_keyboard(
  )  # Tạo bàn phím cho phương thức rút
  bot.send_message(chat_id,
                   "Vui lòng nhắn tin riêng với bot")
  bot.send_message(user_id,
                   "Chọn phương thức nạp tiền:",
                   reply_markup=reply_markup)
  

@bot.callback_query_handler(func=lambda call: call.data in ["nạp momo", "nạp bank"])
def naphandle_withdrawal_method_selection(call):
  user_id = call.from_user.id

  if call.data == "nạp momo":
    user_state[user_id] = "napmomo_account"
    bot.send_message(user_id, "Nhập số MoMo của bạn:")
  elif call.data == "nạp bank":
    user_state[user_id] = "napbank_account"
    bot.send_message(
        user_id, """
Nhập thông tin tài khoản ngân hàng của bạn:
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
❗️ Nạp min 50K
""")

  bot.answer_callback_query(call.id, "Bạn đã chọn phương thức nạp tiền.")


@bot.message_handler(
    func=lambda message: message.from_user.id in user_state and user_state[
        message.from_user.id] in ["napmomo_account", "napbank_account"])
def napprocess_account_info(msg):
  try:
    account_info = msg.text
    user_id = msg.from_user.id

    if user_state[user_id] == "napmomo_account":
      user_state[user_id] = (account_info, "withdraw_amount_napmomo")
      bot.reply_to(
          msg, """
❗️Nhập số tiền bạn muốn nạp qua MoMo💮
🚫VD: 10.000 - 50.000.000🚮
            """)
    elif user_state[user_id] == "napbank_account":
      user_state[user_id] = (account_info, "withdraw_amount_napbank")
      bot.reply_to(
          msg, """
❗️Nhập số tiền bạn muốn nạp qua ngân hàng💮
🚫VD: 10.000 - 50.000.000🚮
            """)

  except ValueError:
    pass


@bot.message_handler(func=lambda message: message.from_user.id in user_state
                     and user_state[message.from_user.id][1] in
                     ["withdraw_amount_napmomo", "withdraw_amount_napbank"])
def napprocess_withdraw_amount(msg):
  try:
    account_info, withdraw_amount_type = user_state[msg.from_user.id]
    withdraw_amount = int(msg.text)
    user_id = msg.from_user.id
    user_balance_value = user_balance.get(user_id, 0)

    if withdraw_amount < 10000:
      bot.reply_to(
          msg, """
🖇 Số tiền nạp phải lớn hơn hoặc bằng 10,000 đồng.🗳
            """)
      del user_state[user_id]
      return


    # Trừ số tiền từ số dư của người chơi
    #user_balance_value += withdraw_amount
    #user_balance[user_id] = user_balance_value

    #with open("id.txt", "r") as f:
      #lines = f.readlines()

    #with open("id.txt", "w") as f:
      #for line in lines:
        #user_id_str, balance_str = line.strip().split()
        #if int(user_id_str) == user_id:
         # balance = int(balance_str)
          #if withdraw_amount <= balance:
          #balance += withdraw_amount
          #f.write(f"{user_id} {balance}\n")
          #else:
            #bot.reply_to(msg, "Số dư không đủ để nạp số tiền này.")
        #else:
          #f.write(line)

    formatted_balance = "{:,.0f} đ".format(user_balance_value)

    account_type = "MoMo" if withdraw_amount_type == "withdraw_amount_napmomo" else "ngân hàng"
    bot.reply_to(
        msg, f"""
⏺Lệnh nạp: {withdraw_amount:,} VNĐ🔚
✅Của bạn từ {account_type}: {account_info} được hệ thống check🔚
☢️Số điểm trước khi nạp của bạn: {user_balance_value-withdraw_amount:,}
            """)
    momo_account = "034xxxxxx"
    caption = f"""
🏧Phương Thức Nạp Bank🏧
💰MB BANK _ MOMO💰
🔊Tài Khoản: {momo_account}🔚
🔊Nội Dung: naptien_{msg.from_user.id}🔚
🔊Min Nạp: 10.000k Min Rút: 100.000k
🔊Min Nạp: 10.000 - 3.000.000🔚
🔊Vui lòng ghi đúng nội dung tiền.🔚
🔊Vui lòng chụp lại bill chuyển tiền.🔚
🔊Không Hỗ Trợ Lỗi Nội Dung.🔚
🔊NẠP NHANH QR PHÍA BÊN DƯỚI NHÉ 🔚
    """
    bot.send_message(user_id, caption)

    request_message = f"""
➤Tên Người Nạp: {msg.from_user.first_name} 
➤ID Người Nạp: {msg.from_user.id} 
➤Yêu Cầu Nạp: {withdraw_amount:,} VNĐ 
➤Từ {account_type}: {account_info}
        """
    another_bot_token = "6755926001:AAGD0Gc9xMomJgnfhwjeIENF9XO0reeST1o"
    another_bot_chat_id = "6337933296"
    requests.get(
        f"https://api.telegram.org/bot{another_bot_token}/sendMessage?chat_id={another_bot_chat_id}&text={request_message}"
    )
    bot.send_message(group_chat_id, request_message)

    del user_state[user_id]

    user_withdraw_history.setdefault(user_id, []).append(
        (account_info, withdraw_amount))
    #time.sleep(10)
    #user_notification = f"""
#📬 Nạp tiền thành công!
#⏺ Số tiền nạp: {withdraw_amount:,} VNĐ
#📈 Số điểm hiện tại: {formatted_balance}
 #       """
   # bot.send_message(user_id, user_notification)
    

  except ValueError:
    pass





################################
# Hàm xem lịch sử cược
def show_bet_history(msg):
  user_id = msg.from_user.id
  bet_history = user_bet_history.get(user_id, [])
  if not bet_history:
    bot.reply_to(
        msg, """
⏩Bạn Vào @kqsoicau☑️.
⏩Để Kiểm Tra Lịch Sử Cược Nhé.
        """)
  else:
    history_text = "Lịch sử cược:\n\n"
    for bet_info in bet_history:
      if len(bet_info) == 3:
        amount, result, outcome = bet_info
        history_text += f"""
Số tiền: {amount}
Kết quả: {result}
Kết quả cuối cùng: {outcome}
                """
      else:
        history_text += "Dữ liệu lịch sử cược không hợp lệ.\n"
    bot.reply_to(msg, history_text)


# Hàm xem lịch sử rút tiền
def show_withdraw_history(msg):
  user_id = msg.from_user.id
  withdraw_history = user_withdraw_history.get(user_id, [])
  if not withdraw_history:
    bot.reply_to(
        msg, """
🚥Bạn chưa có lịch sử rút tiền🔙
🛰/ruttien - Lệnh rút tiền.
    """)
  else:
    history_text = """
Lịch sử rút tiền:
🎑🎑🎑🎑🎑🎑🎑
        """
    for withdraw_info in withdraw_history:
      momo_account, amount = withdraw_info
      history_text += f"""
🧑🏽‍💻Số Tiền Rút: {amount:,} VNĐ 
👑Số Momo: {momo_account}
"""
    bot.reply_to(msg, history_text)






def lsxoso_add_bet_to_history(user_id, bet_type, bet_amount, chosen_number):
    if user_id not in user_bet_history:
        user_bet_history[user_id] = []

    vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time_utc = datetime.utcnow()
    current_time_vietnam = current_time_utc.astimezone(vietnam_timezone).strftime("%Y-%m-%d %H:%M:%S")

    user_bet_history[user_id].append({
        "bet_type": bet_type,
        "bet_amount": bet_amount,
        "chosen_number": chosen_number,
        "timestamp": current_time_vietnam  # Save the timestamp in Vietnam timezone
    })

    # Automatically save the history to "kiemtraxs.txt"
    try:
        history_text = f"Loại cược: {bet_type}\n"
        history_text += f"User ID: {user_id}\n"
        history_text += f"Số tiền đặt cược: {bet_amount}đ\n"
        history_text += f"Số đã chọn: {chosen_number}\n"
        history_text += f"Thời Gian: {current_time_vietnam}\n\n"

        # Define the encoding as 'utf-8' when opening the file
        with open("kiemtraxs.txt", "a", encoding='utf-8') as history_file:
            history_file.write(history_text)
    except Exception as e:
        # Handle any potential errors, e.g., by logging them
        print(f"Error saving history: {str(e)}")


@bot.message_handler(commands=['lsxoso'])
def lsxoso(message):
    user_id = message.from_user.id
    if user_id in user_bet_history and len(user_bet_history[user_id]) > 0:
        # Display the betting history to the user
        # (no need to save it again here)
        history_text = "Lịch Sử Cược XSMB:\n\n"
        vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')

        for bet in user_bet_history[user_id]:
            try:
                timestamp_utc = datetime.strptime(bet["timestamp"], "%Y-%m-%d %H:%M:%S")
                timestamp_vietnam = timestamp_utc.astimezone(vietnam_timezone)

                history_text += f"Loại cược: {bet['bet_type']}\n"
                history_text += f"User ID: {user_id}\n"
                history_text += f"Số tiền đặt cược: {bet['bet_amount']}đ\n"
                history_text += f"Số đã chọn: {bet['chosen_number_formatted']}\n"
                history_text += f"Thời Gian: {timestamp_vietnam.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            except Exception as e:
                print(f"Error processing bet: {str(e)}")
                continue

        bot.send_message(user_id, history_text)
    else:
        bot.send_message(user_id, "Bạn chưa có lịch sử cá cược.")

#chạy bot.polling()
bot.polling()
