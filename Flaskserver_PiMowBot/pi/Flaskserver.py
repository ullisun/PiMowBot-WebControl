#from flask import Flask, jsonify

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import threading
import subprocess
import time
#import json
from gpiozero import LED
#from pathlib import Path
import logging
import socket
#import fcntl

# CUTTER ist das Messer Motor Relais und hängt an GPIO 5
# DRIVER ist das Antriebsrelais und hängt an GPIO 6
# Damit sein Status gelesen werden kann wird die Variable CUTTER und DRIVER
# Hier initialisiert der Ausgang wird hier sofort wieder auf HIGH da der PiMowBot
# Low Active arbeitet

DRIVER=LED(6)
DRIVER.on()
CUTTER=LED(5)
CUTTER.on()
app = Flask(__name__)

CORS(app) # Dies erlaubt Anfragen von allen Quellen (*)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app.logger.disabled = True

motor_Val=0

DEBUG=False

# Diese Daten werden an die Webseite übertragen
class daten:
    l_dist=155
    r_dist=155
    battery=11
    wifi=00
    mow=False
    heading=360
    oldheading=360
class relais:
    drive=False
    driveSetTime=None

data=daten()
rel=relais()    


# Hilfs Funktionen die die Motordateien mit Werten versorgen
# diese Funktionen werden vom Joystick aufgerufen 

def Go_L(val):
    with open ("/dev/shm/.PiMowBot_Motor.left","w") as f:
        f.write(str(val))
def Go_R(val):
    with open ("/dev/shm/.PiMowBot_Motor.right","w") as f:
        f.write(str(val))

def STOP():
    #------- Messerrelais wird ausgeschaltet ------------
    CUTTER.on()
    #------- Antriebsrelais wird ausgeschaltet ------------
    DRIVER.ON()

# =========================================================
# Diese Funktion ermittelt die WiFi Signalstärke 
# =========================================================

def get_wifi_signal_strength():
    try:
        result = subprocess.check_output(["iw", "dev", "wlan0", "link"], text=True)
        for line in result.split("\n"):
            if "signal:" in line:
                parts = line.strip().split()
                # Beispiel: ["signal:", "-48", "dBm"]
                data.wifi= f"{int(parts[1])} dBm"
                return
                #return f"{int(parts[1])} dBm"
        return None
    except Exception as e:
        return None

# =========================================================
# Diese Funktion ermittelt die WiFi Signalstärke 
# =========================================================

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Ermittelt die IP der verwendeten Netzwerkschnittstelle
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()

    return ip


# =========================================================
# Hier werden alle Info Daten aus dem /dev/shm ausgelesen
# und in der variablen data gespeichert 
# =========================================================


def read_data():
    # Daten die übermittelt werden
    #{"Battery": 14.6, "WLAN": "-49 dBm","Blade": False, 
    #"kurs": "231", "ToF_l": "84", "ToF_r": "85"}
    
    try:    
       get_wifi_signal_strength()
    except:
       data.wifi = "-- dBm"
    
    if CUTTER.value==0:
        data.mow=True
    else:
        data.mow=False
    try:
        with open("/dev/shm/.PiMowBot.battery","r") as f:
            content=f.read().strip()
        if content:
            data.battery=round(float(content.split(";")[1]),2)
            # diese Zeile legt fest, dass der 2. Teile des Inhaltes von der
            # /dev/shm/.PiMowBot.battery" gesendet wird, wird der erste oder 3 dritte
            # teil des Inhaltes gewünscht, dann kann das über das verändern von 
            # content.split(";")[1]) nach content.split(";")[0]) oder content.split(";")[2])
            # erzielt werden.

       
    except:
        data.battery="--"
    
    try:
        with open("/dev/shm/.PiMowBot.heading","r") as f:
            cnt=f.read().strip()
        data.heading=cnt
        data.oldheading=data.heading    
    except:
        data.heading=data.oldheading        
    
    try:
        with open("/dev/shm/.PiMowBot_left.distance","r") as f:
            cnt=f.read().strip()
        data.l_dist=cnt    
    except:
        data.l_dist= "--"
    try:
        with open("/dev/shm/.PiMowBot_right.distance","r") as f:
            cnt=f.read().strip()
        data.r_dist=cnt    
    except:
        data.r_dist= "--"

    if DEBUG: 
        print(f"Lese diese Daten: 'Battery':{data.battery}, 'WLAN': {data.wifi},'Blade':{data.mow}, 'kurs':{data.heading},'ToF_l':{data.l_dist},'ToF_r':{data.r_dist}")

# =========================================================
# Hier wird der Status des Messer Relais ermittelt
# =========================================================


def getBladeStatus():
    status = {"Mower":CUTTER.value}
    print(f"Bei Onload der Seite {status}")
    return status

def getDriverStatus():
    if DRIVER.value ==0:
        rel.drive=True
    else:
        rel.drive=False




