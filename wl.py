#!/usr/bin/env python3

import os
import sys
import socket
import numpy as np

words = []
ifile = 'touslesmots.txt'

try:
  fd = open(ifile, mode='rt')
except FileNotFoundError:
  fd = open('listes.txt', mode='rt')
  url = fd.readline()
  fd.close()
  cmd = 'curl ' + url.strip() + ' | gzip -d >' + ifile
  os.system(cmd)

fd = open(ifile, mode='rt')
fd.readline()
while True:
  l = fd.readline()
  if len(l) != 0:
    w = l.split(' ')
    w = list(map(str.strip, w))
    words.extend(w)
  else:
    break

#print(len(words))
#print(words[0:20])

## Remove too short words
min = 3
w2 = []
for w in words:
  if len(w) >= min:
    w2.append(w)
words = w2

print(len(words), "words")
sys.stdout.flush()
#print(words[0:20])

n_letters = 26
## Build graph
class Node:
  def __init__(self):
    self.next = np.ndarray((n_letters + 1,), dtype='object')

def l2i(c):
  return ord(c) - ord('A') + 1
  
def i2l(i):
  return chr(i + ord('A') - 1)
  
def build_tree(n, s, d=0):
  if d < len(s):
    i = l2i(s[d])
    if n.next[i] == None:
      n.next[i] = Node()
    build_tree(n.next[i], s, d + 1)
  else:
    n.next[0] = Node()
  
root = Node()
for w in words:
  build_tree(root, w)

#  n = root
#  for l in w:
#    i = l2i(l)
#    if n.next[i] == None:
#      n.next[i] = Node()
#  n.next[0] = Node()

## Recursive function, whose maximum depth is the longuest word
def explore_node(n, s, f=print):
  if n.next[0] != None:
    ## Found complete word
    f(s)
  for i in range(1, n_letters+1):
    if n.next[i] != None:
      explore_node(n.next[i], s + i2l(i))

#explore_node(root, '')

def print_first_longuest(n):
  while True:
    for i in range(1, n_letters+1):
      if n.next[i] != None:
        break;
    if i < n_letters:
      print(i2l(i))
      n = n.next[i]
    else:
      break

#print_first_longuest(root)

def check_str(n, s, d=0):
  if d < len(s):
    i = l2i(s[d])
    if n.next[i] != None:
      return check_str(n.next[i], s, d+1)
    else:
      return False
  else:
    if n.next[0] != None:
      return True
    else:
      return "Maybe"

def listen():
  serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serversocket.bind(('localhost', 2016))
  serversocket.listen(5) 
  return serversocket

def accept(serversocket):
  (clientsocket, address) = serversocket.accept()
  return clientsocket

print('Listening')
serv = listen()
while True:
  sock = accept(serv)
  print('Connected')
  while True:
    s = sock.recv(1024)
    if s != b'':
      try:
        s = s.decode('utf-8')
      except UnicodeDecodeError:
        continue
      #print(s)
      b = check_str(root, s.strip().upper())
      sock.send(bytes(str(b), 'utf-8'))
    else:
      print('Disconnected')
      break

quit()

sys.stdout.flush()
while True:
  s = sys.stdin.readline()
  if len(s):
    print(check_str(root, s.strip().upper()))
    sys.stdout.flush()
  else:
    quit()

