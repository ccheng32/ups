import sys

# What the fuck is this file?
# Takes init pcts, original pcts, and outputs slack values.

# arg format
# 1 is init pcts, 2 is original pcts, 3 is .slacks output

# pct format
# Format: <PCT in nanoseconds> <source id> <dest id> <flow id> <seq in no.of packets> <time when packet reaches dest in sec> <time when packet reaches dest in nanoseconds>

# fct format
# Format: <FCT in nanoseconds> <source id> <dest id> <flow id> <no. of packets in flow - 1> <time when flow finishes in sec>

# slacks format
# Format: <source id> <dest id> <flow id> <seq num in flow> <slack value>

# compare format
# Format: <flowid> <seq in no. of packets> : <congestion free PCT> <PCT with LSTF> >  <original PCT> by <Difference between the two PCTs>

# ratio format
# Format: <flowid> <seq in no. of packets> : <PCT with LSTF> <original PCT> <Ratio of the two PCTs> <Relative difference between the two PCTs>

# t_min[(src,dst)] is minimum time from src to dst in ns.
def get_t_min(init_pcts, t_min):

  for line in init_pcts:
    words = line.split()
    t_min[(words[1],words[2])] = long(words[0])


# deadlines[(src,dst,flow,seqnum)] = slack for packet seqnum in flow from src to dst.
def get_deadlines(sched_pcts, t_min, deadlines):
  for line in sched_pcts:
    words = line.split()
    deadline = long(words[6]) - t_min[(words[1],words[2])]
    deadlines[(words[1],words[2], words[3], words[4])] = deadline


if __name__ == "__main__":

  # open input and output files
  init_pcts = open(sys.argv[1]).readlines()
  sched_pcts = open(sys.argv[2]).readlines()
  outfile = open(sys.argv[3], "w")

  # t_min[(src,dst)] is minimum time from src to dst in ns.
  t_min = dict()
  get_t_min(init_pcts, t_min)

  # deadlines[(src,dst,flow,seqnum)] = slack for packet seqnum in flow from src to dst.
  deadlines = dict()
  get_deadlines(sched_pcts, t_min, deadlines)

  for key in deadlines.keys():
    outfile.write(key[0] + " " + key[1] + " " + key[2] + " " + key[3] + " " + str(deadlines[key]) + "\n")

