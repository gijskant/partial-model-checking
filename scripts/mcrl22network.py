#! /usr/bin/env python3
# :noTabs=true:
# (c) Copyright (c) 2015-2018  Gijs Kant
"""
mcrl22network.py

Brief: Generates LPS files and a network file from a mCRL2 specification.

Usage: mcrl22network.py <example.mcrl2>

Authors:
 -  Gijs Kant <mail@gijskant.nl>
"""

from network import *


class Console:
    """
    A helper class for displaying messages on the console (stderr).
    """

    Black = '\033[30m'
    BlackBackground = '\033[40m'
    Blue = '\033[94m'
    Green = '\033[92m'
    GreenBackground = '\033[42m'
    Yellow = '\033[93m'
    YellowBackground = '\033[103m'
    Red = '\033[91m'
    RedBackground = '\033[41m'
    Grey = '\033[37m'
    Reset = '\033[0m'

    @staticmethod
    def title(title):
        print('%s%s%s' % (Console.Blue, title, Console.Reset), file=sys.stderr)

    @staticmethod
    def success(message):
        print('%s%s%s' % (Console.Green, message, Console.Reset), file=sys.stderr)

    @staticmethod
    def error(message):
        print('%s%sError%s%s: %s%s' %
              (Console.RedBackground, Console.Black, Console.Reset, Console.Grey, message, Console.Reset),
              file=sys.stderr)

    @staticmethod
    def warning(message):
        print('%s%sWarning%s%s: %s%s' %
              (Console.YellowBackground, Console.Black, Console.Reset, Console.Grey, message, Console.Reset),
              file=sys.stderr)

    @staticmethod
    def info(message):
        print(message, file=sys.stderr)


MCRL2_KEYWORDS = ['sort', 'cons', 'map', 'eqn', 'var', 'glob']
MCRL2_SPLITTERS = ['.', '+', '(', ')', '->', '<>']


