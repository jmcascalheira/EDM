"""Android Bluetooth (classic SPP) serial backend for total-station comms.

Presents the subset of the pyserial ``serial.Serial`` interface that
``totalstation.py`` actually uses (port/baudrate/parity/stopbits/bytesize/
timeout/write_timeout, open/close/is_open, write/read_until/in_waiting,
reset_input_buffer/reset_output_buffer), so the rest of the app is unchanged.

Android only — uses pyjnius / the Android Bluetooth API. Do NOT import this on
desktop (it imports jnius). ``totalstation.py`` imports it lazily inside its
Android-only branches.
"""

import threading
import time

from jnius import autoclass

BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
UUID = autoclass('java.util.UUID')

# Serial Port Profile (SPP) — the standard UUID for classic-Bluetooth serial.
_SPP_UUID = '00001101-0000-1000-8000-00805F9B34FB'


def _adapter():
    return BluetoothAdapter.getDefaultAdapter()


def bluetooth_comports():
    """Paired Bluetooth devices as pyserial-style ``(port, desc, hwid)`` tuples
    so the existing COM-port selection UI can list them. ``port`` is the device
    MAC address (unique, used to connect); ``desc`` is the friendly name."""
    result = []
    adapter = _adapter()
    if adapter is None:
        return result
    try:
        bonded = adapter.getBondedDevices().toArray()
    except Exception:
        return result
    for dev in bonded:
        try:
            mac = dev.getAddress()
            name = dev.getName() or mac
            result.append((mac, name, mac))
        except Exception:
            continue
    return result


class BluetoothSerial:
    """Drop-in for the subset of ``serial.Serial`` used by totalstation.py,
    backed by an Android RFCOMM (SPP) Bluetooth socket. A background thread
    drains the input stream into a buffer so ``in_waiting``/``read_until``
    keep pyserial's semantics."""

    def __init__(self):
        self.port = None            # device MAC address (or name)
        self.baudrate = None
        self.parity = None
        self.stopbits = None
        self.bytesize = None
        self.timeout = 30
        self.write_timeout = 5
        self.is_open = False
        self._socket = None
        self._in = None
        self._out = None
        self._buf = bytearray()
        self._lock = threading.Lock()
        self._reader = None
        self._running = False

    def _find_device(self, adapter):
        target = (self.port or '').strip()
        try:
            bonded = adapter.getBondedDevices().toArray()
        except Exception:
            bonded = []
        for dev in bonded:
            try:
                if dev.getAddress() == target or dev.getName() == target:
                    return dev
            except Exception:
                continue
        if len(target) == 17 and target.count(':') == 5:
            try:
                return adapter.getRemoteDevice(target)
            except Exception:
                return None
        return None

    def open(self):
        adapter = _adapter()
        if adapter is None:
            raise OSError('No Bluetooth adapter available on this device.')
        if not adapter.isEnabled():
            raise OSError('Bluetooth is turned off. Enable it and pair the total station first.')
        device = self._find_device(adapter)
        if device is None:
            raise OSError('Bluetooth device "%s" is not paired. Pair it in Android settings first.' % self.port)
        uuid = UUID.fromString(_SPP_UUID)
        try:
            adapter.cancelDiscovery()
            self._socket = device.createRfcommSocketToServiceRecord(uuid)
            self._socket.connect()
        except Exception:
            # Some stations only accept an insecure RFCOMM socket.
            try:
                self._socket = device.createInsecureRfcommSocketToServiceRecord(uuid)
                self._socket.connect()
            except Exception as ex:
                self._socket = None
                raise OSError('Could not connect to %s: %s' % (self.port, ex))
        self._in = self._socket.getInputStream()
        self._out = self._socket.getOutputStream()
        with self._lock:
            self._buf = bytearray()
        self.is_open = True
        self._running = True
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    def _read_loop(self):
        while self._running and self._in is not None:
            try:
                b = self._in.read()   # blocking; returns an int, -1 at EOF
            except Exception:
                break
            if b == -1:
                break
            with self._lock:
                self._buf.append(b & 0xFF)

    def close(self):
        self._running = False
        try:
            if self._socket is not None:
                self._socket.close()
        except Exception:
            pass
        self._socket = None
        self._in = None
        self._out = None
        self.is_open = False

    def write(self, data):
        if not self.is_open or self._out is None:
            return 0
        if isinstance(data, str):
            data = data.encode()
        self._out.write(bytearray(data))
        self._out.flush()
        return len(data)

    @property
    def in_waiting(self):
        with self._lock:
            return len(self._buf)

    def read_until(self, expected=b'\n', size=None):
        deadline = time.time() + (self.timeout or 30)
        while time.time() < deadline:
            with self._lock:
                idx = self._buf.find(expected)
                if idx != -1:
                    end = idx + len(expected)
                    out = bytes(self._buf[:end])
                    del self._buf[:end]
                    return out
                if size is not None and len(self._buf) >= size:
                    out = bytes(self._buf[:size])
                    del self._buf[:size]
                    return out
            time.sleep(0.02)
        with self._lock:                 # timeout: return whatever is buffered
            out = bytes(self._buf)
            self._buf.clear()
            return out

    def reset_input_buffer(self):
        with self._lock:
            self._buf.clear()

    def reset_output_buffer(self):
        pass
