#!/usr/bin/env python3

# SCRIPT   : PHONE TRACKING
# VERSION  : 1.0
# AUTHOR   : ZLAXTERT
# TEAM     : DARKXCODE
# TELEGRAM : https://t.me/zlaxtert/
# SITE     : https://darkxcode.pw/
# API      : https://api.darkxcode.site/phone-tracking/

import json
import shutil
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

from colorama import just_fix_windows_console

just_fix_windows_console()
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

MINT = "\033[38;5;49m"
MINT2 = "\033[38;5;48m"
MINT3 = "\033[38;5;43m"
DIM = "\033[38;5;242m"
FAINT = "\033[38;5;238m"
TEXT = "\033[38;5;252m"
WHITE = "\033[38;5;231m"
WARN = "\033[38;5;214m"
BAD = "\033[38;5;203m"
R = "\033[0m"

ANIM = sys.stdout.isatty()
DEFAULT_URL = "https://api.darkxcode.site/phone-tracking/api.php"
SUPPORTED = {"US", "CA"}

RAW = "AF:Afghanistan,AL:Albania,DZ:Algeria,AD:Andorra,AO:Angola,AG:Antigua and Barbuda,AR:Argentina,AM:Armenia,AU:Australia,AT:Austria,AZ:Azerbaijan,BS:Bahamas,BH:Bahrain,BD:Bangladesh,BB:Barbados,BY:Belarus,BE:Belgium,BZ:Belize,BJ:Benin,BT:Bhutan,BO:Bolivia,BA:Bosnia and Herzegovina,BW:Botswana,BR:Brazil,BN:Brunei,BG:Bulgaria,BF:Burkina Faso,BI:Burundi,CV:Cabo Verde,KH:Cambodia,CM:Cameroon,CA:Canada,CF:Central African Republic,TD:Chad,CL:Chile,CN:China,CO:Colombia,KM:Comoros,CG:Congo,CD:DR Congo,CR:Costa Rica,CI:Cote d'Ivoire,HR:Croatia,CU:Cuba,CY:Cyprus,CZ:Czechia,DK:Denmark,DJ:Djibouti,DM:Dominica,DO:Dominican Republic,EC:Ecuador,EG:Egypt,SV:El Salvador,GQ:Equatorial Guinea,ER:Eritrea,EE:Estonia,SZ:Eswatini,ET:Ethiopia,FJ:Fiji,FI:Finland,FR:France,GA:Gabon,GM:Gambia,GE:Georgia,DE:Germany,GH:Ghana,GR:Greece,GD:Grenada,GT:Guatemala,GN:Guinea,GW:Guinea-Bissau,GY:Guyana,HT:Haiti,HN:Honduras,HU:Hungary,IS:Iceland,IN:India,ID:Indonesia,IR:Iran,IQ:Iraq,IE:Ireland,IL:Israel,IT:Italy,JM:Jamaica,JP:Japan,JO:Jordan,KZ:Kazakhstan,KE:Kenya,KI:Kiribati,KW:Kuwait,KG:Kyrgyzstan,LA:Laos,LV:Latvia,LB:Lebanon,LS:Lesotho,LR:Liberia,LY:Libya,LI:Liechtenstein,LT:Lithuania,LU:Luxembourg,MG:Madagascar,MW:Malawi,MY:Malaysia,MV:Maldives,ML:Mali,MT:Malta,MH:Marshall Islands,MR:Mauritania,MU:Mauritius,MX:Mexico,FM:Micronesia,MD:Moldova,MC:Monaco,MN:Mongolia,ME:Montenegro,MA:Morocco,MZ:Mozambique,MM:Myanmar,NA:Namibia,NR:Nauru,NP:Nepal,NL:Netherlands,NZ:New Zealand,NI:Nicaragua,NE:Niger,NG:Nigeria,KP:North Korea,MK:North Macedonia,NO:Norway,OM:Oman,PK:Pakistan,PW:Palau,PS:Palestine,PA:Panama,PG:Papua New Guinea,PY:Paraguay,PE:Peru,PH:Philippines,PL:Poland,PT:Portugal,QA:Qatar,RO:Romania,RU:Russia,RW:Rwanda,KN:Saint Kitts and Nevis,LC:Saint Lucia,VC:Saint Vincent,WS:Samoa,SM:San Marino,ST:Sao Tome and Principe,SA:Saudi Arabia,SN:Senegal,RS:Serbia,SC:Seychelles,SL:Sierra Leone,SG:Singapore,SK:Slovakia,SI:Slovenia,SB:Solomon Islands,SO:Somalia,ZA:South Africa,KR:South Korea,SS:South Sudan,ES:Spain,LK:Sri Lanka,SD:Sudan,SR:Suriname,SE:Sweden,CH:Switzerland,SY:Syria,TW:Taiwan,TJ:Tajikistan,TZ:Tanzania,TH:Thailand,TL:Timor-Leste,TG:Togo,TO:Tonga,TT:Trinidad and Tobago,TN:Tunisia,TR:Turkey,TM:Turkmenistan,TV:Tuvalu,UG:Uganda,UA:Ukraine,AE:United Arab Emirates,GB:United Kingdom,US:United States,UY:Uruguay,UZ:Uzbekistan,VU:Vanuatu,VA:Vatican City,VE:Venezuela,VN:Vietnam,YE:Yemen,ZM:Zambia,ZW:Zimbabwe"

