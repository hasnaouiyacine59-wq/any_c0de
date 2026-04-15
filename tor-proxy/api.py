from flask import Flask, jsonify
import socket, requests, os, time, threading, random

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
    # random jitter before rotating to break timing correlation
    time.sleep(random.uniform(0.5, 3.0))
    tor_cmd(b"SIGNAL NEWNYM\r\n")

def _auto_rotate():
    """Rotate circuit every 90-150s to avoid long-lived circuit fingerprinting."""
    while True:
        time.sleep(random.uniform(90, 150))
        _new_circuit()

# start background rotation thread
threading.Thread(target=_auto_rotate, daemon=True).start()

def _get_ip_via_tor():
    proxies = {
        "http":  f"socks5h://127.0.0.1:{SOCKS_PORT}",
        "https": f"socks5h://127.0.0.1:{SOCKS_PORT}",
    }
    time.sleep(random.uniform(0.1, 0.8))
    return requests.get("https://api.ipify.org", proxies=proxies, timeout=15).text

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
        _new_circuit()
        time.sleep(3)  # wait for new circuit
        ip = _get_ip_via_tor()
        return jsonify({"ip": ip, "country": country.lower()})
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
