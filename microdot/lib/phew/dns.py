import uasyncio, usocket

async def _handler(socket, ip_address):
  print(f"[DNS] Starting handler for IP: {ip_address}")
  while True:
    try:
      yield uasyncio.core._io_queue.queue_read(socket)
      request, client = socket.recvfrom(256)
      print(f"[DNS] Received request from {client}")
      
      # Debug print first few bytes of request
      print(f"[DNS] Request bytes: {request[:16]}")
      
      response = request[:2] # request id
      response += b"\x81\x80" # response flags
      response += request[4:6] + request[4:6] # qd/an count
      response += b"\x00\x00\x00\x00" # ns/ar count
      response += request[12:] # origional request body
      response += b"\xC0\x0C" # pointer to domain name at byte 12
      response += b"\x00\x01\x00\x01" # type and class (A record / IN class)
      response += b"\x00\x00\x00\x3C" # time to live 60 seconds
      response += b"\x00\x04" # response length (4 bytes = 1 ipv4 address)
      response += bytes(map(int, ip_address.split("."))) # ip address parts
      
      print(f"[DNS] Sending response: {response[:16]}")
      socket.sendto(response, client)
      print(f"[DNS] Response sent to {client}")
    except Exception as e:
      print("[DNS] Error:", e)

def run_catchall(ip_address, port=53):
  print(f"> starting catch all dns server on {ip_address}:{port}")

  try:
    _socket = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
    print("[DNS] Socket created")
    
    _socket.setblocking(False)
    print("[DNS] Socket set to non-blocking")
    
    _socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
    print("[DNS] Socket options set")
    
    addr = usocket.getaddrinfo(ip_address, port, 0, usocket.SOCK_DGRAM)[0][-1]
    print(f"[DNS] Binding to {addr}")
    _socket.bind(addr)
    print("[DNS] Socket bound successfully")
    
    loop = uasyncio.get_event_loop()
    print("[DNS] Got event loop")
    
    loop.create_task(_handler(_socket, ip_address))
    print("[DNS] Handler task created")
    
    print("[DNS] Server started successfully")
  except Exception as e:
    print(f"[DNS] Server startup failed: {e}")
    if '_socket' in locals():
      _socket.close()
    raise 