GLYPHS = {
    "P": ("█▀▀█", "█▀▀▀", "█   "),
    "H": ("█  █", "█▀▀█", "█  █"),
    "O": ("█▀▀█", "█  █", "█▄▄█"),
    "N": ("█▄ █", "█ ▀█", "█  █"),
    "E": ("█▀▀▀", "█▀▀ ", "█▄▄▄"),
    "T": ("▀▀█▀▀", "  █  ", "  █  "),
    "R": ("█▀▀█", "█▀▀▄", "█  █"),
    "A": ("█▀▀█", "█▀▀█", "▀  ▀"),
    "C": ("█▀▀▀", "█   ", "█▄▄▄"),
    "/": ("    ╱", "   ╱ ", "  ╱  "),
}

COUNTRIES = []
for _row in RAW.split(","):
    _cc, _name = _row.split(":")
    COUNTRIES.append({
        "cc": _cc,
        "name": _name,
        "flag": "".join(chr(0x1F1E6 + ord(c) - 65) for c in _cc),
    })


def dw(text):
    width = 0
    for ch in text:
        if ch in "\ufe0f\u200d":
            continue
        width += 2 if unicodedata.east_asian_width(ch) in "WF" else 1
    return width


def pad(text, width):
    return text + " " * max(0, width - dw(text))


def wrap(text, width):
    lines, cur, used = [], "", 0
    for ch in text:
        w = 0 if ch in "\ufe0f\u200d" else (2 if unicodedata.east_asian_width(ch) in "WF" else 1)
        if used + w > width and cur:
            lines.append(cur)
            cur, used = "", 0
        cur += ch
        used += w
    if cur or not lines:
        lines.append(cur)
    return lines


def out(text=""):
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def banner():
    rows = ["", "", ""]
    for ch in "PHONE//TRACE":
        glyph = GLYPHS.get(ch)
        for i in range(3):
            rows[i] += (glyph[i] if glyph else "  ") + " "
    colors = (MINT2, MINT, MINT3)
    for i, row in enumerate(rows):
        out(colors[i] + row + R)
        if ANIM:
            time.sleep(0.13)
    out()
    out(FAINT + "     ── phone trace & geo intelligence console ── " + DIM + "v1.0" + R)
    out(FAINT + "            author " + MINT + "ZLAXTERT" + FAINT + " · api from " + DIM + "DARKXCODE" + R)
    out()


