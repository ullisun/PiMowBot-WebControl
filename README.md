# PiMowBot-WebControl
__This is an addon for the [TGD PiMowBot](https://github.com/TGD-Consulting) LawnMower__ 
<table>
  <tr>
    <td width="60%" valign="top">
     Das ist die von mir und ChatGPT erstellte Webseite. Ich habe sie auf meinem Heimserver abgelegt und rufe sie dann entweder vom Notebook oder was meistens der Fall ist vom Handy auf. Wenn alles auf dem PiMowBot richtig installiert ist, lässt sich der PiMowBot über die Kompassrose in der Mitte Steuern. Mit dem Punkt auf dem Halbkreis um die Kompassrose herum kann man den PiMowbot dann auf der Stelle drehen lassen.
    </td>
    <td width="40%" valign="top" align="center">
    <img width="200" height="375" alt="grafik" src="https://github.com/user-attachments/assets/4255f3b7-f5c8-4448-bddc-f7af773db0b7" />
    </td>
  </tr>
  
</table>


__1. Flaskserver Installation__

Für den Betrieb der Seite sind auf dem PiMowbot  zwei zusätzliche Bibliotheken erforderlich: Flask sowie flask_cors Die Installation habe ich bei mir durchgeführt nachdem ich ein sudo apt-get update und sudo apt-get upgrade durchgeführt habe. Auch ist eine aktuelle pip Version hilfreich. Da ich auf meinem MINI-PiMowBot noch eine alte pip Version hatte gab es da noch Probleme aber mit 
`python3 -m pip install pi --upgrade pip` konnte ich das dann auch lösen. Danach habe ich `pip install Flask` 

sowie 
`install flask_cors` 
installiert.

Das Script Flaskserver.py habe ich bei meinem MINI- PiMowBot außerhalb des pimowbot Verzeichnisses abgelegt. Dazu habe ich das Verzeichnis /home/pi/Mower/Flaskserver angelegt und in das Verzeichnis Flaskserver das Flaskserver.py Script hinein kopiert. Wenn python Flaskserver.py dann aus diesem Verzeichnis aufgerufen wird, sollte im Ausgabefenster folgendes sichtbar werden. <img width="470" height="131" alt="grafik" src="https://github.com/user-attachments/assets/7a1b5fad-dd4a-4caf-893e-fb3eec5e3bb6" />

Ist das der Fall, dann war schon mal alles auf dem Pi erfolgreich.
Damit später auch beim Start vom PiMoBot der Flaskserver gestartet wird, kann man einen Service einrichten. Das beschreibe ich später. Jetzt kümmern wir uns um die html Seite, dazu ist die ausgegebene IP Adresse noch wichtig.

__2. HTML Seite installieren__

Auf meinem Linux Rechner den ich meistens Nutze habe ich ein Apache2 Webserver laufen. Auf die Installation von Apache falls erforderlich gehe ich nicht weiter ein, dazu gibt es viele Anleitungen im Netz. Ich persönlich würde nicht Apache auf dem PiZero im PiMowBot installieren, der PiZero hat mit dem Rebol Webserver und den anderen PiMowBot Scripten schon genügend Auslastung. Ich habe aber auf einem PiZero 2W Nginx als Webserver installiert, das klappte mit meinen diversen Seiten dann auch sehr gut und war sehr flüssig. Auch hierzu gibt es viele Anleitungen. Wichtig, dass die Zugriffsrechte richtig eingestellt sind, damit man an den Dateien auch noch was ändern kann. Gehen wir mal davon aus, dass alles richtig installiert wurde und es gibt jetzt ein Verzeichnis /var/www/html/remote/ welches der Webserver erreicht. In dieses Verzeichnis muss nun die Datei Mobile.html und rose.png hinein kopiert werden. Im Quellcode der Mobile.html nach dem Eintrag const PI_IP = "192.168.178.60"; // ggf anpassen! 
suchen und den so anpassen, dass er die IP Adresse des PiMowBots hat. Das wäre alles.
Nun solltest Du die Webseite durch eingabe IP Adresse Deines Server und /remote/Mobile.html aufrufen können. Dann sollte die Seite sichtbar sein.

__3. Service für den Flaskserver einrichten__

Ist es gewünscht dass der Flaskserver automatisch nach dem starten des Pi’s sich aktiviert, dann lässt sich das über die Einrichtung eines Services erzielen.
Hier ein Vorschlag für den Service
mit Eingabe von sudo nano  /etc/systemd/system/Flaskserver.service erzeugt nano eine neue Servicedatei. Kopiere diesen Inhalt in den Editor

```bash
[Unit]
Description=MowerFlaskserver
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/home/pi/Mower/Flaskserver
ExecStart=/usr/bin/python /home/pi/Mower/Flaskserver/Flaskserver.py
User=pi
Restart=always
RestartSec=2
StandardOutput=append:/home/pi/Mower/Flaskserver/Flaskserver.log
StandardError=append:/home/pi/Mower/Flaskserver/Flaskserver.log
SyslogIdentifier=Flaskserver

[Install]
WantedBy=multi-user.target
```
Danach mit strg+s speichern und mit strg+x beenden.
Ich persönlich teste dann immer erst den Service bevor ich ihn automatisiert starten lasse. Das Script Flaskserver.py darf jetzt nicht laufen.
Nun mir dem Aufruf `sudo systemctl start Flaskserver.service` dem Service starten.
Ist die html Seite geöffnet erscheint nach wenigen Sekunden „Verbunden“ über dem Not-Aus Button. Also dann ist alles richtig eingerichtet.
Zur Kontrolle noch ein sudo systemctl status Flaskserver.service dieses sollte folgendes ausgeben

<img width="792" height="208" alt="grafik" src="https://github.com/user-attachments/assets/69991724-c457-46c3-88e3-bcf1dee1e786" />

Das grüne Active (running) zeigt, dass alles richtig eingerichtet wurde.
Mit einem `sudo systemctl enable Flaskserver.service wird veranlasst, dass dieser Service nach jedem booten wieder aufgerufen wird.

Eine vollständige [Anleitung](https://github.com/ullisun/PiMowBot-WebControl/blob/main/Flaskserver_PiMowBot/Readme.pdf) findet ihr hier

Viel Erfolg und viel Freude!
