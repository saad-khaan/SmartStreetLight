import machine
import network
import usocket as socket
import utime as time
import _thread
import json 

# Define the IR emitter and Red LED (in this code Red LED is sometimes called as buzzer) pins
ir_emitter_pin = machine.Pin(15, machine.Pin.OUT)
redLED_pin = machine.Pin(14, machine.Pin.OUT)
redLED_status = "Off"
temp_pin = machine.ADC(4)

# Function to control the IR emitter
def control_ir_emitter(status):
    if status == "on":
        ir_emitter_pin.on()
    elif status == "off":
        ir_emitter_pin.off()

# Function to get the buzzer status
def get_redLED_status():
    return "On" if redLED_pin.value() == 1 else "Off"

def toggle_manual():
    global get_redLED_status
    if redLED_pin.value() == 0:
        redLED_pin.value(1)
        redLED_status == "on"
    else: 
        redLED_pin.value(0)
        redLED_status == "off"

def get_temp():
    reading = temp_pin.read_u16()
    temperature = 27 - (reading - 0.706)/0.001721 #Converts voltage reading to Celcius
    return temperature 

import math

def thermistorTemp(Vout):

    # Voltage Divider
    Vin = 3.3
    Ro = 10000  # 10k Resistor

    # Steinhart Constants
    A = 0.001129148
    B = 0.000234125
    C = 0.0000000876741

    # Calculate Resistance
    Rt = (Vout * Ro) / (Vin - Vout) 
    
    # Steinhart - Hart Equation
    TempK = 1 / (A + (B * math.log(Rt)) + C * math.pow(math.log(Rt), 3))

    # Convert from Kelvin to Celsius
    TempC = TempK - 273.15

    return TempC

# Function to periodically check the ADC value and control the redLED
def check_adc_and_control_redLED():
    global redLED_status  # Declare redLED_status as global
    adc = machine.ADC(26) 
    while True:
        adc_value = adc.read_u16()
        print("ADC Value:", adc_value)

        if adc_value > 25000: # the threshold value must be tuned based on test environment. Ambient light also has IR rays. 
            print("Receiver/Transmitter blocked, turning on the red LED")
            redLED_pin.on()
        else:
            print("Receiver/Transmitter not blocked, turning off the red LED")
            redLED_pin.off()

        redLED_status = get_redLED_status()  # Update redLED_status
        print("Red LED Status:", redLED_status)
        time.sleep(1)


# Create a network connection
ssid = 'Smart Street Light'       #Set access point name 
password = 'saadkhan'      #Set your access point password
ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password)
ap.active(True)            #activating

while ap.active() == False:
  pass
print('Connection is successful')
print(ap.ifconfig())