def rule(char="─", color=FAINT):
    out(color + char * min(shutil.get_terminal_size((100, 24)).columns, 74) + R)


def ask(question, default=None):
    tail = f" [{default}]" if default else ""
    try:
        value = input(f"{MINT}❯{R} {DIM}{question}{tail}{R} ").strip()
    except (EOFError, KeyboardInterrupt):
        out()
        return None
    if not value:
        return default if default is not None else ""
    return value


def say(message, tone="dim"):
    out(f"{DIM}  {message}{R}" if tone == "dim" else f"  {message}{R}")


def pick_country(current):
    while True:
        raw = ask(f"country search  ({current['flag']} {current['name']}) › ", default="")
        if raw is None:
            return None
        query = raw.strip().lower()
        if query in ("", "q", "quit", "exit"):
            return current

        hits = [c for c in COUNTRIES if query in c["name"].lower() or c["cc"].lower() == query]
        if not hits:
            say(f"{BAD}no country matches “{raw}”{R}")
            continue

        exact = [c for c in hits if c["name"].lower() == query or c["cc"].lower() == query]
        if len(exact) == 1:
            return exact[0]

        for index, country in enumerate(hits[:8], 1):
            dot = f" {MINT}●{R}" if country["cc"] in SUPPORTED else ""
            out(f"   {DIM}{index}.{R} {country['flag']} {TEXT}{country['name']}{R}"
                f" {FAINT}{country['cc']}{R}{dot}")
        if len(hits) > 8:
            say(f"{FAINT}+{len(hits) - 8} more, refine your search{R}")

        choice = ask("pick number  (Enter to refine, q cancel) › ", default="")
        if choice is None:
            return None
        if choice.lower() in ("q", "quit", "exit"):
            return current
        if choice.isdigit() and 1 <= int(choice) <= min(len(hits), 8):
            return hits[int(choice) - 1]


class Spinner:
    FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self, label):
        self.label = label
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        index = 0
        while not self.stop.is_set():
            frame = self.FRAMES[index % len(self.FRAMES)]
            sys.stdout.write(f"\r   {MINT}{frame}{R} {DIM}{self.label}{R}   ")
            sys.stdout.flush()
            index += 1
            time.sleep(0.075)
        sys.stdout.write("\r" + " " * (len(self.label) + 12) + "\r")
        sys.stdout.flush()

    def __enter__(self):
        if not ANIM:
            out(f"   {DIM}{self.label}{R}")
            return self
        self.thread.start()
        return self

    def __exit__(self, *exc):
        if not ANIM:
            return
        self.stop.set()
        self.thread.join()


class RateLimitError(RuntimeError):
    def __init__(self, message, retry_after):
        super().__init__(message)
        self.retry_after = retry_after


def fetch(endpoint, phone, country, proxies="", proxy_auth="", type_proxy=""):
    params = {"phone": phone, "country": country}
    if proxies:
        params["proxies"] = proxies
        if proxy_auth:
            params["proxy_auth"] = proxy_auth
        if type_proxy:
            params["type_proxy"] = type_proxy

    request = urllib.request.Request(endpoint + "?" + urllib.parse.urlencode(params), headers={
        "Accept": "application/json",
        "User-Agent": "PHONE-TRACE-CLI/1.0",
    })
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", "replace")
        if err.code != 429:
            try:
                message = (json.loads(body).get("data") or {}).get("message") or ""
            except (json.JSONDecodeError, AttributeError):
                message = " ".join(body.split())
            raise RuntimeError(message[:180] or f"http error {err.code}")
        try:
            retry_after = int(json.loads(body)["data"].get("retry_after") or 0)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            retry_after = int(err.headers.get("Retry-After") or 0)
        raise RateLimitError("rate limit exceeded", retry_after or 60)

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        message = " ".join(body.split())
        raise RuntimeError(message[:180] or "empty response from api")
    data = payload.get("data") or {}
    if data.get("status") != "success":
        message = data.get("message") or "lookup failed"
        if data.get("code") == 429:
            raise RateLimitError(message, int(data.get("retry_after") or 60))
        raise RuntimeError(message)
    return data.get("data") or {}, data


