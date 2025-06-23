import socket

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 4533       # Default rotctld port

# Initial dummy azimuth and elevation values
realAz = 180.0
realEl = 35.0

setAz = 0
setEl = 0

def handle_command(cmd):
    global azimuth, elevation
    cmd = cmd.strip()
    # Gpredict sends commands like "p" or "+p" to get position
    if cmd in ('p', '+p', 'get_pos'):
        # Respond with position in format: "P azimuth elevation\n"
        # Uppercase P indicates position response
        response = f" {realAz:.2f}\n {realEl:.2f}"
        print(f"Sent position: Az={realAz:.2f}, El={realEl:.2f}")
        return response.encode('ascii')
    elif cmd.startswith('set_pos') or cmd.startswith('+set_pos'):
        # Optionally handle setting position: e.g. "set_pos 123.4 56.7"
        parts = cmd.split()
        if len(parts) == 3:
            try:
                azimuth = float(parts[1])
                elevation = float(parts[2])
                print(f"Set position to Az={azimuth:.2f}, El={elevation:.2f}")
                return b"RPRT 0\n"  # Report success
            except ValueError:
                return b"RPRT 1\n"  # Report error
        else:
            return b"RPRT 1\n"
    elif cmd == 'q' or cmd == 'quit':
        # Client wants to quit
        return None
    else:
        # Unknown command
        return b"RPRT 0\n"  # Acknowledge with no error

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"rotctld dummy server listening on port {PORT}...")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break

                    cmd = data.decode('utf-8').strip()
                    #print(f"Received command: {cmd}")
                    resp = handle_command(cmd)
                    if cmd.startswith("P"):
                        setAz, setEl, = str(data.decode('utf-8').strip()[2:]).split()
                        print("Recieved position: Az="+ setAz +" El=" + setEl)

                    if resp is None:
                        print("Client requested to close connection")
                        break
                    conn.sendall(resp)

if __name__ == "__main__":
    main()
