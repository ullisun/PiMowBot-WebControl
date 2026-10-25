# PiMowBot-WebControl
This is an addon for the @TGD PiMowBot LawnMower

Das ist die von mir und ChatGPT erstellte Webseite. Ich habe sie  auf meinem Heimserver abgelegt und rufe sie dann entweder vom Notebook oder was meistens der Fall ist vom Handy auf. Wenn alles auf dem PiMowBot richtig installiert ist, lässt sich der PiMowBot über die Kompassrose in der Mitte Steuern. Mit dem Punkt auf dem Halbkreis um die Kompassrose herum kann man den PiMowbot dann auf der Stelle drehen lassen.
1. Flaskserver Installation
Für den Betrieb der Seite sind auf dem PiMowbot  zwei zusätzliche Bibliotheken erforderlich: Flask sowie flask_cors Die Installation habe ich bei mir durchgeführt nachdem ich ein sudo apt-get update und sudo apt-get upgrade durchgeführt habe. Auch ist eine aktuelle pip Version hilfreich. Da ich auf meinem MINI-PiMowBot noch eine alte pip Version hatte gab es da noch Probleme aber mit 
python3 -m pip install pi --upgrade pip konnte ich das dann auch lösen. Danach habe ich 
pip install Flask sowie
pip install flask_cors installiert.
