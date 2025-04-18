import sys
import socket

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
