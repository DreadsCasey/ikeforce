# IKEForce (Python 3)

A maintained **Python 3 port** of [SpiderLabs/ikeforce](https://github.com/SpiderLabs/ikeforce) — the command-line IPsec VPN tool for **IKEv1 Aggressive Mode** group name/ID enumeration and **XAUTH** credential brute forcing.

The original tool is excellent but has been unmaintained and Python 2-only for years. Python 2 is end-of-life, and the existing partial Py3 conversions are incomplete or untested. This fork is a full port with the cryptographic operations validated against known-answer vectors, so output matches the original byte-for-byte.

> **Authorised testing only.** This tool brute forces authentication against VPN endpoints and does **not** implement account-lockout handling. Run it only against systems you own or have explicit written permission to test. You are responsible for staying within scope and the law.

---

## What changed from the original

| Area | Change |
|------|--------|
| **Runtime** | Python 2 → Python 3.x |
| **Crypto backend** | `pycrypto` (dead/unmaintained) → `pycryptodome` |
| **IP handling** | `pyip` (no Py3 support) → bundled custom shim |
| **Hex handling** | Removed Py2 `str.encode('hex')` / `.decode('hex')`; replaced with `binascii` / `bytes.fromhex` throughout |
| **Integer math** | Fixed `/` vs `//` division behaviour under Py3 |
| **Syntax** | `print` statements, exception syntax, and indentation normalised |
| **Validation** | Crypto routines tested against known-answer vectors to confirm parity with the original |

The CLI and behaviour are unchanged — if you've used the original, this is a drop-in replacement.

---

## Installation

```bash
git clone https://github.com/DreadsCasey/ikeforce.git
cd ikeforce
pip install -r requirements.txt
```

Requirements:

- Python 3.x
- `pycryptodome`

```bash
pip install pycryptodome
```

> `pyip` is **no longer required** — the necessary functionality is bundled.

---

## Usage

```
./ikeforce.py [target] [mode] [options]
```

### Modes

| Flag | Mode | Purpose |
|------|------|---------|
| `-a`, `--all` | Transform enumeration | Enumerate all accepted Aggressive Mode transform sets |
| `-e`, `--enum` | Enumeration | Discover the valid group name / ID from a wordlist |
| `-b`, `--brute` | Brute force | Brute force XAUTH credentials |
| `-c`, `--connect` | Connect | Test a connection with known values |

### Common options

| Flag | Description |
|------|-------------|
| `-w WORDLIST` | Path to wordlist (group names or passwords depending on mode) |
| `-i ID` | Group name / ID (brute mode) |
| `-u USERNAME` | XAUTH username (brute mode) |
| `-U USERLIST` | XAUTH username list (optional, brute mode) |
| `-p PASSWORD` | XAUTH password (connect mode) |
| `-k PSK` | Pre-shared key (brute mode) |
| `-s SPEED` | Guess speed `1`–`5` (1 = fastest, 5 = slowest). Default `3` |
| `-y IDTYPE` | ID type for the Identification payload. Default `2` (FQDN) |
| `-l KEYLEN` | Key length, for AES encryption types |
| `-v VENDOR` | Vendor type (`cisco` or `watchguard`) |
| `--sport SPORT` | Source port. Default `500` |
| `--version VERSION` | IKE version. Default `1` |
| `-d`, `--debug` | Enable debug output |

> Verify these against your local `parser.add_option` definitions before relying on them.

### Examples

Enumerate accepted transform sets:

```bash
./ikeforce.py 192.168.1.110 -a -s 1
```

Enumerate the group name / ID:

```bash
./ikeforce.py 192.168.1.110 -e -w wordlists/groupnames.dic -s 1
```

Brute force XAUTH credentials with a known group ID and PSK:

```bash
./ikeforce.py 192.168.1.110 -b -i groupid -u dan -k psk123 -w passwords.txt -s 1
```

---

## Typical workflow

IKEForce fits into the standard IKE Aggressive Mode attack chain alongside `ike-scan` and `psk-crack`:

1. **Identify** IKE endpoints (e.g. `ike-scan -M -A <target>` or a UDP/500 scan).
2. **Enumerate** the group name / ID — `ikeforce.py <target> -e -w groupnames.dic`.
3. **Capture** the Aggressive Mode PSK hash with `ike-scan -A --id=<groupid> -P<target>.key`.
4. **Crack** the hash offline (`psk-crack`, or hashcat mode `5400`).
5. **Brute force** XAUTH credentials with the recovered PSK — `ikeforce.py <target> -b ...`.

---

## Credits

- Original tool and research: **SpiderLabs / Trustwave** — [SpiderLabs/ikeforce](https://github.com/SpiderLabs/ikeforce)
- Background reading — the *Cracking IKE Mission:Improbable* series (parts 1–3) on the SpiderLabs blog
- Python 3 port and validation: **[YOUR NAME]**

## License

This port preserves the licensing of the upstream SpiderLabs project. See `LICENSE`.
