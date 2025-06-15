import socket
import random
import struct
import sys

QUERY_TYPES = {
    "A": 1,
    "NS": 2,
    "CNAME": 5,
    "MX": 15,
    "TXT": 16,
    "AAAA": 28
}

######## USAGE ########
# python dns_tester.py example.com (DNS_server_ip port_number query_type)
# python dns_tester.py example.com 
# python dns_tester.py example.com 8.8.8.8 
# python dns_tester.py example.com 8.8.8.8 53 
# python dns_tester.py example.com 8.8.8.8 53 A
#######################

def build_dns_query(domain_name, qtype_name):
    transaction_id = random.randint(0, 65535)
    flags = 0x0100
    qdcount = 1
    header = struct.pack(">HHHHHH", transaction_id, flags, qdcount, 0, 0, 0)

    def encode_domain(name):
        parts = name.split(".")
        encoded = b''
        for part in parts:
            encoded += bytes([len(part)]) + part.encode()
        return encoded + b'\x00'

    qname = encode_domain(domain_name)
    qtype = QUERY_TYPES.get(qtype_name.upper(), 1)
    qclass = 1  # IN

    question = qname + struct.pack(">HH", qtype, qclass)
    return header + question


def read_name(data, offset):
    labels = []
    jumped = False
    start_offset = offset
    while True:
        length = data[offset]
        if length == 0:
            offset += 1
            break
        if (length & 0xC0) == 0xC0:
            pointer = ((length & 0x3F) << 8) | data[offset + 1]
            if not jumped:
                start_offset = offset + 2
            offset = pointer
            jumped = True
        else:
            offset += 1
            labels.append(data[offset:offset+length].decode(errors='ignore'))
            offset += length
    return ".".join(labels), (start_offset if jumped else offset)


def parse_dns_response_all(data):
    records = []
    try:
        header = struct.unpack(">HHHHHH", data[:12])
        qdcount = header[2]
        ancount = header[3]
        offset = 12

        # Skip questions
        for _ in range(qdcount):
            while data[offset] != 0:
                offset += data[offset] + 1
            offset += 1 + 4

        # Parse answers
        for _ in range(ancount):
            name, offset = read_name(data, offset)
            rtype, rclass, ttl, rdlength = struct.unpack(">HHIH", data[offset:offset+10])
            offset += 10
            rdata = data[offset:offset+rdlength]

            if rtype == 1 and rdlength == 4:  # A
                ip = struct.unpack(">BBBB", rdata)
                records.append(("A", name, ".".join(map(str, ip))))
            elif rtype == 28 and rdlength == 16:  # AAAA
                ipv6 = ":".join(f"{rdata[i]<<8 | rdata[i+1]:x}" for i in range(0, 16, 2))
                records.append(("AAAA", name, ipv6))
            elif rtype in (2, 5):  # NS, CNAME
                ref_name, _ = read_name(data, offset)
                type_name = "NS" if rtype == 2 else "CNAME"
                records.append((type_name, name, ref_name))
            elif rtype == 15:  # MX
                preference = struct.unpack(">H", rdata[:2])[0]
                exchange, _ = read_name(data, offset + 2)
                records.append(("MX", name, f"{preference} {exchange}"))
            elif rtype == 16:  # TXT
                txt_len = rdata[0]
                txt_data = rdata[1:1+txt_len].decode(errors='ignore')
                records.append(("TXT", name, txt_data))

            offset += rdlength

    except Exception as e:
        print("Error while parsing the response:", e)

    return records


def send_dns_query(domain, dns_ip, port, qtype):
    query = build_dns_query(domain, qtype)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(3)
        sock.sendto(query, (dns_ip, port))
        try:
            data, _ = sock.recvfrom(512)
            print(f"Response received (bytes: {len(data)})")
            print(f"Response (HEX): {data.hex()}")

            parsed_records = parse_dns_response_all(data)
            if parsed_records:
                print("Parsed DNS response:")
                for rtype, name, value in parsed_records:
                    print(f" - {rtype} {name} → {value}")
            else:
                print("No valid response records.")

        except socket.timeout:
            print("Timeout: no responses")

if __name__ == "__main__":
    domain = "google.com"
    dns_ip = "127.0.0.1"
    port = 1053
    qtype = "A"

    if len(sys.argv) >= 2:
        domain = sys.argv[1]
    if len(sys.argv) >= 3:
        dns_ip = sys.argv[2]
    if len(sys.argv) >= 4:
        port = int(sys.argv[3])
    if len(sys.argv) >= 5:
        qtype = sys.argv[4]

    if qtype.upper() not in QUERY_TYPES:
        print(f"Not supported query type: {qtype}")
        print(f"The list of supported query types: {', '.join(QUERY_TYPES.keys())}")
        sys.exit(1)

    print(f"[INFO] Sending query '{domain}' ({qtype}) to {dns_ip}:{port}.\n")
    send_dns_query(domain, dns_ip, port, qtype)

