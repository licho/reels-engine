"""Schedules a finished video on YouTube and/or a Facebook Page at a given date and time. The network keeps the
video and publishes it on its own at that time, so nothing has to stay running.

Usage (from the channel root):
  python3 -m channel.publish VIDEO.mp4 "2026-10-25 19:00" --title "..." [--description "..."] [--to youtube,facebook]
  python3 -m channel.publish setup youtube CLIENT_ID CLIENT_SECRET        -> connect a YouTube channel (once)
  python3 -m channel.publish setup facebook APP_ID APP_SECRET USER_TOKEN  -> connect a Facebook Page (once)
  python3 -m channel.publish status                                       -> which networks are connected

The time is read in `Channel.timezone` (or the machine's zone when empty); `--tz` overrides it. Without `--to` the
video goes to every connected network. Credentials are looked up, in order, in the environment variables
REELS_<CHANNEL>_<NETWORK> and REELS_<NETWORK> (the JSON that `setup` prints) and in the file
~/.config/reels-engine/<channel>/<network>.json (folder overridable with REELS_SECRETS_DIR).
Step-by-step guide to get the ids and tokens: "Scheduling videos" in the README."""
import argparse, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from .config import current as _current

_cfg = _current()
NETWORKS = ("youtube", "facebook")
FB_API = "https://graph.facebook.com/v26.0"
FB_UPLOAD = "https://rupload.facebook.com/video-upload/v26.0"
FB_MAX_S = 90                     # Facebook reels: 3 to 90 seconds
YT_SCOPE = "https://www.googleapis.com/auth/youtube"   # the only YouTube write scope the device flow accepts

class PublishError(Exception):
    pass

# ---------- HTTP (stdlib only) ----------

