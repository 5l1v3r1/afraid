#!/usr/bin/env python
#
# afraid.py - freedns.afraid.org DDNS client
#  thed4rkcat@yandex.com		https://github.com/d4rkcat/afraid
#
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 2 of the License, or
## (at your option) any later version.
#
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License at (http://www.gnu.org/licenses/) for
## more details.

from requests import get
from hashlib import sha1
from getpass import getpass
from os import name, path, kill, getpid, mkdir
from sys import exit, stdout
from time import sleep, strftime
from threading import Thread
from random import choice

def fhelp():
	print '\n Usage:\n' \
	'   add <username>\t - Add a new account to the DB.\n' \
	'   ls\t\t\t - List all domains and corresponding ip\'s\n' \
	'   maintain <domains>\t - Keep domains up to date with current ip.\n' \
	'   release <domains>\t - Stop updating domains with current ip.\n' \
	'   <domain> <ip>\t - Point domain at IP, current IP is used if left blank.\n' \
	'   timeout <seconds>\t - Set the interval between IP checks for maintain command.\n' \
	'   refresh\t\t - Update local DB.'

def completer(text, state):
	for cmd in commandlist:
		if cmd.startswith(text):
			if not state:
				return cmd
			else:
				state -= 1

def makeauthkey(username, password):
	return sha1('%s|%s' % (username.lower(), password[:16])).hexdigest()

def cleanprint(data):
	stdout.write("\r" + str(data))
	stdout.flush()

def nicetime():
	return '[%s %s]' % (strftime("%a"), strftime("%c").split(' ')[1])

def currentip():
	return get('http://icanhazip.com').content.strip()

def maintain():
	global upsites, current, iptime
	current, iptime = currentip(), nicetime()
	while True:
		sleep(timeout)
		newip = False
		while not newip:
			try:
				newip = currentip()
				iptime = nicetime()
			except:
				sleep(2)

		if newip != current:
			for site in upsites:
				t = Thread(target=update_entry, args=(site, newip,))
				t.daemon = True
				t.start()
				cleanprint(' %s Updated %s to %s \n' % (nicetime(), site, newip))
			cleanprint('\n\n >')
			current = newip

def update_stats(key):
	global stats
	authkey = key.split(':')[1]
	stat = get_stats(authkey)
	if stat and stat != 'empty':
		stats[authkey] = stat

def get_stats(authkey):
	results = []
	stats = get('https://freedns.afraid.org/api/?action=getdyndns&sha=%s' % (authkey) , headers=randheader()).content
	if stats.startswith('ERROR'):
		return False
	for entry in stats.split('\n'):
		info = entry.split('|')
		try:
			results.append([info[0], info[1], info[2].split('?')[1]])
		except:
			return 'empty'
	return results

def update_entry(site, update_ip):
	update_key = None
	currip = currentip()
	for key in authkeys:
		authkey = key.split(':')[1]
		for entry in stats[authkey]:
			if site in entry[0]:
				if update_ip:
					entry[1] = update_ip
				else:
					entry[1] = currip
				update_key = entry[2]
				break

	if update_key:
		if not update_ip:
			return ' %s %s' % (nicetime(), get('https://freedns.afraid.org/dynamic/update.php?%s' % (update_key) , headers=randheader()).content.strip())
		else:
			return ' %s %s' % (nicetime(), get('https://freedns.afraid.org/dynamic/update.php?%s&address=%s' % (update_key, update_ip) , headers=randheader()).content.strip())
	else:
		return False

def showdomains(silent):
	global commandlist, numdomains
	numdomains = 0
	if len(authkeys) != 0:
		for key in authkeys:
			authkey = key.split(':')[1]
			username = key.split(':')[0]
			if not silent:
				print '\n [*] Results for %s:' % (username)
			try:
				for entry in stats[authkey]:
					if len(entry[0]) <= 10:
						sep = '\t\t'
					else:
						sep = '\t'
					commandlist.append(entry[0] + ' ')
					numdomains += 1
					if not silent:
						print ' [*] %s%s--> %s' % (entry[0], sep, entry[1])
			except:
				pass
		if len(upsites) > 0:
			try:
				upsites.remove('')
			except:
				pass
			if not silent:
				print '\n [!] Maintaining %s domains at a timeout interval of %s seconds:' % (len(upsites), timeout)
				for site in upsites:
					print ' [>] %s' % (site)
				print '\n %s Latest IP address: %s' % (iptime, current)
		commandlist = list(set(commandlist))
	else:
		if not silent:
			print ' [X] No accounts in DB!'

def randheader():
	return { 'User-Agent':choice(useragents) }

commandlist = ['add ', 'maintain ', 'release ', 'timeout ', 'ls', 'refresh', 'help']
useragents = [	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/36.0.1985.125 Safari/537.36",
	"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2166.2 Safari/537.36",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
	"Mozilla/5.0 (X11; U; Linux i686; rv:19.0) Gecko/20100101 Slackware/13 Firefox/19.0",
	"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0",
	"Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0 Iceweasel/19.0.2",
	"Mozilla/5.0 (X11; Linux 3.8-6.dmz.1-liquorix-686) KHTML/4.8.4 (like Gecko) Konqueror/4.8",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.166 Safari/537.36 OPR/20.0.1396.73172",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.4 (KHTML like Gecko) Chrome/22.0.1229.56 Safari/537.4",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/26.0",
	"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-US) AppleWebKit/528.16 (KHTML, like Gecko, Safari/528.16) OmniWeb/v622.8.0",
	"Opera/9.80 (Macintosh; Intel Mac OS X 10.4.11; U; en) Presto/2.7.62 Version/11.00",
	"Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
	"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_2; en-us) AppleWebKit/531.21.8 (KHTML, like Gecko) Version/4.0.4 Safari/531.21.10",
	"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_5; de-de) AppleWebKit/534.15  (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4",
	"Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.16",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/28.0.1469.0 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/28.0.1469.0 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
	"Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0) Gecko/16.0 Firefox/16.0",
	"Mozilla/5.0 (Windows NT 6.2; rv:19.0) Gecko/20121129 Firefox/19.0",
	"Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130401 Firefox/21.0",
	"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0",
	"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0",
	"Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",
	"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:35.0) Gecko/20100101 Firefox/35.0",
	"Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
	"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Trident/5.0)",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.2; Trident/5.0)",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.2; WOW64; Trident/5.0)",
	"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/6.0)",
	"Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0)",
	"Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko", ]
