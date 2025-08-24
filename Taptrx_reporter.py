import os
import random
import asyncio
import time
import re
from pyrogram import Client, filters, errors
from pyrogram.raw import functions, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

api_id = 12134308
api_hash = '6d18eb5e69cfac7dfda54ce0fef6b07b'
bot_token = '7929810959:AAFbc736ro5MrBljqKFxUDpd3Soq5cNa_zM'
owner_id = 7193257772  # Owner's numeric ID

def load_admin_ids():
    """
    Load admin IDs from Admin.txt as a list of integers.
    If file does not exist, return an empty list.
    """
    if os.path.isfile('Admin.txt'):
        with open('Admin.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Convert each non-empty line to an integer
            return [int(line.strip()) for line in lines if line.strip().isdigit()]
    return []

def save_admin_ids(admin_ids):
    """
    Save the given list of admin IDs (as integers) to Admin.txt.
    """
    with open('Admin.txt', 'w', encoding='utf-8') as f:
        for admin in admin_ids:
            f.write(f"{admin}\n")

# Global admin list loaded from file.
# Always ensure the owner_id is included.
bot_admins = list(set(load_admin_ids() + [owner_id]))

sleeping = 2  
step = None  
tempClient = dict() 
isWorking = list()  

tempReportLink_other = ""
tempReportLink_group_other = ""
tempReportLink_group_spam = ""
tempReportLink_group_pornography = ""
tempReportLink_group_violence = ""
tempReportLink_group_illegal = ""
tempReportLink_scam = ""
tempReportLink_personal = ""
tempReportLink_copyright = ""
tempReportLink_child_abuse = ""

# Global variable lock to prevent multiple operations at the same time.
current_operation_admin = None

# Preset report texts for pornography reports (20 texts)
porn_report_texts = [
    "This channel is distributing child sexual abuse material, leaked private photos, and pornography. Urgent removal needed.",
    "Sharing explicit pornography, leaked intimate images of women, and child exploitation content. Please ban now.",
    "Contains illegal child pornography, sexual exploitation, and leaked nude photos. Immediate action required.",
    "Posting obscene sexual abuse videos of minors and leaked girls’ private pictures. Remove this channel immediately.",
    "Spreading pornographic material along with leaked personal nude images without consent. Ban this account urgently.",
    "Distributing illegal pornography and child sexual exploitation content. Urgent moderation required.",
    "Sharing leaked private photos of girls and minors combined with explicit pornography. Immediate ban.",
    "This account is involved in child sexual abuse, leaked women’s intimate pictures, and hardcore pornography. Remove it.",
    "Uploading leaked nude pictures of minors and obscene sexual videos. Please take immediate action.",
    "Posting child pornography, sexual exploitation, and leaked personal content without consent. Ban now.",
    "Distributing obscene sexual material of minors and leaked private photos of women. Remove urgently.",
    "Sharing pornography with illegal leaked intimate photos of underage girls. Immediate review needed.",
    "Contains explicit sexual abuse of children and leaked private sexual images. Please ban this account.",
    "Posting obscene pornography mixed with leaked private nude photos without consent. Urgent removal.",
    "Distributing illegal sexual content involving minors and leaked women’s pictures. Remove now.",
    "This channel spreads leaked nude content of girls and minors with hardcore pornography. Ban urgently.",
    "Uploading child sexual abuse content and leaked intimate images of women. Immediate ban required.",
    "Contains obscene pornography and leaked private photos of underage individuals. Remove immediately.",
    "Sharing leaked personal nude pictures and child sexual exploitation material. Urgent removal.",
    "Distributing explicit pornography along with illegal leaked sexual images of minors. Please ban."
]

if not os.path.isdir('sessions'):
    os.mkdir('sessions')

if not os.path.isfile('app.txt'):
    with open('app.txt', 'w', encoding='utf-8') as file:
        file.write(f"{api_id} {api_hash}")

def parse_message_link(link: str):
    """
    این تابع لینک پیام تلگرام را تجزیه کرده و chat_id و message_id را استخراج می‌کند.
    از الگوی t.me/c/1234567890/1234 برای چت خصوصی استفاده می‌کند که
    chat_id به صورت int("-100" + group_number) و message_id به صورت عدد استخراج می‌شود.
    همچنین از الگوی t.me/somechannel/1234 برای چت‌های عمومی استفاده می‌کند.
    """
    m = re.search(r"t\.me\/c\/(-?\d+)\/(\d+)", link)
    if m:
        chat_id = int("-100" + m.group(1))
        message_id = int(m.group(2))
        return chat_id, message_id

    m = re.search(r"t\.me\/([A-Za-z0-9_]+)\/(\d+)", link)
    if m:
        chat_id = "@" + m.group(1)
        message_id = int(m.group(2))
        return chat_id, message_id

    return None, None

async def randomString() -> str:
    size = random.randint(4, 8)
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVLXYZ') for _ in range(size))

async def randomAPP():
    with open('app.txt', 'r', encoding='utf-8') as file:
        file = file.read().split('\n')
        app_id, app_hash = random.choice(file).split()
    return app_id, app_hash

async def accountList():
    return [myFile.split('.')[0] for myFile in os.listdir('sessions') if os.path.isfile(os.path.join('sessions', myFile))]

async def remainTime(TS):
    TS = time.time() - TS
    if TS < 60:
        return str(int(TS)) + ' ثانیه'
    else:
        mins = int(TS / 60)
        sec = TS % 60
        return str(int(mins)) + ' دقیقه و ' + str(int(sec)) + ' ثانیه'

bot = Client(
    "LampStack",
    bot_token=bot_token,
    api_id=api_id,
    api_hash=api_hash
)

def get_group_report_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('♛𝐑𝐄𝐏𝐎𝐑𝐓 (𝐬𝐜𝐚𝐦)', callback_data='group_report_scam')],
        [InlineKeyboardButton('♛𝐑𝐄𝐏𝐎𝐑𝐓 (𝐬𝐩𝐚𝐦)', callback_data='group_report_spam')],
        [InlineKeyboardButton('♛𝐑𝐄𝐏𝐎𝐑𝐓 (𝐩𝐨𝐫𝐧𝐨𝐠𝐫𝐚𝐩𝐡𝐲)', callback_data='group_report_pornography')],
        [InlineKeyboardButton('♛𝐑𝐄𝐏𝐎𝐑𝐓 (𝐕𝐢𝐨𝐥𝐞𝐧𝐜𝐞)', callback_data='group_report_violence')],
        [InlineKeyboardButton('♛𝐑𝐄𝐏𝐎𝐑𝐓 (𝐈𝐥𝐥𝐞𝐠𝐚𝐥)', callback_data='group_report_illegal')],
        [InlineKeyboardButton('♛𝐑𝐄𝐏𝐎𝐑𝐓 (𝐏𝐞𝐫𝐬𝐨𝐧𝐚𝐥𝐃𝐞𝐓𝐚𝐢𝐥𝐬)', callback_data='group_report_personal')],
        [InlineKeyboardButton('♛𝐑𝐄𝐏𝐎𝐑𝐓 (𝐂𝐨𝐩𝐲𝐫𝐢𝐠𝐡𝐭)', callback_data='group_report_copyright')],
        [InlineKeyboardButton('♛𝐑𝐄𝐏𝐎𝐑𝐓 (𝐂𝐡𝐢𝐥𝐝 𝐚𝐛𝐮𝐬𝐞)', callback_data='group_report_child_abuse')],
        [InlineKeyboardButton('🔙', callback_data='backToMenu')]
    ])

