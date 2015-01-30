#! /usr/bin/env python
import os
import sys
import re
from network import *

class Mcrl22Network:

  keywords = ['sort', 'cons', 'map', 'eqn', 'var', 'glob']

  init = False
  act = False
  proc = False
  act_decl = ""
  init_decl = ""
  proc_decl = ""
  types = {}
  labels = set()
  proc_names = set()
  proc_actions = {}
  proc_refs = {}
  hide = set()
  comm = set()
  allow = set()
  processes = []
  proc_name_map = {}
  proc_filename_map = {}
  proc_filename_n = {}
  line = 0
  init_line = -1
  lin_options = "" # mcrl2 linearisation options

  def add_label(self, label, label_type):
    if not self.types.has_key(label):
      self.types[label] = set()
    self.types[label].add(label_type)
    self.labels.add(label)

  def process_act_decl(self):
    a_list = self.act_decl.split(";")
    for a in a_list:
      a = a.strip()
      if not a == "":
        t = a.split(":")
        labels = ""
        label_type = ""
        if len(t) > 0:
          labels = t[0].strip()
        if len(t) > 1:
          label_type = t[1].strip()
        for l in labels.split(","):
          label = l.strip()
          if not label == "":
            self.add_label(label, label_type)

  def process_comm(self, comm_decl):
    # print "comm:", comm_decl
    comm_decl = comm_decl.strip()
    h = comm_decl.split("{", 1)
    assert(len(h) > 1)
    assert(h[0].strip() == "")
    h = h[1].split("}", 1)
    assert(len(h) > 1)
    comm = h[0].strip()
    comm_triples = []
    c = comm.split(",")
    for sync in c:
      s = sync.split("->")
      sync_pair = s[0].split("|")
      result_action = s[1].strip()
      assert(len(sync_pair)==2)
      triple = (sync_pair[0].strip(), sync_pair[1].strip(), result_action) 
      self.comm.add(triple)
    spec = h[1].strip()
    assert(spec[0] == ",")
    spec = spec[1:]
    # print "comm:", self.comm
    # print "spec:", spec
    self.process_init(spec, ['hide','allow','comm'])

  def process_allow(self, allow_decl):
    # print "allow:", allow_decl
    allow_decl = allow_decl.strip()
    h = allow_decl.split("{", 1)
    assert(len(h) > 1)
    assert(h[0].strip() == "")
    h = h[1].split("}", 1)
    assert(len(h) > 1)
    allows = h[0].strip()
    spec = h[1].strip()
    assert(spec[0] == ",")
    spec = spec[1:]
    for a in allows.split(","):
      a = a.strip()
      if not a == "":
        self.allow.add(a)
    # print "allow:", allows
    # print "spec:", spec
    self.process_init(spec, ['hide','allow'])

  def process_hide(self, hide_decl):
    # print "hide:", hide_decl
    hide_decl = hide_decl.strip()
    h = hide_decl.split("{", 1)
    assert(len(h) > 1)
    assert(h[0].strip() == "")
    h = h[1].split("}", 1)
    assert(len(h) > 1)
    hides = h[0].strip()
    spec = h[1].strip()
    assert(spec[0] == ",")
    spec = spec[1:]
    for h in hides.split(","):
      h = h.strip()
      if not h == "":
        self.hide.add(h)
    # print "hide:", self.hide
    # print "spec:", spec
    self.process_init(spec, ['hide'])

  def process_init(self, decl, invalid_statements):
    i = decl.strip()
    p = i.split("(", 1)
    parse_procs = False
    if len(p) > 1:
      p[0] = p[0].strip()
      if not p[1][-1:] == ')':
        print "error: not in correct form:", p[0]
      if p[0] in invalid_statements:
        print "statement", p[0], "not allowed here."
      elif p[0] == 'hide':
        self.process_hide(p[1][:-1])
      elif p[0] == 'allow':
        self.process_allow(p[1][:-1])
      elif p[0] == 'comm':
        self.process_comm(p[1][:-1])
      else:
        parse_procs = True
    else:
      parse_procs = True
    if parse_procs:
      # print "Process declaration:",i
      p = i.split("||")
      self.processes = []
      for proc in p:
        proc = proc.strip()
        if not proc == "":
          self.processes.append(proc)
          proc_name = self.get_proc_name(proc)
      print "Processes:", self.processes


  def process_init_decl(self):
    # print "init:", self.init_decl
    i = self.init_decl.strip()
    if not i[-1:] == ';':
      print "error: not in correct form. ';' expected."
    i = i[:-1]
    self.process_init(i, [])

  def process_proc_decl(self):
    p = self.proc_decl.split(";")
    # find process names
    for proc in p:
      proc = proc.strip()
      proc_eq = proc.split("=", 1)
      if len(proc_eq)==2:
        assert(len(proc_eq)==2)
        t = proc_eq[0]
        t = t.split("(", 1)
        proc_name = t[0].strip()
        self.proc_names.add(proc_name)

    # find process references and action labels
    for proc in p:
      proc = proc.strip()
      proc_eq = proc.split("=", 1)
      if len(proc_eq)==2:
        t = proc_eq[0]
        t = t.split("(", 1)
        proc_name = t[0].strip()
        proc_params = ""
        if len(t)>1:
          proc_params = t[1].strip()
          assert(proc_params[-1:]==")")
          proc_params = proc_params[:-1]
        proc_body = proc_eq[1]
        print "proc:", proc_name
        # print "params:", proc_params 
        # print "body:", proc_body
        splitters = ['.','+','(',')','->','<>']
        x = [proc_body]
        y = []
        for s in splitters:
          y = []
          for v in x:
            w = v.split(s)
            for z in w:
              z = z.strip()
              if not z == "":
                y.append(z)
          x = y
        # print "tokens:", x
        x = set(x)
        proc_actions = x & self.labels
        self.proc_actions[proc_name] = proc_actions
        proc_refs = x & self.proc_names
        self.proc_refs[proc_name] = proc_refs
        # print "intersection:", x
        print "proc", proc_name, "has action labels:", proc_actions
        print "proc", proc_name, "refers to:", proc_refs
    
    # fixpoint computation for action label propagation
    # print "Propagating action labels"
    fixpoint = False
    while not fixpoint:
      fixpoint = True
      for p1 in self.proc_names:
        # print "Considering proc", p1
        for p2 in self.proc_refs[p1]:
          for a in self.proc_actions[p2]:
            if not a in self.proc_actions[p1]:
              # print "* add",a,"from",p2,"to actions of", p1
              fixpoint = False
              self.proc_actions[p1].add(a)
    #for proc in self.proc_names:
    #  print "proc",proc,"uses action labels:", self.proc_actions[proc]


  def process_data(self):
    if self.act:
      self.process_act_decl()
    elif self.init:
      self.process_init_decl()
    elif self.proc:
      self.process_proc_decl()
    self.init_parser()
   
  def init_parser(self):
    self.init = False
    self.act = False
    self.proc = False
    self.act_decl = ""
    self.init_decl = ""
    self.proc_decl = ""
      
  def parse_mcrl2(self, filename):
    print "Parsing file:", filename
    self.init_parser()
    types = []
    hide = []
    comm = []
    allow = []
    self.line = 0
    with open(filename) as f:
      for l in f:
        self.line = self.line + 1
        l = l.strip()
        c = l.split("%", 1)
        if len(c) > 0:
          l = c[0]
          # print "Line:", l
          p = l.split(None, 1)
          if len(p) > 0:
            for k in self.keywords:
              if p[0] == k:
                self.process_data()
          if len(p) > 0 and p[0] == 'act':
            self.process_data()
            self.act = True
            if len(p) > 1: 
              self.act_decl = p[1]
            l = ""
          elif len(p) > 0 and p[0] == 'init':
            self.process_data()
            self.init = True
            self.init_line = self.line
            if len(p) > 1: 
              self.init_decl = p[1]
            l = ""
          elif len(p) > 0 and p[0] == 'proc':
            self.process_data()
            self.proc = True
            if len(p) > 1:
              self.proc_decl = p[1]
            l = ""
          if self.act:
            # parse action types
            self.act_decl += l	
          elif self.init:
            # parse init declaration
            self.init_decl += l
          elif self.proc:
            # parse process declaration
            self.proc_decl += l
    self.process_data()

  def get_proc_name(self, proc):
    name = self.proc_name_map.get(proc)
    if name is None:
      s = proc.split("(")
      name = s[0]
      self.proc_name_map[proc] = name
    return name

  def get_proc_filename(self, proc):
    filename = self.proc_filename_map.get(proc)
    if filename is None:
      name = self.get_proc_name(proc)
      n = 0
      if name in self.proc_filename_n:
        n = self.proc_filename_n[name]
      n = n + 1
      self.proc_filename_n[name] = n
      filename = name + '_' + str(n)
      self.proc_filename_map[proc] = filename
    return filename

  def generate_vector(self):
    print "Computing synchronization vector..."
    vector_elements = []
    procs = list(self.processes)
    n = len(procs)
    i = 1
    # Compute local actions
    for proc in self.processes:
      #print "Generate local actions for proc", proc
      for a in (self.proc_actions[self.get_proc_name(proc)] & self.allow):
        e = {proc: a}
        if a in self.hide:
          l = "tau"+str(i)
          e["comm"] = l
          self.types[l] = self.types[a]
          i = i + 1
        else:
          e["comm"] = a
        vector_elements.append(e)
    # Maps actions to processes    
    action_procs = {}
    for proc in self.processes:
      for a in self.proc_actions[self.get_proc_name(proc)]:
        if not a in action_procs:
          action_procs[a] = set()
        action_procs[a].add(proc)
    # Compute synchronizing actions
    for c in self.comm:
      #print "comm:",c
      a1 = c[0]
      a2 = c[1]
      r = c[2]
      if a1 in action_procs and a2 in action_procs:
        #print "candidates for a1:", action_procs[a1]
        #print "candidates for a2:", action_procs[a2]
        for p1 in action_procs[a1]:
          for p2 in action_procs[a2]:
            if not p1 == p2 and r in self.allow:
              e = {p1: a1, p2: a2}
              if r in self.hide:
                l = "tau"+str(i)
                e["comm"] = l
                self.types[l] = self.types[r]
                i = i + 1
              else:
                e["comm"] = r
              vector_elements.append(e)
    # print "Vector elements:", vector_elements
    return print_vector(self.processes, self.types, vector_elements)


  def __init__(self, lin_method):
    self.lin_method = lin_method


  def write_network(self, f):
    f.write('length\n')
    f.write(str(len(self.processes)))
    f.write('\n')
    f.write('lps_filenames\n')
    for proc in self.processes:
      f.write(self.get_proc_filename(proc)+'.lps\n')
    f.write('synchronization_vector\n')
    f.write(self.generate_vector())
    f.write('\n')


  def generate_process_files(self, mcrl2_filename):
    procs = set(self.processes)
    files = {}
    for proc in procs:
      filename = self.get_proc_filename(proc) + ".mcrl2"
      procfile = open(filename, 'w')
      files[proc] = procfile

    with open(mcrl2_filename) as f:
      i = 1
      for l in f:
        if i >= self.init_line:
          break
        for pf in files.itervalues():
          pf.write(l)
        i = i + 1
      if i < self.init_line:
        print "Warning: not all", self.init_line, "line read."
    for proc in procs:
      pf = files[proc]
      pf.write("init "+proc+";\n")
      pf.close()
      print "Process written to:", self.get_proc_filename(proc)+".mcrl2"
    print "Linearising processes..."
    res = 0
    for proc in procs:
      # Linearise processes
      cmd = 'mcrl22lps -v '+lin_options+' ' + \
          self.get_proc_filename(proc)+'.mcrl2 ' + \
          self.get_proc_filename(proc)+'.lps'
      print cmd
      res = os.system(cmd)
      if not res==0:
        break
      cmd = 'lpsconstelm -v ' + \
          self.get_proc_filename(proc)+'.lps ' + \
          self.get_proc_filename(proc)+'.lps'
      print cmd
      res = os.system(cmd)
      if not res==0:
        break
      cmd = 'lpsrewr -v ' + \
          self.get_proc_filename(proc)+'.lps ' + \
          self.get_proc_filename(proc)+'.lps'
      print cmd
      res = os.system(cmd)
      if not res==0:
        break



def generate_delta():
  # Generate delta process
  f = open('delta.txt', 'w')
  f.write('''proc P = delta;

init P;
''')
  f.close()
  os.system('txt2lps delta.txt delta.lps')


if __name__ == '__main__':
  if len(sys.argv) > 1:
    filename = sys.argv[1]
    modelname = os.path.splitext(os.path.basename(filename))[0]
    if len(sys.argv) > 2:
      lin_options = sys.argv[2]
    else:
      lin_options = "-f -lregular2"
    print "Linearisation options:", lin_options
    parser = Mcrl22Network(lin_options)
    # parse mcrl2 file
    parser.parse_mcrl2(filename)
    # write synchronization vector
    parser.generate_vector()
    # generate process files
    parser.generate_process_files(filename)
    # write network file
    network_filename = modelname+'.net'
    f = open(network_filename, 'w')
    parser.write_network(f)
    f.close()
    print "Network written to:", network_filename
