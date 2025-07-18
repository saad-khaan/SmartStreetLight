import machine
import network
import usocket as socket
import utime as time
import math
import _thread
import json 

# Define the specific pins on the board.
ir_emitter_pin = machine.Pin(15, machine.Pin.OUT)
ir_receiver_pin = machine.ADC(26)
redLED_pin = machine.Pin(15, machine.Pin.OUT) #LED 1 pin
redLED_pin2 = machine.Pin(14, machine.Pin.OUT) #LED 2 pin
redLED_pin.value(0) #Automatically have the first LED off when the code is run
redLED_pin2.value(0) #Have the second LED off when code is run
redLED_status = "Off"
redLED2_status = "Off"
manual1_check = False
manual2_check = False
manual1_timestamp = None
manual2_timestamp = None
#red_LED_status makes the status of the LED off, this will be used later in the code.
#manual1_check is a flag system that is being used so that the manual override code does not interfere with the
#light sensor code.

voltage_in = 3.3
Ro = 10000
beta = 3933
temp_sensor = machine.ADC(4)

# Function to control the IR
def control_ir_receiver(status):
    if status == "on":
        ir_receiver_pin.on()
    elif status == "off":
        ir_receiver_pin.off()

#change status to on if the light is on, and off if light is off
def get_redLED_status():
    return "On" if redLED_pin.value() == 1 else "Off"

def get_redLED2_status():
    return "On" if redLED_pin2.value() == 1 else "Off"

# Function to check the ADC value and control the LED's based on a threshold
# Actuator code for turning on and off the LED lights based on the ambient light levels.
def check_adc_and_control_redLED():
    global redLED_status  # Declare redLED_status as global
    global redLED2_status
    adc = machine.ADC(26) #Define the light sensor
    while True:
        if not manual1_check and not manual2_check:
            #Use the flag tool, manual1_check and manual2_check should be false. This makes it that the lights don't turn on when the manual override is suppsoed to turn it off
            adc_value = adc.read_u16()
            print("ADC Value:", adc_value) #Print it for debugging

            if adc_value > 60000: # the threshold value must be tuned based on test environment. Ambient light also has IR rays. 
                #We are using 60000 for a sample threshold, this may be changed/
                print("Receiver/Transmitter blocked, turning on the red LED")
                redLED_pin.on()
                redLED_pin2.on()
                #If the adc value exceeds this threshold, the lights will turn on
            else:
                print("Receiver/Transmitter not blocked, turning off the red LED")
                redLED_pin.off()
                redLED_pin2.off()
                #If it is under the threshold value, the lights will turn off.
                #This means that in the dark, the lights are on, and when there is light the LEDs are off.

        redLED_status = get_redLED_status()  # Update redLED_status
        redLED2_status = get_redLED2_status()
        print("Light 1 Status:", redLED_status)
        print("Light 2 Status:", redLED2_status)
        time.sleep(1)
        
#Manual override for the LEDs
#Actuator code, turns on and off the LED if the button is clicked.
def manual_override1():
    global redLED_status  # Declare redLED_status as global
    global manual1_check
    redLED_pin.toggle() #toggles the light
    redLED_status = get_redLED_status()
    manual1_check = True #Changes the flagging system to true

def manual_override2():
    global manual2_check
    global redLED2_status
    redLED_pin2.toggle()
    redLED2_status = get_redLED2_status()
    manual2_check = True

#This function will read the temperature, and return it.
#Converts voltage to kelvin to celcius
def read_temp_room():
    adc = temp_sensor.read_u16()
    voltage_out = adc * (3.3 / 65535)
    resistance = Ro / ((voltage_in / voltage_out) - 1)
    tempK = beta / (math.log(resistance/Ro) + (beta / 298.15))
    tempC = tempK - 273.15
    final_temp = round(tempC, 2) - 31.02
    print(final_temp)
    return final_temp

def read_temp_system():
    adc = temp_sensor.read_u16()
    voltage_out = adc * (3.3 / 65535)
    resistance = Ro / ((voltage_in / voltage_out) - 1)
    tempK = beta / (math.log(resistance/Ro) + (beta / 298.15))
    tempC = tempK - 273.15
    final_temp = round(tempC, 2)
    print(final_temp)
    return final_temp


