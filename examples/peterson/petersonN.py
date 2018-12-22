#! /usr/bin/env python3
# :noTabs=true:
# (c) Copyright (c) 2015-2018  Gijs Kant
"""
petersonN.py

Brief: Generates an instance of the Peterson mutual exclusion algorithm
for n parties as mCRL2 specification.

Usage: petersonN.py <n>

Authors:
 - Gijs Kant <mail@gijskant.nl>
"""

import os
import sys


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


class Peterson:
    """
    Templates for generating the mcrl2 files.
    """

    HeaderTemplate = '''
% This is a model of Peterson's mutual exclusion algorithm for {n} processes.
%

map N: Pos;
eqn N = {n};
'''

    ProcessActionsTemplate = '''    TRY{i}, ENTER{i}, LEAVE{i};
'''

    ActionsTemplate = '''
% Actions
act setLevelReq, setLevelRes, setLevel, getLevelReq, getLevelRes, getLevel: Pos#Nat;
    setLastReq, setLastRes, setLast, getLastReq, getLastRes, getLast: Pos#Pos;
    exists_otherReq, exists_otherRes, exists_other: Pos#Nat#Bool;
{proc_actions}'''

    LevelsProcessTemplate = '''% Levels process
% 0: not set
% 1..N:
proc Levels({levels}: Nat) =
    {summands}
    ;'''

    LastProcessTemplate = '''
% Last process
proc Last({levels}: Pos) =
    {summands}
    ;'''

    PetersonProcessTemplate = '''
% Process Peterson{i}
proc ProcWait{i}(l: Pos) =
    sum i0: Pos . (i0 <= N) -> getLastReq(l, i0) . (
        (i0 != {i}) -> ProcLoop{i}(l + 1)
        <> (
            exists_otherReq({i}, l, false) . ProcLoop{i}(l + 1)
            + exists_otherReq({i}, l, true) . ProcWait{i}(l)
        )
    );

proc ProcLoop{i}(l: Pos) =
    (l == N + 1) -> (ENTER{i} . LEAVE{i} . setLevelReq({i}, 0) . Peterson{i})
    <> setLevelReq({i}, l) . (
        (l == 1) -> TRY{i} . setLastReq(l, {i})
        <> setLastReq(l, {i})
    ) . ProcWait{i}(l);

proc Peterson{i} = ProcLoop{i}(1);
'''

    InitTemplate = '''
init hide( {{{hides}}},
         allow({{{allows}}},
             comm({{{comm}}},
                 {procs}
             )));
'''

    @staticmethod
    def generateLevels(n_procs):
        levels = []
        levels_summands = []
        last_summands = []
        for i in range(1, n_procs + 1):
            levels.append('l{i}'.format(i=i))
            levels_summands.append('''sum l: Nat . (l <= N) -> setLevelRes({i}, l) . Levels(l{i} = l)'''.format(i=i))
            levels_summands.append('''getLevelRes({i}, l{i}) . Levels()'''.format(i=i))
            inequalities = []
            for j in range(1, n_procs + 1):
                if i != j:
                    inequalities.append('l{j} >= l'.format(j=j))
            levels_summands.append('''sum l: Nat . (l <= N) -> exists_otherRes({i}, l, {unequalities}). Levels()'''.format(
                i=i, unequalities=' || '.join(inequalities)))
            last_summands.append('''sum l: Pos . (l <= N) -> setLastRes({i}, l) . Last(l{i} = l)'''.format(i=i))
            last_summands.append('''getLastRes({i}, l{i}) . Last()'''.format(i=i))

        print(Peterson.LevelsProcessTemplate.format(
            levels=', '.join(levels),
            summands='\n    + '.join(levels_summands)))

        print(Peterson.LastProcessTemplate.format(
            levels=', '.join(levels),
            summands='\n    + '.join(last_summands)))

    @staticmethod
    def generate(n_procs):
        print(Peterson.HeaderTemplate.format(n=n_procs))
        proc_actions = ''
        for i in range(1, n_procs + 1):
            proc_actions += Peterson.ProcessActionsTemplate.format(i=i)
        print(Peterson.ActionsTemplate.format(proc_actions=proc_actions))
        Peterson.generateLevels(n_procs)
        for i in range(1, n_procs + 1):
            print(Peterson.PetersonProcessTemplate.format(i=i))
        procs = []
        procs.append('Levels(%s)' % ', '.join([str(0)] * n_procs))
        procs.append('Last(%s)' % ', '.join([str(1)] * n_procs))
        for i in range(1, n_procs + 1):
            procs.append('Peterson{i}'.format(i=i))
        hides = ['setLevel', 'setLast', 'exists_other', 'getLast', 'getLevel']
        allows = ['setLevel', 'setLast', 'exists_other', 'getLast', 'getLevel']
        for i in range(1, n_procs + 1):
            allows.append('TRY{i}'.format(i=i))
            allows.append('ENTER{i}'.format(i=i))
            allows.append('LEAVE{i}'.format(i=i))
        comm = ['setLevelReq|setLevelRes -> setLevel',
                'getLevelReq|getLevelRes -> getLevel',
                'setLastReq|setLastRes -> setLast',
                'getLastReq|getLastRes -> getLast',
                'exists_otherReq|exists_otherRes -> exists_other']
        print(Peterson.InitTemplate.format(
            hides=', '.join(hides),
            allows=', '.join(allows),
            comm=', '.join(comm),
            procs=' || '.join(procs)
        ))


def usage():
    Console.info("Usage: %s <n>" % os.path.basename(sys.argv[0]))
    Console.info("")
    Console.info("Generates an instance of the Peterson mutual exclusion algorithm")
    Console.info("for <n> parties as mCRL2 specification.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        sys.exit(2)

    n = int(sys.argv[1])

    Console.title('peterson.%s' % n)

    Peterson.generate(n)

    Console.info('Done.')
