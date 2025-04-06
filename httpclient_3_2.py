import sys
import socket

#리다이렉트 최대 5번
MAX_REDIRECTS = 5

#url을 host port path 로 나눔
def send_request(url):
  #url 시작이 http://이 아니면 에러 뜨고 종료
  if not url.startswith("http://"):
        sys.stderr.write("Error: URL must start with 'http://'\n")
        sys.exit(1)
  # url 분리
  url = url[len("http://"):]
  parts = url.split("/", 1)
  host_port = parts[0]
  path = "/" + parts[1] if len(parts) > 1 else "/"
  
  # 기본 port 80이고 명시여부 처리
  port = 80
  if ':' in host_port:
    host, port = host_port.split(":")
    if port.isdigit():
      port = int(port)
    else:
      sys.stderr.write("Error: invalid port\n")
      sys.exit(1)
  else:
    host = host_port
  return host, port, path

# http 요청 응답 
def send_http_request(host, port, path):
    
   #소켓 생성 및 연결
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # http 요청 문자열 생성 및 전송
    request = f"GET {path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\n\r\n"
    client_socket.sendall(request.encode())
    # 응답
    response = b""
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        response += data

    client_socket.close()
    return response     

#http 응답을 status_code, header_dic, body으로 나눔
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
      
#url을 가져옴
def fetch(url):
    redirect_count = 0
    current_url = url

    while redirect_count <= MAX_REDIRECTS:
        host, port, path = send_request(current_url)
        response = send_http_request(host, port, path)
        status_code, headers, body = sp_response(response)
        

      # redirect 해결
        if status_code in (301, 302):
          redirect_url = headers.get("location")
          if not redirect_url:
             sys.stderr.write("Error: Https not supported.\n")
             sys.exit(1)
          sys.stderr.write(f"redirected to : {redirect_url}\n")

      
        if status_code >= 400:
          sys.stderr.write(f"Error: Received HTTP {status_code}\n")
          print(body)
          sys.exit(1)



    sys.stderr.write(f'Error: many redirects.\n')
    sys.exit(1)      

# url argv 변수 1에 저장 후 fetch 함수 부르기
if __name__=="__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: phthon {sys.argv[0]} http://example.com/page\n")
        sys.exit(1)
    url = sys.argv[1]
    fetch(url)
    

