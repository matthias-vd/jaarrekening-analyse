#!/bin/bash

# print requirements
clear
echo "------------------------------- BELANGRIJK -------------------------------"
echo "Zorg er zeker voor dat poort 80 van uw URL toegankelijk is, dit wordt immers gebruikt voor Let's Encrypt om domeinvalidatie te doen."
echo "Zorg er tevens voor dat er geen andere toepassingen gebruik maken van poort 80 (HTTP) of poort 443 (HTTPS)."
echo "Zorg er zeker voor dat u in bezit bent van een backup van deze server, indien er een (ernstige) fout optreedt."
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""

# prompt URL
read -p "Voer het URL in van de server: " BASE_URL

# install prerequisites
apt install apache2 certbot python3-certbot-apache -y