class Mcrl22Network:
    """
    Reads a mCRL2 specification and generates for a separate mCRL2 file for each
    process and linearises that process specification, and generates a network file
    with a list of processes and a synchronisation vector.
    """

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
    lin_options = ""  # mcrl2 linearisation options
    bindir = ""  # directory where mcrl2 binaries are

    def add_label(self, label, label_type):
        if label not in self.types:
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
        assert (len(h) > 1)
        assert (h[0].strip() == "")
        h = h[1].split("}", 1)
        assert (len(h) > 1)
        comm = h[0].strip()
        c = comm.split(",")
        for sync in c:
            s = sync.split("->")
            sync_pair = s[0].split("|")
            result_action = s[1].strip()
            assert (len(sync_pair) == 2)
            triple = (sync_pair[0].strip(), sync_pair[1].strip(), result_action)
            self.comm.add(triple)
        spec = h[1].strip()
        assert (spec[0] == ",")
        spec = spec[1:]
        # print "comm:", self.comm
        # print "spec:", spec
        self.process_init(spec, ['hide', 'allow', 'comm'])

    def process_allow(self, allow_decl):
        # print "allow:", allow_decl
        allow_decl = allow_decl.strip()
        h = allow_decl.split("{", 1)
        assert (len(h) > 1)
        assert (h[0].strip() == "")
        h = h[1].split("}", 1)
        assert (len(h) > 1)
        allows = h[0].strip()
        spec = h[1].strip()
        assert (spec[0] == ",")
        spec = spec[1:]
        for a in allows.split(","):
            a = a.strip()
            if not a == "":
                self.allow.add(a)
        # print "allow:", allows
        # print "spec:", spec
        self.process_init(spec, ['hide', 'allow'])

    def process_hide(self, hide_decl):
        # print "hide:", hide_decl
        hide_decl = hide_decl.strip()
        h = hide_decl.split("{", 1)
        assert (len(h) > 1)
        assert (h[0].strip() == "")
        h = h[1].split("}", 1)
        assert (len(h) > 1)
        hides = h[0].strip()
        spec = h[1].strip()
        assert (spec[0] == ",")
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
            if p[0] in invalid_statements:
                Console.error("Statement %s not allowed here." % p[0])
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
            procs = i.split("||")
            self.processes = []
            for proc in procs:
                proc = proc.strip()
                if not proc == "":
                    self.processes.append(proc)
            Console.info("Processes: %s" % self.processes)

    def process_init_decl(self):
        # print "init:", self.init_decl
        i = self.init_decl.strip()
        if not i[-1:] == ';':
            Console.error("Error: not in correct form. ';' expected.")
        i = i[:-1]
        self.process_init(i, [])

    def process_proc_decl(self):
        if len(self.labels) == 0:
            Console.warning("No action labels found. Are process declared before the action declaration?")

        p = self.proc_decl.split(";")
        # find process names
        for proc in p:
            proc = proc.strip()
            proc_eq = proc.split("=", 1)
            if len(proc_eq) == 2:
                assert (len(proc_eq) == 2)
                t = proc_eq[0]
                t = t.split("(", 1)
                proc_name = t[0].strip()
                self.proc_names.add(proc_name)

        # find process references and action labels
        for proc in p:
            proc = proc.strip()
            proc_eq = proc.split("=", 1)
            if len(proc_eq) == 2:
                t = proc_eq[0]
                t = t.split("(", 1)
                proc_name = t[0].strip()
                proc_params = ""
                if len(t) > 1:
                    proc_params = t[1].strip()
                    assert (proc_params[-1:] == ")")
                    proc_params = proc_params[:-1]
                proc_body = proc_eq[1]
                Console.info("proc: %s" % proc_name)
                # print("params:", proc_params)
                # print("body:", proc_body)
                x = [proc_body]
                for s in MCRL2_SPLITTERS:
                    y = []
                    for v in x:
                        w = v.split(s)
                        for z in w:
                            z = z.strip()
                            if not z == "":
                                y.append(z)
                    x = y
                # print("tokens:", x)
                x = set(x)
                proc_actions = x & self.labels
                self.proc_actions[proc_name] = proc_actions
                proc_refs = x & self.proc_names
                self.proc_refs[proc_name] = proc_refs
                # print("intersection:", x)
                Console.info("proc %s has action labels: %s" % (proc_name, str(proc_actions)))
                Console.info("proc %s refers to: %s" % (proc_name, proc_refs))

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
        # for proc in self.proc_names:
        #   print "proc",proc,"uses action labels:", self.proc_actions[proc]

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

    def parse_mcrl2(self, mcrl2_filename):
        Console.info("Parsing file: %s" % mcrl2_filename)
        self.init_parser()
        self.line = 0
        with open(mcrl2_filename) as mcrl2_file:
            for line in mcrl2_file:
                self.line = self.line + 1
                line = line.strip()
                c = line.split("%", 1)
                if len(c) > 0:
                    line = c[0]
                    # print "Line:", line
                    p = line.split(None, 1)
                    if len(p) > 0:
                        for k in MCRL2_KEYWORDS:
                            if p[0] == k:
                                self.process_data()
                    if len(p) > 0 and p[0] == 'act':
                        self.process_data()
                        self.act = True
                        if len(p) > 1:
                            self.act_decl = p[1]
                        line = ""
                    elif len(p) > 0 and p[0] == 'init':
                        self.process_data()
                        self.init = True
                        self.init_line = self.line
                        if len(p) > 1:
                            self.init_decl = p[1]
                        line = ""
                    elif len(p) > 0 and p[0] == 'proc':
                        self.process_data()
                        self.proc = True
                        if len(p) > 1:
                            self.proc_decl = p[1]
                        line = ""
                    if self.act:
                        # parse action types
                        self.act_decl += line
                    elif self.init:
                        # parse init declaration
                        self.init_decl += line
                    elif self.proc:
                        # parse process declaration
                        self.proc_decl += line
        self.process_data()

    def get_proc_name(self, proc):
        name = self.proc_name_map.get(proc)
        if name is None:
            s = proc.split("(")
            name = s[0]
            self.proc_name_map[proc] = name
        return name

    def get_proc_filename(self, proc):
        proc_filename = self.proc_filename_map.get(proc)
        if proc_filename is None:
            name = self.get_proc_name(proc)
            n = 0
            if name in self.proc_filename_n:
                n = self.proc_filename_n[name]
            n = n + 1
            self.proc_filename_n[name] = n
            proc_filename = name + '_' + str(n)
            self.proc_filename_map[proc] = proc_filename
        return proc_filename

    def generate_vector(self):
        Console.info("Computing synchronization vector...")
        vector_elements = []
        i = 1
        # Compute local actions
        for proc in self.processes:
            Console.info("Generate local actions for proc %s" % proc)
            proc_name = self.get_proc_name(proc)
            for action in (self.proc_actions[proc_name] & self.allow):
                elements = {proc: action}
                if action in self.hide:
                    label = "tau" + str(i)
                    elements["comm"] = label
                    self.types[label] = self.types[action]
                    i = i + 1
                else:
                    elements["comm"] = action
                vector_elements.append(elements)

        # Maps actions to processes
        action_procs = {}
        for proc in self.processes:
            for a in self.proc_actions[self.get_proc_name(proc)]:
                if not a in action_procs:
                    action_procs[a] = set()
                action_procs[a].add(proc)
        # Compute synchronizing actions
        for synchronisation in self.comm:
            # print "comm:",c
            action1 = synchronisation[0]
            action2 = synchronisation[1]
            result_action = synchronisation[2]
            if action1 in action_procs and action2 in action_procs:
                # print "candidates for a1:", action_procs[a1]
                # print "candidates for a2:", action_procs[a2]
                for p1 in action_procs[action1]:
                    for p2 in action_procs[action2]:
                        if not p1 == p2 and result_action in self.allow:
                            elements = {p1: action1, p2: action2}
                            if result_action in self.hide:
                                label = "tau" + str(i)
                                elements["comm"] = label
                                self.types[label] = self.types[result_action]
                                i = i + 1
                            else:
                                elements["comm"] = result_action
                            vector_elements.append(elements)
        # print "Vector elements:", vector_elements
        return print_vector(self.processes, self.types, vector_elements)

    def __init__(self, lin_method):
        self.lin_method = lin_method

    def write_network(self, f):
        Console.info("Writing network for processes: %s" % self.processes)
        f.write('length\n')
        f.write(str(len(self.processes)))
        f.write('\n')
        f.write('lps_filenames\n')
        for proc in self.processes:
            f.write(self.get_proc_filename(proc) + '.lps\n')
        f.write('synchronization_vector\n')
        f.write(self.generate_vector())
        f.write('\n')

    def generate_process_files(self, mcrl2_filename):
        procs = self.processes
        Console.info("Writing process files for processes: %s" % procs)
        files = {}
        for proc in procs:
            proc_filename = self.get_proc_filename(proc) + ".mcrl2"
            proc_file = open(proc_filename, 'w')
            files[proc] = proc_file

        with open(mcrl2_filename) as mcrl2_file:
            i = 1
            for l in mcrl2_file:
                if i >= self.init_line:
                    break
                for pf in iter(files.values()):
                    pf.write(l)
                i = i + 1
            if i < self.init_line:
                Console.warning("Warning: not all %d lines read." % self.init_line)

        for proc in procs:
            pf = files[proc]
            pf.write("init " + proc + ";\n")
            pf.close()
            Console.info("Process %s written to: %s.mcrl2" % (proc, self.get_proc_filename(proc)))

        Console.info("Linearising processes...")
        for proc in procs:
            # Linearise processes
            cmd = self.bindir + 'mcrl22lps -v ' + lin_options + ' ' + \
                  self.get_proc_filename(proc) + '.mcrl2 ' + \
                  self.get_proc_filename(proc) + '.lps'
            Console.info(cmd)
            res = os.system(cmd)
            if not res == 0:
                break
            cmd = self.bindir + 'lpsconstelm -v ' + \
                  self.get_proc_filename(proc) + '.lps ' + \
                  self.get_proc_filename(proc) + '.lps'
            Console.info(cmd)
            res = os.system(cmd)
            if not res == 0:
                break
            cmd = self.bindir + 'lpsrewr -v ' + \
                  self.get_proc_filename(proc) + '.lps ' + \
                  self.get_proc_filename(proc) + '.lps'
            Console.info(cmd)
            res = os.system(cmd)
            if not res == 0:
                break

    def generate_delta(self):
        # Generate delta process
        delta_file = open('delta.txt', 'w')
        delta_file.write('''proc P = delta;
    
    init P;
    ''')
        delta_file.close()
        os.system(self.bindir + 'txt2lps delta.txt delta.lps')


def usage():
    Console.info("Usage: %s <file.mcrl2> [linearisation options]" % os.path.basename(sys.argv[0]))
    Console.info("")
    Console.info("Generates a network file <file.net> and required .mcrl2 and .lps filed.")
    Console.info("Default linearisation options: -f -lregular2")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        sys.exit(2)

    filename = sys.argv[1]
    model_name = os.path.splitext(os.path.basename(filename))[0]
    if len(sys.argv) > 2:
        lin_options = sys.argv[2]
    else:
        lin_options = "-f -lregular2 -n"

    Console.title('mcrl22network')

    Console.info("Linearisation options: %s" % lin_options)
    parser = Mcrl22Network(lin_options)
    # parse mcrl2 file
    parser.parse_mcrl2(filename)
    # write synchronization vector
    parser.generate_vector()
    # generate process files
    parser.generate_process_files(filename)
    # write network file
    network_filename = model_name + '.net'
    f = open(network_filename, 'w')
    parser.write_network(f)
    f.close()
    Console.info("Network written to: %s" % network_filename)
