import sys
import socket

if len(sys.argv) != 2:
    print("python httpserver_3_2 .py [포트]")
    sys.exit(1)

port_str = sys.argv[1]

if not port_str.isdigit():
    print("error: 포트번호는 숫자")
    sys.exit(1)

port = int(port_str)

if port < 1024:
    print("error: 포트번호 > 1024")
    sys.exit(1)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", port))
server_socket.listen(1)
print("서버 시작")
print(f"→ 연결 대기: {port}")


# 파일 존재 확인하기
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

#HTTP 서버 클라이언트의 요청
while True:
    conn, addr = server_socket.accept()
    print(f"→ 연결됨: {addr}")
    
    try:
        request = conn.recv(1024).decode("utf-8")
        print(f"받은 요청:\n{request}")

        if not request:
            conn.close()
            continue

        lines = request.splitlines()
        request_line = lines[0]
        parts = request_line.split()

        #HTTP 요청 형식 확인
        if len(parts) != 3:
            conn.sendall(HTTP_403.encode())
            conn.close()
            continue

        method, path, _ = parts
        path_parts = path.split("/")
        filename = path_parts[-1] or "index.html"  

        if method != "GET":
            conn.sendall(HTTP_403.encode())
            conn.close()
            continue

        if not (filename.endswith(".html") or filename.endswith(".htm")):
            conn.sendall(HTTP_403.encode())
            conn.close()
            continue

        if not file_exist(filename):
            conn.sendall(HTTP_404.encode())
            conn.close()
            continue
        with open(filename, "r", encoding="utf-8") as f:
            body = f.read()
            response= (HTTP_200 + CONTENT_TYPE + f"Content-Length: {len(body.encode())}\r\n" + "\r\n" + body)
            conn.sendall(response.encode())

    except Exception as e:
        print("서버 오류:", e)
        conn.sendall(b"HTTP/1.0 500 Internal Server Error\r\n\r\n<h1>500 Internal Server Error</h1>")

    conn.close()
