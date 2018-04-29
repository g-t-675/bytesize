import subprocess
import argparse
import sys

# set up the nmap calls we want to do
# parse them in from a file for user customisation
outputData = []
commandFileName = "commands.txt"

def setUpIPTables(target):
	scanArgs = ["iptables", "-I", "INPUT", "1", "-s", target, "-j", "ACCEPT"]
	proc = subprocess.Popen(scanArgs, stdout=subprocess.PIPE, shell=False)
	(out, err) = proc.communicate()

	scanArgs = ["iptables", "-I", "OUTPUT", "1", "-d", target, "-j", "ACCEPT"]
	proc = subprocess.Popen(scanArgs, stdout=subprocess.PIPE, shell=False)
	(out, err) = proc.communicate()

def clearIPTables():
	scanArgs = ["iptables", "-Z"]
	proc = subprocess.Popen(scanArgs, stdout=subprocess.PIPE, shell=False)
	(out, err) = proc.communicate()

def flushIPTables():
	scanArgs = ["iptables", "-F"]
	proc = subprocess.Popen(scanArgs, stdout=subprocess.PIPE, shell=False)
	(out, err) = proc.communicate()

def dumpIPTablesData():
	scanArgs = ["iptables", "-vn", "-L"]
	proc = subprocess.Popen(scanArgs, stdout=subprocess.PIPE, shell=False)
	(out, err) = proc.communicate()
	out = out.decode().split('\n')

	targetDataLine = ""
	lineIndex = 0
	for l in out:
		if "Chain OUTPUT" in l:
			targetDataLine = out[lineIndex+2]
		lineIndex += 1

	lineChunks = targetDataLine.split(' ')
	lineChunks = list(filter(None, lineChunks))
	outputData.append(lineChunks[0] + " " + lineChunks[1])
	print("packets: " + lineChunks[0] + " & bytes: " + lineChunks[1])

def loadCommands(target):
	print("Loading custom commands...")

	commands = []
	with open(commandFileName) as f:
		commands = f.readlines()
		commands = [x.strip() for x in commands]
		commands = [x.replace('<ip>', target) for x in commands]

	print("Loaded: %s custom commands\n" % len(commands))
	return commands

def performCommand(cmd):
	print("Cmd: %s" % cmd)
	scanArgs = cmd.split(' ')
	proc = subprocess.Popen(scanArgs, stdout=subprocess.PIPE, shell=False)
	(out, err) = proc.communicate()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', action='store', dest='target', required=True, help='Target IP address')
	results = parser.parse_args()

	target = results.target

	networkCommands = loadCommands(target)
	setUpIPTables(target)
	clearIPTables()

	print("--- Starting ---")

	for cmd in networkCommands:
		performCommand(cmd)
		dumpIPTablesData()
		clearIPTables()

	flushIPTables()

	print("--- Completed ---")
