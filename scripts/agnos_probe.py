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
import re
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

    def __init__(self, timeout=10, rcvbuf=None):
        if rcvbuf is None:
            self.s = socket.create_connection((HOST, PORT), timeout=timeout)
        else:
            # SO_RCVBUF only shrinks the advertised window if it is set BEFORE
            # connect(), so this path cannot use create_connection.
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, rcvbuf)
            self.s.settimeout(timeout)
            self.s.connect((HOST, PORT))
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
    # Every room render carries an "Exits:" line (session_show_room). The old
    # check also passed on ANY reply over 60 bytes, which a passphrase or class
    # prompt satisfies just as well as a room.
    in_world = "exits:" in looked.lower()
    record("login+world", in_world,
           "character created and placed in a room" if in_world
           else f"no room render after login: {looked.strip()[:80]!r}")
except Exception as e:
    record("banner", False, f"exception: {e}")
    record("login+world", False, "could not reach the world")
    a = None

# --- Scenario BK: does the clock advance? ----------------------------------
# The observable is energy regeneration. classes_upkeep is the only thing that
# refills energy, and only the tick runs it (ENERGY_REGEN a tick). So: spend
# some with `brace` (Pikeman, 5 energy), then poll `examine me` with no other
# command in between. Any rise proves a tick ran. If the clock is frozen it never
# rises while the session still answers commands, which is exactly the
# signature BK predicts.
#
# Do not go back to a mob fight or to "any unsolicited output". The start room
# holds no mob (mobs wander), and a bare newline gets no reply even on Linux, so
# that version reported a frozen clock on a healthy server (2026-11-02).
def energy_of(txt):
    m = re.search(r"Energy\s+(\d+)/\d+", txt)
    return int(m.group(1)) if m else None


if SCENARIO in ("all", "tick") and a is not None:
    try:
        a.wr("brace", 1.2)
        spent = energy_of(a.wr("examine me", 1.2))
        t0 = time.time()
        now = spent
        while spent is not None and time.time() - t0 < 15.0:
            time.sleep(2.5)
            now = energy_of(a.wr("examine me", 1.2))
            if now is not None and now > spent:
                break
        elapsed = time.time() - t0
        ticked = spent is not None and now is not None and now > spent
        if spent is None:
            detail = "could not read Energy from 'examine me'"
        elif ticked:
            detail = f"energy {spent} -> {now} within {elapsed:.1f}s"
        else:
            detail = f"energy stuck at {spent} for {elapsed:.0f}s — the clock looks frozen"
        record("BK tick advances", ticked, detail)
    except Exception as e:
        record("BK tick advances", False, f"exception: {e}")

# --- Scenario BJ: does a stalled client freeze everyone? -------------------
# Open a client, get the server queueing prose at it, then STOP READING while a
# second player asks for something. On Linux the drain would hit EAGAIN and move
# on. On AGNOS sock_send #48 blocks, so the whole loop should stall.
#
# The latency is TIME TO FIRST BYTE. The old version timed `wr("look", 6.0)`,
# which always waits out its 6 s read timeout, so its `< 3.0` could never pass.
#
# ⚠ A pass is weaker than a fail. QEMU's SLIRP buffers on the host side, so
# the guest's send window only fills once SLIRP's buffer is full too. The
# stalled client shrinks its receive window and asks for ~2,000 room renders
# (over 1 MB) to push past that, but nothing here can prove the guest's window
# actually filled.
STALL_LOOKS = 2000

if SCENARIO in ("all", "stall"):
    try:
        bystander = S()
        bystander.login("agnoswatch")
        bystander.rd(1.0)

        stalled = S(rcvbuf=4096)
        stalled.login("agnosstall")
        # Ask for a lot of output and then stop reading it.
        stalled.s.sendall(b"look\n" * STALL_LOOKS)
        time.sleep(3.0)

        bystander.s.settimeout(30.0)
        t0 = time.time()
        bystander.s.sendall(b"look\n")
        try:
            first = bystander.s.recv(65536)
        except socket.timeout:
            first = b""
        latency = time.time() - t0
        ok = latency < 3.0 and len(first) > 0
        record(
            "BJ bystander unaffected",
            ok,
            (f"bystander's first byte after {latency:.3f}s"
             + (" (SLIRP buffering: a pass does not prove the window filled)" if ok
                else " — the loop stalled behind the unread client"))
            if first else "bystander got NOTHING in 30s — the loop is stalled",
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
        # On FAIL, look in the guest's /data/players for a stranded <name>.cyml.tmp:
        # agnos's ext2 rename cannot replace an existing file (roadmap item BV).
        record("persistence round-trip", kept,
               "inventory survived logout on a real kernel" if kept
               else "inventory LOST across logout — the save did not publish (see roadmap BV)")
        b.close()
    except Exception as e:
        record("persistence round-trip", False, f"exception: {e}")

log("")
passed = sum(1 for _, ok, _ in results if ok)
log(f"=== {passed}/{len(results)} scenarios passed ===")
sys.exit(0 if passed == len(results) else 1)
