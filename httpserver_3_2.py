import sys
import socket

# 명령줄 인자의 개수가 2가 아니면 종료
if len(sys.argv) != 2:
    print("python httpserver_3_2 .py [포트]")
    sys.exit(1)

# 명령줄 인자에서 포트 번호 가져옴
port_str = sys.argv[1]

# 포트 번호가 숫자가 아니면 종료
if not port_str.isdigit():
    print("error: 포트번호는 숫자")
    sys.exit(1)

# 포트 번호 정수
port = int(port_str)

# 포트 번호가 1024미만이면 종료
if port < 1024:
    print("error: 포트번호 > 1024")
    sys.exit(1)

# TCP소켓 생성, 모든 ip에서 연결할수 있도록 바인딩, 최대 1개 연결 요청
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", port))
server_socket.listen(1)
print("서버 시작")
print(f" 연결 대기: {port}")


# 파일 존재 확인
def file_exist(filename):
    try:
        f = open(filename, "r")  
        f.close()
        return True
    except:
        return False

# HTTP 응답 메시지
HTTP_200 = "HTTP/1.0 200 OK\r\n"
HTTP_403 = "HTTP/1.0 403 Forbidden\r\n\r\n<html><body><h1>403 Forbidden</h1></body></html>"
HTTP_404 = "HTTP/1.0 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>"
CONTENT_TYPE = "Content-Type: text/html\r\n"

# HTTP 서버 클라이언트의 요청
while True:
    conn, addr = server_socket.accept() # 클라이언트 연결 요청 수락, 주소 출력
    print(f" 연결됨: {addr}")
    
    try:
        request = conn.recv(1024).decode("utf-8") # 요청 메시지 수신 및 디코딩, 내용 출력
        print(f"받은 요청:\n{request}")

        # 빈 요청이면 종료
        if not request:
            conn.close()
            continue

        lines = request.splitlines() # 줄별로 분리
        request_line = lines[0]      # 첫 줄 가져옴
        parts = request_line.split() # 요청 라인을 공백으로 분리

        # HTTP 요청 형식 확인(메소드, 패스, http) 아니면 403 오류
        if len(parts) != 3:
            conn.sendall(HTTP_403.encode())
            conn.close()
            continue

        method, path, _ = parts                    # 메소드와 패스만 나눔
        path_parts = path.split("/")               # 패스를 /로 분리
        filename = path_parts[-1] or "index.html"  # 파일 이름 추출

        # get 요청이 아니면 오류
        if method != "GET":
            conn.sendall(HTTP_403.encode())
            conn.close()
            continue
        
        # .html .htm 이 아니면 오류
        if not (filename.endswith(".html") or filename.endswith(".htm")):
            conn.sendall(HTTP_403.encode())
            conn.close()
            continue
        # 파일이 존재하지 않으면 오류
        if not file_exist(filename):
            conn.sendall(HTTP_404.encode())
            conn.close()
            continue
        # 파일이 존재하면 http 전송
        with open(filename, "r", encoding="utf-8") as f:
            body = f.read()
            response= (HTTP_200 + CONTENT_TYPE + f"Content-Length: {len(body.encode())}\r\n" + "\r\n" + body)
            conn.sendall(response.encode())
    # 예외 발생 시 오류
    except Exception as e:
        print("서버 오류:", e)
        conn.sendall(b"HTTP/1.0 500 Internal Server Error\r\n\r\n<h1>500 Internal Server Error</h1>")
    
    # 연결 소켓 종료
    conn.close()