# Define HTTP response
def web_page():
    ir_emitter_status = get_ir_emitter_status()
    redLED_status = get_redLED_status()
    ir_emitter_color = "purple" if ir_emitter_status == "ON" else "black"
    buzzer_color = "red" if redLED_status == "On" else "gray"
    
    html = """<html><head>
    <title>Smart Lighting Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,">

    <style>
      /* 
            Styling for the main body section of the user interface, choosing the font Arial, the flexbox layout and the background
        */
        body {
            font-family: Arial, sans-serif; /* Choosing arial */
            display: flex; /* The flexbot layout creates the giant box in the middle which is our main UI interface */
            align-items: center; /* All items that will be later created will be aligned in the center*/
            justify-content: center;
            background-color: #f0f0f0;
        }


        /* 
            Dashboard container which uses elements such as width, margin, padding to design the dashboard
        */
        .dashboard {
            width: 80%; 
            max-width: 1000px; 
            margin: 40px;
            padding: 40px; 
            border: 2px solid #ffffff;
            border-radius: 10px;
            background-color: #ffffff;
        }

        /*
            Header div, using the same flex box layout, spacing equally and aligning in the center.
        */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
        }

        /*
            All h2 and h3 style headers will have this set font size.
        */
        h2, h3 {
            font-size: 24px; 
        }

        /*
           All paragraphs will have this set font size.
        */
        p {
            font-size: 20px;
        }

        /*
            Manual override button, sets the padding, font size, border radius.
        */
        .manual-override {
            padding: 20px 40px; /* Increased padding for a larger button */
            font-size: 24px; /* Larger font size for better visibility */
            border-radius: 8px;
            cursor: pointer;
            outline: none;
        }

        /*
            Sets the position for the manual override button, flexbox layout, and the position so it is set to the bottom right corner of the interface.
        */
        .override_position {
            display: flex;
            justify-content: flex-end; /* Align child elements (the button) to the right */
            position: absolute;
            bottom: 0; /* Adjusted to 0 to stick to the bottom */
            right: 0; /* Adjusted to 0 to stick to the right */
            width: 100%; /* Ensures the container stretches across the parent width */
            padding: 20px; /* Adds some space inside the container, moving the button a bit inward from the corner */
        }

        /*
            Sets the container for the status indicatior section, including the three lights.
        */
        .status-indicator {
            display: flex;
            justify-content: space-evenly;
            position: absolute;
            right: 20px;
            top: 20px;
        }

        /*
            Styling for the lights position, and the lights color, green, yellow, and red.
        */
        .status-indicator div {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin-left: 10px;
        }
        
        .green_light {
            background-color: #4CAF50;
            right: 20px;
        }

        .yellow_light {
            background-color: #FFEB3B;
            right: 90px;
        }

        .red_light {
            background-color: #F44396;
            right: 160px;
        }

        .alerts {
            margin-bottom: 10px;
        }

    </style>

    <script>
        function toggleManual() {
            window.location = '/toggle-manual';
        }

        function updateTemperature() {
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var data = JSON.parse(xhr.responseText);
                    document.getElementById("temperature-value").innerHTML = data.temperature.toFixed(2);
                }
            };
            xhr.open("GET", "/temperature", true);
            xhr.send();
        }
        setInterval(updateTemperature, 2000);

        function updateStatus() {
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var data = JSON.parse(xhr.responseText);
                    document.getElementById("irEmitterStatus").innerHTML = data.irEmitterStatus;
                    var irEmitterColor = data.irEmitterStatus === "ON" ? "purple" : "black";
                    document.getElementById("irEmitterIndicator").style.backgroundColor = irEmitterColor;
                    document.getElementById("RedLEDStatus").innerHTML = data.RedLEDStatus;
                    var buzzerColor = data.RedLEDStatus === "On" ? "red" : "gray";
                    document.getElementById("buzzerIndicator").style.backgroundColor = buzzerColor;
                }
            };
            xhr.open("GET", "/status", true);
            xhr.send();
        }
        setInterval(updateStatus, 1000); // Refresh every 1 second
    </script>
    </head>


<body>
    <div class="dashboard">
        <div class="header">
            <h2>Dashboard</h2>
            <div class="status-indicator">
                <div class="green_light"></div>
                <div class="yellow_light"></div>
                <div class="red_light"></div>
        </div>
    </div>

<!-- Status container, including activity and manual override button-->
    <div class="status">
        <div class="activity">
            <h2>Status:</h2>
            <p>Lights are: <strong id="RedLEDStatus">""" + redLED_status + """</strong><div class="circle" id="buzzerIndicator" style="background-color: """ + buzzer_color + """;"></div></p>
            <div class="override_position">
                <button onclick="toggleManual()" class="manual-override">Manual Override</button>

            </div>
        </div>

<!-- Alerts section, to be implemented later in our design. -->
        <div class="alerts">
            <h3>Alerts</h3>>
            <p>Temperature: <span id="temperature-value">--</span> °C</p>
        </div>
    </div>
</body>
    </html>"""
    return html

# Function to get the IR emitter status
def get_ir_emitter_status():
    return "ON" if ir_emitter_pin.value() == 1 else "OFF"

def get_status():
    status = {
        "irEmitterStatus": get_ir_emitter_status(),
        "RedLEDStatus": redLED_status,
    }
    return json.dumps(status)

# Start the ADC monitoring function in a separate thread
_thread.start_new_thread(check_adc_and_control_redLED, ())

# Create a socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #this is socket server s
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept() #Opens a connection conn from socket server s
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024) #reads request from conn at 1024 bytes, request from html webpage to server
    if request: 
        request = str(request) #converts request to data structure of type string
        print('Content = %s' % request)
        buzzer_on = request.find('/?redLED_pin=on') #buzzer is the red LED
        buzzer_off = request.find('/?redLED_pin=off') 
        ir_emitter_on = request.find('/?ir_emitter_pin=on')
        ir_emitter_off = request.find('/?ir_emitter_pin=off')

    if buzzer_on == 6:
        print('BUZZER ON')
        redLED_pin.value(1) #light turns on 
    elif buzzer_off == 6:
        print('BUZZER OFF')
        redLED_pin.value(0) #light turns off

    if ir_emitter_on == 6:
        print('IR EMITTER ON')
        control_ir_emitter("on") #emitter turns on
    elif ir_emitter_off == 6:
        print('IR EMITTER OFF')
        control_ir_emitter("off") #emitter turns off
        
    if '/toggle_manual' in request:
        toggle_manual()
        response = web_page() # Update the page to reflect the new state

    if '/temperature' in request:
        temperature = get_temp()
        response = json.dumps({"temperature": temperature})

    if request.find("/status") == 6:
        response = get_status()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: application/json\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)
    else:
        response = web_page()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)
    conn.close()