def get_main_menu_keyboard_owner():
    # منوی مالک شامل دکمه‌های اضافه کردن اکانت، حساب لیست، مدیریت ادمین و سایر عملیات است.
    base_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton('Aᴅᴅ ᴀᴄᴄᴏᴜɴᴛ ➕', callback_data='addAccount')],
        [InlineKeyboardButton('Aᴄᴄᴏᴜɴᴛ ʟɪsᴛ 📊', callback_data='accountsList')],
        [InlineKeyboardButton('✖️ Dᴇʟᴇᴛᴇ ᴀᴄᴄᴏᴜɴᴛ', callback_data='removeAccount')],
        [InlineKeyboardButton('Pᴏsᴛ Rᴇᴀᴄᴛɪᴏɴ Oᴘᴇʀᴀᴛɪᴏɴ ⚫️', callback_data='reActionEval')],
        [InlineKeyboardButton('🔴 Pᴏsᴛ Rᴇᴘᴏʀᴛ Oᴘᴇʀᴀᴛɪᴏɴ', callback_data='reportPostPublic')],
        [InlineKeyboardButton('♻️ Aᴄᴄᴏᴜɴᴛ Rᴇᴠɪᴇᴡ', callback_data='checkAccounts')],
        [InlineKeyboardButton('Sᴇᴛ Tɪᴍᴇ ⏱', callback_data='setTime')],
        [InlineKeyboardButton('📛 Cᴀɴᴄᴇʟ Aʟʟ Oᴘᴇʀᴀᴛɪᴏɴs', callback_data='endAllEvals')],
        [InlineKeyboardButton('☠ Rᴇᴘᴏʀᴛ', callback_data='groupReport')],
        [InlineKeyboardButton('⛔️ Bʟᴏᴄᴋ ᴜsᴇʀ', callback_data='blockUser')]
    ])
    kb = base_keyboard.inline_keyboard.copy()
    kb.append([InlineKeyboardButton('➕Aᴅᴅ ᴀᴅᴍɪɴ', callback_data='addAdmin')])
    kb.append([InlineKeyboardButton('➖Dᴇʟᴇᴛᴇ ᴀᴅᴍɪɴ', callback_data='removeAdmin')])
    return InlineKeyboardMarkup(kb)

def get_main_menu_keyboard_admin():
    # منوی ادمین غیر مالک با دکمه اضافه کردن اکانت به همراه سایر دکمه‌ها
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('Aᴅᴅ ᴀᴄᴄᴏᴜɴᴛ ➕', callback_data='addAccount')],
        [InlineKeyboardButton('Pᴏsᴛ Rᴇᴀᴄᴛɪᴏɴ Oᴘᴇʀᴀᴛɪᴏɴ ⚫️', callback_data='reActionEval')],
        [InlineKeyboardButton('🔴 Pᴏsᴛ Rᴇᴘᴏʀᴛ Oᴘᴇʀᴀᴛɪᴏɴ', callback_data='reportPostPublic')],
        [InlineKeyboardButton('♻️ Aᴄᴄᴏᴜɴᴛ Rᴇᴠɪᴇᴡ', callback_data='checkAccounts')],
        [InlineKeyboardButton('Sᴇᴛ Tɪᴍᴇ ⏱', callback_data='setTime')],
        [InlineKeyboardButton('📛 Cᴀɴᴄᴇʟ Aʟʟ Oᴘᴇʀᴀᴛɪᴏɴs', callback_data='endAllEvals')],
        [InlineKeyboardButton('☠ Rᴇᴘᴏʀᴛ', callback_data='groupReport')],
        [InlineKeyboardButton('⛔️ Bʟᴏᴄᴋ ᴜsᴇʀ', callback_data='blockUser')]
    ])

print('Bot is Running ...')

@bot.on_message(filters.command(['start', 'cancel']) & filters.private)
async def StartResponse(client, message):
    global step, tempClient, isWorking, bot_admins, current_operation_admin
    try:
        tempClient['client'].disconnect()
    except Exception:
        pass
    tempClient = {}
    step = None
    current_operation_admin = None  # Reset the operation lock when starting over.
    # Reload admin IDs from file to update bot_admins list
    bot_admins = list(set(load_admin_ids() + [owner_id]))
    user_id = message.from_user.id
    if user_id == owner_id:
        keyboard = get_main_menu_keyboard_owner()
    elif user_id in bot_admins:
        keyboard = get_main_menu_keyboard_admin()
    else:
        await message.reply("<b>❌ شما ادمین نیستید</b>")
        return
    await message.reply('<b>> به منوی اصلی خوش آمدید :</b>',
                        reply_markup=keyboard, quote=True)

@bot.on_message(filters.regex('^/stop_\\w+') & filters.private & filters.user(bot_admins))
async def StopEval(client, message):
    global step, isWorking, current_operation_admin
    evalID = message.text.replace('/stop_', '')
    if evalID in isWorking:
        isWorking.remove(evalID)
        # آزادسازی قفل عملیات
        current_operation_admin = None
        await message.reply(f'<b>عملیات با شناسه {evalID} با موفقیت خاتمه یافت ✅</b>')
    else:
        await message.reply(f'<b>عملیات موردنظر یافت نشد !</b>')

