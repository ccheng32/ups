## Reproducing UPS Results for the default scenario

Instructions for reproducing UPS results on the default scenario (Internet2 1Gbps-10Gbps topology, 70% link utilization)

#### General:
1. Clone the UPS repository.
2. cd ns-allinone-2.35
3. sudo apt-get install xorg-dev (if needed)
4. sudo apt-get install gcc-4.4 g++-4.4 (if needed)
5. export CC=gcc-4.4 CXX=g++-4.4
6. ./install
7. cd ns-2.35
8. Open Makefile and replace "queue/sfq.o queue/fq.o queue/drr.o queue/srr.o queue/cbq.o" with "queue/sfq.o queue/fq.o queue/drr.o queue/srr.o queue/cbq.o queue/sfqcodel.o queue/random-dequeue.o queue/lifo.o queue/lstf.o queue/edge-replay.o queue/edge-tail-pkt-delay-lstf.o queue/fine-priorities.o queue/srpt.o queue/edge-fq-lstf.o"
9. make clean; make 
10. Scripts to run various experiments can be found in ns-allinone-2.35/ns-2.35/tcl/ex/ups/scripts. All scripts should be run from this directory.
11. Results for various experiments get stored in specific directories in ns-allinone-2.35/ns-2.35/tcl/ex/ups/


The scripts and results directories for various experiments are listed below. Specific details about result format can be found in the README files in the specific result directory. The total time taken to run each script (on a machine with 2.6GHz processor and atleast 5GB memory) has also been reported.

#### LSTF replay for Random, FIFO, LIFO and FQ
- Script: ns-allinone-2.35/ns-2.35/tcl/ex/ups/scripts/replay-internet2-1Gbps-10Gbps.sh
- Results directory: ns-allinone-2.35/ns-2.35/tcl/ex/ups/replay-results
- Time taken: 2-3hrs 

#### Mean FCTs
- Script: ns-allinone-2.35/ns-2.35/tcl/ex/ups/scripts/meanfcts-tcp-internet2-1Gbps-10Gbps.sh
- Results directory: ns-allinone-2.35/ns-2.35/tcl/ex/ups/meanfcts-results
- Time taken: 11-12hrs 

#### Tail Packet Delays
- Script: ns-allinone-2.35/ns-2.35/tcl/ex/ups/scripts/tail-pkt-delays-internet2-1Gbps-10Gbps.sh
- Results directory: ns-allinone-2.35/ns-2.35/tcl/ex/ups/tail-pkt-delays-results
- Time taken: 9-10hrs 

#### Long-lived fairness
- Script: ns-allinone-2.35/ns-2.35/tcl/ex/ups/scripts/fairness-longlived-internet2-10Gbps-10Gbps.sh
- Results directory: ns-allinone-2.35/ns-2.35/tcl/ex/ups/fairness-results/longlived/
- Time taken: 9-10mins

#### Short-term fairness
- Script: ns-allinone-2.35/ns-2.35/tcl/ex/ups/scripts/fairness-shortterm-internet2-1Gbps-10Gbps.sh  
- Results directory: ns-allinone-2.35/ns-2.35/tcl/ex/ups/fairness-results/shortterm/
- Time taken: 18-19hrs

#### AQM: FQ-CoDel
- Script: ns-allinone-2.35/ns-2.35/tcl/ex/ups/scripts/fqcodel-internet2-1Gbps-10Gbps.sh
- Results directory: ns-allinone-2.35/ns-2.35/tcl/ex/ups/fqcodel-results/
- Time taken: 8-9hrs

Please contact me at radhika @ eecs dot berkeley dot edu
- if you would like to run experiments under more scenarios as done in the paper. I can send you the required workloads and topologies, along with further instructions.
- if you happen to find a bug!
- if you have any other questions
