"""Drive headless Chrome over the DevTools protocol with the Python standard library only.

Used by export_ai.py to lay a page out once and get two things from that same layout:
the PDF (vector artwork and text positions) and the page's own structure (which letters
belong to which text block, alignment, and the data-ai-* tags).
"""
import base64, json, os, shutil, socket, struct, subprocess, tempfile, time, urllib.request


def find_chrome():
    env = os.environ.get("CHROME")
    for c in [env, "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
              "/Applications/Chromium.app/Contents/MacOS/Chromium"]:
        if c and os.access(c, os.X_OK):
            return c
    raise SystemExit("Google Chrome not found - install it, or set CHROME=/path/to/chrome.")


class _WebSocket:
    """Just enough of RFC 6455 for one DevTools connection (text frames, no extensions)."""

    def __init__(self, url):
        hostport, path = url[len("ws://"):].split("/", 1)
        host, port = hostport.rsplit(":", 1)
        self.sock = socket.create_connection((host, int(port)), timeout=120)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\n"
                           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
                           f"Sec-WebSocket-Version: 13\r\n\r\n").encode())
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("Chrome closed the DevTools connection during the handshake")
            data += chunk
        head, rest = data.split(b"\r\n\r\n", 1)
        if b" 101 " not in head.split(b"\r\n")[0]:
            raise ConnectionError("DevTools handshake refused: " + head[:120].decode(errors="replace"))
        self.buf = bytearray(rest)

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(1 << 20)
            if not chunk:
                raise ConnectionError("Chrome closed the DevTools connection")
            self.buf += chunk
        out = bytes(self.buf[:n])
        del self.buf[:n]
        return out

    def _frame(self, opcode, data):
        head = bytearray([0x80 | opcode])
        n = len(data)
        if n < 126:
            head.append(0x80 | n)
        elif n < 65536:
            head.append(0x80 | 126)
            head += struct.pack(">H", n)
        else:
            head.append(0x80 | 127)
            head += struct.pack(">Q", n)
        mask = os.urandom(4)
        head += mask
        self.sock.sendall(bytes(head) + bytes(b ^ mask[i & 3] for i, b in enumerate(data)))

    def send(self, text):
        self._frame(0x1, text.encode())

    def recv(self):
        msg = bytearray()
        while True:
            b1, b2 = self._read(2)
            opcode, n = b1 & 0x0F, b2 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read(8))[0]
            mask = self._read(4) if b2 & 0x80 else None
            payload = self._read(n)
            if mask:
                payload = bytes(b ^ mask[i & 3] for i, b in enumerate(payload))
            if opcode == 0x8:
                raise ConnectionError("Chrome closed the DevTools connection")
            if opcode == 0x9:
                self._frame(0xA, payload)
                continue
            msg += payload
            if b1 & 0x80:
                return msg.decode()


class Chrome:
    """One headless Chrome with one page. Use as a context manager."""

    def __enter__(self):
        self.profile = tempfile.mkdtemp(prefix="export_ai_chrome_")
        self.proc = subprocess.Popen(
            [find_chrome(), "--headless=new", "--remote-debugging-port=0", f"--user-data-dir={self.profile}",
             "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--hide-scrollbars",
             "--allow-file-access-from-files", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        port_file = os.path.join(self.profile, "DevToolsActivePort")
        deadline = time.time() + 30
        while not (os.path.exists(port_file) and open(port_file).read().strip()):
            if time.time() > deadline or self.proc.poll() is not None:
                raise SystemExit("Chrome did not start (no DevTools port after 30 s).")
            time.sleep(0.1)
        port = int(open(port_file).read().split()[0])
        targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list"))
        self.ws = _WebSocket(next(t for t in targets if t["type"] == "page")["webSocketDebuggerUrl"])
        self.next_id, self.events = 0, []
        return self

    def __exit__(self, *exc):
        try:
            self.proc.terminate()
            self.proc.wait(10)
        except Exception:
            self.proc.kill()
        shutil.rmtree(self.profile, ignore_errors=True)

    def call(self, method, **params):
        self.next_id += 1
        mid = self.next_id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == mid:
                if "error" in m:
                    raise RuntimeError(f"Chrome {method}: {m['error'].get('message')}")
                return m.get("result", {})
            self.events.append(m)

    def wait_event(self, name):
        while True:
            for i, m in enumerate(self.events):
                if m.get("method") == name:
                    return self.events.pop(i)
            self.events.append(json.loads(self.ws.recv()))

    def load(self, url):
        self.call("Page.enable")
        self.call("Page.navigate", url=url)
        self.wait_event("Page.loadEventFired")
        # Web fonts and images must be in before anything is measured or printed.
        self.evaluate("Promise.all([document.fonts.ready,"
                      " ...Array.from(document.images).map(i => i.decode().catch(() => null))]).then(() => true)")

    def evaluate(self, expression):
        r = self.call("Runtime.evaluate", expression=expression, awaitPromise=True, returnByValue=True)
        if "exceptionDetails" in r:
            d = r["exceptionDetails"]
            raise RuntimeError("Page script failed: " + (d.get("exception", {}).get("description") or d.get("text", "")))
        return r["result"].get("value")

    def pdf(self, **options):
        return base64.b64decode(self.call("Page.printToPDF", transferMode="ReturnAsBase64", **options)["data"])
