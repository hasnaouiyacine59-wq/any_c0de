import random
import string
import sys
import os
import requests
sys.path.insert(0, os.path.dirname(__file__))
from faker import Faker
from get_2FA import get_2fa
from playwright.sync_api import sync_playwright

fake = Faker()

# ── Colors ────────────────────────────────────────────────────────────────────
R = "\033[0m"; B = "\033[1m"
GREEN = "\033[92m"; CYAN = "\033[96m"; YELLOW = "\033[93m"
RED = "\033[91m"; BLUE = "\033[94m"; MAGENTA = "\033[95m"

TOTAL_STEPS = 9

def banner():
    print(f"""
{B}{MAGENTA}
  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  ░  {CYAN}any_c0de {YELLOW}—Funny Project{MAGENTA}  ░
  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{R}
""")

def step(n, msg, color=CYAN, status="•"):
    bar = f"{BLUE}[{n:02d}/{TOTAL_STEPS}]{R}"
    print(f"  {bar} {B}{color}{status}{R} {msg}")

def biss():
    input(f"  {B}{YELLOW}[PAUSE]{R} Press Enter to continue...")

def dump(page, label="dump"):
    import json
    path = f"/tmp/{label}.json"
    data = page.evaluate("""() => Array.from(document.querySelectorAll('*')).map(el => ({
        tag: el.tagName, id: el.id || null,
        class: el.className || null,
        text: (el.innerText || '').slice(0, 80)
    }))""")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    step(0, f"Dumped {len(data)} elements → {path}", MAGENTA, "📄")

# ── Tor IP helpers ─────────────────────────────────────────────────────────────
def get_ip_info(proxy_url=None, retries=6, delay=5):
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    urls = ["http://ipwho.is/", "http://ip-api.com/json", "http://api.ipify.org?format=json"]
    for attempt in range(retries):
        for url in urls:
            try:
                r = requests.get(url, timeout=10, proxies=proxies)
                data = r.json()
                if data.get("ip") or data.get("query"):
                    data.setdefault("ip", data.get("query"))
                    data.setdefault("country_code", data.get("countryCode", "US"))
                    return data
            except Exception as e:
                pass
        step(0, f"IP lookup retry {attempt+1}/{retries}...", YELLOW, "⟳")
        import time as _t; _t.sleep(delay)
    return {}

CC_LANG = {
    "US": ("en-US", "America/New_York",    "en-US,en;q=0.9"),
    "GB": ("en-GB", "Europe/London",       "en-GB,en;q=0.9"),
    "DE": ("de-DE", "Europe/Berlin",       "de-DE,de;q=0.9,en;q=0.8"),
    "FR": ("fr-FR", "Europe/Paris",        "fr-FR,fr;q=0.9,en;q=0.8"),
    "IT": ("it-IT", "Europe/Rome",         "it-IT,it;q=0.9,en;q=0.8"),
    "ES": ("es-ES", "Europe/Madrid",       "es-ES,es;q=0.9,en;q=0.8"),
    "NL": ("nl-NL", "Europe/Amsterdam",    "nl-NL,nl;q=0.9,en;q=0.8"),
    "PL": ("pl-PL", "Europe/Warsaw",       "pl-PL,pl;q=0.9,en;q=0.8"),
    "BR": ("pt-BR", "America/Sao_Paulo",   "pt-BR,pt;q=0.9,en;q=0.8"),
    "RU": ("ru-RU", "Europe/Moscow",       "ru-RU,ru;q=0.9,en;q=0.8"),
    "TR": ("tr-TR", "Europe/Istanbul",     "tr-TR,tr;q=0.9,en;q=0.8"),
    "JP": ("ja-JP", "Asia/Tokyo",          "ja-JP,ja;q=0.9,en;q=0.8"),
    "CN": ("zh-CN", "Asia/Shanghai",       "zh-CN,zh-Hans;q=0.9,en;q=0.8"),
    "SE": ("sv-SE", "Europe/Stockholm",    "sv-SE,sv;q=0.9,en;q=0.8"),
    "CA": ("en-CA", "America/Toronto",     "en-CA,en;q=0.9,fr;q=0.8"),
    "AU": ("en-AU", "Australia/Sydney",    "en-AU,en;q=0.9"),
    "IN": ("en-IN", "Asia/Kolkata",        "en-IN,en;q=0.9,hi;q=0.8"),
    "MX": ("es-MX", "America/Mexico_City", "es-MX,es;q=0.9,en;q=0.8"),
    "KR": ("ko-KR", "Asia/Seoul",          "ko-KR,ko;q=0.9,en;q=0.8"),
    "SG": ("en-SG", "Asia/Singapore",      "en-SG,en;q=0.9,zh;q=0.8"),
    "NO": ("nb-NO", "Europe/Oslo",         "nb-NO,nb;q=0.9,en;q=0.8"),
    "CH": ("de-CH", "Europe/Zurich",       "de-CH,de;q=0.9,en;q=0.8"),
    "AT": ("de-AT", "Europe/Vienna",       "de-AT,de;q=0.9,en;q=0.8"),
    "BE": ("fr-BE", "Europe/Brussels",     "fr-BE,fr;q=0.9,nl;q=0.8,en;q=0.7"),
    "MA": ("ar-MA", "Africa/Casablanca",   "ar-MA,ar;q=0.9,fr;q=0.8,en;q=0.7"),
    "DZ": ("ar-DZ", "Africa/Algiers",      "ar-DZ,ar;q=0.9,fr;q=0.8,en;q=0.7"),
    "SA": ("ar-SA", "Asia/Riyadh",         "ar-SA,ar;q=0.9,en;q=0.8"),
    "AE": ("ar-AE", "Asia/Dubai",          "ar-AE,ar;q=0.9,en;q=0.8"),
    "ZA": ("en-ZA", "Africa/Johannesburg", "en-ZA,en;q=0.9"),
    "NG": ("en-NG", "Africa/Lagos",        "en-NG,en;q=0.9"),
    "UA": ("uk-UA", "Europe/Kyiv",         "uk-UA,uk;q=0.9,en;q=0.8"),
    "RO": ("ro-RO", "Europe/Bucharest",    "ro-RO,ro;q=0.9,en;q=0.8"),
    "CZ": ("cs-CZ", "Europe/Prague",       "cs-CZ,cs;q=0.9,en;q=0.8"),
    "PT": ("pt-PT", "Europe/Lisbon",       "pt-PT,pt;q=0.9,en;q=0.8"),
    "HU": ("hu-HU", "Europe/Budapest",     "hu-HU,hu;q=0.9,en;q=0.8"),
    "GR": ("el-GR", "Europe/Athens",       "el-GR,el;q=0.9,en;q=0.8"),
    "ID": ("id-ID", "Asia/Jakarta",        "id-ID,id;q=0.9,en;q=0.8"),
    "TH": ("th-TH", "Asia/Bangkok",        "th-TH,th;q=0.9,en;q=0.8"),
    "VN": ("vi-VN", "Asia/Ho_Chi_Minh",    "vi-VN,vi;q=0.9,en;q=0.8"),
    "PH": ("en-PH", "Asia/Manila",         "en-PH,en;q=0.9,fil;q=0.8"),
    "NZ": ("en-NZ", "Pacific/Auckland",    "en-NZ,en;q=0.9"),
    "AR": ("es-AR", "America/Argentina/Buenos_Aires", "es-AR,es;q=0.9,en;q=0.8"),
    "CL": ("es-CL", "America/Santiago",    "es-CL,es;q=0.9,en;q=0.8"),
    "CO": ("es-CO", "America/Bogota",      "es-CO,es;q=0.9,en;q=0.8"),
    "HK": ("zh-HK", "Asia/Hong_Kong",      "zh-HK,zh-Hant;q=0.9,en;q=0.8"),
    "TW": ("zh-TW", "Asia/Taipei",         "zh-TW,zh-Hant;q=0.9,en;q=0.8"),
    "IE": ("en-IE", "Europe/Dublin",       "en-IE,en;q=0.9"),
    "FI": ("fi-FI", "Europe/Helsinki",     "fi-FI,fi;q=0.9,en;q=0.8"),
    "DK": ("da-DK", "Europe/Copenhagen",   "da-DK,da;q=0.9,en;q=0.8"),
    "BG": ("bg-BG", "Europe/Sofia",        "bg-BG,bg;q=0.9,en;q=0.8"),
    "HR": ("hr-HR", "Europe/Zagreb",       "hr-HR,hr;q=0.9,en;q=0.8"),
    "SK": ("sk-SK", "Europe/Bratislava",   "sk-SK,sk;q=0.9,en;q=0.8"),
    "LT": ("lt-LT", "Europe/Vilnius",      "lt-LT,lt;q=0.9,en;q=0.8"),
    "LV": ("lv-LV", "Europe/Riga",         "lv-LV,lv;q=0.9,en;q=0.8"),
    "EE": ("et-EE", "Europe/Tallinn",      "et-EE,et;q=0.9,en;q=0.8"),
    "RS": ("sr-RS", "Europe/Belgrade",     "sr-RS,sr-Cyrl;q=0.9,en;q=0.8"),
    "PK": ("ur-PK", "Asia/Karachi",        "ur-PK,ur;q=0.9,en;q=0.8"),
    "BD": ("bn-BD", "Asia/Dhaka",          "bn-BD,bn;q=0.9,en;q=0.8"),
    "EG": ("ar-EG", "Africa/Cairo",        "ar-EG,ar;q=0.9,en;q=0.8"),
    "IL": ("he-IL", "Asia/Jerusalem",      "he-IL,he;q=0.9,en;q=0.8"),
    "KZ": ("kk-KZ", "Asia/Almaty",         "kk-KZ,kk;q=0.9,ru;q=0.8,en;q=0.7"),
    "MY": ("ms-MY", "Asia/Kuala_Lumpur",   "ms-MY,ms;q=0.9,en;q=0.8"),
}

