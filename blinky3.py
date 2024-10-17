import machine
import time
import socket
import network

class LED:
    def __init__(self, pin_name):
        self.led = machine.Pin(pin_name, machine.Pin.OUT)

    def turn_on(self):
        self.led.value(1)

    def turn_off(self):
        self.led.value(0)
    
    def get_state(self):
        return "on" if self.led.value() == 1 else "off"
    
class Wifi:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wifi = network.WLAN(network.STA_IF)
        self.wifi.active(True)
        self.wifi.disconnect()

    def connect(self):
        self.wifi.connect(self.ssid, self.password)
        while not self.wifi.isconnected():
            time.sleep(1)
            print("connecting...")
        print("connected")
        print(self.wifi.ifconfig())

class website:
    def __init__(self, led_con):
        self.led_con = led_con
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("", 80))
        self.server_socket.listen(5)
    
    def web_page(self):
        gpio_state = self.led_con.get_state()
        html = f"""
        <html>
            <head>
                <title>Pico W Web Server</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link rel="icon" href="data:,">
                <style>
                    html{{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}}
                    h1{{color: #0F3376; padding: 2vh;}}
                    p{{font-size: 1.5rem;}}
                    button{{display: inline-block; background-color: #4286f4; border: none; border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}}
                    button2{{background-color: #4286f4;}}
                </style>
            </head>
            <body>
                <h1>Pico W Web Server</h1>
                <p>GPIO state: <strong>{gpio_state}</strong></p>
                <p><a href="/?led=on"><button class="button">ON</button></a></p>
                <p><a href="/?led=off"><button class="button button2">OFF</button></a></p>
            </body>
        </html>
        """
        return html
    
    def handle_request(self):
        conn,addr = self.server_socket.accept()
        request = conn.recv(1024).decode()
        print("request", request)
        if "/?led=on" in request:
            self.led_con.turn_on()
        elif "/?led=off" in request:
            self.led_con.turn_off()
        response = self.web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()

ssid = "ssid "                #ersätt med wifinamn
password = "password "        #ersätt med wifilösenord

wifi_con = Wifi(ssid, password)
wifi_con.connect()
led_con = LED("LED")
web_server = website(led_con)

try:
    while True:
        web_server.handle_request()
except Exception as e:
    print("Exception -", e)
    web_server.server_socket.close()