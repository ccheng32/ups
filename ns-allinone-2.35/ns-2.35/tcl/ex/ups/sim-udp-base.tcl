# Adapted by Radhika from code written by Anirudh/Keith/Hari

#!/bin/sh
# the next line finds ns \
nshome=`dirname $0`; [ ! -x $nshome/ns ] && [ -x ../../../ns ] && nshome=../../..
# the next line starts ns \
export nshome; exec $nshome/ns "$0" "$@"

if [info exists env(nshome)] {
	set nshome $env(nshome)
} elseif [file executable ../../../ns] {
	set nshome ../../..
} elseif {[file executable ./ns] || [file executable ./ns.exe]} {
	set nshome "[pwd]"
} else {
	puts "$argv0 cannot find ns directory"
	exit 1
}
set env(PATH) "$nshome/bin:$env(PATH)"

source opt-sender-udp.tcl

proc Getopt {} {
    global opt argc argv
    for {set i 0} {$i < $argc} {incr i} {
        set key [lindex $argv $i]
        if ![string match {-*} $key] continue
        set key [string range $key 1 end]
        set val [lindex $argv [incr i]]
        set opt($key) $val
        if [string match {-[A-z]*} $val] {
            incr i -1
            continue
        }
    }
}

proc create-topology {topofoldername} {
    global ns opt nodes gw d nshome nends ncores ntotal nlinks 


    set fp [open "$topofoldername/topo.txt"]
    set topofile_data [read $fp]
    close $fp
    set fp [open "$topofoldername/endhosts.txt"]
    set endfile_data [read $fp]
    close $fp
    set topolines [split $topofile_data "\n"]
    set endlines [split $endfile_data "\n"]
    set ntotal [lindex $topolines 0]
    set nlinks [lindex $topolines 1]
    set nends [lindex $endlines 0]
    set ncores [expr $ntotal - $nends]

    puts " Core = $ncores and Endhosts = $nends " 

    for {set i 0} {$i < $ntotal} {incr i} {
       set nodes($i) [$ns node]
    }
    
    for {set i 0} {$i < $nlinks} {incr i} {
       set j [expr $i + 2]
       set words [split [lindex $topolines $j]]
       set n1 [split [lindex $words 0]]
       set n2 [split [lindex $words 1]]
       set bw [split [lindex $words 2]]
       append bw "Mb"
       set delay [split [lindex $words 3]]
       
       if [info exists opt(us_delay)] {
          append delay "us"
       } else {
          append delay "ms"
       }

       if { $n2 < $ncores } {
          $ns duplex-link $nodes($n1) $nodes($n2) $bw $delay $opt(gw) 
          if { [info exists opt(queueLogTime)] } {
               $ns queue-log-time $nodes($n1) $nodes($n2) $opt(queueLogTime)
               $ns queue-log-time $nodes($n2) $nodes($n1) $opt(queueLogTime)
          } 
          $ns queue-n1 $nodes($n1) $nodes($n2) $n1
          $ns queue-n2 $nodes($n1) $nodes($n2) $n2
          $ns queue-n1 $nodes($n2) $nodes($n1) $n2
          $ns queue-n2 $nodes($n2) $nodes($n1) $n1
          $ns queue-limit $nodes($n1) $nodes($n2) $opt(maxq)
          $ns queue-limit $nodes($n2) $nodes($n1) $opt(maxq)
       } else {
          $ns simplex-link $nodes($n1) $nodes($n2) $bw $delay $opt(gw)
          $ns simplex-link $nodes($n2) $nodes($n1) $bw $delay DropTail
          if { [info exists opt(queueLogTime)] } {
               $ns queue-log-time $nodes($n1) $nodes($n2) $opt(queueLogTime)
          } 
          $ns queue-n1 $nodes($n1) $nodes($n2) $n1
          $ns queue-n2 $nodes($n1) $nodes($n2) $n2
          $ns queue-limit $nodes($n1) $nodes($n2) $opt(maxq)
          $ns queue-limit $nodes($n2) $nodes($n1) 100000000
       }
        	
    }

}

proc create-sources-sinks {workloadfile} {
      global ns opt src recvapp tp f nflows nends ncores nodes

      set numsrc $nends
      set fp [open $workloadfile r]
     set file_data [read $fp]
     close $fp
     set data [split $file_data "\n"]
     set nflows_file [expr [llength $data] - 1] 
     set nflows 0
     for {set i 0} {$i < $nflows_file} {incr i} {
     	set words [split [lindex $data $i]]
	if { [llength $words] > 0 } {
		set sendtime [lindex $words 0]
		set flowsize [lindex $words 1]
		set sender [lindex $words 2]
		set destination [lindex $words 3]
		if { $sendtime < $opt(simtime) } {		
			set j $nflows
        		#puts "At $sendtime time send $flowsize bytes from $sender to $destination"


        		set tp($j) [$ns create-connection-list "UDP" $nodes($sender) "UDP" $nodes($destination) $j]
        		set udpsrc($j) [lindex $tp($j) 0]
        		set udpsink($j) [lindex $tp($j) 1]
        		$udpsrc($j) set packetSize_ $opt(pktsize)
                        if { [info exists opt(pct_log)] } {
        		  $udpsrc($j) set pct_log_ $opt(pct_log)
                        } 
        
			set src($j) [ $udpsrc($j) attach-app FTP/OptSenderUDP  ]
        		$src($j) setup_and_start 0 $j $flowsize $sendtime $opt(simtime)
			set nflows [expr $nflows + 1]
		}
	}

    }
}

proc finish {} {
    global ns opt src nflows linuxcc
    global f
    if { [info exists f] } {
        $ns flush-trace
        close $f           
    }                                                                                                       
    exit 0
}


## MAIN ##

Getopt


set ns [new Simulator]

if { [info exists opt(sjfPrio)] } {
  Agent/UDP set sjfPrio_mode_ $opt(sjfPrio)
} 


if { [info exists opt(codel_target)] } {
  Queue/sfqCoDel set target_ $opt(codel_target)
}
if { [info exists opt(maxbins)] } {
  Queue/sfqCoDel set maxbins_ $opt(maxbins)
}

create-topology $opt(topofolder) 
create-sources-sinks "$opt(topofolder)/$opt(workloadfile)"

$ns at $opt(simtime) "finish"
$ns run

