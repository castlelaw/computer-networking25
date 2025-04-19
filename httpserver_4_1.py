import sys
import socket
import os

if len(sys.argv) != 2:
    print("python httpserver_4_1.py [포트]")
    sys.exit(1)

port_str = sys.argv[1]

if not port_str.isdigit():
    print("error: 포트번호는 숫자")
    sys.exit(1)

port = int(port_str)

if port < 1024:
    print("error: 포트번호 > 1024.")
    sys.exit(1)

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
