import sys
import socket
import select
import queue

HOST = ''            # 서버가 바인드할 IP 주소
PORT = 0             # 기본 포트 번호
RECV_BUFFER = 4096   # 한번에 읽을 최대 바이트 수

#포트 입력 확인
if len(sys.argv) != 2:
    print(f"사용법: python {sys.argv[0]} <포트번호>", file=sys.stderr)
    sys.exit(1)

#포트 번호를 정수로 변환, 잘못 입력하면 종료
try:
    PORT = int(sys.argv[1])
except ValueError:
    print("포트는 정수여야 합니다.", file=sys.stderr)
    sys.exit(1)

#서버 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   #주소 재사용 옵션 설정
server_socket.bind((HOST, PORT)) # 지정된 IP와 포트에 바인드
server_socket.listen(5) # 최대 5개 까지 대기 연결 허용
server_socket.setblocking(False) # 소켓을 논블로킹 모드 설정

print(f"{PORT}번 포트에서 연결 대기 중...")

# select()에서 관리할 소켓 목록
inputs = [server_socket] # 읽기를 대기할 소켓
client_buffers = {} # 클라이언트별 수신 데이터 저장

#요청 처리 함수
def handle_request(data):
    try:
        request_line = data.split('\r\n')[0] # 첫 줄 
        method, path, _ = request_line.split() # 메서드, 경로, 버전 

        if method != 'GET': #get 이외의 요청은 405 반환
            return "HTTP/1.0 405 Method Not Allowed\r\n\r\n허용되지 않는 메소드입니다.".encode()

        if path == '/': # 루트 요청이면 index.html
            path = '/index.html'
        
        filename = '.' + path #상대경로로 파일이름
        try:
            with open(filename, 'rb') as f: # 파일 열기 성공시 내용 읽기
                body = f.read()
        
        except FileNotFoundError:
            return "HTTP/1.1 404 Not Found\r\n\r\n요청한 파일이 없습니다.".encode()
        
        header = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode()
        return header + body
    except Exception:
        return "HTTP/1.1 400 Bad Request\r\n\r\n잘못된 요청입니다.".encode() # 요청 파싱 실패시 400반환

while True:
    readable, _, _ = select.select(inputs, [], []) # 읽기 가능한 소켓 대기

    for sock in readable:
        if sock is server_socket:
            # 새로운 연결 수락
            client_sock, addr = server_socket.accept()
            print(f"연결됨: {addr}")
            client_sock.setblocking(False)
            inputs.append(client_sock)
            client_buffers[client_sock] = b''  # 버퍼 초기화
        else:
            try:
                data = sock.recv(RECV_BUFFER)
            except ConnectionResetError:
                data = b''  # 연결이 비정상 종료됨

            if data:
                client_buffers[sock] += data
                # 요청 전체 수신 여부 확인
                if b'\r\n\r\n' in client_buffers[sock]:
                    request_data = client_buffers[sock].decode(errors='ignore')
                    response = handle_request(request_data)
                    try:
                        sock.sendall(response)
                    except BrokenPipeError:
                        pass
                    sock.close()
                    inputs.remove(sock)
                    del client_buffers[sock]
            else:
                # 클라이언트가 연결을 끊음
                print("연결 종료됨")
                sock.close()
                if sock in inputs:
                    inputs.remove(sock)
                if sock in client_buffers:
                    del client_buffers[sock]


