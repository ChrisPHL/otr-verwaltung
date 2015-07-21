#!/bin/bash

cleanup() {
  EXIT_CODE=$?
  
  case $EXIT_CODE in
    0)
      trap - 0
      echo "Script ganz durchgelaufen. Wenn nicht etwas schief ging, sollte OTR Verwaltung++ jetzt per Menü startbar sein."
      ;;
    *)
      echo "Unbekannter Fehler. Sie müssen OTRV++ manuell installieren, falls sie das Script nicht gerade selbst abgebrochen haben."
      rm ~/Downloads/master.zip
      sudo apt-add-repository -y -r ppa:djcj/hybrid
      sudo apt-add-repository -y -r ppa:mc3man/gstffmpeg-keep
      sudo apt-add-repository -y -r ppa:mc3man/mplayer-test
      ;;
  esac
  echo bitte ENTER drücken, um das Script zu beenden; read;
  exit $EXIT_CODE
}

for sig in 0 1 2 3 6 14 15; do
  trap "cleanup $sig" $sig
done

# bei Fehler abbrechen
set -e
INSTALLDIR="Software"
source /etc/lsb-release

echo "Installscript OTRV++ für Ubuntu 14.04 Trusty"
echo ""
echo "Dieses Script ist nur für Ubuntu 14.04 und nicht für vorherige oder zukünftige Ubuntu Versionen oder Derivaten gedacht."
echo "Benutzung auf eigene Gefahr."
echo ""
echo "Das Script wird die zahlreichen Abhängigkeiten von OTR installieren und benötigt root Rechte zum Installieren."
echo "Auch wird das eine oder andere Paket eine Bestätigung der EULA benötigen."
echo "Dafür muss man den OK Button per Enter Taste bestätigen. Also keine Maus"
echo "Sollte beim Bestätigen nichts passieren, ist der OK Button nicht ausgewählt. Kommt manchmal vor. Dann per TAB Taste zuerst auswählen."  

# Paketliste updaten und Abhängigkeiten installieren
sudo apt-get -y update
sudo apt-get -y install python-glade2 python-libtorrent avidemux avidemux-cli avidemux-qt wine mediainfo-gui gstreamer0.10-gnonlin gstreamer0.10-plugins-ugly python-xdg python-gst0.10

# gstreamer0.10-ffmpeg aus PPA installieren und PPA wieder entfernen
sudo apt-add-repository -y ppa:mc3man/gstffmpeg-keep
sudo apt-get -y update
sudo apt-get -y install gstreamer0.10-ffmpeg
sudo apt-add-repository -y -r ppa:mc3man/gstffmpeg-keep

# mplayer aus PPA installieren und PPA wieder entfernen
if [ "$DISTRIB_RELEASE" == "14.04" ]
  then
    sudo apt-add-repository -y ppa:mc3man/mplayer-test
    sudo apt-get -y update
    sudo apt-get -y install mplayer
    sudo apt-add-repository -y -r ppa:mc3man/mplayer-test
  elif [ "$DISTRIB_RELEASE" == "14.10" ]
    then
    sudo apt-add-repository -y ppa:mc3man/mplayer-test
    sudo apt-get -y update
    sudo apt-get -y install mplayer
    sudo apt-add-repository -y -r ppa:mc3man/mplayer-test
  elif [ "$DISTRIB_RELEASE" == "15.04" ]
    then
    sudo apt-add-repository -y ppa:djcj/hybrid
    sudo apt-get -y update
    sudo apt-get -y install mplayer
    sudo apt-add-repository -y -r ppa:djcj/hybrid
  else
    echo "Für diese Ubuntu Version konnte keine geeignete mplayer Version gefunden werden."
    echo "OTRV++ bitte manuell installieren."
    exit -1
fi


# otrv++ laden
wget -P ~/Downloads https://github.com/monarc99/otr-verwaltung/archive/master.zip

# und entpacken
mkdir -p ~/"$INSTALLDIR"
unzip -uod ~/"$INSTALLDIR" ~/Downloads/master.zip
rm ~/Downloads/master.zip

# Menü Eintrag erstellen
mkdir -p ~/.local/share/applications/
sed -e "/Icon=/d" ~/"$INSTALLDIR"/otr-verwaltung-master/otrverwaltung.desktop.in > ~/.local/share/applications/otrverwaltung.desktop
echo Icon=$(eval echo ~)/"$INSTALLDIR"/otr-verwaltung-master/data/media/icon.png >> ~/.local/share/applications/otrverwaltung.desktop

# Link auf otrverwaltung setzen

sudo ln -sf $(eval echo ~)/"$INSTALLDIR"/otr-verwaltung-master/bin/otrverwaltung /usr/local/bin/otrverwaltung
