# IKEForce — Python 3 port notes

Mechanical + semantic port of SpiderLabs IKEForce (archived, Python 2) to
Python 3. Tested on Python 3.12.

## Dependencies (changed)

| Original (Py2)      | Replacement (Py3)                    | Why |
|---------------------|--------------------------------------|-----|
| `pycrypto`          | `pycryptodome`                       | pycrypto is dead/unmaintained; pycryptodome is the drop-in `Crypto.*` successor |
| `pyip` (`udp`)      | bundled `udp.py` (pure stdlib)       | pyip is Python 2-only and uninstallable on 3 |
| `pyopenssl` (`OpenSSL.rand`) | `os.urandom`                | `OpenSSL.rand` was removed from modern pyOpenSSL |

Install: `pip install pycryptodome`  (pyopenssl no longer required.)

Run still requires **root** — `sendPacket()` uses a raw socket, exactly as the
original did.

## What changed in the code

- **print statements → `print()`** (≈760 sites), `raw_input → input`,
  `dict.iteritems() → .items()`, `SocketServer → socketserver`,
  `long → int`, `except X, e: → except X as e:` (via a 2to3-class pass).
- **Indentation**: original mixed hard tabs and 8-space indents (equivalent
  under Py2, rejected by Py3). Normalised leading indentation to spaces; tabs
  inside string literals left untouched.
- **str vs bytes** — the substantive work. Py2 used `str` as both text and
  bytes. Mapping applied: hex representations stay `str`; raw packet/crypto
  data is `bytes`.
  - `X.decode('hex')` → `bytes.fromhex(X)`  (hex str → bytes)
  - `b.encode('hex')` → `b.hex()`           (bytes → hex str)
  - `hmac.new(psk, …)` — PSK encoded to bytes; Py3.8+ also **requires** an
    explicit `digestmod`, so MD5 branches now pass `hashlib.md5`
    (SHA branches already passed `hashlib.sha1`).
  - byte literals used in crypto/packet concatenation: `"\x00"` → `b"\x00"`
    (also `\x01`, `\x02`).
  - `ord(data[-1])` → `data[-1]` (indexing `bytes` already yields `int`).
  - `b''.join(...)` where cookies/raw values are joined (was `''.join`).
- **dh.py**: `(self.prime-1)/2` → `//2` (modular-exponent argument must stay
  int); `s.update(str(secret))` → `…encode()`.

The receive path converts socket bytes to a hex string immediately
(`data.hex()`), so packet **parsing** is all str-based and ports cleanly; the
bytes boundary is re-crossed only at send time (`bytes.fromhex` → `struct.pack`
→ raw socket).

## Verification done

- All 7 modules byte-compile and import.
- **IKE crypto known-answer vectors pass byte-for-byte** (SKEYID, HASH_R,
  SKEYID_d/a/e, encryption key, IV) — validates the whole str/bytes path
  through the crypto.
- Diffie-Hellman key generation, `secRandom`, `packPacket`, and
  `parseHeader` exercised; CLI (`-h`) works.

## Caveats / not exercised

- **No live IKE endpoint or root** was available here, so the full
  enum/brute/connect round-trips and the deeper `ikehandler` parse branches
  (SA/transform/encrypted payloads) were not run end-to-end. Logic was ported
  faithfully and the primitives verified, but exercise against a real target
  before relying on it.
- **`udp.py`** sends with UDP checksum = 0 (legal over IPv4, RFC 768; matches
  the original `udp.assemble(pkt, 0)` call). If a middlebox demands a real
  checksum, swap `sendPacket()` for scapy.
- `ikecrypto.py`'s own `main()` self-test still aborts at the final 3DES
  decrypt: it calls `calcKa(…, keyLen=48)`, `calcKa` doubles it, yielding a
  48-byte key — not a valid 3DES key length. **Pre-existing harness bug**
  (pycrypto was lax, pycryptodome enforces it), not a port defect; the key
  derivation itself is correct (see KAT above).
- `decrypt-test.py` is a leftover dev scratch script (it imported a `crypto`
  module absent from the repo). Import fixed to `ikecrypto`; otherwise left
  as-is. Not part of normal use.