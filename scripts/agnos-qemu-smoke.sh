#!/bin/bash
# agnos-qemu-smoke.sh — run Yeoman's Descent on a REAL AGNOS kernel under QEMU
# and drive it over TCP from the host.
#
# WHY THIS EXISTS. descent has shipped a `--agnos` target since 1.1.0 — a second
# copy of the event loop (ADR 0003) — and until 1.7.21 **no sweep had ever
# executed it.** Gate re-run #5 pointed the first instrument at that target and
# three highs fell out of the first hour (items BI, BJ, BK). All three were found
# by reading two arms of a preprocessor or by running under an agnos->Linux
# syscall translator, which by its own ADR validates agnos *userland* and does
# NOT exercise the kernel's scheduler, net stack or preempt/IF semantics — which
# is exactly where the remaining unknowns live.
#
# `docs/guides/running.md` used to point at a container harness in the agnosticos
# repo. That harness was RETIRED 2026-07-07: its architecture was
# QEMU-inside-Docker, which that project killed deliberately ("the dead
# VM-in-a-container pattern"). Kernel / net validation there lives on
# **QEMU-direct**, and this script is descent's QEMU-direct harness. It is
# modelled on agnos's own `scripts/smoke/{tcp-listen,ark-run,bench-connect}-smoke.sh`.
#
# WHAT IT DOES NOT NEED. No change to the agnos kernel source. The kernel's
# BENCH_CONNECT_SELFTEST hook reads a command from `/etc/probe-cmd` on the ext2
# root and runs it through `sh_exec` — it is a general "run this at boot" hook,
# so descent is launched by staging a file rather than by adding a hook of its
# own. That is deliberate: descent should not need a patch in someone else's
# kernel to be testable.
#
# REQUIREMENTS
#   qemu-system-x86_64, OVMF, parted, sgdisk, mtools (mformat/mmd/mcopy),
#   mkfs.ext2, python3, and:
#     - a built gnoboot   (GNOBOOT_ROOT, default ../gnoboot)
#     - an agnos checkout (AGNOS_ROOT,  default ../agnos)
#
# The agnos kernel MUST be built with the run hook:
#     BENCH_CONNECT_SELFTEST=1 sh scripts/build.sh
# Point AGNOS_KERNEL at one built that way, or let this script use
# $AGNOS_ROOT/build/agnos and it will check.
#
# USAGE
#   scripts/agnos-qemu-smoke.sh              # boot + play + assert
#   KEEP=1 scripts/agnos-qemu-smoke.sh       # keep the work dir for poking at
#   SCENARIO=tick scripts/agnos-qemu-smoke.sh   # only the BK tick probe
#
# Exit 0 if every selected scenario passes, 1 otherwise. Logs under
# build/agnos-qemu-logs/.

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGNOS_ROOT="${AGNOS_ROOT:-$ROOT/../agnos}"
GNOBOOT_ROOT="${GNOBOOT_ROOT:-$ROOT/../gnoboot}"
AGNOS_KERNEL="${AGNOS_KERNEL:-$AGNOS_ROOT/build/agnos}"
GNOBOOT="${GNOBOOT:-$GNOBOOT_ROOT/build/BOOTX64.EFI}"
HOST_PORT="${HOST_PORT:-14400}"
GUEST_PORT="${GUEST_PORT:-4000}"
QEMU_TIMEOUT="${QEMU_TIMEOUT:-120}"
SCENARIO="${SCENARIO:-all}"

for tool in qemu-system-x86_64 parted sgdisk mformat mmd mcopy mkfs.ext2 dd python3 strings; do
    command -v "$tool" >/dev/null 2>&1 || { echo "ERROR: '$tool' not on PATH" >&2; exit 1; }
done

OVMF_CODE=""
for c in /usr/share/edk2/x64/OVMF_CODE.4m.fd /usr/share/edk2/x64/OVMF_CODE.fd \
         /usr/share/OVMF/OVMF_CODE.fd /usr/share/OVMF/OVMF_CODE_4M.fd; do
    [ -f "$c" ] && { OVMF_CODE="$c"; break; }
done
OVMF_VARS_SRC=""
for c in /usr/share/edk2/x64/OVMF_VARS.4m.fd /usr/share/edk2/x64/OVMF_VARS.fd \
         /usr/share/OVMF/OVMF_VARS.fd /usr/share/OVMF/OVMF_VARS_4M.fd; do
    [ -f "$c" ] && { OVMF_VARS_SRC="$c"; break; }
done
[ -n "$OVMF_CODE" ] && [ -n "$OVMF_VARS_SRC" ] || {
    echo "ERROR: OVMF firmware not found (install edk2-ovmf / ovmf)." >&2; exit 1; }

[ -f "$GNOBOOT" ] || { echo "ERROR: gnoboot not built at $GNOBOOT" >&2; exit 1; }
[ -f "$AGNOS_KERNEL" ] || { echo "ERROR: agnos kernel not found at $AGNOS_KERNEL" >&2; exit 1; }

