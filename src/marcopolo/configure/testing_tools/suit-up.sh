#! /bin/bash

# Install+configure apache
#apt remove apache2 -y
apt install apache2 -y
cp 000-default.conf /etc/apache2/sites-available/
cp apache2.conf /etc/apache2/
a2enmod rewrite #just a thing you need to do

# Install website files, allow port 80
if [ -f "/var/www/html/index.html" ]; then
  rm "/var/www/html/index.html"
fi
if [ -d "/var/www/html/pretend-crypto-wallet.com" ]; then
  rm -r "/var/www/html/pretend-crypto-wallet.com"
fi
cp -r pretend-crypto-wallet.com /var/www/html/
ufw allow 80






################### EVERYTHING AFTER THIS POINT ISN'T REALLY NECESSARY FOR THIS PROJECT ###################################

# Install certbot, gcloud, 
#apt remove certbot
snap install --classic certbot

# Install bind, and enable logging (otherwise default to syslog, which sucks)
#apt remove bind9
apt install bind9 -y
mkdir -p /var/log/bind
chown bind /var/log/bind
cp named.conf.options /etc/bind/
cp usr.sbin.named /etc/apparmor.d/
systemctl restart apparmor
named-checkconf /etc/bind/named.conf  #test it works
rndc reconfig

# Start apache, now that you updated /var/www/html/
service apache2 restart

ip addr add 66.180.191.1 dev lo

exit 0

#*********************************** GCLOUD *************************#

# First you need to clear whatever exists with the following few commands
#apt remove gcloud
#rm /usr/share/keyrings/cloud.google.gpg
#rm /etc/apt/sources.list.d/google-cloud-sdk.list

# Then you install it with the following 
#apt install apt-transport-https ca-certificates gnupg curl sudo -y
#echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
#curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo tee /usr/share/keyrings/cloud.google.gpg
#apt update && sudo apt-get install google-cloud-cli

# Now you actually have to sign in to Gcloud


#*********************************** END *************************#