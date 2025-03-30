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
    
