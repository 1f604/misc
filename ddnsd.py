#!/usr/bin/env python
# change these parameters as necessary
QUERY_DOMAIN = "example.com"
UPDATE_CMD = "cloudflare-ddns-updater"
WAIT_PERIOD = 60

# this script does a DNS query via cloudflare and asks ipify "what is my IP?"
# based on https://github.com/stamparm/python-doh/blob/master/client.py

POLLING_INTERVAL = 2 # how many seconds to wait before polling cloudflare and ipify again
DOH_SERVER = "1.1.1.1"
IP_API_SERVERS = ['https://api.ipify.org', 'https://ipinfo.io/ip', 'https://bot.whatismyipaddress.com/', 'https://icanhazip.com/', 'https://ifconfig.me/', 'https://ident.me']
import sys
MIN_PYTHON = (3, 0)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

import json
import re
import socket
import ssl
import subprocess
import urllib.request
import os
import time

_urlopen = urllib.request.urlopen
_Request = urllib.request.Request

ipv4_regexp = '^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
pat = re.compile(ipv4_regexp)

def getexternalip():
	for server in IP_API_SERVERS:
		try:	
			ip = urllib.request.urlopen(server).read().decode('utf8').strip()
			assert(pat.match(ip))
			return ip
		except: 
			pass
	raise Exception("No IP API servers were usable.")
	sys.exit()

def dnsquery(name, type='A', server=DOH_SERVER):
	retval = None
	req = _Request("https://%s/dns-query?name=%s&type=%s" % (server, name, type), headers={"Accept": "application/dns-json"})
	content = _urlopen(req).read().decode()
	reply = json.loads(content)

	if "Answer" in reply:
	    answer = json.loads(content)["Answer"]
	    retval = [_["data"] for _ in answer]
	else:
	    retval = []
	return retval

def check_synchronized():
	external_ip = getexternalip().strip()
	query_ip = dnsquery(QUERY_DOMAIN)[0].strip()
	synchronized = external_ip == query_ip
	if not synchronized:
		print("ATTENTION: Domain {} has IP {} which does not match the current external IP {}".format(QUERY_DOMAIN, query_ip, external_ip))
	if len(sys.argv) > 1: # if just checking, say the result and exit.
		if synchronized:
			print("Everything is fine. Domain {} IP {} matches external IP {}".format(QUERY_DOMAIN, query_ip, external_ip))
		sys.exit()
	return synchronized

def main(): # main polling loop
	while True:
		if not check_synchronized(): # need to fix the DDNS
			print('Now forcing IP update using the command \"{}\"'.format(UPDATE_CMD))
			os.system(UPDATE_CMD)
			time.sleep(WAIT_PERIOD)
			if check_synchronized(): # everything went well
				print("Update successful.")
			else:
				print("ERROR: Something went wrong with the DDNS updater. You need to fix it manually.")
				return
		time.sleep(POLLING_INTERVAL)

pid = str(os.getpid())
pidfile = "/tmp/ddnsd.pid"

if os.path.isfile(pidfile):
    print("%s already exists, exiting" % pidfile)
    sys.exit()

with open(pidfile, 'w') as f:
    f.write(pid)

try:
    main()
finally:
    os.unlink(pidfile) 