def get_ip():
    try:
        r = requests.get("http://127.0.0.1:5000/ip", timeout=5)
        return r.json().get("ip", "unknown")
    except Exception as e:
        return f"error({e})"

def reset_ip():
    try:
        r = requests.get("http://127.0.0.1:5000/reset-ip", timeout=15)
        step(0, f"reset-ip status={r.status_code} body={r.text[:200]}", YELLOW)
        new_ip = get_ip()
        step(0, f"IP rotated → {new_ip}", GREEN, "🔄")
        return new_ip
    except Exception as e:
        step(0, f"reset-ip failed: {e}", RED, "✗")
        return None

DOMAINS = ["alpha-sig.eu.org","ubua83@ziw0tempemail.eu.org", "alpha804.eu.org", "bitcoin-plazza.eu.org", "youoneshell.eu.org"]
VIEWPORTS = [(1366, 768), (1440, 900), (1536, 864), (1920, 1080), (1280, 720)]
LOCALES = ["en-US", "en-GB", "en-CA", "fr-FR", "de-DE"]
TIMEZONES = ["America/New_York", "Europe/London", "Europe/Paris", "America/Chicago", "Asia/Tokyo"]

def random_num(n=4):
    return ''.join(random.choices(string.digits, k=n))

def generate_user():
    fname = fake.first_name()
    lname = fake.last_name()
    num = random_num()

    # email = f"kalawssimatrix+{num}@gmail.com"
    email = f"{fname.lower()}.{lname.lower()}@{random.choice(DOMAINS)}"
    username = f"{fname.lower()}{lname.lower()}{num}"
    password = f"{fname}{lname}{num}!"

    return {
        "first_name": fname,
        "last_name": lname,
        "email": email,
        "username": username,
        "password": password,
    }

