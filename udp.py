"""
Minimal pure-Python replacement for the `udp` module from the (Python 2-only)
`pyip` package, which IKEForce used to hand-assemble UDP datagrams for sending
over a raw socket.

Only the small surface that ikeclient.sendPacket() relies on is implemented:

    p = udp.Packet()
    p.sport = <int>
    p.dport = <int>
    p.data  = <bytes>
    datagram = udp.assemble(p, 0)   # -> bytes (UDP header + data)

The assembled datagram is an 8-byte UDP header followed by the payload, sent
via socket(AF_INET, SOCK_RAW, IPPROTO_UDP); the kernel supplies the IP header.

Note on the checksum: the original call site passes 0, i.e. "do not compute a
checksum". A zero UDP checksum is explicitly legal over IPv4 (RFC 768), so the
checksum field is left as 0 here. If you ever need a computed checksum (e.g. to
satisfy a picky middlebox) you would have to build an IPv4 pseudo-header, which
requires knowing the source IP - out of scope for this drop-in shim. A pentester
who needs that level of control can swap this for scapy.
"""

import struct


class Packet(object):
    def __init__(self):
        self.sport = 0
        self.dport = 0
        self.data = b""


def assemble(packet, cksum=1):
    data = packet.data
    if not isinstance(data, (bytes, bytearray)):
        # tolerate an iterable of ints / a str of latin-1 bytes
        if isinstance(data, str):
            data = data.encode("latin-1")
        else:
            data = bytes(data)
    length = 8 + len(data)
    checksum = 0  # see module docstring re: zero checksum being valid for IPv4
    header = struct.pack("!HHHH", packet.sport & 0xFFFF,
                         packet.dport & 0xFFFF, length & 0xFFFF, checksum)
    return header + bytes(data)