# Create a network connection
ssid = 'SaadKhan_Lighting'       #Set access point name 
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
    redLED2_status = get_redLED2_status()
    temperature = read_temp_room()
    system_temp = read_temp_system()

    if 50 <= system_temp <= 57.6:
        green_light = "#4CAF50"
        yellow_light = "#FFFFFF"
        red_light = "#FFFFFF"
    elif 57.7 < system_temp <= 60:
        green_light = "#FFFFFF"
        yellow_light = "FFEB3B"
        red_light = "#FFFFFF"
    elif 60 < system_temp:
        green_light = "#FFFFFF"
        yellow_light = "#FFFFFF"
        red_light = "#F44336"


    #User interface code, has javascript codes for wireless communication
    html = """<html><head>
    <title>Pico Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,">
   
    <title>Smart Lighting Dashboard</title>
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
            position: relative;
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
            position: fixed;
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
            background-color: #FFFFFF; //#4CAF50
            right: 20px;
        }

        .yellow_light {
            background-color: #FFFFFF; //#FFEB3B
            right: 90px;
        }

        .red_light {
            background-color: #FFFFFF; //#F44396
            right: 160px;
        }

        .alerts {
            margin-bottom: 10px;
        }

    </style>

    <script>

    //On click button for manual override 1 and 2.
        function manual_override1() {
            var xhr = new XMLHttpRequest();
            xhr.open("GET", "/?redLED_pin=on", true);
            xhr.send();
        }
        function manual_override2() {
            var xhr = new XMLHttpRequest();
            xhr.open("GET", "/?redLED2_pin=on", true);
            xhr.send();
        }

        function updateStatus() {
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var data = JSON.parse(xhr.responseText);
                    document.getElementById("RedLEDStatus").innerHTML = data.RedLEDStatus;
                    document.getElementById("RedLED2Status").innerHTML = data.RedLED2Status;
                    document.getElementById("Temperature").innerHTML = data.Temperature;
                    document.getElementById("SystemTemperature").innerHTML = data.SystemTemperature;

            var systemTemp = parseFloat(data.SystemTemperature);
            if(systemTemp >= 50 && systemTemp <= 57.6){
                document.querySelector(".green_light").style.backgroundColor = "#4CAF50"; // Green
                document.querySelector(".yellow_light").style.backgroundColor = "#FFFFFF"; // Off
                document.querySelector(".red_light").style.backgroundColor = "#FFFFFF"; // Off
            } else if(systemTemp > 57.6 && systemTemp < 60){
                document.querySelector(".green_light").style.backgroundColor = "#FFFFFF"; // Off
                document.querySelector(".yellow_light").style.backgroundColor = "#FFEB3B"; // Yellow
                document.querySelector(".red_light").style.backgroundColor = "#FFFFFF"; // Off
            } else {
                document.querySelector(".green_light").style.backgroundColor = "#FFFFFF"; // Off
                document.querySelector(".yellow_light").style.backgroundColor = "#FFFFFF"; // Off
                document.querySelector(".red_light").style.backgroundColor = "#F44336"; // Red
            }
        }
            };
            xhr.open("GET", "/status"x, true);
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
                <p>Lights 1 is: <strong id="RedLEDStatus">""" + redLED_status + """</strong></p>
                <p>Lights 2 is: <strong id="RedLED2Status">""" + redLED2_status + """</strong></p>
        </div>
<!-- Alerts section, to be implemented later in our design. -->
        <div class="alerts">
            <h3>Alerts</h3>>
            <p>Recorded Outside Temperature: <strong id="Temperature">--</strong> °C</p>
            <p>Recorded System Temperature: <strong id="SystemTemperature">--</strong> °C</p>
        </div>
    </div>
    <div class="override_position">
            <button id="manual-override" onclick="manual_override1()">Light 1 Manual Override</button>
            <button id="manual-override2" onclick="manual_override2()">Light 2 Manual Override</button>
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
        "RedLED2Status": redLED2_status,
        "Temperature": read_temp_room(),
        "SystemTemperature": read_temp_system(),
    }
    return json.dumps(status)

# Start the ADC monitoring function in a separate thread
_thread.start_new_thread(check_adc_and_control_redLED, ())

# Create a socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

#backend code
while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    if request:
        request = str(request)
        print('Content = %s' % request)
        led_on = request.find('/?redLED_pin=on') 
        led_off = request.find('/?redLED_pin=off')
        
        led2_on = request.find('/?redLED2_pin=on') #buzzer is the red LED
        led2_off = request.find('/?redLED2_pin=off')
        ir_emitter_on = request.find('/?ir_emitter_pin=on')
        ir_emitter_off = request.find('/?ir_emitter_pin=off')

    #if Ledon is on, then toggle
    if led_on > 0:
        manual_override1()
    elif led2_on > 0:
        manual_override2()

    if ir_emitter_on == 6:
        print('IR EMITTER ON')
        control_ir_emitter("on")
    elif ir_emitter_off == 6:
        print('IR EMITTER OFF')
        control_ir_emitter("off")

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


