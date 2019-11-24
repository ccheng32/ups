import sys

# What the fuck is this file?
# Takes a .compare file, max_trans_time number (default 11680), and outputs late-packets file.

# arg format
# 1 is the .compare file, 2 is the max_trans_time number (default is 11680).

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

lines = open(sys.argv[1]).readlines()
max_trans_time = long(sys.argv[2])

delay = dict()
total = int(lines[-1].split()[3])
total_flows = int(lines[-1].split()[10])
total_delayed = int(lines[-1].split()[0])
flows = list()

not_reached = 0
for line in lines[:-1]:
  try:
    words = line.split()
    diff = long(words[8])
    if(diff in delay.keys()):
      delay[diff].append((words[0], int(long(words[3])/1000000), words[6]))
    else:
      delay[diff] = list()
      delay[diff].append((words[0], int(long(words[3])/1000000), words[6]))
  except:
    not_reached = not_reached + 1
  if (words[0] not in flows):
    flows.append(words[0])

#for key in sorted(delay.keys()):
#  if(key > 116800):
#	  print str(key) + " : " + str(delay[key])

print "***************************"


buckets = dict()
buckets["1ns"] = dict()
buckets["0-1"] = dict()
buckets["1"] = dict()
buckets["1-2"] = dict()
buckets["2"] = dict()
buckets[">2"] = dict()
buckets[">1"] = dict()
buckets["2-10"] = dict()
buckets["10-50"] = dict()
buckets["50-100"] = dict()
buckets[">100"] = dict()

for key in buckets.keys():
  buckets[key]["Total"] = 0
  buckets[key]["Flows"] = list()
  buckets[key]["Base Time"] = dict()
  buckets[key]["Max Delay"] = long(0)
  buckets[key]["Slack(ms)"] = dict()


for key in sorted(delay.keys()):
  if (key == 1):
    bucketid = "1ns"
  else:
    if (key < max_trans_time):
      bucketid = "0-1"
    else:
      if (key == max_trans_time):
          bucketid = "1"
      else:
       buckets[">1"]["Total"] = buckets[">1"]["Total"] + len(delay[key])
       if (key < 2 * max_trans_time):
          bucketid = "1-2"
       else:
          if (key == 2 * max_trans_time):
            bucketid = "2"
          else :
            buckets[">2"]["Total"] = buckets[">2"]["Total"] + len(delay[key])
            if (key <= 10 * max_trans_time):
              bucketid = "2-10"
            else:
              if (key <= 50 * max_trans_time):
                bucketid = "10-50"
              else:
                if (key <= 100 * max_trans_time):
                  bucketid = "50-100"
                else:
                  bucketid = ">100"

  if(key > buckets[bucketid]["Max Delay"]):
     buckets[bucketid]["Max Delay"] = key
  buckets[bucketid]["Total"] = buckets[bucketid]["Total"] + len(delay[key])
  for x in delay[key]:
     if(x[0] not in buckets[bucketid]["Flows"]):
        buckets[bucketid]["Flows"].append(x[0])
     if(x[1] not in buckets[bucketid]["Base Time"].keys()):
        buckets[bucketid]["Base Time"][x[1]] = 1
     else:
        buckets[bucketid]["Base Time"][x[1]] = buckets[bucketid]["Base Time"][x[1]] + 1

     slack_ms = int(float(x[2]) / 1000000)
     if (slack_ms not in buckets[bucketid]["Slack(ms)"].keys()):
         buckets[bucketid]["Slack(ms)"][slack_ms] = 1
     else:
         buckets[bucketid]["Slack(ms)"][slack_ms] =  buckets[bucketid]["Slack(ms)"][slack_ms] + 1

for key in buckets.keys():
  print "\n" + str(key) + ":"
  for key2 in buckets[key]:
    if(key2 == "Total"):
      print str(key2) + " : " + str(buckets[key][key2]) + " ( " + str(float(buckets[key][key2])*100/float(total)) + " ) "
    else:
      if (key2 == "Flows"):
        print "Num of Flows: " + str(len(buckets[key][key2]))
      else:
        print str(key2) + ": " + str(buckets[key][key2])


print "***************************"
print "Number of packets not finished: " + str(not_reached)
print "Flows Delayed " + str(len(flows)) + " = " + str(float(len(flows))*100/float(total_flows)) + "%"
print "Total Packets Delayed " + str(total_delayed) + " = " + str(float(total_delayed)*100/float(total)) + "%"
print "***************************"