stats, timeout, upsites = {}, 120, []

try:
	import readline
	readline.parse_and_bind("tab: complete")
	readline.set_completer(completer)
except:
	print ' %s ERROR: pyreadline module is required for windows. \n [>]  Try Install with: pip install pyreadline\n' % (nicetime())
	exit()

try:
	mkdir('data')
except:
	pass

if path.isfile('data/authkeys'):
	with open('data/authkeys', 'rb') as a:
		authkeys = a.read().strip().split('\n')
	print ' %s Downloading records for %s users..' % (nicetime(), len(authkeys))
	try:
		for key in authkeys:
			t = Thread(target=update_stats, args=(key,))
			t.daemon = True
			t.start()
			t.join()
		current = currentip()
	except:
		print ' %s Connection failed.' % (nicetime())
		exit()
else:
	authkeys = []
showdomains(True)
if path.isfile('data/maintain'):
	with open('data/maintain', 'rb') as a:
		upsites = a.read().replace('\r', '').strip().split('\n')
else:
	upsites = []

print ' %s Local records updated.' % (nicetime())
if len(upsites) > 0:
		print ' %s Maintaining %s out of %s domains.' % (nicetime(), len(upsites), numdomains)
for site in upsites:
	if site:
		t = Thread(target=update_entry, args=(site, None,))
		t.daemon = True
		t.start()

print ' %s Current IP address: %s' % (nicetime(), current)
fhelp()
t = Thread(target=maintain, args=())
t.daemon = True
t.start()
while True:
	command = False
	while not command:
		try:
			command = raw_input('\n >').strip()
		except:
			print
			exit()

	if command.startswith('add '):
		username = command.split(' ')[1]
		while True:
			password = getpass(' [>] Please enter the password:')
			password2 = getpass(' [>] One more time:')
			if password == password2:
				authkey = makeauthkey(username, password)
				newstats = get_stats(authkey)
				if newstats:
					if newstats == 'empty':
						print ' %s Auth-key saved, no stats to import!' % (nicetime())
					else:
						print ' %s Auth-key saved, stats imported.' % (nicetime())
						stats[authkey] = newstats
					authkeys.append(username + ':' + authkey)
					authkeys = list(set(authkeys))
					with open('data/authkeys', 'wb') as a:
						for key in authkeys:
							a.write(key + '\n')
				else:
					print ' %s ERROR: Could not authenticate.' % (nicetime())
				break
			else:
				print ' [X] Passwords do not match, try again..\n'

	elif command.startswith('ls'):
		showdomains(False)

	elif command.startswith('maintain '):
		try:
			sites = command.split(' ')[1:]
			for site in sites:
				if site:
					try:
						if site.strip() not in upsites and site.find('.') != -1:
							t = Thread(target=update_entry, args=(site, None,))
							t.daemon = True
							t.start()
							print ' [*] Thread started to maintain %s' % (site)
							upsites.append(site.strip())
							with open('data/maintain', 'a') as a:
								a.write(site + '\n')
						else:
							print ' [*] %s is already maintained.' % (site)
					except:
						pass
		except:
			fhelp()

	elif command.startswith('release '):
		try:
			sites = command.split(' ')[1:]
			for site in sites:
				try:
					if site in upsites:
						print ' [X] %s is no longer being maintained.' % (site)
						upsites.remove(site)
						with open('data/maintain', 'wb') as a:
							for s in upsites:
								a.write(s + '\n')
				except:
					pass
		except:
			fhelp()

	elif command.startswith('timeout '):
		try:
			timeout = int(command.split(' ')[1])
			print ' [*] Timeout set to %s seconds.' % (timeout)
		except:
			fhelp()

	elif command.startswith('refresh'):
		print ' %s Downloading records for %s users..' % (nicetime(), len(authkeys))
		for key in authkeys:
			t = Thread(target=update_stats, args=(key,))
			t.daemon = True
			t.start()
			t.join()
		print ' %s Local records updated.' % (nicetime())

	elif command == 'help' or command == '?':
		fhelp()

	else:
		site = command.split(' ')[0]
		try:
			update_ip = command.split(' ')[1]
		except:
			update_ip = None
		result = update_entry(site, update_ip)
		if result:
			print result
			if site in upsites:
				upsites.remove(site)
				print ' [*] %s is no longer being maintained.' % (site)
		else:
			print ' [X] Update for %s failed.\n   syntax: mydomain.us.to 192.168.13.37' % (site)
