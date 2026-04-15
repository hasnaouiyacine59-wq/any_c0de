from flask import Flask, jsonify
import socket, requests, os, time, threading, random, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = Flask(__name__)

SOCKS_PORT   = int(os.environ.get("SOCKS_PORT",   9050))
CONTROL_PORT = int(os.environ.get("CONTROL_PORT", 9051))
API_PORT     = int(os.environ.get("API_PORT",     5000))

def tor_cmd(cmd: bytes) -> tuple:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(("127.0.0.1", CONTROL_PORT))
            s.sendall(b'AUTHENTICATE ""\r\n')
            s.recv(1024)
            s.sendall(cmd)
            resp = s.recv(4096).decode()
            return "250" in resp, resp.strip()
    except Exception as e:
        return False, str(e)

def _new_circuit():
    tor_cmd(b"SIGNAL NEWNYM\r\n")

def _auto_rotate():
    """Rotate circuit every 90-150s to avoid long-lived circuit fingerprinting."""
    while True:
        time.sleep(random.uniform(90, 150))
        _new_circuit()

# start background rotation thread
threading.Thread(target=_auto_rotate, daemon=True).start()

IP_SERVICES = [
    "https://api.ipify.org",
    "https://icanhazip.com",
    "https://ifconfig.me/ip",
    "https://ipecho.net/plain",
    "https://checkip.amazonaws.com",
]

def _wait_for_circuit(timeout=10):
    """Poll bootstrap status instead of fixed sleep."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        ok, detail = tor_cmd(b"GETINFO status/bootstrap-phase\r\n")
        if ok and "PROGRESS=100" in detail:
            return True
        time.sleep(0.5)
    return False

def _get_ip_via_tor():
    proxies = {
        "http":  f"socks5h://127.0.0.1:{SOCKS_PORT}",
        "https": f"socks5h://127.0.0.1:{SOCKS_PORT}",
    }
    # try all services in parallel, return first success
    from concurrent.futures import ThreadPoolExecutor, as_completed
    def fetch(url):
        return requests.get(url, proxies=proxies, timeout=30).text.strip()
    with ThreadPoolExecutor(max_workers=len(IP_SERVICES)) as ex:
        futures = {ex.submit(fetch, url): url for url in IP_SERVICES}
        for f in as_completed(futures):
            try:
                return f.result()
            except Exception as e:
                logging.warning("IP service %s failed: %s", futures[f], e)
    raise RuntimeError("all IP services failed")

@app.route("/reset-ip")
def reset_ip():
    _new_circuit()
    return jsonify({"status": "ok"})

@app.route("/ip")
def get_ip():
    try:
        return jsonify({"ip": _get_ip_via_tor()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ip/<country>")
def get_ip_from_country(country):
    try:
        node = "{" + country.lower() + "}"
        ok, resp = tor_cmd(f"SETCONF ExitNodes={node} StrictNodes=1\r\n".encode())
        if not ok:
            return jsonify({"error": "failed to set exit country", "detail": resp}), 500
        # retry up to 3 circuits
        for attempt in range(3):
            _new_circuit()
            _wait_for_circuit()
            try:
                ip = _get_ip_via_tor()
                return jsonify({"ip": ip, "country": country.lower()})
            except Exception:
                if attempt == 2:
                    raise
        return jsonify({"error": "no exit node found"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear-country")
def clear_country():
    ok, resp = tor_cmd(b"SETCONF ExitNodes= StrictNodes=0\r\n")
    return jsonify({"status": "ok" if ok else "error", "detail": resp})

@app.route("/status")
def status():
    ok, detail = tor_cmd(b"GETINFO status/bootstrap-phase\r\n")
    ready = "PROGRESS=100" in detail
    return jsonify({"bootstrapped": ready, "detail": detail})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=API_PORT)