def angle_to_motor_values(angle):
    """
    Wandelt Winkelbereich 270°..360°..90°
    in Motorwerte X/Y von -100..100 um.
    """
    angle = angle % 360  # Sicherheit

    # Nur gültiger Bereich erlaubt
    if not (angle >= 270 or angle <= 90):
        raise ValueError("Winkel muss zwischen 270° und 90° liegen.")

    # Bereich 270..360 -> -100..0
    if angle >= 270:
        x = (angle - 270) / 90 * 100 - 100

    # Bereich 0..90 -> 0..100
    else:
        x = angle / 90 * 100

    y = -x

    return round(x, 2), round(y, 2)

@app.route("/api/onload")
def onload():
    
    data=getBladeStatus()
    return jsonify(data)


@app.route("/api/status")
def status():
    try:
        send_data = {
               "Battery":data.battery, 
               "WLAN": data.wifi, 
               "Blade":data.mow, 
               "kurs":data.heading, 
               "ToF_l":data.l_dist,
               "ToF_r":data.r_dist
        }
        
        if DEBUG:
            print(f"Sende diese Daten {send_data}")
        return jsonify(send_data)

    except:
        print("Error")
        return {"error": "no data"}, 500


@app.route("/api/control", methods=["POST"])
def control():
    data = request.get_json()
    #print(f"Control-Data={data}")
    cmd = data.get("cmd", 0)
    action = data.get("value", 0)
    #print(f"Control-Data={data}")
    if cmd=="MOWER" and action =="ON":
        CUTTER.off()
        #print(f"Cutter on= {CUTTER.value}")
    if cmd=="MOWER" and action =="OFF":
        CUTTER.on()
        #print(f"Cutter off= {CUTTER.value}")
    if cmd=="NOTAUS" and action =="True":
        CUTTER.on()
        DRIVER.on()
        Go_L(0)
        Go_R(0)
        STOP()
        #print("==================== NOTAUS WAS PRESSED =====================")
    if cmd=="SHUTDOWN" and action =="True":

        print("Hier soll der shutdown ausgeführt werden")
        os.system("sudo shutdown -h now")

    if cmd=="AUTO_MODE" and action =="ON":
        print("Paltzhalter zur Aktivierung eines Services")
        #subprocess.run(["sudo", "systemctl", "start", "rtk.service"])
        #print(f"Result={result}")
 
    if cmd=="AUTO_MODE" and action =="OFF":    
        print("Paltzhalter zur Deaktivierung eines Services")
        #subprocess.run(["sudo", "systemctl", "stop", "rtk.service"])
    


    return {"ok": True}



# ========================================================
#     Hie werden die Daten vom Joystick verarbeitet
# ========================================================

@app.route("/api/joystick", methods=["POST"])
def joystick():
    global motor_Val
    data = request.get_json()
    #print(f"Data={data}")
    x = data.get("x", 0)
    y = data.get("y", 0)

    #print("Joystick:", x, y)

    # Beispiel Mapping:
    left = y - x
    right = y + x

    # Begrenzen
    left = max(-1, min(1, left))
    right = max(-1, min(1, right))
    motor_Val = abs(left*100)+abs(right*100)
    #getDriverStatus()
    if rel.drive ==False:
        DRIVER.off()
        rel.drive=True
        rel.driveSetTime=time.time()
    Go_L(-left*100)
    Go_R(-right*100)
    
    return {"ok": True}


@app.route("/api/turn", methods=["POST"])
def turn():
    global motor_Val
    data = request.get_json()
    #print(f"Data={data}")
    angle = data.get("angle", 0)
    #angle = max(270, min(angle, 90))
    #print(f"Arc:  {angle:.0f}")
    left, right = angle_to_motor_values(angle)
    #print(f"Links: {left}, Rechts:{right}")
    # Begrenzen
    #left = max(-100, min(100, left))
    #right = max(-100, min(100, right))
    motor_Val = abs(left)+abs(right)
    #getDriverStatus()
    if rel.drive ==False:
        DRIVER.off()
        rel.drive=True
        rel.driveSetTime=time.time()
    Go_L(left)
    Go_R(right)
    return {"ok": True}


# ========================================================
#     Server starten
# ========================================================

def run_server():
    app.run(host="0.0.0.0", port=5005, threaded=True)

# ========================================================
#     Hier das eigentlich Hauptprogramm
# ========================================================
print(f"\nFlaskserver erreichbar unter:")
print(f"http://{get_ip_address()}:5005\n")


threading.Thread(target=run_server, daemon=True).start()

while True:
    read_data()
    #----------- hier wird nach 20 Sekunden ohne Fahrbefehl
    #----------- das Antriebsrelais wieder abgeschaltet.
    if rel.driveSetTime:
        if time.time()- float(rel.driveSetTime) > 20:
            DRIVER.on()
            rel.drive=False
    time.sleep(0.5)