@bot.on_callback_query()
async def callbackQueries(client, query):
    global step, tempClient, isWorking, sleeping, bot_admins, current_operation_admin
    chat_id = query.message.chat.id
    message_id = query.message.id
    data = query.data
    query_id = query.id

    # Debug: چاپ وضعیت قفل عملیات
    print("DEBUG: current_operation_admin =", current_operation_admin, " | current chat_id =", chat_id)

    # بررسی قفل عملیات: اگر یک ادمین عملیات درحال انجام دارد و این کاربر همان نیست
    if current_operation_admin is not None and current_operation_admin != chat_id:
        await bot.answer_callback_query(
            query.id,
            "ادمین دیگری درحال انجام عملیات است ، لطفاً تا اتمام عملیات صبر کنید ❤️✅",
            show_alert=True
        )
        return

    # زمانی که یک عملیات جدید شروع می‌شود، اگر قفل آزاد است، قفل را تنظیم می‌کنیم.
    if current_operation_admin is None:
        if data in ['addAdmin', 'removeAdmin', 'addAccount', 'removeAccount', 'reportPostPublic', 'reActionEval',
                    'voteEval', 'blockEval', 'groupReport', 'group_report_spam', 'group_report_pornography',
                    'group_report_violence', 'group_report_illegal', 'group_report_personal', 'group_report_copyright',
                    'group_report_child_abuse', 'group_report_scam']:
            current_operation_admin = chat_id

    # فقط مالک به دکمه‌های مدیریت ادمین و حساب لیست دسترسی داشته باشد
    if chat_id == owner_id:
        if data == 'addAdmin':
            step = 'getAddAdminId'
            await bot.edit_message_text(chat_id, message_id, '<b>آیدی عددی کاربر را جهت ادمین شدن وارد کنید :</b>')
        elif data == 'removeAdmin':
            step = 'getRemoveAdminId'
            await bot.edit_message_text(chat_id, message_id, '<b>آیدی کاربر را جهت حذف شدن از ادمینی وارد کنید:</b>')
    # بررسی دکمه حساب لیست؛ تنها مالک می‌تواند از آن استفاده کند
    elif data == 'accountsList':
        await bot.edit_message_text(chat_id, message_id, '<b>شما دسترسی به این دکمه را ندارید!</b>')
        return

    # دکمه‌های عمومی برای تمامی ادمین‌ها
    if data == 'backToMenu':
        try:
            tempClient['client'].disconnect()
        except Exception:
            pass
        tempClient = {}
        step = None
        current_operation_admin = None  # آزادسازی قفل
        if chat_id == owner_id:
            keyboard = get_main_menu_keyboard_owner()
        else:
            keyboard = get_main_menu_keyboard_admin()
        await bot.edit_message_text(chat_id, message_id, '<b>> به منوی اصلی خوش آمدید :</b>',
                                    reply_markup=keyboard)
    elif data == 'endAllEvals':
        step = None
        evalsCount = len(isWorking)
        isWorking = list()
        await bot.invoke(functions.messages.SetBotCallbackAnswer(
            query_id=int(query_id),
            cache_time=1,
            alert=True,
            message=f'تمام {evalsCount} عملیات فعال با موفقیت متوقف شدند.'
        ))
        current_operation_admin = None
    elif data == 'addAccount':
        step = 'getPhoneForLogin'
        await bot.edit_message_text(chat_id, message_id,
                                    '<b>- برای افزودن اکانت لطفا شماره مورد نظرتان را ارسال نمایید :</b>')
    elif data == 'removeAccount':
        step = 'removeAccount'
        await bot.edit_message_text(chat_id, message_id,
                                    '<b>- برای حذف اکانت لطفا شماره مورد نظرتان را ارسال نمایید :</b>')
    elif data == 'reportPostPublic':
        step = 'reportPostPublic'
        await bot.edit_message_text(chat_id, message_id,
                                    '<b>لطفا لینک پست کانال|گروه مورد نظر را ارسال نمایید :</b>')
    elif data == 'reActionEval':
        step = 'reActionEval'
        await bot.edit_message_text(chat_id, message_id,
                                    '<b>لطفا در خط اول لینک پست، در خط دوم ایموجی‌ها و در خط سوم تعداد ری اکشن را وارد کنید :</b>')
    elif data == 'voteEval':
        step = 'voteEval'
        await bot.edit_message_text(chat_id, message_id,
                                    '<b>لطفا در خط اول لینک پست و در خط دوم شماره گزینه موردنظرتان را وارد کنید :</b>')
    elif data == 'blockEval':
        step = 'blockEval'
        await bot.edit_message_text(chat_id, message_id,
                                    '<b>یوزرنیم کاربر مورد نظرتان را با @ وارد کنید :</b>')
    elif data == 'blockUser':
        step = 'blockEval'
        await bot.edit_message_text(chat_id, message_id,
                                    '<b>یوزرنیم کاربر مورد نظرتان را با @ وارد کنید :</b>')
    elif data == 'accountsList':
        if chat_id != owner_id:
            await bot.edit_message_text(chat_id, message_id, '<b>شما دسترسی به این دکمه را ندارید!</b>')
        else:
            accounts = await accountList()
            if accounts:
                text_to_reply = "<b>لیست اکانت‌ها:</b>\n" + "\n".join(accounts)
            else:
                text_to_reply = "<b>هیچ اکانتی موجود نیست.</b>"
            await bot.edit_message_text(chat_id, message_id, text_to_reply)
    elif data == 'checkAccounts':
        if len(await accountList()) == 0:
            await bot.invoke(functions.messages.SetBotCallbackAnswer(
                query_id=int(query_id),
                cache_time=1,
                alert=True,
                message='اکانتی یافت نشد ❗️'
            ))
        else:
            evalID = await randomString()
            isWorking.append(evalID)
            deleted = 0
            error = 0
            free = 0
            cli = None
            TS = time.time()
            AllCount = len(await accountList())
            await bot.edit_message_text(chat_id, message_id, '<b>عملیات بررسی اکانت ها شروع شد ...</b>')
            for session in await accountList():
                if evalID not in isWorking:
                    break
                try:
                    await cli.disconnect()
                except Exception:
                    pass
                await asyncio.sleep(sleeping)
                try:
                    api_id2, api_hash2 = await randomAPP()
                    cli = Client(f'sessions/{session}', api_id2, api_hash2)
                    await cli.connect()
                    await cli.resolve_peer("@durov")
                    await cli.disconnect()
                except (errors.SessionRevoked, errors.UserDeactivated, errors.AuthKeyUnregistered, errors.UserDeactivatedBan, errors.Unauthorized):
                    try:
                        await cli.disconnect()
                    except Exception:
                        pass
                    os.unlink(f'sessions/{session}.session')
                    deleted += 1
                except Exception as e:
                    try:
                        await cli.disconnect()
                    except Exception:
                        pass
                    error += 1
                else:
                    free += 1
                finally:
                    spendTime = await remainTime(TS)
                    allChecked = deleted + free + error
                    await bot.edit_message_text(
                        chat_id,
                        message_id,
                        f'''♻️ عملیات بررسی اکانت های ربات ...

• کل اکانت ها : {AllCount}
• اکانت های بررسی شده : {allChecked}
• اکانت های سالم : {free}
• سشن های خراب : {deleted}
• خطاهای ناشناخته : {error}
• زمان سپری شده : {spendTime}

برای لغو این عملیات از دستور ( /stop_{evalID} ) استفاده نمایید.'''
                    )
            try:
                isWorking.remove(evalID)
            except Exception:
                pass
            allChecked = deleted + free + error
            spendTime = await remainTime(TS)
            my_keyboard = [
                [InlineKeyboardButton('🔙', callback_data='backToMenu')],
            ]
            await bot.send_message(
                chat_id,
                f'''عملیات بررسی اکانت ها با موفقیت به اتمام رسید ✅

• کل اکانت ها : {AllCount}
• اکانت های بررسی شده : {allChecked}
• اکانت های سالم : {free}
• سشن های خراب : {deleted}
• خطاهای ناشناخته : {error}
• زمان سپری شده : {spendTime}''',
                reply_markup=InlineKeyboardMarkup(my_keyboard)
            )
    elif data == 'setTime':
        step = 'setTime'
        await bot.edit_message_text(chat_id, message_id, "<b>لطفاً زمان (در ثانیه) جدید را وارد کنید:</b>")
    elif data == 'groupReport':
        await bot.edit_message_text(chat_id, message_id, '<b>> لطفاً یکی از گزینه‌های گزارش زیر را انتخاب کنید :</b>', reply_markup=get_group_report_keyboard())
    elif data == 'group_report_spam':
        step = 'group_report_spam_request_link'
        await bot.edit_message_text(chat_id, message_id, '<b>لطفاً لینک پیام ها را ارسال کنید : (هر خط یک لینک)</b>')
    elif data == 'group_report_pornography':
        step = 'group_report_pornography_request_link'
        await bot.edit_message_text(chat_id, message_id, '<b>لطفاً لینک پیام ها را ارسال کنید : (هر خط یک لینک)</b>')
    elif data == 'group_report_violence':
        step = 'group_report_violence_request_link'
        await bot.edit_message_text(chat_id, message_id, '<b>لطفاً لینک پیام ها را ارسال کنید : (هر خط یک لینک)</b>')
    elif data == 'group_report_illegal':
        step = 'group_report_illegal_request_link'
        await bot.edit_message_text(chat_id, message_id, '<b>لطفاً لینک پیام ها را ارسال کنید : (هر خط یک لینک)</b>')
    elif data == 'group_report_personal':
        step = 'group_report_personal_request_link'
        await bot.edit_message_text(chat_id, message_id, '<b>لطفاً لینک پیام ها را ارسال کنید : (هر خط یک لینک)</b>')
    elif data == 'group_report_copyright':
        step = 'group_report_copyright_request_link'
        await bot.edit_message_text(chat_id, message_id, '<b>لطفاً لینک پیام ها را ارسال کنید : (هر خط یک لینک)</b>')
    elif data == 'group_report_child_abuse':
        step = 'group_report_child_abuse_request_link'
        await bot.edit_message_text(chat_id, message_id, '<b>لطفاً لینک پیام ها را ارسال کنید : (هر خط یک لینک)</b>')
    elif data == 'group_report_scam':
        step = 'group_report_scam_request_link'
        await bot.edit_message_text(chat_id, message_id, '<b>لطفاً لینک پیام ها را ارسال کنید : (هر خط یک لینک)</b>')

