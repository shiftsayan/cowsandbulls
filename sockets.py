'''
This file deals with the Arena mode. Uses sockets.
https://kdchin.gitbooks.io/sockets-module-manual/content/
'''

####################################
# Modules
####################################

import socket
import threading
from queue import Queue

####################################
# Sockets
####################################

# HOST = "" # IP Address
from port import HOST, PORT

####################################
# Initialize the connnection
####################################

# Source: https://kdchin.gitbooks.io/sockets-module-manual/content/
def handleServerMsg(server, serverMsg):
  server.setblocking(1)
  msg = ""
  command = ""
  while True:
    msg += server.recv(10).decode("UTF-8")
    command = msg.split("\n")
    while (len(command) > 1):
      readyMsg = command[0]
      msg = "\n".join(command[1:])
      serverMsg.put(readyMsg)
      command = msg.split("\n")

def startServer(data):
    try:
        # Source: https://kdchin.gitbooks.io/sockets-module-manual/content/
        data.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data.server.connect((HOST,PORT))
        print("Connected to server.")
        data.serverMsg = Queue(100)
        threading.Thread(target = handleServerMsg, args = (data.server, data.serverMsg)).start()
    except:
        print("Server not running.")
        data.arena = None

####################################
# Receive socket (ran in timerFired)
####################################

# Source: https://kdchin.gitbooks.io/sockets-module-manual/content/
def receiveSocket(data):
    while (data.serverMsg.qsize() > 0):
      msg = data.serverMsg.get(False)

      try:
        print("Received: ", msg, "\n")
        msg = msg.split()
        command = msg[0]
        # print(msg)
        # Various commands
        if command == "myIDis": data.pID = int(msg[1][-1])
        elif command == "newPlayer": data.players += 1
        elif command == "update": deconstructSocket(data, msg[2])

      except:
        print("Failed")

      data.serverMsg.task_done()

####################################
# Convert data to socket
####################################

def constructSocketWord(word):
    result = ""
    for char in word:
        if char != None: result += char
        else: result += "_"
    return result

def constructSocket(data):
    result = [ constructSocketWord(data.curWord),
               constructSocketWord(data.curTarget),
               str(int(data.player)),
               str(int(data.stage)),
               str(int(data.betweenRounds)),
               data.pvpScore[0],
               data.pvpScore[1],
               str(data.score[0]),
               str(data.score[1]),
               str(data.turnsLeft)
             ]
    return "update " + ";".join(result) + "\n"

####################################
# Convert socket to data
####################################

def deconstructSocketWord(word):
    result = []
    for char in word:
        if char != "_": result.append(char)
        else: result.append(None)
    return result

def deconstructSocket(data, msg):
    # Temporary Variables
    word, target, player, stage, betweenRoungs, cows, bulls, player1score, player2score, turnsLeft = msg.split(";")
    # Store in data
    data.curWord = deconstructSocketWord(word)
    data.curTarget = deconstructSocketWord(target)
    data.player = bool(int(player))
    data.stage = bool(int(stage))
    data.betweenRounds = bool(int(betweenRoungs))
    data.pvpScore = [cows, bulls]
    data.score = [int(player1score), int(player2score)]
    data.turnsLeft = int(turnsLeft)
