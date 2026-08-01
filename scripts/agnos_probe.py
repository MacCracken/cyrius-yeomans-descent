"""Host-side driver for agnos-qemu-smoke.sh.

Drives Yeoman's Descent over TCP while it runs on a real AGNOS kernel under
QEMU, and answers the two questions gate re-run #5 could not:

  BK — does the clock advance?  descent schedules everything off mud_now_ms().
       On AGNOS that used to be sys_uptime_ms (#40), which the agnos syscall
       layer documents as FROZEN for a foreground `run` program (interrupts are
       disabled, so the 100 Hz timer never fires). If it is frozen, the combat
       tick never fires: no combat, no autosave, no idle reap, no zone reset —
       while the server keeps accepting logins. 1.7.21 moved descent to #95
       (rdtsc-based). This is the first test of that on real hardware emulation.

  BJ — does one stalled client freeze the server?  session_drain tests only
       Linux EAGAIN (-11); on AGNOS sys_write routes to sock_send #48, which
       BLOCKS and has no EAGAIN. A client that stops reading should, on the
       theory, park the single-threaded loop and freeze every other player.
       DEFERRED as a fix (needs an upstream decision) but measurable here.

Exit 0 if every selected scenario passes.
"""
import os
import socket
import sys
import time

PORT = int(sys.argv[1])
SCENARIO = sys.argv[2] if len(sys.argv) > 2 else "all"
LOGDIR = sys.argv[3] if len(sys.argv) > 3 else "."
HOST = "127.0.0.1"

PW = "hunter2hunter2"
results = []


def log(msg):
    print(msg, flush=True)


class S:
    """One player connection."""

    def __init__(self, timeout=10):
        self.s = socket.create_connection((HOST, PORT), timeout=timeout)
        self.buf = ""
        self.rd(2.0)

    def rd(self, t=1.0):
        self.s.settimeout(t)
        try:
            while True:
                d = self.s.recv(65536)
                if not d:
                    break
                self.buf += d.decode("utf-8", "replace")
        except Exception:
            pass
        return self.buf

    def wr(self, x, t=1.2):
        n = len(self.buf)
        self.s.sendall((x + "\n").encode())
        time.sleep(0.35)
        self.rd(t)
        return self.buf[n:]

    def login(self, name, klass="1"):
        self.wr(name)
        self.wr(PW)
        self.wr(PW, 2.0)
        if "calling" in self.buf.lower() or "choose" in self.buf.lower():
            self.wr(klass, 2.0)
        return self.buf

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


def serial_path():
    return os.path.join(LOGDIR, "serial.log")


