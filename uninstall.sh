#!/bin/bash
#gTock removal script.

if [ "$(whoami)" != "root" ]; then
 exec sudo $0
fi

prompt_yes_no() {
    while true; do
        read -p "$1 (yes/no): " answer
        case $answer in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}


if prompt_yes_no "This installer will remove gTock. Do you want to proceed?"; then
    echo "Removing gTock...."
else
    echo "Uninstallation cancelled"
    exit 1
fi


for rfile in gtock gtock-import gtock-export
do
 rm -f /usr/bin/${rfile}
done

rm -rf /usr/share/gtock
rm -f /usr/share/applications/gtock.desktop
rm -f /usr/share/glib-2.0/schemas/org.gtk.gtock.gschema.xml

glib-compile-schemas /usr/share/glib-2.0/schemas/

echo "gTock uninstallation complete!
