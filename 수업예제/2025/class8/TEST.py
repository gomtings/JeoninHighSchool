import socket
try:
    sock = socket.create_connection(("Solimatics.iptime.org", 53200), timeout=50)
    print("✅ 서버 응답 확인됨!")
    sock.close()
except Exception as e:
    print(f"❌ 서버 응답 없음: {e}")