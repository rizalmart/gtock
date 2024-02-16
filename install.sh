#!/bin/bash
#gTock installer script.

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


if prompt_yes_no "This installer will install gTock. Do you want to proceed?"; then
    echo "Installing gTock...."
else
    echo "Installation cancelled"
    exit 1
fi


script_dir=$(realpath $(dirname "$0"))

if [ ! -d $script_dir/gtock-src ]; then
 echo "gtock source files was missing"
 exit 1
fi

cp -rf $script_dir/gtock-src/* /

glib-compile-schemas /usr/share/glib-2.0/schemas/

sudo chmod +x /usr/bin/gtock
echo "gTock installation complete!"