def carrier_emoji(name):
    name = str(name or "")
    if "verizon" in name.lower():
        return "📡"
    if "t-mobile" in name.lower() or "tmobile" in name.lower():
        return "📲"
    if "sprint" in name.lower():
        return "🛰️"
    if "at&t" in name.lower() or "at and t" in name.lower():
        return "📶"
    return "☎️"


def type_emoji(kind):
    kind = str(kind or "").lower()
    if "mobile" in kind or "wireless" in kind or "cell" in kind:
        return "📱"
    if "landline" in kind or "fixed" in kind:
        return "☎️"
    if "voip" in kind or "virtual" in kind:
        return "🛰️"
    return "📞"


def fmt_phone(number):
    number = str(number or "")
    if len(number) == 10:
        return f"({number[:3]}) {number[3:6]}-{number[6:]}"
    return number or "—"


def show_result(record, meta):
    columns = min(shutil.get_terminal_size((100, 24)).columns, 74)
    key_width = 19
    value_width = max(24, columns - key_width - 7)

    pairs = [
        ("📱 phone", fmt_phone(record.get("phone"))),
        ("📡 carrier", f"{carrier_emoji(record.get('carrier_name'))} {record.get('carrier_name') or 'N/A'}"),
        ("✅ valid", "✅ TRUE" if record.get("carrier_valid") else "⚠️  FALSE"),
        ("🏷️  code", record.get("carrier_abbrev") or "N/A"),
        ("📶 line type", f"{type_emoji(record.get('phone_type'))} {record.get('phone_type') or 'N/A'}"),
        ("💬 sms gateway", record.get("sms_gateway") or "N/A"),
        ("📨 mms gateway", record.get("mms_gateway") or "N/A"),
        ("👥 social", f"👥 {record.get('social_profiles_count')}" if record.get("social_profiles_count") is not None else "N/A"),
        ("🗺️  address", record.get("address") or "N/A"),
        ("🏙️  city", f"🏙️  {record.get('city') or 'N/A'}"),
        ("🏛️  state", f"🏛️  {record.get('state') or 'N/A'}"),
        ("📮 postcode", f"📮 {record.get('postcode') or 'N/A'}"),
        ("🌐 country", f"{record.get('country') or 'N/A'} ({record.get('country_code') or '—'})"),
        ("📡 coords", f"{record.get('latitude')}, {record.get('longitude')}" if record.get("latitude") else "N/A"),
    ]

    out()
    out(f" {MINT}┏{'━' * (key_width + 2)}┳{'━' * (value_width + 2)}┓{R}")
    out(f" {MINT}┃{R} {DIM}{pad(' TRACE REPORT', key_width)}{R} {MINT}┃{R} "
        f"{MINT3}{pad(' ' + str(meta.get('DATE', '')), value_width)}{R} {MINT}┃{R}")
    out(f" {MINT}┡{'━' * (key_width + 2)}╇{'━' * (value_width + 2)}┩{R}")

    for key, value in pairs:
        chunks = wrap(str(value), value_width)
        for index, chunk in enumerate(chunks):
            left = pad(f" {key}" if index == 0 else " ", key_width)
            out(f" {MINT}│{R} {FAINT}{left}{R} {MINT}│{R} {TEXT}{pad(chunk, value_width)}{R} {MINT}│{R}")
        if ANIM:
            time.sleep(0.03)

    out(f" {MINT}└{'─' * (key_width + 2)}┴{'─' * (value_width + 2)}┘{R}")
    out()

    lat, lon = record.get("latitude"), record.get("longitude")
    link = record.get("google_maps") or ""
    if lat and lon:
        out(f"   {MINT}🛰️  {WHITE}{lat}, {lon}{R}")
        out(f"   {DIM}map › {R}{MINT3}{link}{R}")
        if ANIM and ask("open map in browser? (y/N) › ", default="n").lower().startswith("y"):
            webbrowser.open(link)
    else:
        say(f"{WARN}no coordinates in this report{R}")

    out()
    out(f"   {MINT}✔ {WHITE}{meta.get('message', 'TRACE COMPLETE')}{R}")
    out(f"   {FAINT}source {DIM}{meta.get('API_FROM', 'DARKXCODE')}{FAINT} · operator {MINT}{meta.get('AUTHOR', 'ZLAXTERT')}{R}")
    out()


