#!/bin/sh

name='otr-verwaltung';
version='0.4';

rm $name-$version.orig.tar.gz
rm -r $name-$version

mv src "$name-$version";
tar czvf $name-$version.orig.tar.gz $name-$version --exclude=*.pyc --exclude=.svn --exclude=.* --exclude=*~ --exclude=screenshots --exclude=log --exclude=conf;
mv "$name-$version" src;

tar -xf $name-$version.orig.tar.gz;

cd $name-$version

cat > README << EOF
####################################################################   
OTR-Verwaltung $version
Copyright (C) 2008 Benjamin Elbers (elbersb@googlemail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
####################################################################
EOF

dh_make -e elbersb@gmail.com
rm ../$name-$version.orig.tar.gz

cd debian
rm *.ex *.EX README.Debian

# Fill files

cat > control << EOF
Source: otr-verwaltung
Section: misc
Priority: optional
Maintainer: Benjamin Elbers <elbersb@gmail.com>
Build-Depends: debhelper (>= 7)
Standards-Version: 3.7.3
Homepage: <insert the upstream URL, if relevant>

Package: otr-verwaltung
Architecture: all
Depends: python, python-gtk2
Description: Manages otrkeys and avis from onlinetvrecorder.com
 Manages otrkeys and avis from onlinetvrecorder.com
 Feature list:
    - Decode otrkey files
    - Cut avi files with avidemux by cutlists
    - Organize your files by undecoded, decoded, cut, ...
    - Keep track of files you want to download later
EOF

cp ../../rules rules

cat > dirs << EOF
/usr/bin
/usr/share/applications
/usr/share/icons
EOF

cat > copyright << EOF
This package was debianized by benjamin <elbersb@gmail.com> on
Wed, 31 Dec 2008 18:07:07 +0100.

Upstream Author(s):

    Benjamin Elbers <elbersb@gmail.com>

Copyright:

    Copyright (C) 2008 Benjamin Elbers
    
License:

    GPL v3

The Debian packaging is (C) 2008, benjamin <elbersb@gmail.com> and
is licensed under the GPL, see /usr/share/common-licenses/GPL.
EOF

cd ..

cat >> otr-verwaltung.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
Name=OTR-Verwaltung
Exec=otrverwaltung
Icon=/usr/share/icons/hicolor/48x48/apps/otrverwaltung.png
Comment=Verwalten von otrkey- und avi-Dateien von onlinetvrecorder.com
Type=Application
Categories=AudioVideo;
EOF

dpkg-buildpackage   

cd ..
rm -r $name-$version
