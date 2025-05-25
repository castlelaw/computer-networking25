import sys
import socket
import select
import queue

HOST = ''  
PORT = 0   
RECV_BUFFER = 4096   # 한번에 읽을 최대 바이트 수

#포트 입력 확인
if len(sys.argv) != 2:
    print(f"사용법: python3 {sys.argv[0]} <포트번호>", file=sys.stderr)
    sys.exit(1)

#포트 번호를 정수로 변환
try:
    PORT = int(sys.argv[1])
except ValueError:
    print("포트는 정수여야 합니다.", file=sys.stderr)
    sys.exit(1)

#서버 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   #주소 재사용 옵션 설정
server_socket.bind((HOST, PORT))
server_socket.listen(5)
server_socket.setblocking(False)

print(f"{PORT}번 포트에서 연결 대기 중...")

inputs = [server_socket]
client_buffers = {}

#요청 처리 함수
def handle_request(data):
    try:
        request_line = data.split('\r\n')[0]
        method, path, _ = request_line.split()

        if method != 'GET':
            return "HTTP/1.0 405 Method Not Allowed\r\n\r\n허용되지 않는 메소드입니다.".encode()

        if path == '/':
            path = '/index.html'
        
        filename = '.' + path
        try:
            with open(filename, 'rb') as f:
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
        return "HTTP/1.1 400 Bad Request\r\n\r\n잘못된 요청입니다.".encode()
while True:
    readable, _, _ = select.select(inputs, [], [] )

    for sock in readable:
        if sock is server_socket:
            client_sock, addr = server_socket.accept()
            print(f"연결됨: {addr}")
    




