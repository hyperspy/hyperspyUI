#!/bin/bash

APP="hyperspyui"
EXTENSIONS="hdf5 msa"
COMMENT="HyperSpy document"
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Install icons
xdg-icon-resource install --context mimetypes --size 256 "$DIR/images/icon/hyperspy256.png" x-application-$APP
xdg-icon-resource install --context mimetypes --size 128 "$DIR/images/icon/hyperspy128.png" x-application-$APP
xdg-icon-resource install --context mimetypes --size 64 "$DIR/images/icon/hyperspy64.png" x-application-$APP
xdg-icon-resource install --context mimetypes --size 48 "$DIR/images/icon/hyperspy48.png" x-application-$APP
xdg-icon-resource install --context mimetypes --size 32 "$DIR/images/icon/hyperspy32.png" x-application-$APP
xdg-icon-resource install --context mimetypes --size 22 "$DIR/images/icon/hyperspy22.png" x-application-$APP
xdg-icon-resource install --context mimetypes --size 16 "$DIR/images/icon/hyperspy16.png" x-application-$APP

# Create directories if missing
mkdir -p ~/.local/share/mime/packages
mkdir -p ~/.local/share/applications

# Create mime xml 
echo "<?xml version=\"1.0\"?>
<mime-info xmlns=\"http://www.freedesktop.org/standards/shared-mime-info\">
    <mime-type type=\"application/x-$APP\">
        <comment>$COMMENT</comment>
        <icon name=\"application-x-$APP\"/>" > ~/.local/share/mime/packages/application-x-$APP.xml
for EXT in $EXTENSIONS
do
    echo "        <glob pattern=\"*.$EXT\"/>" >> ~/.local/share/mime/packages/application-x-$APP.xml
done
echo "    </mime-type>
</mime-info>" >> ~/.local/share/mime/packages/application-x-$APP.xml

# Create application desktop
echo "[Desktop Entry]
Name=$APP
Exec=python \"$DIR/hyperspyui/main.py\" %U
MimeType=application/x-$APP
Icon=x-application-$APP
Terminal=false
Type=Application
Categories=
Comment=
"> ~/.local/share/applications/$APP.desktop

# update databases for both application and mime
update-desktop-database ~/.local/share/applications
update-mime-database    ~/.local/share/mime

xdg-mime default $APP application/x-$APP