def _http(method, url, data=None, headers=None, form=None, raw=False):
    """Sends a request and returns (json_or_bytes, response_headers). Raises PublishError with the API message."""
    headers = dict(headers or {})
    if form is not None:
        data = urllib.parse.urlencode(form).encode(); headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    elif isinstance(data, (dict, list)):
        data = json.dumps(data).encode(); headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            body = r.read(); hdrs = r.headers
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err = json.loads(body).get("error")
            body = err.get("message", body) if isinstance(err, dict) else f"{err} ({json.loads(body).get('error_description', '')})"
        except (ValueError, AttributeError): pass
        raise PublishError(f"{method} {url.split('?')[0]} -> HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        raise PublishError(f"{method} {url.split('?')[0]} -> can't connect ({e.reason}). Is the host allowed by the network?")
    if raw or not body: return body, hdrs
    return json.loads(body), hdrs

# ---------- credentials ----------

def _env_key(net, channel=True):
    return "REELS_" + (re.sub(r"[^A-Za-z0-9]+", "_", _cfg.name).upper() + "_" if channel else "") + net.upper()

def _secrets_file(net):
    base = os.environ.get("REELS_SECRETS_DIR") or os.path.join(os.path.expanduser("~"), ".config", "reels-engine")
    return os.path.join(base, _cfg.name, f"{net}.json")

def load_creds(net):
    """Credentials of a network, or None when it isn't connected."""
    for k in (_env_key(net), _env_key(net, channel=False)):
        if os.environ.get(k): return json.loads(os.environ[k])
    f = _secrets_file(net)
    return json.load(open(f)) if os.path.exists(f) else None

def save_creds(net, creds):
    f = _secrets_file(net); os.makedirs(os.path.dirname(f), exist_ok=True)
    fd = os.open(f, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh: json.dump(creds, fh)
    return f

# ---------- time ----------

def parse_when(text, tz=None):
    """'2026-10-25 19:00' in the channel's time zone -> aware datetime (UTC)."""
    try: dt = datetime.strptime(text.strip().replace("T", " "), "%Y-%m-%d %H:%M")
    except ValueError: raise PublishError(f"Can't read the date '{text}'. Use YYYY-MM-DD HH:MM, e.g. 2026-10-25 19:00")
    tz = tz or _cfg.timezone
    if tz:
        from zoneinfo import ZoneInfo
        dt = dt.replace(tzinfo=ZoneInfo(tz))
    else:
        dt = dt.astimezone()                     # machine's zone
    return dt.astimezone(timezone.utc)

def _duration(path):
    import subprocess
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                             capture_output=True, text=True, check=True).stdout
        return float(out.strip())
    except Exception:
        return None

# ---------- YouTube ----------

def youtube_setup(client_id, client_secret):
    """Device flow: shows a code to enter at google.com/device, then stores the refresh token."""
    r, _ = _http("POST", "https://oauth2.googleapis.com/device/code", form={"client_id": client_id, "scope": YT_SCOPE})
    print(f"\n  1. Open {r['verification_url']} (phone or computer)\n  2. Enter the code: {r['user_code']}\n"
          f"  3. Choose the channel's Google account and allow access.\n\nWaiting…", flush=True)
    wait, deadline = r.get("interval", 5), time.time() + r.get("expires_in", 1800)
    while time.time() < deadline:
        time.sleep(wait)
        try:
            tok, _ = _http("POST", "https://oauth2.googleapis.com/token", form={
                "client_id": client_id, "client_secret": client_secret, "device_code": r["device_code"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code"})
        except PublishError as e:
            if "authorization_pending" in str(e): continue
            if "slow_down" in str(e): wait += 5; continue
            raise
        creds = {"client_id": client_id, "client_secret": client_secret, "refresh_token": tok["refresh_token"]}
        me, _ = _http("GET", "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
                      headers={"Authorization": f"Bearer {tok['access_token']}"})
        items = me.get("items") or []
        creds["channel"] = items[0]["snippet"]["title"] if items else ""
        return creds
    raise PublishError("The code expired before access was allowed. Run setup again.")

def _yt_token(creds):
    tok, _ = _http("POST", "https://oauth2.googleapis.com/token", form={
        "client_id": creds["client_id"], "client_secret": creds["client_secret"],
        "refresh_token": creds["refresh_token"], "grant_type": "refresh_token"})
    return tok["access_token"]

def youtube_schedule(creds, video, when, title, description="", tags=(), made_for_kids=False):
    """Uploads the video as private with publishAt: YouTube makes it public at that time. Returns the video URL."""
    token = _yt_token(creds)
    meta = {"snippet": {"title": title[:100], "description": description[:5000], "tags": list(tags), "categoryId": "22"},
            "status": {"privacyStatus": "private", "publishAt": when.strftime("%Y-%m-%dT%H:%M:%SZ"),
                       "selfDeclaredMadeForKids": made_for_kids}}
    size = os.path.getsize(video)
    _, h = _http("POST", "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", data=meta,
                 headers={"Authorization": f"Bearer {token}", "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)})
    with open(video, "rb") as fh:
        r, _ = _http("PUT", h["Location"], data=fh.read(), headers={"Content-Type": "video/mp4", "Content-Length": str(size)})
    return f"https://youtu.be/{r['id']}"

# ---------- Facebook ----------

def facebook_setup(app_id, app_secret, user_token, page=None):
    """Turns a short user token into a Page token that doesn't expire. With several Pages, `page` picks one (name or id)."""
    tok, _ = _http("GET", f"{FB_API}/oauth/access_token?" + urllib.parse.urlencode({
        "grant_type": "fb_exchange_token", "client_id": app_id, "client_secret": app_secret, "fb_exchange_token": user_token}))
    pages, _ = _http("GET", f"{FB_API}/me/accounts?" + urllib.parse.urlencode({"access_token": tok["access_token"], "fields": "id,name,access_token"}))
    pages = pages.get("data", [])
    if page: pages = [p for p in pages if page in (p["id"], p["name"])]
    if len(pages) != 1:
        names = ", ".join(f"{p['name']} ({p['id']})" for p in pages) or "none"
        raise PublishError(f"Expected one Page and found: {names}. Pass the Page's name or id as the last argument.")
    p = pages[0]
    return {"page_id": p["id"], "page": p["name"], "page_token": p["access_token"]}

def facebook_schedule(creds, video, when, description=""):
    """Uploads a reel to the Page in SCHEDULED state. Returns the reel URL."""
    pid, token = creds["page_id"], creds["page_token"]
    r, _ = _http("POST", f"{FB_API}/{pid}/video_reels", data={"upload_phase": "start", "access_token": token})
    vid = r["video_id"]
    with open(video, "rb") as fh: data = fh.read()
    _http("POST", f"{FB_UPLOAD}/{vid}", data=data, headers={
        "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(data)), "Content-Type": "application/octet-stream"})
    _http("POST", f"{FB_API}/{pid}/video_reels", data={
        "access_token": token, "video_id": vid, "upload_phase": "finish", "video_state": "SCHEDULED",
        "scheduled_publish_time": int(when.timestamp()), "description": description})
    return f"https://www.facebook.com/reel/{vid}"

# ---------- command ----------

def schedule(video, when, title, description="", to=None, tz=None):
    """Schedules `video` on each network in `to` (default: every connected one). Returns {network: url or error}."""
    if not os.path.exists(video): raise PublishError(f"The video doesn't exist: {video}")
    at = parse_when(when, tz) if isinstance(when, str) else when.astimezone(timezone.utc)
    nets = list(to) if to else [n for n in NETWORKS if load_creds(n)]
    if not nets: raise PublishError("No network is connected. Run: python3 -m channel.publish setup youtube|facebook …")
    mins = (at - datetime.now(timezone.utc)).total_seconds() / 60
    if mins < 15: raise PublishError("The date must be at least 15 minutes from now.")
    problems = []                                # checked before uploading anything, so nothing is half scheduled
    for n in nets:
        if n not in NETWORKS: problems.append(f"unknown network '{n}' (use {', '.join(NETWORKS)})"); continue
        if not load_creds(n): problems.append(f"{n} isn't connected (python3 -m channel.publish setup {n} …)")
        if n == "facebook":
            dur = _duration(video)
            if mins > 29 * 24 * 60: problems.append("Facebook only schedules up to 29 days ahead")
            if dur and dur > FB_MAX_S: problems.append(f"Facebook reels last at most {FB_MAX_S} s and this video lasts {dur:.0f} s (use --to youtube)")
    if problems: raise PublishError("; ".join(problems) + ". Nothing was uploaded.")
    out = {}
    for n in nets:
        try:
            if n == "youtube":
                out[n] = youtube_schedule(load_creds(n), video, at, title, description)
            else:
                text = (title + "\n\n" + description).strip() if description else title
                out[n] = facebook_schedule(load_creds(n), video, at, text)
        except PublishError as e:
            out[n] = e
    return out

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["status"]:
        for n in NETWORKS:
            c = load_creds(n)
            print(f"{n}: " + (f"connected ({c.get('channel') or c.get('page') or 'ok'})" if c else "not connected"))
        return 0
    if argv[:1] == ["setup"]:
        if len(argv) < 2 or argv[1] not in NETWORKS:
            print(__doc__); return 2
        try:
            if argv[1] == "youtube" and len(argv) == 4: creds = youtube_setup(argv[2], argv[3])
            elif argv[1] == "facebook" and len(argv) in (5, 6): creds = facebook_setup(*argv[2:6])
            else: print(__doc__); return 2
        except PublishError as e:
            print("Error:", e); return 1
        f = save_creds(argv[1], creds)
        print(f"\n✔ {argv[1]} connected: {creds.get('channel') or creds.get('page')}\n  Saved in {f}")
        print(f"  To use it in another machine or a cloud session, store this value in the secret {_env_key(argv[1])}:\n"
              f"  {json.dumps(creds)}")
        return 0
    ap = argparse.ArgumentParser(prog="python3 -m channel.publish", description="Schedules a video on YouTube and/or Facebook.")
    ap.add_argument("video"); ap.add_argument("when", help='"YYYY-MM-DD HH:MM" in the channel time zone')
    ap.add_argument("--title", required=True); ap.add_argument("--description", default="")
    ap.add_argument("--to", help="youtube,facebook (default: every connected network)")
    ap.add_argument("--tz", help="time zone, e.g. America/Lima (default: Channel.timezone or the machine's)")
    a = ap.parse_args(argv)
    try:
        res = schedule(a.video, a.when, a.title, a.description, a.to.split(",") if a.to else None, a.tz)
    except PublishError as e:
        print("Error:", e); return 1
    at = parse_when(a.when, a.tz)
    print(f"Scheduled for {a.when} ({a.tz or _cfg.timezone or 'local time'}) = {at:%Y-%m-%d %H:%M} UTC")
    for n, r in res.items():
        print(f"  {n}: " + (f"✘ {r}" if isinstance(r, Exception) else f"✔ {r}"))
    return 0 if not any(isinstance(r, Exception) for r in res.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
