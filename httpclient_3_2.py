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

    client_socket.close()
    return response     
       
def sp_response(response):         
      response_str = response.decode(errors='ignore')
      headers, body = response_str.split("\r\n\r\n", 1)
      status_line = headers.split("\r\n")[0]
      status_code = int(status_line.split()[1])
        
      header_dic ={}
      for header in headers.split("\r\n")[1:]:
          if ":" in header:
              key, value = header.split(':',1)
              header_dic[key.strip().lower()] = value.strip()
      return status_code, header_dic, body
      
      if status_code == 200:
          print("Success, 200 OK")
          sys.exit(0)
      
      if status_code >= 400:
          print("Error: Received HTTP", status_code)
          print(body)
          sys.exit(1)
          




if __name__=="__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: phthon {sys.argv[0]} http://example.com/page\n")
        sys.exit(1)

    