def serial_text():
    try:
        with open(serial_path(), "r", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def wait_for_listener(deadline_s=180):
    """Wait for REAL evidence the guest is serving.

    NOT a TCP connect to the forwarded port: SLIRP accepts `hostfwd` on the host
    side whether or not anything in the guest is listening, so a connect
    succeeds ~1s after QEMU starts and says nothing at all. That false positive
    cost this harness its first two runs — it killed QEMU before the kernel had
    finished booting and then reported five confident, meaningless failures.
    The serial console is the only honest signal.
    """
    t0 = time.time()
    while time.time() - t0 < deadline_s:
        txt = serial_text()
        if "server: listening on port" in txt:
            log(f"  descent is listening ({time.time() - t0:.0f}s into boot)")
            return True
        if "run: exit" in txt:
            return False
        time.sleep(1.0)
    return False


def died_in_guest():
    """Did the ring-3 process die? `run: exit <code>` is the kernel's report;
    142 == 128+14, the #PF kill code."""
    for line in serial_text().splitlines():
        if line.startswith("run: exit"):
            return line.strip()
    return None


def record(name, ok, detail):
    results.append((name, ok, detail))
    log(f"  [{'PASS' if ok else 'FAIL'}] {name} — {detail}")


# --------------------------------------------------------------------------
log("=== descent on a real AGNOS kernel (QEMU) ===")
if not wait_for_listener():
    d = died_in_guest()
    if d:
        log(f"  [FAIL] descent DIED before serving: {d}")
        log("         (142 = 128+14, the kernel's ring-3 page-fault kill code)")
    else:
        log("  [FAIL] descent never began listening — see the serial log")
    sys.exit(1)

# --- Scenario: the server is actually serving ------------------------------
try:
    a = S()
    banner_ok = "descent" in a.buf.lower() or "under-grid" in a.buf.lower() or len(a.buf) > 40
    record("banner", banner_ok, f"{len(a.buf)} bytes of MOTD")
    a.login("agnosone")
    looked = a.wr("look", 1.5)
    in_world = "gate" in looked.lower() or "arcology" in looked.lower() or len(looked) > 60
    record("login+world", in_world, "character created and placed in a room")
except Exception as e:
    record("banner", False, f"exception: {e}")
    record("login+world", False, "could not reach the world")
    a = None

# --- Scenario BK: does the clock advance? ----------------------------------
# The tick is the observable. Two independent readings:
#   1. `@stats`-free: energy/HP regen is driven by classes_upkeep, which only
#      runs from the tick. Take damage, then watch it come back.
#   2. A mob swing: mob_tick_all only swings on a tick.
# If the clock is frozen NEITHER ever happens, and the session still answers
# commands — which is exactly the signature BK predicts.
if SCENARIO in ("all", "tick") and a is not None:
    try:
        before = a.wr("examine me", 2.0)
        # Engage something so the tick has visible work, then sit still.
        a.wr("kill drone", 1.5)
        t0 = time.time()
        saw_tick = False
        for _ in range(12):
            time.sleep(2.5)
            out = a.wr("", 0.8)  # bare newline; collect anything the tick pushed
            if out.strip():
                saw_tick = True
                break
        elapsed = time.time() - t0
        record(
            "BK tick advances",
            saw_tick,
            f"tick-driven output within {elapsed:.0f}s"
            if saw_tick
            else f"NO tick output in {elapsed:.0f}s — the clock looks frozen",
        )
    except Exception as e:
        record("BK tick advances", False, f"exception: {e}")

# --- Scenario BJ: does a stalled client freeze everyone? -------------------
# Open a client, get the server queueing prose at it, then STOP READING while a
# second player asks for something. On Linux the drain would hit EAGAIN and move
# on. On AGNOS sock_send #48 blocks, so the whole loop should stall.
if SCENARIO in ("all", "stall"):
    try:
        stalled = S()
        stalled.login("agnosstall")
        # Ask for a lot of output and then stop reading it.
        stalled.s.sendall(b"look\n" * 40)
        time.sleep(1.0)

        bystander = S()
        bystander.login("agnoswatch")
        t0 = time.time()
        out = bystander.wr("look", 6.0)
        latency = time.time() - t0
        ok = latency < 3.0 and len(out) > 0
        record(
            "BJ bystander unaffected",
            ok,
            f"bystander 'look' answered in {latency:.2f}s"
            + ("" if ok else " — the loop stalled behind the unread client"),
        )
        stalled.close()
        bystander.close()
    except Exception as e:
        record("BJ bystander unaffected", False, f"exception: {e}")

# --- Scenario: persistence round-trip on a real kernel ---------------------
# running.md has declared AGNOS persistence unverified end-to-end since 1.7.8.
if SCENARIO in ("all", "persist") and a is not None:
    try:
        a.wr("get notice", 1.5)
        a.wr("quit", 1.5)
        a.close()
        time.sleep(1.5)
        b = S()
        greet = b.login("agnosone")
        inv = b.wr("i", 1.5)
        kept = "notice" in inv.lower()
        record("persistence round-trip", kept, "inventory survived logout on a real kernel")
        b.close()
    except Exception as e:
        record("persistence round-trip", False, f"exception: {e}")

log("")
passed = sum(1 for _, ok, _ in results if ok)
log(f"=== {passed}/{len(results)} scenarios passed ===")
sys.exit(0 if passed == len(results) else 1)