def ask_proxy():
    """Optional proxy block. Returns (proxies, proxy_auth, type_proxy) or (None, ...) on abort."""
    raw = ask("proxy  (host:port, Enter for direct)", default="")
    if raw is None:
        return None, "", ""
    proxies = raw.strip()
    if not proxies:
        return "", "", ""

    proxy_auth = ask("proxy auth  (user:pass, optional)", default="").strip()
    out(f"{DIM}   types:{R} {TEXT}http https socks4 socks4a socks5 socks5h{R} {FAINT}(Enter = auto){R}")
    type_proxy = ask("type_proxy", default="").strip().lower()
    return proxies, proxy_auth, type_proxy


def main():
    banner()

    endpoint = ask("api endpoint", default=DEFAULT_URL)
    if endpoint is None:
        return
    if not endpoint.lower().startswith(("http://", "https://")):
        endpoint = "http://" + endpoint

    country = next(c for c in COUNTRIES if c["cc"] == "US")
    out()
    say(f"{DIM}tip: All country accepted by this api endpoint{R}")
    out()

    proxies, proxy_auth, type_proxy = ask_proxy()
    if proxies is None:
        return
    if proxies:
        say(f"{MINT}●{R} {DIM}routing via {MINT}{proxies}{R}{DIM} · {type_proxy or 'auto'}{R}")
    else:
        say(f"{FAINT}● direct connection{R}")
    out()

    while True:
        country = pick_country(country)
        if country is None:
            break
        if country["cc"] not in SUPPORTED:
            say(f"{BAD}✖ {country['name']} is not supported by this endpoint · use US or CA{R}")
            continue

        raw = ask(f"phone number  ({country['flag']} {country['cc']}) › ", default="")
        if raw is None:
            break
        if raw.lower() in ("q", "quit", "exit"):
            break

        digits = "".join(ch for ch in raw if ch.isdigit())
        if len(digits) < 10:
            say(f"{BAD}✖ invalid format · need at least 10 digits{R}")
            continue

        out()
        try:
            with Spinner(f"querying carrier & geo databases · {fmt_phone(digits)}"):
                record, meta = fetch(endpoint, digits, country["cc"].lower(), proxies, proxy_auth, type_proxy)
        except RateLimitError as err:
            wait = err.retry_after
            say(f"{BAD}✖ rate limit hit · api max 2×/min · wait {MINT}{wait}s{R}")
            while wait > 0:
                step = min(wait, 5)
                with Spinner(f"cooling down · {wait}s left"):
                    time.sleep(step)
                wait -= step
        except urllib.error.URLError as err:
            say(f"{BAD}✖ connection failed · {err.reason}{R}")
        except RuntimeError as err:
            say(f"{BAD}✖ {err}{R}")
        except TimeoutError:
            say(f"{BAD}✖ request timed out{R}")
        else:
            show_result(record, meta)

        again = ask("trace another number? (Y/n) › ", default="y")
        if again is None or again.lower().startswith("n"):
            break

    out(f"{FAINT}  ── session closed · stay curious ──{R}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        out(f"\n{FAINT}  ── interrupted ──{R}")
        sys.exit(0)
