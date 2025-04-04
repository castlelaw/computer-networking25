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
            
        response_str = response.decode(errors='ignore')
        headers, body = response_str.split("\r\n\r\n", 1)
        status_line = headers.split("\r\n")[0]
        status_code = int(status_line.split()[1])
        
        print(f"Status: {status_code}")
        
        if status_code == 200:
            print("Success, 200 OK")
            sys.exit(0)
        
        if status_code >= 400:
            print("Error: Received HTTP", status_code)
            print(body)
            sys.exit(1)
          

def http_headers(header_str):
    headers = {}
    line = header_str.split("\r\n")
    for dic in line[1:]:
        if ':' in dic:
            key, value = dic.split(':', 1)
            headers[key.strip().lower()] = value.strip()
    return headers