if __name__ == "__main__":
    user = generate_user()
    password = "testpassw0rdDZA*"

    with sync_playwright() as p:
        banner()
        vp = random.choice(VIEWPORTS)

        # unique per-run fingerprint values
        fp = {
            "canvas_r": random.randint(-8, 8),
            "canvas_g": random.randint(-8, 8),
            "canvas_b": random.randint(-8, 8),
            "webgl_vendor": "Google Inc.",
            "webgl_renderer": "__PLACEHOLDER__",  # set after profile selection
            "hardwareConcurrency": random.choice([2, 4, 6, 8, 12, 16]),
            "deviceMemory": random.choice([2, 4, 8]),
            "platform": random.choice(["Win32", "Linux x86_64", "MacIntel"]),
            "screen_w": vp[0], "screen_h": vp[1],
            "depth": random.choice([24, 30]),
            "tz_offset": random.choice([-300, -240, 0, 60, 120, 330, 540]),
        }

        # rotate IP before launch
        step(0, f"Current IP: {get_ip()}", CYAN, "🌐")
        reset_ip()
        _new_ip = get_ip()
        step(0, f"New IP: {_new_ip}", GREEN, "🌐")

        # resolve locale/tz/lang from exit IP country
        _ip_info = get_ip_info("socks5://127.0.0.1:9050")
        _cc      = (_ip_info.get("country_code") or "US").upper()
        _ip_locale, _ip_tz, _ip_accept = CC_LANG.get(_cc, CC_LANG["US"])
        step(0, f"IP country: {_ip_info.get('country','?')} ({_cc}) → locale={_ip_locale} tz={_ip_tz}", CYAN, "🗺")

        # ── profile vars — must be before launch (used in --user-agent arg) ──
        import json as _json
        PROFILES = [
            {"os": "Windows", "_platform": "Win32",    "_ua_platform": "Windows", "_ua_platform_ver": "10.0.0",
             "chrome_ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
             "fonts": ['Arial','Arial Black','Comic Sans MS','Courier New','Georgia','Impact','Times New Roman','Trebuchet MS','Verdana','Tahoma','Segoe UI','Calibri','Cambria']},
            {"os": "Mac",     "_platform": "MacIntel", "_ua_platform": "macOS",   "_ua_platform_ver": "13.4.0",
             "chrome_ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
             "fonts": ['Arial','Helvetica','Times New Roman','Courier New','Georgia','Verdana','Trebuchet MS','Arial Black','Impact','Helvetica Neue','Menlo']},
        ]
        prof             = random.choice(PROFILES)
        _platform        = prof["_platform"]
        _ua_platform     = prof["_ua_platform"]
        _ua_platform_ver = prof["_ua_platform_ver"]
        chrome_ua        = prof["chrome_ua"]
        _chrome_ver      = "130"
        _app_version     = chrome_ua.split("Mozilla/5.0 ")[1]
        chosen_locale    = _ip_locale
        chosen_tz        = _ip_tz
        accept_lang      = _ip_accept
        lang_primary     = chosen_locale
        lang_base        = chosen_locale.split("-")[0]
        chosen_viewport  = {"width": vp[0], "height": vp[1]}
        toolbar_height   = random.choice([74, 85, 90])
        dpr              = random.choice([1, 1.25, 1.5, 2])
        hw_concurrency   = fp["hardwareConcurrency"]
        device_memory    = fp["deviceMemory"]
        canvas_salt      = random.randint(1, 15)
        audio_salt       = round(random.uniform(0.00001, 0.00009), 6)
        webgl_vendor     = "Google Inc."
        # OS-matched ANGLE renderer from exampl1.py
        _webgl_windows = [
            "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (AMD, AMD Radeon RX 6600 XT Direct3D11 vs_5_0 ps_5_0, D3D11)",
        ]
        _webgl_mac = [
            "ANGLE (Apple, ANGLE Metal Renderer: Apple M1, Unspecified Version)",
            "ANGLE (Apple, ANGLE Metal Renderer: Apple M1 Pro, Unspecified Version)",
            "ANGLE (Apple, ANGLE Metal Renderer: Apple M2, Unspecified Version)",
            "ANGLE (Intel, ANGLE Metal Renderer: Intel(R) Iris(R) Plus Graphics, Unspecified Version)",
        ]
        if "Windows" in chrome_ua:
            webgl_renderer = random.choice(_webgl_windows)
        else:
            webgl_renderer = random.choice(_webgl_mac)
        battery_charging = "true" if random.random() > 0.4 else "false"
        battery_level    = round(random.uniform(0.4, 1.0), 2)
        rtt              = random.choice([50, 100, 150, 200])
        downlink         = round(random.uniform(5, 50), 1)

        import tempfile, shutil
        _tmp_profile = tempfile.mkdtemp(prefix="pw_profile_")
        step(1, "Launching browser...", CYAN, "⟳")

        _ext_path = os.path.join(os.path.dirname(__file__), 'ext')
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                f"--disable-extensions-except={_ext_path}",
                f"--load-extension={_ext_path}",
                "--disable-plugins-discovery",
                "--start-maximized",
                "--force-device-scale-factor=1",
                "--font-render-hinting=none",
                "--proxy-server=socks5://127.0.0.1:9050",
                "--disable-webrtc",
                "--enforce-webrtc-ip-permission-check",
                "--webrtc-ip-handling-policy=disable_non_proxied_udp",
                "--force-webrtc-ip-handling-policy",
                "--disable-background-networking",
                "--disable-features=ServiceWorker,SharedWorker",
                f"--user-agent={chrome_ua}",
            ],
            ignore_default_args=["--enable-automation"],
        )

        context = browser.new_context(
            no_viewport=True,
            locale=chosen_locale,
            timezone_id=chosen_tz,
            color_scheme=random.choice(["light", "dark"]),
            user_agent=chrome_ua,
        )

        step(1, f"Fingerprint seed: concurrency={fp['hardwareConcurrency']} mem={fp['deviceMemory']}GB platform={fp['platform']}", CYAN)
        step(1, "Browser launched + Tor proxy active (socks5://127.0.0.1:9050).", GREEN, "✓")
        page = context.new_page()

        # clear any cached service workers via CDP before any navigation
        cdp = context.new_cdp_session(page)
        try:
            cdp.send("Network.clearBrowserCache")
            cdp.send("Network.clearBrowserCookies")
            # unregister all service workers
            cdp.send("ServiceWorker.enable")
            regs = cdp.send("ServiceWorker.getRegistrations") or {}
            for reg in regs.get("registrations", []):
                try:
                    cdp.send("ServiceWorker.unregister", {"scopeURL": reg["scopeURL"]})
                except Exception:
                    pass
            cdp.send("ServiceWorker.stopAllWorkers")
        except Exception:
            pass
        cdp.send("Network.setUserAgentOverride", {
            "userAgent": chrome_ua,
            "platform":  _platform,
        })
        step(1, f"CDP UA override → {chrome_ua[:60]}...", GREEN, "✓")


        context.add_init_script(f"""
            // ── 1. webdriver ──
            try {{ delete Object.getPrototypeOf(navigator).webdriver; }} catch(e) {{}}

            // ── fix ActiveText color (headless detection) ──
            // In Xvfb/headless, getComputedStyle returns rgb(255,0,0) for ActiveText
            // Patch getComputedStyle to return a normal color instead
            (function() {{
                const _origGCS = window.getComputedStyle;
                window.getComputedStyle = function(el, pseudo) {{
                    const style = _origGCS.call(this, el, pseudo);
                    const _origGPV = style.getPropertyValue.bind(style);
                    style.getPropertyValue = function(prop) {{
                        const val = _origGPV(prop);
                        if (val === 'rgb(255, 0, 0)') return 'rgb(220, 53, 69)';
                        return val;
                    }};
                    if (style.backgroundColor === 'rgb(255, 0, 0)')
                        Object.defineProperty(style, 'backgroundColor', {{ get: () => 'rgb(220, 53, 69)' }});
                    return style;
                }};
            }})();

            // ── block service/shared workers from leaking real values ──
            (function() {{
                // Override serviceWorker.register to prevent creepworker from loading
                if (navigator.serviceWorker) {{
                    Object.defineProperty(navigator, 'serviceWorker', {{
                        get: () => ({{
                            register: () => Promise.reject(new Error('blocked')),
                            ready: new Promise(() => {{}}),
                            getRegistrations: () => Promise.resolve([]),
                            addEventListener: () => {{}},
                        }})
                    }});
                }}
                // Block SharedWorker + DedicatedWorker pointing to creepworker
                window.SharedWorker = undefined;
                Object.defineProperty(window, 'SharedWorker', {{ get: () => undefined, set: () => {{}} }});
                // Patch Worker to intercept creepworker.js
                const _Worker = window.Worker;
                window.Worker = function(url, ...a) {{
                    if (typeof url === 'string' && url.includes('creep')) {{
                        throw new TypeError('blocked');
                    }}
                    return new _Worker(url, ...a);
                }};
                window.Worker.prototype = _Worker.prototype;
            }})();
            // ── 2. window.chrome ──
            // inject early so chrome appears at correct index in window properties
            (function() {{
                function _nativeThrow() {{ throw new TypeError('Illegal invocation'); }}
                const _runtime = {{
                    id: undefined,
                    lastError: undefined,
                    OnInstalledReason: {{}}, OnRestartRequiredReason: {{}},
                    PlatformArch: {{}}, PlatformNaclArch: {{}},
                    PlatformOs: {{}}, RequestUpdateCheckStatus: {{}},
                    connect: function connect() {{ return undefined; }},
                    sendMessage: function sendMessage() {{
                        try {{ new (function(){{}})(); }} catch(e) {{}}
                        throw new TypeError('Error in invocation of runtime.sendMessage');
                    }},
                    getManifest: function getManifest() {{ return {{}}; }},
                    getURL: function getURL(p) {{ return `chrome-extension://invalid/${{p}}`; }},
                }};
                // make sendMessage/connect throw on `new`
                Object.defineProperty(_runtime.sendMessage, 'prototype', {{ get: _nativeThrow }});
                Object.defineProperty(_runtime.connect,     'prototype', {{ get: _nativeThrow }});

                window.chrome = {{
                    app: {{ isInstalled: false, InstallState: {{}}, RunningState: {{}} }},
                    csi: function csi() {{ return {{ pageT: Date.now(), startE: Date.now(), tran: Math.floor(Math.random()*20)+1 }}; }},
                    loadTimes: function loadTimes() {{
                        const t = Date.now() / 1000;
                        return {{ commitLoadTime: t-0.4, connectionInfo:'h2', finishDocumentLoadTime:t-0.1,
                                  finishLoadTime:t, firstPaintAfterLoadTime:0, firstPaintTime:t-0.3,
                                  navigationType:'Other', npnNegotiatedProtocol:'h2', requestTime:t-0.5,
                                  startLoadTime:t-0.5, wasAlternateProtocolAvailable:false,
                                  wasFetchedViaSpdy:true, wasNpnNegotiated:true }};
                    }},
                    runtime: _runtime,
                    webstore: {{ onInstallStageChanged: {{}}, onDownloadProgress: {{}} }},
                }};
            }})();

            // ── 3. plugins ──
            (function() {{
                function _mime(type,suf,desc) {{ return {{type,suffixes:suf,description:desc,enabledPlugin:null}}; }}
                function _plugin(name,fn,desc,mimes) {{
                    const p={{name,filename:fn,description:desc,length:mimes.length}};
                    mimes.forEach((m,i)=>{{p[i]=m;m.enabledPlugin=p;}});
                    p.item=(i)=>p[i]??null; p.namedItem=(n)=>mimes.find(m=>m.type===n)??null;
                    p[Symbol.iterator]=function*(){{for(let i=0;i<this.length;i++)yield this[i];}};
                    return p;
                }}
                const pdf1=_mime('application/pdf','pdf','Portable Document Format');
                const pdf2=_mime('text/pdf','pdf','Portable Document Format');
                const plugins=[
                    _plugin('PDF Viewer','internal-pdf-viewer','Portable Document Format',[pdf1,pdf2]),
                    _plugin('Chrome PDF Viewer','internal-pdf-viewer','Portable Document Format',[pdf1,pdf2]),
                    _plugin('Chromium PDF Viewer','internal-pdf-viewer','Portable Document Format',[pdf1,pdf2]),
                ];
                const pa={{length:plugins.length}};
                plugins.forEach((p,i)=>{{pa[i]=p;}});
                pa.item=(i)=>pa[i]??null; pa.namedItem=(n)=>plugins.find(p=>p.name===n)??null;
                pa.refresh=()=>{{}}; pa[Symbol.iterator]=function*(){{for(let i=0;i<this.length;i++)yield this[i];}};
                Object.defineProperty(navigator,'plugins',{{get:()=>pa}});
                const allMimes=[pdf1,pdf2]; const ma={{length:allMimes.length}};
                allMimes.forEach((m,i)=>{{ma[i]=m;}});
                ma.item=(i)=>ma[i]??null; ma.namedItem=(n)=>allMimes.find(m=>m.type===n)??null;
                ma[Symbol.iterator]=function*(){{for(let i=0;i<this.length;i++)yield this[i];}};
                Object.defineProperty(navigator,'mimeTypes',{{get:()=>ma}});
            }})();

            // ── 4. platform ──
            Object.defineProperty(navigator,'platform',{{get:()=>'{_platform}'}});

            // ── 5. userAgentData ──
            (function() {{
                const _brands=[
                    {{brand:'Not=A?Brand',version:'99'}},
                    {{brand:'Chromium',version:'{_chrome_ver}'}},
                    {{brand:'Google Chrome',version:'{_chrome_ver}'}},
                ];
                const _uad={{
                    brands:_brands, mobile:false, platform:'{_ua_platform}',
                    toJSON:()=>({{brands:_brands,mobile:false,platform:'{_ua_platform}'}}),
                    getHighEntropyValues:(hints)=>Promise.resolve({{
                        architecture:'x86', bitness:'64', brands:_brands,
                        fullVersionList:[
                            {{brand:'Not=A?Brand',version:'99.0.0.0'}},
                            {{brand:'Chromium',version:'{_chrome_ver}.0.0.0'}},
                            {{brand:'Google Chrome',version:'{_chrome_ver}.0.0.0'}},
                        ],
                        mobile:false, model:'', platform:'{_ua_platform}',
                        platformVersion:'{_ua_platform_ver}', uaFullVersion:'{_chrome_ver}.0.0.0', wow64:false,
                    }}),
                }};
                Object.defineProperty(navigator,'userAgentData',{{get:()=>_uad}});
            }})();

            // ── 6. touch ──
            Object.defineProperty(navigator,'maxTouchPoints',{{get:()=>0}});

            // ── 7. language ──
            Object.defineProperty(navigator,'languages',{{get:()=>{_json.dumps([t.split(';')[0] for t in accept_lang.split(',')])}}});
            Object.defineProperty(navigator,'language', {{get:()=>'{lang_primary}'}});

            // ── 8. misc navigator ──
            Object.defineProperty(navigator,'vendor',       {{get:()=>'Google Inc.'}});
            Object.defineProperty(navigator,'doNotTrack',   {{get:()=>null}});
            Object.defineProperty(navigator,'cookieEnabled',{{get:()=>true}});
            Object.defineProperty(navigator,'appName',      {{get:()=>'Netscape'}});
            Object.defineProperty(navigator,'appVersion',   {{get:()=>'{_app_version}'}});
            Object.defineProperty(navigator,'product',      {{get:()=>'Gecko'}});
            Object.defineProperty(navigator,'productSub',   {{get:()=>'20030107'}});

            // ── 9. window geometry ──
            const _toolbarH={toolbar_height};
            Object.defineProperty(window, 'outerHeight',{{get:()=>window.innerHeight+_toolbarH}});
            Object.defineProperty(window, 'outerWidth', {{get:()=>window.innerWidth}});
            Object.defineProperty(screen, 'width',      {{get:()=>{chosen_viewport['width']}}});
            Object.defineProperty(screen, 'height',     {{get:()=>{chosen_viewport['height']}}});
            Object.defineProperty(screen, 'availWidth', {{get:()=>{chosen_viewport['width']}}});
            Object.defineProperty(screen, 'availHeight',{{get:()=>{chosen_viewport['height']}}});
            Object.defineProperty(screen, 'availTop',   {{get:()=>0}});
            Object.defineProperty(screen, 'availLeft',  {{get:()=>0}});
            Object.defineProperty(screen, 'colorDepth', {{get:()=>24}});
            Object.defineProperty(screen, 'pixelDepth', {{get:()=>24}});
            Object.defineProperty(window,'devicePixelRatio',{{get:()=>{dpr}}});

            // ── 10. hardware ──
            Object.defineProperty(navigator,'hardwareConcurrency',{{get:()=>{hw_concurrency}}});
            Object.defineProperty(navigator,'deviceMemory',       {{get:()=>{device_memory}}});

            // ── 11. canvas noise — use defineProperty to avoid prototype lie detection ──
            (function() {{
                const SEED = {canvas_salt} * 1000 + Math.floor(Math.random() * 0xffff);
                function _rng(i) {{ const x = Math.sin(SEED+i)*10000; return x-Math.floor(x); }}
                function _noise(data) {{
                    for(let i=0;i<data.length;i+=4) {{
                        data[i]  =Math.min(255,Math.max(0,data[i]  +Math.floor(_rng(i)  *4)-2));
                        data[i+1]=Math.min(255,Math.max(0,data[i+1]+Math.floor(_rng(i+1)*4)-2));
                        data[i+2]=Math.min(255,Math.max(0,data[i+2]+Math.floor(_rng(i+2)*4)-2));
                    }}
                }}
                const _orig2d  = CanvasRenderingContext2D.prototype.getImageData;
                const _origURL = HTMLCanvasElement.prototype.toDataURL;
                const _origBlob= HTMLCanvasElement.prototype.toBlob;

                function _noisedURL(canvas, args) {{
                    const off=document.createElement('canvas');
                    off.width=canvas.width; off.height=canvas.height;
                    const ctx=off.getContext('2d');
                    ctx.drawImage(canvas,0,0);
                    if(canvas.width&&canvas.height){{
                        const img=_orig2d.call(ctx,0,0,off.width,off.height);
                        _noise(img.data); ctx.putImageData(img,0,0);
                    }}
                    return _origURL.apply(off,args);
                }}

                // replace via defineProperty on prototype — less detectable than direct assignment
                const _toDataURL = function toDataURL(...a) {{ return _noisedURL(this,a); }};
                const _toBlob    = function toBlob(cb,...a) {{
                    const off=document.createElement('canvas');
                    off.width=this.width; off.height=this.height;
                    const ctx=off.getContext('2d'); ctx.drawImage(this,0,0);
                    if(this.width&&this.height){{
                        const img=_orig2d.call(ctx,0,0,off.width,off.height);
                        _noise(img.data); ctx.putImageData(img,0,0);
                    }}
                    return _origBlob.call(off,cb,...a);
                }};
                const _getImageData = function getImageData(...a) {{
                    const d=_orig2d.apply(this,a); _noise(d.data); return d;
                }};
                Object.defineProperty(HTMLCanvasElement.prototype,'toDataURL',{{value:_toDataURL,writable:true,configurable:true}});
                Object.defineProperty(HTMLCanvasElement.prototype,'toBlob',   {{value:_toBlob,   writable:true,configurable:true}});
                Object.defineProperty(CanvasRenderingContext2D.prototype,'getImageData',{{value:_getImageData,writable:true,configurable:true}});
            }})();

            // ── 12. WebGL — defineProperty to avoid lie detection ──
            (function() {{
                const V='{webgl_vendor}', R='{webgl_renderer}';
                const SEED = {canvas_salt} * 997 + Math.floor(Math.random() * 0xffff);
                function _patch(proto) {{
                    const _gp = proto.getParameter;
                    const _patched = function getParameter(p) {{
                        if(p===37445)return V; if(p===37446)return R;
                        if(p===7937) return R; if(p===7936) return V;
                        if(p===3379) return 16384; if(p===34076)return 16384;
                        if(p===3386) return new Int32Array([16384,16384]);
                        if(p===33902)return new Float32Array([1,1]);
                        if(p===33901)return new Float32Array([1,1024]);
                        return _gp.call(this,p);
                    }};
                    Object.defineProperty(proto,'getParameter',{{value:_patched,writable:true,configurable:true}});
                    const _gse = proto.getSupportedExtensions;
                    const _patchedGSE = function getSupportedExtensions() {{
                        return (_gse.call(this)||[]).filter(e=>!e.includes('debug')&&!e.includes('WEBGL_debug'));
                    }};
                    Object.defineProperty(proto,'getSupportedExtensions',{{value:_patchedGSE,writable:true,configurable:true}});

                    // noise readPixels so WebGL image hash changes per session
                    const _rp = proto.readPixels;
                    const _patchedRP = function readPixels(...a) {{
                        _rp.apply(this,a);
                        const buf=a[6];
                        if(buf instanceof Uint8Array && buf.length>=4) {{
                            buf[0]^=(SEED&0xff);
                            buf[1]^=((SEED>>8)&0xff);
                            buf[2]^=((SEED>>16)&0xff);
                            buf[3]^=((SEED>>24)&0xff);
                        }}
                    }};
                    Object.defineProperty(proto,'readPixels',{{value:_patchedRP,writable:true,configurable:true}});
                }}
                _patch(WebGLRenderingContext.prototype);
                _patch(WebGL2RenderingContext.prototype);
            }})();

            // ── 13. AudioContext noise ──
            (function() {{
                const ASALT={audio_salt};
                const _origStart=OfflineAudioContext.prototype.startRendering;
                const _patched = function startRendering() {{
                    return _origStart.call(this).then(buf=>{{
                        const ch=buf.getChannelData(0);
                        for(let i=0;i<ch.length;i++) ch[i]+=(Math.random()-0.5)*ASALT;
                        return buf;
                    }});
                }};
                Object.defineProperty(OfflineAudioContext.prototype,'startRendering',{{value:_patched,writable:true,configurable:true}});
            }})();

            // ── 14. Battery ──
            navigator.getBattery=()=>Promise.resolve({{
                charging:{battery_charging},level:{battery_level},
                chargingTime:0,dischargingTime:Infinity,addEventListener:()=>{{}}
            }});

            // ── 15. Network ──
            (function() {{
                const _conn={{type:'wifi',effectiveType:'4g',rtt:{rtt},downlink:{downlink},
                    downlinkMax:Infinity,saveData:false,onchange:null,
                    addEventListener:()>{{}},removeEventListener:()>{{}} }};
                Object.defineProperty(navigator,'connection',{{get:()=>_conn}});
            }})();

            // ── 16. Permissions ──
            (function() {{
                const _pq=navigator.permissions.query.bind(navigator.permissions);
                navigator.permissions.query=function(p){{
                    if(p.name==='notifications')return Promise.resolve({{state:'default'}});
                    if(p.name==='geolocation')  return Promise.resolve({{state:'prompt'}});
                    if(p.name==='camera')       return Promise.resolve({{state:'prompt'}});
                    if(p.name==='microphone')   return Promise.resolve({{state:'prompt'}});
                    return _pq(p);
                }};;
            }})();

            // ── 17. speechSynthesis ──
            (function() {{
                const _voices=[
                    {{voiceURI:'Google {lang_primary}',name:'Google {lang_primary}',lang:'{lang_primary}',localService:false,default:true}},
                    {{voiceURI:'Google {lang_base}',   name:'Google {lang_base}',   lang:'{lang_base}',   localService:false,default:false}},
                ];
                speechSynthesis.getVoices=()=>_voices;
            }})();

            // ── 18. mediaDevices ──
            (function() {{
                function _rnd(){{return crypto.randomUUID?crypto.randomUUID():Math.random().toString(16).slice(2).padEnd(36,'0');}}
                const _devs=[
                    {{kind:'audioinput', label:'',deviceId:_rnd(),groupId:_rnd()}},
                    {{kind:'audiooutput',label:'',deviceId:_rnd(),groupId:_rnd()}},
                    {{kind:'videoinput', label:'',deviceId:_rnd(),groupId:_rnd()}},
                ];
                if(navigator.mediaDevices)
                    navigator.mediaDevices.enumerateDevices=()=>Promise.resolve(_devs),'enumerateDevices');
            }})();

            // ── 19-22. misc ──
            Error.stackTraceLimit=10;
            if(typeof Notification!=='undefined')
                Object.defineProperty(Notification,'permission',{{get:()=>'default'}});
            (function(){{
                const _origNow=performance.now.bind(performance);
                performance.now=function(){{return _origNow()+(Math.random()-0.5)*0.1;}};;
            }})();
            (function(){{
                const _fakeLen=Math.floor(Math.random()*8)+2;
                try{{Object.defineProperty(history,'length',{{get:()=>_fakeLen}});}}catch(e){{}}
            }})();

            // ── 25. Intl consistency ──
            (function() {{
                const _origDTF=Intl.DateTimeFormat;
                Intl.DateTimeFormat=function(loc,opts){{
                    opts=opts||{{}};
                    if(!opts.timeZone)opts.timeZone='{chosen_tz}';
                    return new _origDTF(loc||'{lang_primary}',opts);
                }};;
                Intl.DateTimeFormat.prototype=_origDTF.prototype;
                Intl.DateTimeFormat.supportedLocalesOf=_origDTF.supportedLocalesOf.bind(_origDTF);
            }})();

            // ── 26. RTCPeerConnection — block IP leak ──
            (function() {{
                const _origRTC=window.RTCPeerConnection;
                if(!_origRTC)return;
                window.RTCPeerConnection=function(cfg,...a){{
                    cfg=cfg||{{}};
                    cfg.iceTransportPolicy='relay';
                    return new _origRTC(cfg,...a);
                }};;
                window.RTCPeerConnection.prototype=_origRTC.prototype;
            }})();

            // ── 30. Chrome globals ──
            if(!navigator.scheduling)
                Object.defineProperty(navigator,'scheduling',{{get:()=>({{isInputPending:()=>false}})}});
            if(!navigator.locks)
                Object.defineProperty(navigator,'locks',{{get:()=>({{request:()=>Promise.resolve(),query:()=>Promise.resolve({{held:[],pending:[]}})}})}});

            // ── 33. Font check ──
            (function() {{
                if(!document.fonts)return;
                const _origCheck=document.fonts.check.bind(document.fonts);
                const _knownFonts={_json.dumps(prof['fonts'])};
                document.fonts.check=function(font,text){{
                    const name=font.replace(/^[\\d.]+px\\s+/,'').replace(/['"]/g,'');
                    if(_knownFonts.some(f=>name.includes(f)))return true;
                    return _origCheck(font,text);
                }};;
            }})();

        """)

        # ── CreepJS fingerprint snapshot ──────────────────────────────────────
        import json, time as _time
        step(0, "Visiting CreepJS for fingerprint snapshot...", CYAN, "🔍")

        # intercept creepworker.js and return empty script — kills all worker fingerprinting
        def _block_worker(route):
            url = route.request.url
            rtype = route.request.resource_type
            if "creepworker" in url or rtype in ("script",) and "worker" in url.lower():
                route.fulfill(status=200, content_type="application/javascript", body="self.close && self.close();")
            else:
                route.continue_()
        page.route("**/*", _block_worker)

        # unregister any cached service workers before loading
        try:
            cdp.send("ServiceWorker.enable")
            cdp.send("ServiceWorker.stopAllWorkers")
        except Exception:
            pass

        page.goto("https://abrahamjuliot.github.io/creepjs", timeout=60000)

        # open cryptyos in a new tab simultaneously
        cryptyos_page = context.new_page()
        cryptyos_page.goto("https://cryptyos.nl.eu.org/", timeout=60000, wait_until="domcontentloaded")
        step(0, "Opened cryptyos.nl.eu.org in new tab", GREEN, "🌐")
        biss()

        page.wait_for_timeout(18000)  # let CreepJS fully evaluate
        creep = page.evaluate("""() => {
            const txt = document.body.innerText;
            const m = (re) => { const r = txt.match(re); return r ? r[1] : null; };
            return {
                fp_id:     m(/FP ID:\\s*([a-f0-9]{10,})/),
                headless:  m(/(\\d+)% like headless/),
                stealth:   m(/(\\d+)% stealth/),
                platform:  m(/device:\\s*([^\\n]+)/),
                cores_ram: m(/cores: (\\d+, ram: \\d+)/),
                webrtc_ip: m(/\\nip: ([\\d\\.]+)/),
                raw_summary: txt.slice(0, 6000),
            };
        }""")
        session_id = str(int(_time.time()))

        # organized session dir
        sess_dir = os.path.join(os.path.dirname(__file__), "sessions_fp", session_id)
        os.makedirs(sess_dir, exist_ok=True)

        # save structured creepjs report
        report = {
            "session_id":  session_id,
            "tor_ip":      get_ip(),
            "fingerprint": {
                "fp_id":     creep.get("fp_id"),
                "headless%": creep.get("headless"),
                "stealth%":  creep.get("stealth"),
                "platform":  creep.get("platform"),
                "cores_ram": creep.get("cores_ram"),
                "webrtc_ip": creep.get("webrtc_ip"),
            },
            "raw_summary": creep.get("raw_summary"),
        }
        with open(os.path.join(sess_dir, "creepjs.json"), "w") as _f:
            json.dump(report, _f, indent=2)

        # print summary table
        print(f"\n  {B}{MAGENTA}{'─'*50}{R}")
        print(f"  {B}{CYAN}  SESSION  {R}: {session_id}")
        print(f"  {B}{CYAN}  TOR IP   {R}: {report['tor_ip']}  [{_cc}] {_ip_info.get('country','?')}")
        print(f"  {B}{CYAN}  LOCALE   {R}: {chosen_locale} / {chosen_tz}")
        for k, v in report["fingerprint"].items():
            color = RED if k == "headless%" and v and int(v) > 20 else GREEN
            print(f"  {B}{CYAN}  {k:<10}{R}: {B}{color}{v}{R}")
        print(f"  {B}{MAGENTA}{'─'*50}{R}")
        print(f"  {B}{YELLOW}  Saved → {sess_dir}/creepjs.json{R}\n")

        biss()
        page.unroute("**/*")  # remove worker block before signup flow
        # ─────────────────────────────────────────────────────────────────────

        try:
            step(1, "Navigating to signup page...", CYAN, "⟳")
            page.goto("https://id.atlassian.com/signup/")
            step(1, f"URL: {page.url}", YELLOW)
            dump(page, "dump_1_navigate")
        except Exception as e:
            step(1, f"ERROR navigating: {e}", RED, "✗")
            context.close()
            raise

        try:
            step(2, "Waiting for email field...", CYAN, "⟳")
            step(2, f"Current URL: {page.url}", YELLOW)
            dump(page, "dump_2_before_email_wait")
            page.wait_for_selector('input[data-testid="signup-email-idf-testid"]', timeout=30000)
            step(2, "Email field found.", GREEN, "✓")
            dump(page, "dump_2_email_field")
        except Exception as e:
            step(2, f"ERROR: {e}", RED, "✗")
            context.close()
            raise

        try:
            step(3, "Filling email and submitting...", CYAN, "⟳")
            step(3, f"Email: {user['email']}", YELLOW)
            page.fill('input[data-testid="signup-email-idf-testid"]', user["email"])
            page.wait_for_timeout(500)
            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)
            step(3, f"After submit URL: {page.url}", YELLOW)
            dump(page, "dump_3_after_submit")
            warning = page.query_selector('span[aria-label="warning"]')
            if warning:
                step(3, "Warning icon detected!", RED, "⚠")
                input('yoh')
            else:
                page.wait_for_timeout(random.randint(4000, 8000))
        except Exception as e:
            step(3, f"ERROR: {e}", RED, "✗")
            context.close()
            raise

        # Wait 10s then loop until iframe found
        step(3, "Waiting 10s before iframe scan...", YELLOW, "⟳")
        page.wait_for_timeout(10000)
        dump(page, "dump_3_before_iframe_scan")
        iframe_found = False
        while not iframe_found:
            # dump live frame URLs for debugging
            frame_urls = [f.url for f in page.frames]
            step(3, f"Live frames ({len(frame_urls)}): {frame_urls}", YELLOW)
            frames = page.query_selector_all('iframe')
            step(3, f"Found {len(frames)} iframe(s) in DOM", CYAN)
            for i, fr in enumerate(frames):
                src = fr.get_attribute('src') or ''
                step(3, f"  iframe[{i}] src={src}", YELLOW)
                if 'recaptcha' in src:
                    step(3, f"reCAPTCHA iframe found at index {i}", GREEN, "✓")
                    iframe_found = True
                    break
            if not iframe_found:
                step(3, "No reCAPTCHA iframe yet, retrying in 2s...", YELLOW, "⟳")
                page.wait_for_timeout(2000)

        # Switch into anchor iframe and loop until checkbox found, then click
        step(3, "Switching into reCAPTCHA iframe, looking for checkbox...", CYAN, "⟳")
        page.wait_for_timeout(5000)  # wait for iframe to fully load
        checkbox_clicked = False
        while not checkbox_clicked:
            all_frame_urls = [f.url for f in page.frames]
            step(3, f"All frames: {all_frame_urls}", YELLOW)
            anchor_frame = next((f for f in page.frames if f.url and 'recaptcha' in f.url and 'anchor' in f.url), None)
            if anchor_frame is None:
                # fallback: any recaptcha frame
                anchor_frame = next((f for f in page.frames if f.url and 'recaptcha' in f.url), None)
            step(3, f"anchor_frame={anchor_frame.url if anchor_frame else None}", YELLOW)
            if anchor_frame:
                import json
                anchor_els = anchor_frame.evaluate("""() => Array.from(document.querySelectorAll('*')).map(el => ({
                    tag: el.tagName, id: el.id||null, class: el.className||null
                }))""")
                with open("/tmp/dump_3_anchor_frame.json", "w") as _f:
                    json.dump(anchor_els, _f, indent=2)
                step(3, f"Anchor frame dumped ({len(anchor_els)} els)", MAGENTA, "📄")
                els = anchor_frame.query_selector_all('div.recaptcha-checkbox-border[role="presentation"]')
                step(3, f"  checkbox elements found: {len(els)}", YELLOW)
                if els:
                    els[0].click()
                    step(3, "Checkbox clicked.", GREEN, "✓")
                    checkbox_clicked = True
                    continue
            step(3, "Waiting 3s for frame to load...", YELLOW, "⟳")
            page.wait_for_timeout(3000)
        page.wait_for_timeout(2000)
        dump(page, "dump_3_after_checkbox")
        biss()

        # Click audio challenge button inside bframe
        step(3, "Looking for audio button in bframe...", CYAN, "⟳")
        bframe = next((f for f in page.frames if f.url and 'recaptcha' in f.url and 'bframe' in f.url), None)
        step(3, f"bframe={bframe.url if bframe else None}", YELLOW)
        if bframe:
            audio_btn = bframe.query_selector('#recaptcha-audio-button')
            if audio_btn:
                audio_btn.click()
                step(3, "Audio button clicked.", GREEN, "✓")
            else:
                step(3, "Audio button not found in bframe.", RED, "✗")
        else:
            step(3, "bframe not found.", RED, "✗")
        biss()

        try:
            anchor_frame = page.frame_locator('iframe[src*="recaptcha/api2/anchor"]')
            anchor_frame.locator('#recaptcha-anchor').click()
            page.wait_for_timeout(2000)

            challenge_frame = page.frame_locator('iframe[src*="recaptcha/api2/bframe"]')
            challenge_frame.locator('#recaptcha-audio-button').click()
            page.wait_for_timeout(2000)

            import urllib.request
            audio_src = challenge_frame.locator('.rc-audiochallenge-tdownload-link').get_attribute('href')
            urllib.request.urlretrieve(audio_src, '/tmp/captcha_audio.mp3')
            step(3, "Audio downloaded → /tmp/captcha_audio.mp3", GREEN, "✓")

            challenge_frame.locator('#audio-response').fill('hola')
            challenge_frame.locator('#recaptcha-verify-button').click()
            page.wait_for_timeout(2000)
            step(3, "Captcha submitted.", GREEN, "✓")
        except Exception as e:
            step(3, f"Captcha skipped/failed: {e}", YELLOW, "⚠")

        step(4, "Fetching 2FA code...", CYAN, "⟳")
        code = get_2fa(user["email"])
        if code:
            step(4, f"2FA code: {code}", GREEN, "✓")
        else:
            step(4, "2FA code not found.", RED, "✗")

        try:
            step(5, "Entering OTP...", CYAN, "⟳")
            page.wait_for_selector('[data-testid="otp-input-index-0"]', timeout=15000)
            for i, char in enumerate(code or ""):
                page.click(f'[data-testid="otp-input-index-{i}"]')
                page.keyboard.type(char)
            step(5, "OTP entered.", GREEN, "✓")
        except Exception as e:
            step(5, f"ERROR: {e}", RED, "✗")

        try:
            step(6, "Waiting for display name field...", CYAN, "⟳")
            page.wait_for_selector('[data-testid="displayName"]', timeout=15000)
            full_name = f"{user['first_name']} {user['last_name']}"
            step(6, f"Name: {full_name}", YELLOW)
            page.fill('[data-testid="displayName"]', full_name)
            page.keyboard.press("Tab")
            page.wait_for_timeout(300)
            page.keyboard.type(password)
            for _ in range(4):
                page.wait_for_timeout(400)
                page.keyboard.press("Tab")
            page.wait_for_timeout(400)
            page.keyboard.press("Enter")
            step(6, "Form submitted.", GREEN, "✓")
        except Exception as e:
            step(6, f"ERROR: {e}", RED, "✗")

        try:
            step(7, "Waiting for redirect...", CYAN, "⟳")
            page.wait_for_url("https://home.atlassian.com/?utm_source=identity", timeout=60000)
            step(7, f"Success! URL: {page.url}", GREEN, "✓")
            page.wait_for_selector('span:has-text("Home")', timeout=15000)
            step(7, "Home element appeared.", GREEN, "✓")
            with open("accounts.txt", "a") as f:
                f.write(
                    f"email   : {user['email']}\n"
                    f"name    : {user['first_name']} {user['last_name']}\n"
                    f"username: {user['username']}\n"
                    f"password: {password}\n\n"
                )
            step(7, "Account saved to accounts.txt", GREEN, "✓")

            try:
                step(8, "Opening Codeanywhere + Bitbucket...", CYAN, "⟳")
                ca_page = context.new_page()
                ca_page.goto("https://app.codeanywhere.com/", wait_until="networkidle")
                ca_page.wait_for_timeout(3000)
                step(8, f"URL: {ca_page.url}", YELLOW)
                ca_page.wait_for_selector('#social-bitbucket', timeout=30000)
                ca_page.wait_for_timeout(1000)
                ca_page.click('#social-bitbucket')
                step(8, f"Clicked Bitbucket → {ca_page.url}", GREEN, "✓")
                ca_page.wait_for_selector('button[value="approve"]', timeout=60000)
                ca_page.click('button[value="approve"]')
                step(8, f"Access granted → {ca_page.url}", GREEN, "✓")
            except Exception as e:
                step(8, f"ERROR: {e}", RED, "✗")
            input('done!')

            try:
                step(9, "Waiting for New button...", CYAN, "⟳")
                ca_page.wait_for_selector('.Button_button__dboXH:has-text("New")', timeout=120000)
                ca_page.click('.Button_button__dboXH:has-text("New")')
                step(9, "Clicked New.", GREEN, "✓")
                ca_page.keyboard.press('Tab')
                ca_page.keyboard.press('Enter')

                step(9, "Waiting for repo selector...", CYAN, "⟳")
                ca_page.wait_for_selector('.GitRepositoryDropdown_placeholder-wrapper__XeYoL', timeout=30000)
                ca_page.click('.GitRepositoryDropdown_selected-option-caret-icon__cFRRk')

                try:
                    step(9, "Selecting Codeanywhere-Templates/empty...", CYAN, "⟳")
                    ca_page.wait_for_timeout(2000)
                    clicked = ca_page.evaluate("""() => {
                        const labels = document.querySelectorAll('.GitRepositoryInfo_label__QUpyv');
                        for (const el of labels) {
                            if (el.textContent.trim() === 'Codeanywhere-Templates/empty') {
                                el.scrollIntoView({ block: 'center' });
                                (el.closest('li') || el.closest('[role="option"]') || el.parentElement).click();
                                return true;
                            }
                        }
                        return false;
                    }""")
                    if not clicked:
                        raise Exception("Codeanywhere-Templates/empty not found in DOM")
                    step(9, "Repo selected.", GREEN, "✓")
                except Exception as e:
                    step(9, f"ERROR selecting repo: {e}", RED, "✗")
                    input('fix repo selection then press Enter...')

                with open("dump_after_repo_select.html", "w") as _df:
                    _df.write(ca_page.content())
                step(9, "Page dumped.", YELLOW)

                import json, os
                ca_cookies = [c for c in context.cookies() if 'codeanywhere.com' in c['domain']]
                cookies_file = f"sessions/ca_cookies_{user['first_name'].lower()}_{user['last_name'].lower()}_{user['email'].split('@')[0]}.json"
                with open(cookies_file, "w") as f:
                    json.dump(ca_cookies, f, indent=2)
                step(9, f"Saved {len(ca_cookies)} cookies → {cookies_file}", GREEN, "✓")

                step(9, "Waiting for Continue...", CYAN, "⟳")
                ca_page.wait_for_selector('button[type="submit"]:has-text("Continue")', timeout=30000)
                ca_page.wait_for_function('document.querySelector(\'button[type="submit"]\') && !document.querySelector(\'button[type="submit"]\').disabled', timeout=30000)
                ca_page.click('button[type="submit"]:has-text("Continue")')
                step(9, f"Clicked Continue → {ca_page.url}", GREEN, "✓")
                ca_page.wait_for_timeout(20000)
                step(9, "Checking workspace setup...", CYAN, "⟳")
                while ca_page.query_selector('.WorkspaceLogs_top-level-message__zu6NS'):
                    step(9, "Still setting up, waiting...", YELLOW, "⟳")
                    ca_page.wait_for_timeout(5000)
                step(9, "Workspace ready.", GREEN, "✓")
                input('lol')
                biss()
            except Exception as e:
                step(9, f"ERROR: {e}", RED, "✗")
        except Exception as e:
            step(7, f"ERROR: {e}", RED, "✗")
        context.close()
        browser.close()
