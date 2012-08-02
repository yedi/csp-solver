csp-solver
=============

csp-solver is a constraint satisfaction problem solver that uses various optimization techniques.

Requirements
------------
You need to have python installed. Preferably 2.7

Usage
------------

    ~$ python csp.py [FILEPATH] <[OPTIONS]>

__All optimization options default to False.__

    Options:
      -h, --help    show this help message and exit
      -m, --mrv     Use MRV optimization
      -l, --lcv     Use LCV
      -d, --degree  Use Degree heuristics (has priority over -l)
      -c, --fc      Use forward checking
      -a, --ac3      Use AC-3 checking
      -v, --verbose  Enables trace of how to solve the problem.

The FILEPATH is the location of the CSP problem file. The command line options provide the ON/OFF functionality of the various optimizations for the CSP problem. For example, to solve test_17.txt with forward checking, MRV, and degree heuristics, one may call:
    ~$ python csp.py test_17.txt -c -m -d