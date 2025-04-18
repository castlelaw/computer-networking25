import sys
import socket

# HTTP 응답 메시지
HTTP_200 = "HTTP/1.0 200 OK\r\n"
HTTP_403 = "HTTP/1.0 403 Forbidden\r\n\r\n<html><body><h1>403 Forbidden</h1></body></html>"
HTTP_404 = "HTTP/1.0 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>"
CONTENT_TYPE = "Content-Type: text/html\r\n"
