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
  host = parts[0]
  pat
