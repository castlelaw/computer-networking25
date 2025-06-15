import sys
import socket

class DNSProxy: # DNS 프록시 서버 클래스 정의
    def __init__(self, listen_ip='0.0.0.0', listen_port=5353, upstream_dns='8.8.8.8', upstream_port=53, fake_ip='YOUR_PUBLIC_IP_HERE'):
        self.listen_ip = listen_ip                # DNS 요청을 로컬에서 수신할 IP
        self.listen_port = listen_port            # DNS 요청을 로컬에서 수신할 포트
        self.upstream_dns = upstream_dns          # 실제 DNS 서버주소 (구글 DNS)
        self.upstream_port = upstream_port        # 업스트림 DNS 포트 (기본:53)
        self.fake_ip = fake_ip                    # 조작된 응답에 사용할 IP

    def start(self): #DNS 프록시 서버 시작
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     # UDP 소켓 생성
        sock.bind((self.listen_ip, self.listen_port))               # 소켓을 로컬 IP와 포트에 바인딩
        print(f"[*] DNS 프록시 실행 중: {self.listen_ip}:{self.listen_port}")

        while True:
            data, addr = sock.recvfrom(512)  # 클라이언트로부터 최대 512바이트 데이터 수신
            print(f"[>] 클라이언트 {addr}로부터 DNS 요청 수신")
            response = self.forward_to_upstream(data)  # 업스트림 DNS서버에 요청 전달

            if not response: #업스트림 서버로부터 응답 없으면
                print("[!] 업스트림 DNS 응답 없고 무시됨")
                continue #다음으로 넘어감

            if self.is_nxdomain(response):  # 응답이 NXDOMAIN인지 확인(RCODE == 3)
                print("[!] NXDOMAIN 발견 - 조작된 A 레코드로 응답합니다")
                response = self.build_fake_response(data)  # 조작된 응답 생성

            sock.sendto(response, addr)  # 응답 클라이언트로 전달

    def forward_to_upstream(self, query):
        # 클라이언트로 부터 받은 질의를 업스트림 DNS 서버로 전달
        upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #업스트림용 UDP 소켓 생성
        upstream_sock.settimeout(2) #타임아웃 2초 설정
        try:
            upstream_sock.sendto(query, (self.upstream_dns, self.upstream_port)) # DNS 질의 전송
            response, _ = upstream_sock.recvfrom(512) # 응답 수신
            return response
        except socket.timeout:
            print("[!] 업스트림 DNS 타임아웃")#타임아웃 발생시 출력
            return b'' # 빈 응답 
        finally:
            upstream_sock.close() # 소켓 종료


    def is_nxdomain(self, response):  #응답 메시지가 nxdomain 인지 확인
        if not response or len(response) < 4: # 응답이 없거나 너무 짧으면 False
            return False

    # 응답 메시지의 4번째 바이트에서 하위 4비트만 추출 → RCODE 값
        rcode = response[3] & 0x0F
        return rcode == 3  # RCODE ==3 이면 NXDOMAIN (존재하지 않는 도메인)
        
    def build_fake_response(self, query): # 가짜 A 레코드 응답 만들기
        transaction_id = query[:2]            # 클라이언트 요청과 같은 ID로 응답
        flags = b'\x81\x80'                   # 응답이고, 정상 상태 (QR=1, RCODE=0)
        question_count = b'\x00\x01'          # 질문 1개
        answer_count = b'\x00\x01'            # 응답 1개
        authority_count = b'\x00\x00'
        additional_count = b'\x00\x00'
        
        dns_header = transaction_id + flags + question_count + answer_count + authority_count + additional_count
        
        # [2] 질문 영역 그대로 복사 (도메인 이름, 타입, 클래스)
        question_part = query[12:]  # 질문 부분은 12바이트 이후부터 끝까지

        # [3] A 레코드(IPv4 주소) 응답 만들기
        name_pointer = b'\xC0\x0C'             # 0x0C 위치의 이름을 참조하겠다는 뜻 (압축)
        type_A = b'\x00\x01'                   # A 레코드
        class_IN = b'\x00\x01'                 # 인터넷 클래스
        ttl = self.to_bytes(60, 4)             # TTL 60초 (4바이트)
        rdlength = b'\x00\x04'                 # 응답 데이터 길이 = 4바이트
        ip_address_bytes = socket.inet_aton(self.fake_ip)  # 문자열 ip를 바이트로 변환

        answer_part = name_pointer + type_A + class_IN + ttl + rdlength + ip_address_bytes

        # [4] 최종 응답 = 헤더 + 질문 + 답변
        response = dns_header + question_part + answer_part
        return response
    def to_bytes(self, val, length):  # 정수를 지정된 길이의 바이트로 변환
        return val.to_bytes(length, byteorder='big')

    
    
    
if __name__ == '__main__':
    # 실행 시, 본인 서버의 실제 공인 IP를 넣어주세요
        if len(sys.argv) != 3:
            print(f"사용법: python {sys.argv[0]} <조작할_공인_IP> <수신 포트>")
            sys.exit(1)
        fake_ip = sys.argv[1]           # 조작할 IP주소
        listen_port = int(sys.argv[2])  # 명령행에서 받은 수신 포트

        proxy = DNSProxy(fake_ip=fake_ip, listen_port=listen_port) #DNS 객체 생성
        proxy.start()