# The launch hook is what makes this work without patching the kernel. Fail loudly
# rather than boot a kernel that will simply never start descent.
if ! strings "$AGNOS_KERNEL" | grep -q "/etc/probe-cmd"; then
    echo "ERROR: that kernel has no /etc/probe-cmd run hook." >&2
    echo "       Rebuild it with:  BENCH_CONNECT_SELFTEST=1 sh scripts/build.sh" >&2
    exit 1
fi

WORK="$ROOT/build/agnos-qemu"
LOGS="$ROOT/build/agnos-qemu-logs"
rm -rf "$WORK"; mkdir -p "$WORK" "$LOGS"

# --- descent, cross-built for agnos ---------------------------------------
echo "=== building descent --agnos ==="
cyrius build --agnos "$ROOT/src/main.cyr" "$WORK/descent-agnos" >"$LOGS/build.log" 2>&1 || {
    echo "ERROR: --agnos build failed; see $LOGS/build.log" >&2; tail -5 "$LOGS/build.log" >&2; exit 1; }
DESCENT="$WORK/descent-agnos"

# --- stage the ext2 root ---------------------------------------------------
# descent reads absolute paths (/data/zones/..., /data/classes.cyml) and WRITES
# /data/players + /data/audit.libro, so the root has to be a real writable fs.
SEED="$WORK/seed"
mkdir -p "$SEED/bin" "$SEED/etc" "$SEED/data/zones" "$SEED/data/players"
cp "$DESCENT" "$SEED/bin/descent"
chmod +x "$SEED/bin/descent"
cp "$ROOT"/data/zones/*.cyml "$SEED/data/zones/"
cp "$ROOT"/data/classes.cyml "$SEED/data/"
# The run hook reads this one line and sh_exec's it. A low tick keeps the probe
# short; YD_ADMIN is off — nothing here needs the @-namespace.
echo "run /bin/descent serve $GUEST_PORT" > "$SEED/etc/probe-cmd"

IMG="$WORK/agnos-descent.img"
ESP_MIB=33
PART_OFFSET=$(( ESP_MIB * 1048576 ))
TOTAL_MIB=192
dd if=/dev/zero of="$IMG" bs=1M count=$TOTAL_MIB status=none
parted -s "$IMG" mklabel gpt \
    mkpart ESP fat32 1MiB ${ESP_MIB}MiB set 1 esp on \
    mkpart agnos-fs ext2 ${ESP_MIB}MiB 100%
sgdisk -t 2:8300 "$IMG" >/dev/null
mformat -i "$IMG"@@1048576 -F
mmd -i "$IMG"@@1048576 ::EFI ::EFI/BOOT ::boot
mcopy -i "$IMG"@@1048576 "$GNOBOOT" ::EFI/BOOT/BOOTX64.EFI
mcopy -i "$IMG"@@1048576 "$AGNOS_KERNEL" ::boot/agnos
PART_BLOCKS=$(( (TOTAL_MIB - ESP_MIB) * 1048576 / 4096 ))
mkfs.ext2 -F -q -L AGNOS-DESCENT -b 4096 -m 0 \
    -d "$SEED" -E offset=$PART_OFFSET "$IMG" $PART_BLOCKS

echo "  kernel:  $AGNOS_KERNEL ($(stat -c %s "$AGNOS_KERNEL") B)"
echo "  descent: $DESCENT ($(stat -c %s "$DESCENT") B)"
echo "  image:   $IMG"
echo "  hostfwd: 127.0.0.1:$HOST_PORT -> guest :$GUEST_PORT"
echo ""

KVM_ARGS="-cpu max"
if [ -w /dev/kvm ] && [ -z "${NO_KVM:-}" ]; then KVM_ARGS="-enable-kvm -cpu host"; fi

LOG="$LOGS/serial.log"
cp "$OVMF_VARS_SRC" "$WORK/vars.fd"; chmod +w "$WORK/vars.fd"
timeout "$QEMU_TIMEOUT" qemu-system-x86_64 \
    -machine q35 -m 1G $KVM_ARGS \
    -drive "if=pflash,format=raw,readonly=on,file=$OVMF_CODE" \
    -drive "if=pflash,format=raw,file=$WORK/vars.fd" \
    -drive "file=$IMG,format=raw,if=none,id=disk0" \
    -device "nvme,drive=disk0,serial=AGNOS-DESCENT" \
    -netdev "user,id=u1,hostfwd=tcp:127.0.0.1:$HOST_PORT-:$GUEST_PORT" \
    -device "virtio-net-pci,netdev=u1" \
    -serial stdio -display none -no-reboot 2>/dev/null > "$LOG" &
QEMU_PID=$!

python3 "$ROOT/scripts/agnos_probe.py" "$HOST_PORT" "$SCENARIO" "$LOGS" 2>&1 | tee "$LOGS/probe.log"
PROBE_RC=${PIPESTATUS[0]}

kill "$QEMU_PID" 2>/dev/null
wait "$QEMU_PID" 2>/dev/null

echo ""
echo "=== kernel serial (tail) ==="
tail -25 "$LOG"
echo ""
echo "logs: $LOGS"
[ -n "${KEEP:-}" ] || rm -rf "$WORK"
exit "$PROBE_RC"
