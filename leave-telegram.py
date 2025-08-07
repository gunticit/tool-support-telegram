import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.functions.messages import DeleteHistoryRequest
from telethon.tl.functions.channels import LeaveChannelRequest, EditBannedRequest, InviteToChannelRequest
from telethon.tl.types import ChatBannedRights
from telethon.errors import UserIdInvalidError, UserNotParticipantError
import asyncio
from getpass import getpass


load_dotenv()

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')

if not api_id or not api_hash:
    print("❌ Vui lòng thiết lập biến môi trường api_id và api_hash trong file .env")
    exit(1)

api_id = int(api_id)
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
    print(f"🔑 Chuỗi session:\n{session_str}")

    while True:
        print("\n📋 Chọn chức năng:")
        print("1. Rời khỏi tất cả nhóm/kênh")
        print("2. Thêm người dùng vào nhóm/kênh")
        print("3. Xóa người dùng khỏi nhóm/kênh")
        print("4. Chặn người dùng khỏi nhóm/kênh")
        print("5. Xóa tất cả bot khỏi một nhóm/kênh")
        print("6. Tự động block tất cả bot trong các nhóm/kênh")
        print("7. Tự động block và xoá tất cả bot (trò chuyện riêng)")
        print("8. Thoát")

        choice = input("👉 Nhập lựa chọn: ").strip()

        if choice == "1":
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

        elif choice == "2":
            group = input("📛 Nhập username hoặc ID nhóm: ")
            user = input("👤 Nhập username hoặc ID người dùng để thêm: ")
            try:
                entity = await client.get_entity(group)
                user_to_add = await client.get_entity(user)
                await client(InviteToChannelRequest(channel=entity, users=[user_to_add]))
                print("✅ Đã thêm người dùng.")
            except Exception as e:
                print(f"❌ Lỗi khi thêm người dùng: {e}")

        elif choice == "3":
            group = input("📛 Nhập username hoặc ID nhóm: ")
            user = input("👤 Nhập username hoặc ID người dùng để xóa: ")
            try:
                entity = await client.get_entity(group)
                user_to_kick = await client.get_entity(user)
                rights = ChatBannedRights(until_date=None, view_messages=True)
                await client(EditBannedRequest(entity, user_to_kick, rights))
                print("✅ Đã xóa người dùng khỏi nhóm.")
            except Exception as e:
                print(f"❌ Lỗi khi xóa người dùng: {e}")

        elif choice == "4":
            group = input("📛 Nhập username hoặc ID nhóm: ")
            user = input("👤 Nhập username hoặc ID người dùng để chặn: ")
            try:
                entity = await client.get_entity(group)
                user_to_ban = await client.get_entity(user)
                rights = ChatBannedRights(
                    until_date=None,
                    view_messages=True,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_games=True,
                    send_inline=True,
                    embed_links=True
                )
                await client(EditBannedRequest(entity, user_to_ban, rights))
                print("✅ Đã chặn người dùng.")
            except Exception as e:
                print(f"❌ Lỗi khi chặn người dùng: {e}")

        elif choice == "5":
            group = input("📛 Nhập username hoặc ID nhóm: ")
            try:
                entity = await client.get_entity(group)
                participants = await client.get_participants(entity)
                bot_count = 0

                for user in participants:
                    if user.bot:
                        try:
                            rights = ChatBannedRights(until_date=None, view_messages=True)
                            await client(EditBannedRequest(entity, user, rights))
                            print(f"🦾 Đã xóa bot: {user.username or user.id}")
                            bot_count += 1
                        except Exception as e:
                            print(f"❌ Không thể xóa bot {user.username or user.id}: {e}")

                print(f"✅ Đã xóa {bot_count} bot khỏi nhóm.")
            except Exception as e:
                print(f"❌ Lỗi khi xử lý nhóm: {e}")

        elif choice == "6":
            dialogs = await client.get_dialogs()
            total_blocked = 0
            total_groups = 0

            for dialog in dialogs:
                if dialog.is_group or dialog.is_channel:
                    group = dialog.entity
                    try:
                        participants = await client.get_participants(group)
                        blocked_in_group = 0

                        for user in participants:
                            if user.bot:
                                try:
                                    rights = ChatBannedRights(
                                        until_date=None,
                                        view_messages=True,
                                        send_messages=True,
                                        send_media=True,
                                        send_stickers=True,
                                        send_gifs=True,
                                        send_games=True,
                                        send_inline=True,
                                        embed_links=True
                                    )
                                    await client(EditBannedRequest(group, user, rights))
                                    print(f"✅ Bot bị block trong {dialog.name}: {user.username or user.id}")
                                    blocked_in_group += 1
                                except Exception as e:
                                    print(f"❌ Không thể block bot {user.username or user.id} trong {dialog.name}: {e}")
                        if blocked_in_group > 0:
                            total_groups += 1
                            total_blocked += blocked_in_group
                    except Exception as e:
                        print(f"⚠️ Không thể truy cập nhóm {dialog.name}: {e}")

            print(f"\n🎉 Đã chặn {total_blocked} bot trong {total_groups} nhóm/kênh.")
        
        elif choice == "7":
            print("🚀 Đang quét và xoá từng lô 100 bot...")

            processed_ids = set()
            batch_size = 100
            pause_seconds = 300  # 5 phút

            while True:
                dialogs = await client.get_dialogs()
                bots_to_process = []

                for dialog in dialogs:
                    entity = dialog.entity
                    if (
                        hasattr(entity, 'bot') and entity.bot
                        and not (dialog.is_group or dialog.is_channel)
                        and entity.id not in processed_ids
                    ):
                        bots_to_process.append(entity)

                if not bots_to_process:
                    print("🎉 Không còn bot nào để xử lý.")
                    break

                batch = bots_to_process[:batch_size]
                print(f"\n⚙️ Đang xử lý {len(batch)} bot...")

                for bot in batch:
                    try:
                        # Block bot
                        await client(BlockRequest(bot.id))

                        # Delete chat
                        await client(DeleteHistoryRequest(
                            peer=bot,
                            max_id=0,
                            revoke=True
                        ))

                        print(f"✅ Đã block & xoá chat với bot: {bot.username or bot.id}")
                        processed_ids.add(bot.id)
                    except Exception as e:
                        print(f"❌ Lỗi khi xử lý bot {bot.username or bot.id}: {e}")
                        processed_ids.add(bot.id)  # Đánh dấu đã thử, không lặp lại

                if len(batch) < batch_size:
                    print("🎯 Đã xử lý toàn bộ bot hiện tại.")
                    break

                print(f"⏳ Đợi {pause_seconds} giây trước khi tiếp tục...")
                await asyncio.sleep(pause_seconds)

        elif choice == "8":
            print("👋 Tạm biệt!")
            break

        else:
            print("❗ Lựa chọn không hợp lệ, vui lòng thử lại.")

    await client.disconnect()

asyncio.run(main())
