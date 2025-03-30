$ python httpclient_4_1.py http://example.com
import sys
import socket

MAX_REDIRECTS = 5

def send_request(url):
  if not url.startswith("http://"):
        sys.stderr.write("Error: URL must start with 'http://'\n")
        sys.exit(1)

  url = url[len("http://"):]
  parts = url.split("/", 1)
  host_port = parts[0]
  path = "/" + parts[1] if len(parts) > 1 else "/"
  
  
  port = 80
  if ':' in host:
    host, port = host_port.split(":")
    if port.isdigit():
      port = int(port)
    else:
      sys.stderr.write("Error: invalid port\n")
      sys.exit(1)
  else:
    host = host_port
  return host, port, path


def send_http_request(host, port, path):
   try: 
          client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          client_socket.connect((host, port))


          request = f"GET {path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\n\r\n"
          client_socket.sendall(request.encode())

          response = b""
          while True:
            data = client_socket.recv(1024)
            if not data:
                break
            response += data

