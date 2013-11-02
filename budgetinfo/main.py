#!/usr/bin/python

import argparse
import getpass
import sys

import client_lib.servercall as servercall

#command line parsing
cmd_parser = argparse.ArgumentParser(description='Vraag budgetinformatie op voor 1 of meer verenigingen')

cmd_parser.add_argument(
	'verenigingen', 
	metavar='vereniging', 
	type=str, nargs='+', 
	help='Vereniging waarover informatie verlangt wordt.'
)
cmd_parser.add_argument(
	'--user', '-u',
	type=str,
	help='Gebruikersnaam om mee in te loggen (standaard de gebruikersnaam waarme is ingelogd op de lokale machine).',
	default=getpass.getuser()
)

arguments = cmd_parser.parse_args()

# login
password = getpass.getpass()
try:
	servercall.login(arguments.user, password)
except servercall.ServerCallException:
	print >> sys.stderr, 'Kon geen verbinding opbouwen met madmin server.'
	sys.exit(1)
except servercall.ServerLoginError:
	print >> sys.stderr, 'Kon niet inloggen met gegeven gebruikersnaam/wachtwoord.'
	sys.exit(1)

#Retrieve vereniging information
verenigingen = servercall.remote_call('/verenigingen')

for vereniging in arguments.verenigingen:
	selection = filter(lambda x: x['naam'] == vereniging, verenigingen)
	if len(selection) == 0:
		print >> sys.stderr, 'Vereniging {0} bestaat niet.'.format(vereniging)
		continue
	try:
		budgetten = servercall.remote_call('/budget/ver', [('vereniging_id', selection[0]['id'])])
	except servercall.ServerCallException:
		print >> sys.stderr, 'Kon geen verbinding opbouwen met madmin server'
		sys.exit(1)
	print '{0}:'.format(vereniging)
	for budget in budgetten:
		current_euro = budget['current']/100
		current_cent = budget['current']%100
		minimum_euro = budget['minimum']/100
		minimum_cent = budget['minimum']%100
		print '{0}: {1}.{2:02} (Minimum: {3}.{4:02})'.format(current_euro, current_cent, minimum_euro, minimum_cent)