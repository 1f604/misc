#!/bin/bash

# iptable rules to allow outgoing connections to all ips on port 443, incoming and outgoing icmp (ping) requests, and everything on localhost.
# Requires iptables-persistent.
# Based on rules from here: https://gist.github.com/thomasfr/9712418
# Test: 
# ping google.com # should work
# wget google.com # should fail
# wget https://google.com # should work

IPT="/sbin/iptables"
IPT6="/sbin/ip6tables"

echo "Flushing iptable rules"
$IPT  -F
$IPT6 -F
$IPT  -X
$IPT6 -X
$IPT  -t nat -F
$IPT6 -t nat -F
$IPT  -t nat -X
$IPT6 -t nat -X

echo "Setting default policy to 'DROP'"
$IPT  -P INPUT   DROP
$IPT6 -P INPUT   DROP
$IPT  -P FORWARD DROP
$IPT6 -P FORWARD DROP
$IPT  -P OUTPUT  DROP
$IPT6 -P OUTPUT  DROP

echo "Allowing everything on localhost"
$IPT -A INPUT  -i lo -j ACCEPT
$IPT -A OUTPUT -o lo -j ACCEPT

echo "Allowing pings"
$IPT -A INPUT  -p icmp --icmp-type 8 -m conntrack --ctstate NEW,ESTABLISHED,RELATED -j ACCEPT
$IPT -A INPUT  -p icmp --icmp-type 0 -m conntrack --ctstate NEW,ESTABLISHED,RELATED -j ACCEPT
$IPT -A OUTPUT -p icmp --icmp-type 8 -m conntrack --ctstate NEW,ESTABLISHED,RELATED -j ACCEPT
$IPT -A OUTPUT -p icmp --icmp-type 0 -m conntrack --ctstate NEW,ESTABLISHED,RELATED -j ACCEPT

echo "Allowing outgoing connections to all IPs on port 443"
$IPT -A INPUT  -p tcp --sport 443  -m conntrack --ctstate ESTABLISHED     -j ACCEPT
$IPT -A OUTPUT -p tcp --dport 443  -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT

echo "Allow outgoing connections to port 123 (nts)"
$IPT -A INPUT  -p udp --sport 123  -m conntrack --ctstate ESTABLISHED     -j ACCEPT
$IPT -A OUTPUT -p udp --dport 123  -m owner --uid-owner ntpuser           -j ACCEPT

echo "Allow outgoing connections to port 4460 (nts-ke)"
$IPT -A INPUT  -p tcp --sport 4460 -m conntrack --ctstate ESTABLISHED     -j ACCEPT
$IPT -A OUTPUT -p tcp --dport 4460 -m owner --uid-owner ntpuser           -j ACCEPT

# Log before dropping
# $IPT -A INPUT  -j LOG  -m limit --limit 12/min --log-level 4 --log-prefix 'IP INPUT drop: '
$IPT -A INPUT  -j DROP

# $IPT -A OUTPUT -j LOG  -m limit --limit 12/min --log-level 4 --log-prefix 'IP OUTPUT drop: '
$IPT -A OUTPUT -j DROP

netfilter-persistent save
netfilter-persistent reload

echo "All done."
