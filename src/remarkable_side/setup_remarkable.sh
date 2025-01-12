# Stop eerst eventuele Entware services
/opt/etc/init.d/rc.unslung stop

# Backup huidige opt (voor de zekerheid)
cp -a /opt /home/opt_backup

# Verwijder huidige /opt
rm -rf /opt

# Maak nieuwe opt directory in /home (hier is ~6GB beschikbaar)
mkdir -p /home/opt

# Maak symbolic link
ln -s /home/opt /opt

# Download en installeer Entware
wget http://bin.entware.net/armv7sf-k3.2/installer/generic.sh
sh ./generic.sh

# Update package lijst
/opt/bin/opkg update

# Installeer Python en pip
/opt/bin/opkg install python3
/opt/bin/opkg install python3-pip

# Installeer Flask via pip
pip3 install flask