@bot.on_message(filters.text & filters.private & filters.user(bot_admins))
async def TextResponse(client, message):
    global step, isWorking, tempClient, api_hash, api_id, sleeping, bot_admins, current_operation_admin
    chat_id = message.chat.id
    text = message.text

    # بررسی قفل عملیات برای دریافت پاسخ متنی:
    if current_operation_admin is not None and current_operation_admin != chat_id:
        await message.reply('<b>ادمین دیگری درحال انجام عملیات است ، لطفاً تا اتمام عملیات صبر کنید ❤️✅</b>')
        return

    # Handling admin management for owner
    if step == 'getAddAdminId':
        step = None
        current_operation_admin = None  # آزادسازی قفل پس از اتمام عمل
        if text.strip().isdigit():
            admin_id = int(text.strip())
            if admin_id not in bot_admins:
                bot_admins.append(admin_id)
                save_admin_ids([admin for admin in bot_admins if admin != owner_id])
            await message.reply('<b>اضافه شد ✅</b>')
        else:
            await message.reply('<b>ورودی معتبر نیست. لطفا یک آیدی عددی وارد کنید.</b>')
    elif step == 'getRemoveAdminId':
        step = None
        current_operation_admin = None
        if text.strip().isdigit():
            admin_id = int(text.strip())
            if admin_id in bot_admins and admin_id != owner_id:
                bot_admins.remove(admin_id)
                save_admin_ids([admin for admin in bot_admins if admin != owner_id])
                await message.reply('<b>حذف شد ❌</b>')
            else:
                await message.reply('<b>آیدی وارد شده یافت نشد یا مالک قابل حذف نیست.</b>')
        else:
            await message.reply('<b>ورودی معتبر نیست. لطفا یک آیدی عددی وارد کنید.</b>')

    if step == 'getPhoneForLogin' and text.replace('+', '').replace(' ', '').replace('-', '').isdigit():
        phone_number = text.replace('+', '').replace(' ', '').replace('-', '')
        if os.path.isfile(f'sessions/{phone_number}.session'):
            await message.reply('<b>این شماره از قبل در پوشه sessions سرور موجود است !</b>')
        else:
            tempClient['number'] = phone_number
            tempClient['client'] = Client(f'sessions/{phone_number}', int(api_id), api_hash)
            await tempClient['client'].connect()
            try:
                tempClient['response'] = await tempClient['client'].send_code(phone_number)
            except (errors.BadRequest, errors.PhoneNumberBanned, errors.PhoneNumberFlood, errors.PhoneNumberInvalid):
                await message.reply('<b>خطایی رخ داد !</b>')
            else:
                step = 'get5DigitsCode'
                await message.reply(f'<b>کد 5 رقمی به شماره {phone_number} ارسال شد ✅</b>')
    elif step == 'get5DigitsCode' and text.replace(' ', '').isdigit():
        telegram_code = text.replace(' ', '')
        try:
            await tempClient['client'].sign_in(tempClient['number'], tempClient['response'].phone_code_hash, telegram_code)
            await tempClient['client'].disconnect()
            tempClient = {}
            step = 'getPhoneForLogin'
            current_operation_admin = None  # آزادسازی قفل پس از اتمام عمل
            await message.reply('<b>اکانت با موفقیت ثبت شد ✅\nدرصورتیکه قصد افزودن شماره دارید, شماره موردنظر را ارسال کنید</b>')
        except errors.PhoneCodeExpired:
            await tempClient['client'].disconnect()
            tempClient = {}
            step = None
            current_operation_admin = None
            await message.reply('<b>کد ارسال شده منقضی شده است, لطفا عملیات را /cancel کنید و مجدداً تلاش کنید.</b>')
        except errors.PhoneCodeInvalid:
            await message.reply('<b>کد وارد شده اشتباه است یا منقضی شده, لطفا دوباره تلاش کنید.</b>')
        except errors.BadRequest:
            await message.reply('<b>کد وارد شده اشتباه است یا منقضی شده, لطفا دوباره تلاش کنید.</b>')
        except errors.AuthKeyUnregistered:
            await asyncio.sleep(3)
            name = await randomString()
            try:
                await tempClient['client'].sign_up(tempClient['number'], tempClient['response'].phone_code_hash, name)
            except Exception:
                pass
            await tempClient['client'].disconnect()
            tempClient = {}
            step = 'getPhoneForLogin'
            current_operation_admin = None
            await message.reply('<b>اکانت با موفقیت ثبت شد ✅\nدرصورتیکه قصد افزودن شماره دارید, شماره موردنظر را ارسال کنید</b>')
        except errors.SessionPasswordNeeded:
            step = 'SessionPasswordNeeded'
            await message.reply('<b>لطفا رمز تایید دو مرحله ای را وارد نمایید :</b>')
    elif step == 'SessionPasswordNeeded':
        twoFaPass = text
        try:
            await tempClient['client'].check_password(twoFaPass)
        except errors.BadRequest:
            await message.reply('<b>رمز وارد شده اشتباه میباشد, لطفا مجدداً ارسال نمایید.</b>')
        else:
            await tempClient['client'].disconnect()
            tempClient = {}
            step = 'getPhoneForLogin'
            current_operation_admin = None
            await message.reply('<b>اکانت با موفقیت ثبت شد ✅\nدرصورتیکه قصد افزودن شماره دارید, شماره موردنظر را ارسال کنید</b>')
    
    if step == 'removeAccount':
        step = None
        current_operation_admin = None
        phone_number = text.replace('+', '').replace(' ', '').replace('-', '')
        if not os.path.isfile(f'sessions/{phone_number}.session'):
            await message.reply('<b>شماره مورد نظر در سرور یافت نشد !</b>')
        else:
            await bot.send_document(message.chat.id, f'sessions/{phone_number}.session',
                                      caption='<b>شماره مورد نظر با موفقیت حذف شد ✅\nسشن پایروگرام حذف شده است.</b>')
            os.unlink(f'sessions/{phone_number}.session')
    
    if step == 'setTime':
        step = None
        current_operation_admin = None
        sleeping = float(text)
        await message.reply('<b>زمان جدید با موفقیت تنظیم شد ✅</b>')
    
    if step == 'joinAccounts':
        step = None
        evalID = await randomString()
        isWorking.append(evalID)
        link = text.split()[0].replace('@', '').replace('+', 'joinchat/')
        allAcccounts = len(await accountList())
        all = 0
        error = 0
        done = 0
        TS = time.time()
        msg = await message.reply('<b>عملیات عضویت شروع شد ...</b>')
        for session in await accountList():
            if evalID not in isWorking:
                break
            all += 1
            await asyncio.sleep(sleeping)
            try:
                api_id2, api_hash2 = await randomAPP()
                cli = Client(f'sessions/{session}', api_id2, api_hash2)
                await cli.connect()
                await asyncio.sleep(0.2)
                await cli.join_chat(link)
                await asyncio.sleep(0.2)
                await cli.disconnect()
            except Exception as e:
                try:
                    await cli.disconnect()
                except Exception:
                    pass
                error += 1
            else:
                done += 1
            finally:
                spendTime = await remainTime(TS)
                await bot.edit_message_text(chat_id, msg.id,
                                            f'''♻️ عملیات عضویت اکانت های ربات ...
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور ( /stop_{evalID} ) استفاده نمایید.''')
        try:
            isWorking.remove(evalID)
        except Exception:
            pass
        spendTime = await remainTime(TS)
        await message.reply(f'''<b>عملیات عضویت با موفقیت به پایان رسید ✅
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}</b>''')
    
    if step == 'leaveAccounts':
        step = None
        evalID = await randomString()
        isWorking.append(evalID)
        allAcccounts = len(await accountList())
        all = 0
        error = 0
        done = 0
        TS = time.time()
        msg = await message.reply('<b>عملیات خروج شروع شد ...</b>')
        for session in await accountList():
            if evalID not in isWorking:
                break
            all += 1
            await asyncio.sleep(sleeping)
            try:
                api_id2, api_hash2 = await randomAPP()
                cli = Client(f'sessions/{session}', api_id2, api_hash2)
                await cli.connect()
                await asyncio.sleep(0.2)
                await cli.leave_chat(int(text), delete=True)
                await asyncio.sleep(0.2)
                await cli.disconnect()
            except Exception as e:
                try:
                    await cli.disconnect()
                except Exception:
                    pass
                error += 1
            else:
                done += 1
            finally:
                spendTime = await remainTime(TS)
                await bot.edit_message_text(chat_id, msg.id,
                                            f'''♻️ عملیات خروج اکانت های ربات ...
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور ( /stop_{evalID} ) استفاده نمایید.''')
        try:
            isWorking.remove(evalID)
        except Exception:
            pass
        spendTime = await remainTime(TS)
        await message.reply(f'''<b>عملیات خروج با موفقیت به پایان رسید ✅</b>
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    if step == 'sendViewToPost':
        step = None
        evalID = await randomString()
        isWorking.append(evalID)
        username = text.split('/')[3]
        msg_id = int(text.split('/')[4])
        allAcccounts = len(await accountList())
        all = 0
        error = 0
        done = 0
        TS = time.time()
        msg = await message.reply('<b>عملیات ویو پست کانال شروع شد ...</b>')
        for session in await accountList():
            if evalID not in isWorking:
                break
            try:
                await cli.disconnect()
            except Exception:
                pass
            all += 1
            await asyncio.sleep(sleeping)
            try:
                api_id2, api_hash2 = await randomAPP()
                cli = Client(f'sessions/{session}', api_id2, api_hash2)
                await cli.connect()
                await asyncio.sleep(0.2)
                await cli.invoke(functions.messages.GetMessagesViews(peer=await cli.resolve_peer(username), id=[msg_id], increment=True))
                await asyncio.sleep(0.2)
                await cli.disconnect()
            except Exception as e:
                try:
                    await cli.disconnect()
                except Exception:
                    pass
                error += 1
            else:
                done += 1
            finally:
                spendTime = await remainTime(TS)
                await bot.edit_message_text(chat_id, msg.id,
                                            f'''♻️ عملیات ارسال ویو اکانت های ربات ...
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور ( /stop_{evalID} ) استفاده نمایید.''')
        try:
            isWorking.remove(evalID)
        except Exception:
            pass
        spendTime = await remainTime(TS)
        await message.reply(f'''<b>عملیات بازدید پست کانال با موفقیت به پایان رسید ✅</b>
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    if step == 'reportPostPublic':
        step = None
        evalID = await randomString()
        isWorking.append(evalID)
        if text.split('/')[3] != 'c':
            peerID = '@' + text.split('/')[3]
            peerMessageID = int(text.split('/')[4])
        else:
            peerID = int('-100' + text.split('/')[4])
            peerMessageID = int(text.split('/')[5])
        allAcccounts = len(await accountList())
        all = 0
        error = 0
        done = 0
        TS = time.time()
        if text.split('/')[3].isdigit():
            await message.reply('<b>لینکی که برام ارسال کردی مربوط به یک چت خصوصی است ❗️</b>')
        else:
            msg = await message.reply('<b>عملیات ریپورت پست کانال عمومی شروع شد ...</b>')
            for session in await accountList():
                if evalID not in isWorking:
                    break
                try:
                    await cli.disconnect()
                except Exception:
                    pass
                all += 1
                await asyncio.sleep(sleeping)
                try:
                    api_id2, api_hash2 = await randomAPP()
                    cli = Client(f'sessions/{session}', api_id2, api_hash2)
                    await cli.connect()
                    await asyncio.sleep(0.2)
                    await cli.invoke(functions.messages.Report(
                        peer=await cli.resolve_peer(peerID),
                        id=[peerMessageID],
                        reason=types.InputReportReasonPornography(),
                        message=''))
                    await asyncio.sleep(0.2)
                    await cli.disconnect()
                except Exception as e:
                    try:
                        await cli.disconnect()
                    except Exception:
                        pass
                    error += 1
                else:
                    done += 1
                finally:
                    spendTime = await remainTime(TS)
                    await bot.edit_message_text(chat_id, msg.id,
                                                f'''♻️ عملیات ریپورت پست کانال ...
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور ( /stop_{evalID} ) استفاده نمایید.''')
            try:
                isWorking.remove(evalID)
            except Exception:
                pass
            spendTime = await remainTime(TS)
            await message.reply(f'''<b>عملیات ریپورت پست با موفقیت به پایان رسید ✅</b>
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    if step == 'reActionEval':
        step = None
        evalID = await randomString()
        isWorking.append(evalID)
        peerID = '@' + text.split("\n")[0].split('/')[3]
        peerMessageID = int(text.split("\n")[0].split('/')[4])
        emojies = text.split("\n")[1].split()
        countOfWork = int(text.split("\n")[2])
        allAcccounts = len(await accountList())
        all = 0
        error = 0
        done = 0
        TS = time.time()
        if text.split("\n")[0].split('/')[3].isdigit():
            await message.reply('<b>لینکی که برام ارسال کردی مربوط به یک چت خصوصی است ❗️</b>')
        else:
            msg = await message.reply('<b>عملیات ارسال ری اکشن شروع شد ...</b>')
            for session in await accountList():
                if all >= countOfWork:
                    break
                if evalID not in isWorking:
                    break
                try:
                    await cli.disconnect()
                except Exception:
                    pass
                all += 1
                await asyncio.sleep(sleeping)
                try:
                    api_id2, api_hash2 = await randomAPP()
                    cli = Client(f'sessions/{session}', api_id2, api_hash2)
                    await cli.connect()
                    await asyncio.sleep(0.2)
                    await cli.send_reaction(peerID, peerMessageID, random.choice(emojies))
                    await asyncio.sleep(0.2)
                    await cli.disconnect()
                except Exception as e:
                    try:
                        await cli.disconnect()
                    except Exception:
                        pass
                    error += 1
                else:
                    done += 1
                finally:
                    spendTime = await remainTime(TS)
                    await bot.edit_message_text(chat_id, msg.id,
                                                f'''♻️ عملیات ارسال ری اکشن پست کانال ...
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور ( /stop_{evalID} ) استفاده نمایید.''')
            try:
                isWorking.remove(evalID)
            except Exception:
                pass
            spendTime = await remainTime(TS)
            await message.reply(f'''<b>عملیات ری اکشن پست با موفقیت به پایان رسید ✅</b>
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    if step == 'voteEval':
        step = None
        evalID = await randomString()
        isWorking.append(evalID)
        peerID = '@' + text.split("\n")[0].split('/')[3]
        peerMessageID = int(text.split("\n")[0].split('/')[4])
        opt = text.split("\n")[1]
        allAcccounts = len(await accountList())
        all = 0
        error = 0
        done = 0
        TS = time.time()
        if not opt.isdigit():
            await message.reply('<b>گزینه وارد شده صحیح نمیباشد ❗️</b>')
        else:
            msg = await message.reply('<b>عملیات ارسال نظرسنجی شروع شد ...</b>')
            for session in await accountList():
                if evalID not in isWorking:
                    break
                try:
                    await cli.disconnect()
                except Exception:
                    pass
                all += 1
                await asyncio.sleep(sleeping)
                try:
                    api_id2, api_hash2 = await randomAPP()
                    cli = Client(f'sessions/{session}', api_id2, api_hash2)
                    await cli.connect()
                    await asyncio.sleep(0.2)
                    await cli.vote_poll(peerID, peerMessageID, int(opt))
                    await asyncio.sleep(0.2)
                    await cli.disconnect()
                except Exception as e:
                    try:
                        await cli.disconnect()
                    except Exception:
                        pass
                    error += 1
                else:
                    done += 1
                finally:
                    spendTime = await remainTime(TS)
                    await bot.edit_message_text(chat_id, msg.id,
                                                f'''♻️ عملیات نظرسنجی ...
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور ( /stop_{evalID} ) استفاده نمایید.''')
            try:
                isWorking.remove(evalID)
            except Exception:
                pass
            spendTime = await remainTime(TS)
            await message.reply(f'''<b>عملیات نظرسنجی با موفقیت به پایان رسید ✅</b>
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    if step == 'blockEval':
        step = None
        evalID = await randomString()
        isWorking.append(evalID)
        peerID = text.replace('@', '')
        allAcccounts = len(await accountList())
        all = 0
        error = 0
        done = 0
        TS = time.time()
        msg = await message.reply('<b>عملیات بلاک کاربر شروع شد ...</b>')
        for session in await accountList():
            if evalID not in isWorking:
                break
            try:
                await cli.disconnect()
            except Exception:
                pass
            all += 1
            await asyncio.sleep(sleeping)
            try:
                api_id2, api_hash2 = await randomAPP()
                cli = Client(f'sessions/{session}', api_id2, api_hash2)
                await cli.connect()
                await asyncio.sleep(0.2)
                await cli.block_user(peerID)
                await asyncio.sleep(0.2)
                await cli.disconnect()
            except Exception as e:
                try:
                    await cli.disconnect()
                except Exception:
                    pass
                error += 1
            else:
                done += 1
            finally:
                spendTime = await remainTime(TS)
                await bot.edit_message_text(chat_id, msg.id,
                                            f'''♻️ عملیات بلاک کاربر ...
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور ( /stop_{evalID} ) استفاده نمایید.''')
        try:
            isWorking.remove(evalID)
        except Exception:
            pass
        spendTime = await remainTime(TS)
        await message.reply(f'''<b>عملیات بلاک کاربر با موفقیت به پایان رسید ✅</b>
• اکانت های بررسی شده : {all}/{allAcccounts}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    # Group report (other) - این بخش قبلاً مورد استفاده قرار می‌گرفت؛ اکنون توسط دکمه fake/scam حذف شده است.
    elif step == 'group_report_other_request_link':
         global tempReportLink_group_other
         tempReportLink_group_other = text.strip()
         step = 'group_report_other'
         await message.reply('<b>در خط اول تعداد اکانت، در خط دوم تعداد گزارش و در خط سوم به بعد متن ریپورت را وارد کنید :</b>')
    elif step == 'group_report_other':
         evalID = await randomString()
         isWorking.append(evalID)
         parts = text.split("\n")
         if len(parts) < 3:
             await message.reply("<b>ورودی نامعتبر! لطفاً در خط اول تعداد اکانت، در خط دوم تعداد گزارش و در خط سوم به بعد متن ریپ[...]\nreturn</b>")
             return
         try:
             acc_count = int(parts[0].strip())
             rpt_count = int(parts[1].strip())
         except:
             await message.reply("<b>عدد وارد شده معتبر نیست!</b>")
             return
         report_text = "\n".join(parts[2:])
         links = [line.strip() for line in tempReportLink_group_other.splitlines() if line.strip()]
         total_reports = len(links) * acc_count * rpt_count
         accounts = await accountList()
         chosen_accounts = accounts[:acc_count]
         all_reports = 0
         error = 0
         done = 0
         TS = time.time()
         msg = await message.reply('<b>♻️ عملیات ریپورت (other) شروع شد ...</b>')
         for link in links:
             chat_id_extracted, message_id_extracted = parse_message_link(link)
             if chat_id_extracted is None or message_id_extracted is None:
                 await message.reply("<b>یکی از لینک‌های وارد شده معتبر نیست. لطفاً لینک درست را ارسال نمایید.</b>")
                 continue
             for i in range(rpt_count):
                 for session in chosen_accounts:
                     if evalID not in isWorking:
                         break
                     all_reports += 1
                     await asyncio.sleep(sleeping)
                     try:
                         api_id2, api_hash2 = await randomAPP()
                         cli = Client(f'sessions/{session}', api_id2, api_hash2)
                         await cli.connect()
                         await cli.invoke(functions.messages.Report(
                             peer=await cli.resolve_peer(chat_id_extracted),
                             id=[message_id_extracted],
                             reason=types.InputReportReasonOther(),
                             message=report_text))
                         await cli.disconnect()
                     except Exception as e:
                         try:
                             await cli.disconnect()
                         except Exception:
                             pass
                         error += 1
                     else:
                         done += 1
                     spendTime = await remainTime(TS)
                     await bot.edit_message_text(chat_id, msg.id,
                     f'''♻️ عملیات ریپورت (other)
• کل ریپورت ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور (/stop_{evalID}) استفاده نمایید.''')
         try:
             isWorking.remove(evalID)
         except Exception:
             pass
         spendTime = await remainTime(TS)
         await message.reply(f'''<b>♻️ عملیات ریپورت (other) با موفقیت به پایان رسید ✅</b>
• کل ریپورت ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    # Group report (spam)
    elif step == 'group_report_spam_request_link':
         global tempReportLink_group_spam
         tempReportLink_group_spam = text.strip()
         step = 'group_report_spam'
         await message.reply('<b>در خط اول تعداد اکانت، در خط دوم تعداد گزارش و در خط سوم به بعد متن ریپورت را وارد کنید :</b>')
    elif step == 'group_report_spam':
         evalID = await randomString()
         isWorking.append(evalID)
         parts = text.split("\n")
         if len(parts) < 3:
             await message.reply("<b>ورودی نامعتبر! لطفاً در خط اول تعداد اکانت، در خط دوم تعداد گزارش و در خط سوم به بعد متن ریپ[...]\nreturn</b>")
             return
         try:
             acc_count = int(parts[0].strip())
             rpt_count = int(parts[1].strip())
         except:
             await message.reply("<b>عدد وارد شده معتبر نیست!</b>")
             return
         report_text = "\n".join(parts[2:])
         links = [line.strip() for line in tempReportLink_group_spam.splitlines() if line.strip()]
         total_reports = len(links) * acc_count * rpt_count
         accounts = await accountList()
         chosen_accounts = accounts[:acc_count]
         all_reports = 0
         error = 0
         done = 0
         TS = time.time()
         msg = await message.reply('<b>♻️ عملیات ریپورت (spam) شروع شد ...</b>')
         for link in links:
             chat_id_extracted, message_id_extracted = parse_message_link(link)
             if chat_id_extracted is None or message_id_extracted is None:
                 await message.reply("<b>یکی از لینک‌های وارد شده معتبر نیست. لطفاً لینک درست را ارسال نمایید.</b>")
                 continue
             for i in range(rpt_count):
                 for session in chosen_accounts:
                     if evalID not in isWorking:
                         break
                     all_reports += 1
                     await asyncio.sleep(sleeping)
                     try:
                         api_id2, api_hash2 = await randomAPP()
                         cli = Client(f'sessions/{session}', api_id2, api_hash2)
                         await cli.connect()
                         await cli.invoke(functions.messages.Report(
                             peer=await cli.resolve_peer(chat_id_extracted),
                             id=[message_id_extracted],
                             reason=types.InputReportReasonSpam(),
                             message=report_text))
                         await cli.disconnect()
                     except Exception as e:
                         try:
                             await cli.disconnect()
                         except Exception:
                             pass
                         error += 1
                     else:
                         done += 1
                     spendTime = await remainTime(TS)
                     await bot.edit_message_text(chat_id, msg.id,
                     f'''♻️ عملیات ریپورت (spam)
• کل ریپورت ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور (/stop_{evalID}) استفاده نمایید.''')
         try:
             isWorking.remove(evalID)
         except Exception:
             pass
         spendTime = await remainTime(TS)
         await message.reply(f'''<b>♻️ عملیات ریپورت (spam) با موفقیت به پایان رسید ✅</b>
• کل ریپورت ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    # Group report (pornography)
    elif step == 'group_report_pornography_request_link':
         global tempReportLink_group_pornography
         tempReportLink_group_pornography = text.strip()
         step = 'group_report_pornography_auto'
         await message.reply('<b>در خط اول تعداد اکانت و در خط دوم تعداد گزارش را وارد کنید :</b>')
    elif step == 'group_report_pornography_auto':
         evalID = await randomString()
         isWorking.append(evalID)
         parts = text.split("\n")
         if len(parts) < 2:
             await message.reply("<b>ورودی نامعتبر! لطفاً در خط اول تعداد اکانت و در خط دوم تعداد گزارش را وارد کنید.</b>")
             return
         try:
             acc_count = int(parts[0].strip())
             rpt_count = int(parts[1].strip())
         except:
             await message.reply("<b>عدد وارد شده معتبر نیست!</b>")
             return
         links = [line.strip() for line in tempReportLink_group_pornography.splitlines() if line.strip()]
         total_reports = len(links) * acc_count * rpt_count
         accounts = await accountList()
         chosen_accounts = accounts[:acc_count]
         all_reports = 0
         error = 0
         done = 0
         TS = time.time()
         msg = await message.reply('<b>♻️ عملیات ریپورت (pornography) شروع شد ...</b>')
         for link in links:
             chat_id_extracted, message_id_extracted = parse_message_link(link)
             if chat_id_extracted is None or message_id_extracted is None:
                 await message.reply("<b>یکی از لینک‌های وارد شده معتبر نیست. لطفاً لینک درست را ارسال نمایید.</b>")
                 continue
             for i in range(rpt_count):
                 for idx, session in enumerate(chosen_accounts):
                     if evalID not in isWorking:
                         break
                     all_reports += 1
                     await asyncio.sleep(sleeping)
                     curr_text = porn_report_texts[idx % len(porn_report_texts)]
                     try:
                         api_id2, api_hash2 = await randomAPP()
                         cli = Client(f'sessions/{session}', api_id2, api_hash2)
                         await cli.connect()
                         await cli.invoke(functions.messages.Report(
                             peer=await cli.resolve_peer(chat_id_extracted),
                             id=[message_id_extracted],
                             reason=types.InputReportReasonPornography(),
                             message=curr_text))
                         await cli.disconnect()
                     except Exception as e:
                         try:
                             await cli.disconnect()
                         except Exception:
                             pass
                         error += 1
                     else:
                         done += 1
                     spendTime = await remainTime(TS)
                     await bot.edit_message_text(chat_id, msg.id,
                     f'''♻️ عملیات ریپورت (pornography)
• کل ریپورت‌ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور (/stop_{evalID}) استفاده نمایید.''')
         try:
             isWorking.remove(evalID)
         except Exception:
             pass
         spendTime = await remainTime(TS)
         await message.reply(f'''<b>♻️ عملیات ریپورت (pornography) با موفقیت به پایان رسید ✅</b>
• کل ریپورت‌ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    # Group report (Violence)
    elif step == 'group_report_violence_request_link':
         global tempReportLink_group_violence
         tempReportLink_group_violence = text.strip()
         step = 'group_report_violence'
         await message.reply('<b>در خط اول تعداد اکانت، در خط دوم تعداد گزارش و در خط سوم به بعد متن ریپورت را وارد کنید :</b>')
    elif step == 'group_report_violence':
         evalID = await randomString()
         isWorking.append(evalID)
         parts = text.split("\n")
         if len(parts) < 3:
             await message.reply("<b>ورودی نامعتبر! لطفاً در خط اول تعداد اکانت، در خط دوم تعداد گزارش و در خط سوم به بعد متن ریپ[...]\nreturn</b>")
             return
         try:
             acc_count = int(parts[0].strip())
             rpt_count = int(parts[1].strip())
         except:
             await message.reply("<b>عدد وارد شده معتبر نیست!</b>")
             return
         report_text = "\n".join(parts[2:])
         links = [line.strip() for line in tempReportLink_group_violence.splitlines() if line.strip()]
         total_reports = len(links) * acc_count * rpt_count
         accounts = await accountList()
         chosen_accounts = accounts[:acc_count]
         all_reports = 0
         error = 0
         done = 0
         TS = time.time()
         msg = await message.reply('<b>♻️ عملیات ریپورت (Violence) شروع شد ...</b>')
         for link in links:
             chat_id_extracted, message_id_extracted = parse_message_link(link)
             if chat_id_extracted is None or message_id_extracted is None:
                 await message.reply("<b>یکی از لینک‌های وارد شده معتبر نیست. لطفاً لینک درست را ارسال نمایید.</b>")
                 continue
             for i in range(rpt_count):
                 for session in chosen_accounts:
                     if evalID not in isWorking:
                         break
                     all_reports += 1
                     await asyncio.sleep(sleeping)
                     try:
                         api_id2, api_hash2 = await randomAPP()
                         cli = Client(f'sessions/{session}', api_id2, api_hash2)
                         await cli.connect()
                         await cli.invoke(functions.messages.Report(
                             peer=await cli.resolve_peer(chat_id_extracted),
                             id=[message_id_extracted],
                             reason=types.InputReportReasonViolence(),
                             message=report_text))
                         await cli.disconnect()
                     except Exception as e:
                         try:
                             await cli.disconnect()
                         except Exception:
                             pass
                         error += 1
                     else:
                         done += 1
                     spendTime = await remainTime(TS)
                     await bot.edit_message_text(chat_id, msg.id,
                     f'''♻️ عملیات ریپورت (Violence)
• اکانت های بررسی شده : {all_reports}/{len(chosen_accounts)}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور (/stop_{evalID}) استفاده نمایید.''')
         try:
             isWorking.remove(evalID)
         except Exception:
             pass
         spendTime = await remainTime(TS)
         await message.reply(f'''<b>♻️ عملیات ریپورت (Violence) با موفقیت به پایان رسید ✅</b>
• کل ریپورت‌ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    # Group report (Illegal)
    elif step == 'group_report_illegal_request_link':
         global tempReportLink_group_illegal
         tempReportLink_group_illegal = text.strip()
         step = 'group_report_illegal'
         await message.reply('<b>در خط اول تعداد اکانت، در خط دوم تعداد گزارش و در خط سوم به بعد متن ریپورت را وارد کنید :</b>')
    elif step == 'group_report_illegal':
         evalID = await randomString()
         isWorking.append(evalID)
         parts = text.split("\n")
         if len(parts) < 3:
             await message.reply("<b>ورودی نامعتبر! لطفاً در خط اول تعداد اکانت، در خط دوم تعداد گزارش و در خط سوم به بعد متن ریپ[...]\nreturn</b>")
             return
         try:
             acc_count = int(parts[0].strip())
             rpt_count = int(parts[1].strip())
         except:
             await message.reply("<b>عدد وارد شده معتبر نیست!</b>")
             return
         report_text = "\n".join(parts[2:])
         links = [line.strip() for line in tempReportLink_group_illegal.splitlines() if line.strip()]
         total_reports = len(links) * acc_count * rpt_count
         accounts = await accountList()
         chosen_accounts = accounts[:acc_count]
         all_reports = 0
         error = 0
         done = 0
         TS = time.time()
         msg = await message.reply('<b>♻️ عملیات ریپورت (Illegal) شروع شد ...</b>')
         for link in links:
             chat_id_extracted, message_id_extracted = parse_message_link(link)
             if chat_id_extracted is None or message_id_extracted is None:
                 await message.reply("<b>یکی از لینک‌های وارد شده معتبر نیست. لطفاً لینک درست را ارسال نمایید.</b>")
                 continue
             for i in range(rpt_count):
                 for session in chosen_accounts:
                     if evalID not in isWorking:
                         break
                     all_reports += 1
                     await asyncio.sleep(sleeping)
                     try:
                         api_id2, api_hash2 = await randomAPP()
                         cli = Client(f'sessions/{session}', api_id2, api_hash2)
                         await cli.connect()
                         await cli.invoke(functions.messages.Report(
                             peer=await cli.resolve_peer(chat_id_extracted),
                             id=[message_id_extracted],
                             reason=types.InputReportReasonIllegalDrugs(),
                             message=report_text))
                         await cli.disconnect()
                     except Exception as e:
                         try:
                             await cli.disconnect()
                         except Exception:
                             pass
                         error += 1
                     else:
                         done += 1
                     spendTime = await remainTime(TS)
                     await bot.edit_message_text(chat_id, msg.id,
                     f'''♻️ عملیات ریپورت (Illegal)
• اکانت های بررسی شده : {all_reports}/{len(chosen_accounts)}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور (/stop_{evalID}) استفاده نمایید.''')
         try:
             isWorking.remove(evalID)
         except Exception:
             pass
         spendTime = await remainTime(TS)
         await message.reply(f'''<b>♻️ عملیات ریپورت (Illegal) با موفقیت به پایان رسید ✅</b>
• کل ریپورت‌ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    # Group report (PersonalDetails)
    elif step == 'group_report_personal_request_link':
         global tempReportLink_personal
         tempReportLink_personal = text.strip()
         step = 'group_report_personal'
         await message.reply('<b>در خط اول تعداد اکانت، در خط دوم تعداد گزارش و در خط سوم به بعد متن ریپورت را وارد کنید :</b>')
    elif step == 'group_report_personal':
         evalID = await randomString()
         isWorking.append(evalID)
         parts = text.split("\n")
         if len(parts) < 2:
             await message.reply("<b>ورودی نامعتبر! لطفاً در خط اول تعداد اکانت و در خط دوم تعداد گزارش را وارد کنید.</b>")
             return
         try:
             acc_count = int(parts[0].strip())
             rpt_count = int(parts[1].strip())
         except:
             await message.reply("<b>عدد وارد شده معتبر نیست!</b>")
             return
         report_text = "\n".join(parts[2:])  # report message (optional)
         links = [line.strip() for line in tempReportLink_personal.splitlines() if line.strip()]
         total_reports = len(links) * acc_count * rpt_count
         accounts = await accountList()
         chosen_accounts = accounts[:acc_count]
         all_reports = 0
         error = 0
         done = 0
         TS = time.time()
         msg = await message.reply('<b>♻️ عملیات ریپورت (PersonalDetails) شروع شد ...</b>')
         for link in links:
             chat_id_extracted, message_id_extracted = parse_message_link(link)
             if chat_id_extracted is None or message_id_extracted is None:
                 await message.reply("<b>یکی از لینک‌های وارد شده معتبر نیست. لطفاً لینک درست را ارسال نمایید.</b>")
                 continue
             for i in range(rpt_count):
                 for session in chosen_accounts:
                     if evalID not in isWorking:
                         break
                     all_reports += 1
                     await asyncio.sleep(sleeping)
                     try:
                         api_id2, api_hash2 = await randomAPP()
                         cli = Client(f'sessions/{session}', api_id2, api_hash2)
                         await cli.connect()
                         await cli.invoke(functions.messages.Report(
                             peer=await cli.resolve_peer(chat_id_extracted),
                             id=[message_id_extracted],
                             reason=types.InputReportReasonPersonalDetails(),
                             message=report_text))
                         await cli.disconnect()
                     except Exception as e:
                         try:
                             await cli.disconnect()
                         except Exception:
                             pass
                         error += 1
                     else:
                         done += 1
                     spendTime = await remainTime(TS)
                     await bot.edit_message_text(chat_id, msg.id,
                     f'''♻️ عملیات ریپورت (PersonalDetails)
• کل ریپورت ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور (/stop_{evalID}) استفاده نمایید.''')
         try:
             isWorking.remove(evalID)
         except Exception:
             pass
         spendTime = await remainTime(TS)
         await message.reply(f'''<b>♻️ عملیات ریپورت (PersonalDetails) با موفقیت به پایان رسید ✅</b>
• کل ریپورت ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    # Group report (Copyright)
    elif step == 'group_report_copyright_request_link':
         global tempReportLink_copyright
         tempReportLink_copyright = text.strip()
         step = 'group_report_copyright'
         await message.reply('<b>در خط اول تعداد اکانت، در خط دوم تعداد گزارش و در خط سوم به بعد متن ریپورت را وارد کنید :</b>')
    elif step == 'group_report_copyright':
         evalID = await randomString()
         isWorking.append(evalID)
         parts = text.split("\n")
         if len(parts) < 2:
             await message.reply("<b>ورودی نامعتبر! لطفاً در خط اول تعداد اکانت و در خط دوم تعداد گزارش را وارد کنید.</b>")
             return
         try:
             acc_count = int(parts[0].strip())
             rpt_count = int(parts[1].strip())
         except:
             await message.reply("<b>عدد وارد شده معتبر نیست!</b>")
             return
         report_text = "\n".join(parts[2:])
         links = [line.strip() for line in tempReportLink_copyright.splitlines() if line.strip()]
         total_reports = len(links) * acc_count * rpt_count
         accounts = await accountList()
         chosen_accounts = accounts[:acc_count]
         all_reports = 0
         error = 0
         done = 0
         TS = time.time()
         msg = await message.reply('<b>♻️ عملیات ریپورت (Copyright) شروع شد ...</b>')
         for link in links:
             chat_id_extracted, message_id_extracted = parse_message_link(link)
             if chat_id_extracted is None or message_id_extracted is None:
                 await message.reply("<b>یکی از لینک‌های وارد شده معتبر نیست. لطفاً لینک درست را ارسال نمایید.</b>")
                 continue
             for i in range(rpt_count):
                 for session in chosen_accounts:
                     if evalID not in isWorking:
                         break
                     all_reports += 1
                     await asyncio.sleep(sleeping)
                     try:
                         api_id2, api_hash2 = await randomAPP()
                         cli = Client(f'sessions/{session}', api_id2, api_hash2)
                         await cli.connect()
                         await cli.invoke(functions.messages.Report(
                             peer=await cli.resolve_peer(chat_id_extracted),
                             id=[message_id_extracted],
                             reason=types.InputReportReasonCopyright(),
                             message=report_text))
                         await cli.disconnect()
                     except Exception as e:
                         try:
                             await cli.disconnect()
                         except Exception:
                             pass
                         error += 1
                     else:
                         done += 1
                     spendTime = await remainTime(TS)
                     await bot.edit_message_text(chat_id, msg.id,
                     f'''♻️ عملیات ریپورت (Copyright)
• کل ریپورت ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور (/stop_{evalID}) استفاده نمایید.''')
         try:
             isWorking.remove(evalID)
         except Exception:
             pass
         spendTime = await remainTime(TS)
         await message.reply(f'''<b>♻️ عملیات ریپورت (Copyright) با موفقیت به پایان رسید ✅</b>
• کل ریپورت ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    # Group report (Child Abuse)
    elif step == 'group_report_child_abuse_request_link':
         global tempReportLink_child_abuse
         tempReportLink_child_abuse = text.strip()
         step = 'group_report_child_abuse'
         await message.reply('<b>در خط اول تعداد اکانت، در خط دوم تعداد گزارش و در خط سوم به بعد متن ریپورت را وارد کنید :</b>')
    elif step == 'group_report_child_abuse':
         evalID = await randomString()
         isWorking.append(evalID)
         parts = text.split("\n")
         if len(parts) < 2:
             await message.reply("<b>ورودی نامعتبر! لطفاً در خط اول تعداد اکانت و در خط دوم تعداد گزارش را وارد کنید.</b>")
             return
         try:
             acc_count = int(parts[0].strip())
             rpt_count = int(parts[1].strip())
         except:
             await message.reply("<b>عدد وارد شده معتبر نیست!</b>")
             return
         report_text = "\n".join(parts[2:])
         links = [line.strip() for line in tempReportLink_child_abuse.splitlines() if line.strip()]
         total_reports = len(links) * acc_count * rpt_count
         accounts = await accountList()
         chosen_accounts = accounts[:acc_count]
         all_reports = 0
         error = 0
         done = 0
         TS = time.time()
         msg = await message.reply('<b>♻️ عملیات ریپورت (ChildAbuse) شروع شد ...</b>')
         for link in links:
             chat_id_extracted, message_id_extracted = parse_message_link(link)
             if chat_id_extracted is None or message_id_extracted is None:
                 await message.reply("<b>یکی از لینک‌های وارد شده معتبر نیست. لطفاً لینک درست را ارسال نمایید.</b>")
                 continue
             for i in range(rpt_count):
                 for session in chosen_accounts:
                     if evalID not in isWorking:
                         break
                     all_reports += 1
                     await asyncio.sleep(sleeping)
                     try:
                         api_id2, api_hash2 = await randomAPP()
                         cli = Client(f'sessions/{session}', api_id2, api_hash2)
                         await cli.connect()
                         await cli.invoke(functions.messages.Report(
                             peer=await cli.resolve_peer(chat_id_extracted),
                             id=[message_id_extracted],
                             reason=types.InputReportReasonChildAbuse(),
                             message=report_text))
                         await cli.disconnect()
                     except Exception as e:
                         try:
                             await cli.disconnect()
                         except Exception:
                             pass
                         error += 1
                     else:
                         done += 1
                     spendTime = await remainTime(TS)
                     await bot.edit_message_text(chat_id, msg.id,
                     f'''♻️ عملیات ریپورت (ChildAbuse)
• کل ریپورت ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور (/stop_{evalID}) استفاده نمایید.''')
         try:
             isWorking.remove(evalID)
         except Exception:
             pass
         spendTime = await remainTime(TS)
         await message.reply(f'''<b>♻️ عملیات ریپورت (ChildAbuse) با موفقیت به پایان رسید ✅</b>
• کل ریپورت ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')
    
    # Group report (scam) - تغییر یافته: از کاربر متن ریپورت را می‌گیرد.
    elif step == 'group_report_scam_request_link':
         global tempReportLink_scam
         tempReportLink_scam = text.strip()
         step = 'group_report_scam_auto'
         await message.reply('<b>در خط اول تعداد اکانت، در خط دوم تعداد گزارش و از خط سوم به بعد متن ریپورت را وارد کنید :</b>')
    elif step == 'group_report_scam_auto':
         evalID = await randomString()
         isWorking.append(evalID)
         parts = text.split("\n")
         if len(parts) < 3:
             await message.reply("<b>ورودی نامعتبر! لطفاً در خط اول تعداد اکانت، در خط دوم تعداد گزارش و از خط سوم به بعد متن ریپ[...]\nreturn</b>")
             return
         try:
             acc_count = int(parts[0].strip())
             rpt_count = int(parts[1].strip())
         except:
             await message.reply("<b>عدد وارد شده معتبر نیست!</b>")
             return
         report_text = "\n".join(parts[2:])
         links = [line.strip() for line in tempReportLink_scam.splitlines() if line.strip()]
         total_reports = len(links) * acc_count * rpt_count
         accounts = await accountList()
         chosen_accounts = accounts[:acc_count]
         all_reports = 0
         error = 0
         done = 0
         TS = time.time()
         msg = await message.reply('<b>♻️ عملیات ریپورت (scam) شروع شد ...</b>')
         for link in links:
             chat_id_extracted, message_id_extracted = parse_message_link(link)
             if chat_id_extracted is None or message_id_extracted is None:
                 await message.reply("<b>یکی از لینک‌های وارد شده معتبر نیست. لطفاً لینک درست را ارسال نمایید.</b>")
                 continue
             for i in range(rpt_count):
                 for session in chosen_accounts:
                     if evalID not in isWorking:
                         break
                     all_reports += 1
                     await asyncio.sleep(sleeping)
                     try:
                         api_id2, api_hash2 = await randomAPP()
                         cli = Client(f'sessions/{session}', api_id2, api_hash2)
                         await cli.connect()
                         await cli.invoke(functions.messages.Report(
                             peer=await cli.resolve_peer(chat_id_extracted),
                             id=[message_id_extracted],
                             reason=types.InputReportReasonOther(),  # تغییر از Fake به Other
                             message=report_text))
                         await cli.disconnect()
                     except Exception as e:
                         try:
                             await cli.disconnect()
                         except Exception:
                             pass
                         error += 1
                     else:
                         done += 1
                     spendTime = await remainTime(TS)
                     await bot.edit_message_text(chat_id, msg.id,
                     f'''♻️ عملیات ریپورت (scam)
• کل ریپورت‌ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}
برای لغو این عملیات از دستور (/stop_{evalID}) استفاده نمایید.''')
         try:
             isWorking.remove(evalID)
         except Exception:
             pass
         spendTime = await remainTime(TS)
         await message.reply(f'''<b>♻️ عملیات ریپورت (scam) با موفقیت به پایان رسید ✅</b>
• کل ریپورت‌ها: {total_reports}
• موفق : {done}
• خطا : {error}
• زمان سپری شده : {spendTime}''')

bot.run()