'''
Run this file before playing in Arena mode.
This code has been sourced in its entirely from the provided module. Only few
small changes have been made to adjust to the variables I was using.
https://kdchin.gitbooks.io/sockets-module-manual/content/
'''

####################################
# Modules
####################################

import socket
import threading
from queue import Queue

####################################
# Global Variables
####################################

# HOST = "" # IP Address
BACKLOG = 4
from port import HOST, PORT

####################################
# Server
####################################

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))
server.listen(BACKLOG)
print("Running on port %d..." % PORT)

####################################
# Server Functions
####################################

def handleClient(client, serverChannel, cID, clientele):
  client.setblocking(1)
  msg = ""
  while True:
    try:
      msg += client.recv(10).decode("UTF-8")
      command = msg.split("\n")
      while (len(command) > 1):
        readyMsg = command[0]
        msg = "\n".join(command[1:])
        serverChannel.put(str(cID) + " " + readyMsg)
        command = msg.split("\n")
    except:
      # we failed
      return

def serverThread(clientele, serverChannel):
  while True:
    msg = serverChannel.get(True, None)
    print("Message Received: ", msg)
    msgList = msg.split(" ")
    senderID = msgList[0]
    instruction = msgList[1]
    details = " ".join(msgList[2:])
    if (details != ""):
      for cID in clientele:
        if cID != senderID:
          sendMsg = instruction + " " + senderID + " " + details + "\n"
          clientele[cID].send(sendMsg.encode())
          print("> Sent to %s:" % cID, sendMsg[:-1])
    print()
    serverChannel.task_done()

####################################
# Add clients
####################################

clientele = dict()
playerNum = 0

serverChannel = Queue(100)
threading.Thread(target = serverThread, args = (clientele, serverChannel)).start()

names = ["Player0", "Player1"]

while playerNum < 2:
    client, address = server.accept()
    # myID is the key to the client in the clientele dictionary
    myID = names[playerNum]
    print(myID, playerNum)
    for cID in clientele:
        print (repr(cID), repr(playerNum))
        clientele[cID].send(("newPlayer %s\n" % myID).encode())
        client.send(("newPlayer %s\n" % cID).encode())
    clientele[myID] = client
    client.send(("myIDis %s \n" % myID).encode())
    print("Connection recieved from %s" % myID)
    threading.Thread(target = handleClient, args =
                        (client ,serverChannel, myID, clientele)).start()
    playerNum += 1
