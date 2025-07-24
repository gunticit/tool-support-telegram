import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import LeaveChannelRequest
import asyncio
from getpass import getpass

load_dotenv()

# 🛠 API ID và HASH của bạn
api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')

if not api_id or not api_hash:
    print("❌ Vui lòng thiết lập biến môi trường api_id và api_hash trong file .env")
    exit(1)

api_id = int(api_id)

# 📱 Nhập số điện thoại (bắt buộc định dạng quốc tế)
phone_number = input("📱 Nhập số điện thoại của bạn (vd: +84901234567): ")

client = TelegramClient(StringSession(), api_id, api_hash)

async def main():
    try:
        await client.start(
            phone=lambda: phone_number,
            code_callback=lambda: input("🔐 Nhập mã xác thực Telegram gửi về: "),
            password=lambda: getpass("🔑 Nhập mật khẩu 2 bước (nếu có, Enter nếu không): ")
        )
    except Exception as e:
        print(f"❌ Không thể đăng nhập: {e}")
        return

    print("✅ Đăng nhập thành công!")
    session_str = client.session.save()
    print(f"🔑 Chuỗi session (có thể copy lưu dùng lần sau):\n{session_str}")

    dialogs = await client.get_dialogs()
    count = 0

    for dialog in dialogs:
        if dialog.is_group or dialog.is_channel:
            try:
                print(f"🚪 Đang rời khỏi: {dialog.name}")
                await client(LeaveChannelRequest(dialog.entity))
                count += 1
            except Exception as e:
                print(f"❌ Không thể rời {dialog.name}: {e}")

    print(f"🎉 Đã rời khỏi {count} nhóm/kênh.")
    await client.disconnect()

asyncio.run(main())
