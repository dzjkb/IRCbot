#coding: utf-8

import socket
import sys
import threading

from threading import Thread
from time import strftime

irc = socket.socket()
displaymutex = threading.Lock()

def get_input():
	inp = []

	print("Please enter the address to connect to:")
	inp.append(input())

	print("Your nickname?")
	inp.append(input())

	print("Username?")
	inp.append(input())

	print("Real name?")
	inp.append(input())

	return inp

def send(sock, msg):
	totalsent = 0
	msg = msg.encode('utf-8')
	while totalsent < len(msg):
		try:
			sent = sock.send(msg[totalsent:])
		except:
			print('Connection aborted')
			raise

		if sent == 0:
			raise RuntimeError("Cannot send, connection broken!")
		totalsent += sent

def sendthread():
	userinput = ''
	currentchannel = ''
	run = True
	while run:
		print(currentchannel +'> ', end="")
		userinput = input()
		if len(userinput) == 0: userinput = ' '
		if userinput[0] == '/': #command mode
			userinput = userinput[1:]
			userinput = userinput.split()
			if userinput[0] == 'join':
				print('Joining ' + userinput[1] + '...')
				send(irc, 'JOIN #' + userinput[1] + '\r\n')
				currentchannel = '#' + userinput[1]

			elif userinput[0] == 'leave':
				if currentchannel == '':
					print('Currently not in any channel')
				else:
					print('Leaving #' + currentchannel + '...')
					send(irc, 'QUIT\r\n')

			elif userinput[0] == 'quit':
				print('Bye bye :(')
				run = False

		elif '#' not in currentchannel:
			print('No channel joined, cant send')
		else:
			send(irc, 'PRIVMSG ' + currentchannel + ' :' + userinput + '\r\n')

	irc.close()
	exit()

def recvthread():
	bufff = b''
	while True:
		if b'\r\n' not in bufff:
			try:
				bufff += irc.recv(512)
			except:
				print('Connection aborted')
				raise

			if bufff == b'':
				print('Connection closed')
				raise

			continue

		time = '[%s]' % strftime('%H:%M')
		line, bufff = bufff.split(b'\r\n', 1)
		if b'PING' in line:
			send(irc, 'PONG ' + line[5:].decode('utf-8'))

		print(time + line.decode('utf-8'))

# parsing the input; for simplicity all names are set to the entered nickname

#inplist = get_input()
ADDRESS = 'irc.freenode.net:6667' #inplist[0]
NAME = 'ciulerson2bot' #inplist[1]
ADDRESS = ADDRESS.split(sep=':')

try:
	ADDRESS[1] = int(ADDRESS[1])
except IndexError:
	print("No port specified!")
	exit(1)
except ValueError:
	print("Invalid port number:", ADDRESS[1])
	exit(1)
except:
	print("Invalid address entered!")
	exit(1)

ADDRESS = tuple(ADDRESS)
print(ADDRESS)

try:
	irc.connect(ADDRESS)
except:
	print("Could not connect to specified server!")
	raise

print("Connected to:", ADDRESS[0])

# the IRC protocol initiation messages

send(irc, 'NICK ' + NAME + '\r\n')
send(irc, 'USER ' + NAME + ' 0 * :' + NAME + '\r\n')

bufff = b''
dupa = True
while dupa:
	if b'\r\n' not in bufff:
		bufff += irc.recv(512)
		if bufff == b'':
			print('Connection closed')
			raise

		continue

	line, bufff = bufff.split(b'\r\n', 1)
	if b'End of /MOTD command' in line:
		dupa = False

	print(line.decode('utf-8'))

send_thread = Thread(target=sendthread)
recv_thread = Thread(target=recvthread, daemon=True)

recv_thread.start()
send_thread.start()
