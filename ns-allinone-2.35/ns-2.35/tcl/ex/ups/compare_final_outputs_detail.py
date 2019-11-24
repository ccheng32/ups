import sys

# What the fuck is this file?
# Takes original pct, lstf pcts, init pcts, and outputs .compare and .ratios.

# arg format
# 1 is original pct, 2 is lstf pct, 3 is init pcts, 4 is .compare output, 5 is .ratios output

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

base_file = open(sys.argv[1]).readlines()
lstf_file = open(sys.argv[2]).readlines()
max_flow_id = 0

tmin = dict()
minTimes = open(sys.argv[3]).readlines()
for line in minTimes:
  words = line.split()
  tmin[(words[1],words[2])] = long(words[0])

out_file_compare = open(sys.argv[4], 'w')
out_file_ratios = open(sys.argv[5], 'w')

lstf_ts = dict()
for line in lstf_file:
  words = line.split()
  lstf_ts[(int(words[3]), int(words[4]))] = long(words[0])

count = 0
base_ts = dict()
for line in base_file:
  words = line.split()
  if(int(words[3]) > max_flow_id):
    max_flow_id = int(words[3])
  key = (int(words[3]), int(words[4]))
  base = tmin[(words[1], words[2])]
  pct_base = long(words[0]) - base
  if(pct_base < 0): #correcting 1ns rounding issues
    pct_base = 0
  try:
    pct_lstf = lstf_ts[key] - base
    if (pct_lstf < 0):
      pct_lstf = 0
    out_file_ratios.write(str(key[0]) + " " + str(key[1])  + " : " + " " + str(pct_lstf) + " " + str(pct_base) + " " + str(float(pct_lstf + 1)/float(pct_base + 1)) + " " + str(float(pct_lstf - pct_base)/float(pct_base + 1)) + "\n")
    if(pct_lstf > pct_base):
        count = count + 1
        out_file_compare.write(str(key[0]) + " " + str(key[1])  + " : " + str(base) + " " + str(pct_lstf) + " > " + str(pct_base) + " by " + str(long(pct_lstf) - long(pct_base)) + "\n")

  except:
      out_file_compare.write("Not in LSTF: " + str(key) + "\n")
out_file_compare.write(str(count) + " out of " + str(len(base_file)) + " ; Approx no. of flows = " + str(max_flow_id) + "\n")
