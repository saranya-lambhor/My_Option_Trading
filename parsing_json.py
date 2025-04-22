import socket
import json

HOST = '127.0.0.1'  # localhost
PORT = 65432        # Any unused port

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[Main] Listening on {HOST}:{PORT}")

        conn, addr = s.accept()
        with conn:
            print(f"[Main] Connected by {addr}")
            buffer = ""
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                buffer += data.decode()

                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        json_data = json.loads(line.strip())
                        print("[Main] Received JSON:", json_data)
                    except json.JSONDecodeError:
                        print("[Main]  Invalid JSON:", line.strip())

if __name__ == "__main__":
    start_server()
