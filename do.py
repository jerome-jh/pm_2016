#!/usr/bin/env python3

import numpy as np
import itertools as it
import copy
import sys
import subprocess
import socket

north = 0
east = 1
south = 2
west = 3
ne = 4
se = 5
so = 6
no = 7

valeurs = {
  'A': 1,
  'B': 3,
  'C': 3,
  'D': 2,
  'E': 1,
  'F': 4,
  'G': 2,
  'H': 4,
  'I': 1,
  'J': 6,
  'K': 5,
  'L': 1,
  'M': 3,
  'N': 1,
  'O': 1,
  'P': 3,
  'Q': 5,
  'R': 1,
  'S': 1,
  'T': 1,
  'U': 1,
  'V': 4,
  'W': 8,
  'X': 8,
  'Y': 4,
  'Z': 10,
}

class Node:
  def __init__(self, multiplier = 0, x = -1, y = -1):
    self.neighbor = np.ndarray((8,), dtype='object')
    self.letter = 0
    self.multiplier = multiplier
    self.x = x
    self.y = y

class Path:
  def __init__(self, nodes):
    self.word = ''
    self.value = 0
    self.multiplier = 1
    self.score(nodes)

  def score(self, nodes):
    for n in nodes:
      self.word += n.letter
      self.value += valeurs[n.letter]
      ## Multipliers count only once per word
      if n.multiplier > self.multiplier:
        self.multiplier = n.multiplier
    self.value = int(self.value * self.multiplier)
    if len(self.word) > 4:
      self.value += 2* len(self.word)
 
  def print(self):
    if self.multiplier == 1:
      print(self.value, self.word)
    else:
      print(self.value, self.word, 'x%d'%self.multiplier)

## Construct grid
def empty_grid(width):
  grid = np.ndarray((width,width), dtype='object')
  for i,j in it.product(range(width),range(width)):
    grid[i][j] = Node(x=i, y=j)

  for i,j in it.product(range(width),range(width)):
    if i != 0:
      grid[i][j].neighbor[north] = grid[i-1][j]
      if j != 0:
        grid[i][j].neighbor[no] = grid[i-1][j-1]
      if j != width - 1:
        grid[i][j].neighbor[ne] = grid[i-1][j+1]
    if i != width - 1:
      grid[i][j].neighbor[south] = grid[i+1][j]
      if j != 0:
        grid[i][j].neighbor[so] = grid[i+1][j-1]
      if j != width - 1:
        grid[i][j].neighbor[se] = grid[i+1][j+1]
    if j != 0:
      grid[i][j].neighbor[west] = grid[i][j-1]
    if j != width - 1:
      grid[i][j].neighbor[east] = grid[i][j+1]

  return grid

def fill_grid(grid, letters, multipliers):
  if len(letters) != len(grid.reshape(-1)):
    print(letters, len(letters), len(grid.reshape(-1)))
    quit()
  for i, c in enumerate(grid.reshape(-1)):
    c.letter = letters[i]
    c.multiplier = multipliers[i]

def print_grid(grid, width):
  for i in range(width):
    for j in range(width):
      print(grid[i][j].letter, end=' ')
    print()

def print_path(p):
  s = ''
  for n in p:
    s = s + str(n.letter)
  print(s)
  return s

def get_path(p):
  s = ''
  for n in p:
    s = s + str(n.letter)
  return s

path_min = 3

def visit(n, path):
  if n in path:
    return
  path.append(n)
  if len(path) >= path_min:
    print_path(path) 
  for i in range(no + 1):
    if n.neighbor[i] != None:
      visit(n.neighbor[i], copy.copy(path))

def visit_checked(sock, n, path, l):
  if n in path:
    return
  path.append(n)
  if len(path) >= path_min:
    s = get_path(path) 
    r = check(sock, s)
    if r == 0:
      return
    if r == 1:
      p = Path(path)
      #p.print()
      l.append(p)
  for i in range(no + 1):
    if n.neighbor[i] != None:
      visit_checked(sock, n.neighbor[i], copy.copy(path), l)

def prepwl():
  proc = subprocess.Popen(['/usr/bin/python3', 'wl.py'], bufsize=1, universal_newlines=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
  print("wait")
  for l in proc.stdout:
    print("Got:", l)
    if str.strip(l) == "ready":
      break
  print("OK")
  return proc

def checkwl(proc, s):
  proc.stdin.write(s + '\n')
  proc.stdin.flush()
  l = str.strip(proc.stdout.readline())
  if l == 'True':
    return 1
  elif l == 'False':
    return 0
  elif l == 'Maybe':
    return 2
  else:
    print('Oh pooh', l)

def connect():
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(('localhost', 2016))
  return s
  
def check(sock, s):
  sock.send(bytes(str(s), 'utf-8'))
  s = sock.recv(1024)
  if s != b'':
    try:
      s = s.decode('utf-8')
    except UnicodeDecodeError:
      s = ''
  else:
    s = ''
  l = str.strip(s)
  if l == 'True':
    return 1
  elif l == 'False':
    return 0
  elif l == 'Maybe':
    return 2
  else:
    print('Oh pooh', l)

def i2l(i):
  return chr(i + ord('A') - 1)
  
def sort_value_f(p):
  return p.value

def sort_alpha_f(p):
  return p.word

def sort_len_f(p):
  return len(p.word)

if __name__ == '__main__':
  w = 4
  grid = empty_grid(w)

  if len(sys.argv) > 2:
    letters = list(map(str.upper, sys.argv[1:]))
    multipliers = np.ones((len(letters,)))
    for i, l in enumerate(letters):
      if len(l) == 2 and l[1].isdigit():
        multipliers[i] = int(l[1])
        letters[i] = l[0]
    #print(letters, multipliers)
    fill_grid(grid, letters, multipliers)
  elif len(sys.argv) == 2:
    s = str.upper(sys.argv[1])
    letters = list(it.repeat('', w * w))
    multipliers = np.ones((len(letters,)))
    j = 0
    for i in range(len(letters)):
      letters[i] = s[j]
      j += 1
      if j < len(s) and s[j].isdigit():
        multipliers[i] = int(s[j])
        j += 1
    #print(letters, multipliers)
    fill_grid(grid, letters, multipliers)
  else:
    fill_grid(grid, list(map(i2l, np.random.random_integers(1, 26, w * w))), np.ones((w * w,)))
    #fill_grid(grid, np.arange(1, w*w+1))

  #print_grid(grid, w)

  if False:
    p = prepwl()
    #print(checkwl(p, 'caca'))
  else:
    sock = connect()
    #print(check(sock, 'caca'))
  
  l = list()
  for i,j in it.product(range(w),range(w)):
    visit_checked(sock, grid[i][j], [], l)

  l.sort(key=sort_alpha_f) 
  #for p in l:
  #  p.print()
  #print()
  ## Remove duplicates
  i = 0
  while i < len(l) - 1:
    if l[i].word == l[i+1].word:
      if l[i].value > l[i+1].value:
        l.pop(i+1)
      else:
        l.pop(i)
    else:
      i += 1
  #l.sort(key=sort_len_f) 
  l.sort(key=sort_value_f) 
  tot = 0
  for p in l:
    p.print()
    tot = tot + p.value

  print("%d words, %d total points"%(len(l), tot))

  quit()

  for i,j in it.product(range(w),range(w)):
    visit(grid[i][j], [])

