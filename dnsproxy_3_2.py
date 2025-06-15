import sys
import socket

class DNSProxy:
    def __init__(self, listen_ip='0.0.0.0', listen_port=5353, upstream_dns='8.8.8.8', upstream_port=53, fake_ip='YOUR_PUBLIC_IP_HERE'):
        self.listen_ip = listen_ip                # 로컬에서 수신할 IP
        self.listen_port = listen_port            # 로컬에서 수신할 포트
        self.upstream_dns = upstream_dns          # 업스트림 DNS 서버 (구글 DNS)
        self.upstream_port = upstream_port        # 업스트림 DNS 포트
        self.fake_ip = fake_ip                    # 조작된 응답에 사용할 IP

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP 소켓 생성
        sock.bind((self.listen_ip, self.listen_port))             # 로컬 IP와 포트에 바인딩
        print(f"[*] DNS 프록시 실행 중: {self.listen_ip}:{self.listen_port}")

        while True:
            data, addr = sock.recvfrom(512)  # 클라이언트로부터 512바이트 이하 데이터 수신
            print(f"[>] 클라이언트 {addr}로부터 DNS 요청 수신")
            response = self.forward_to_upstream(data)  # 업스트림 DNS에 요청 전달

            if self.is_nxdomain(response):  # 응답이 NXDOMAIN인지 확인
                print("[!] NXDOMAIN 발견 - 조작된 A 레코드로 응답합니다")
                response = self.build_fake_response(data)  # 조작된 응답 생성

            sock.sendto(response, addr)  # 응답 클라이언트로 전달

    def forward_to_upstream(self, query):
        # 업스트림 DNS 서버로 요청 전달
        upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        upstream_sock.settimeout(2)
        upstream_sock.sendto(query, (self.upstream_dns, self.upstream_port))
        try:
            response, _ = upstream_sock.recvfrom(512)
            return response
        except socket.timeout:
            print("[!] 업스트림 DNS 타임아웃")
            return b''
