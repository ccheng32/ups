/* LSTF: Author - Radhika Mittal, UC Berkeley, radhika@eecs.berkeley.edu */

#include <math.h>
#include <sys/types.h>
#include "config.h"
#include "template.h"
#include "random.h"
#include "lstf.h"
#include "tcp.h"
#include "rtp.h"

//#include "docsislink.h"

static class LstfClass : public TclClass {
public:
    LstfClass()
        : TclClass("Queue/Lstf")
    {
    }
    TclObject* create(int, const char* const*)
    {
        return (new LstfQueue);
    }
} class_Lstf;

std::ofstream LstfQueue::ofs_usage;
bool LstfQueue::print_n_queues = false;

LstfQueue::LstfQueue()
    : queueid_(-1)
    , tchan_(0)
{

    bind("curq_", &curq_); // current queue size in bytes
    bind("debug_", &debug_); // tcl settable ma
    bind("queueid_", &queueid_);
    bind("kTime_", &kTime_);
    bind("control_packets_", &control_packets_);
    bind("control_packets_time_", &control_packets_time_);
    bind("bandwidth_", &bandwidth_);

    // initialize queues
    for (int i = 0; i <= LSTF_NUM_QUEUES; i++) {
        bin_[i].q_ = new PacketQueue();
        bin_[i].index = i;
    }

    delta = MAX_SLACK/LSTF_NUM_QUEUES;

    for (int i = 1; i <= LSTF_NUM_QUEUES; ++i){
        q_bounds_[i] = i*delta;
    }

    for (int i = 0; i <= LSTF_NUM_QUEUES; ++i){
	q_max_[i] = 10000000000000;
    }

    if (!LstfQueue::ofs_usage.is_open()){
        ofs_usage.open("usage.txt");
    }

    if (!LstfQueue::print_n_queues){
	ofs_usage << LSTF_NUM_QUEUES << '\n';
	print_n_queues = true;
    }
    
    pq_ = bin_[0].q_; //does ns need this?
    reset();
}

void LstfQueue::reset()
{
    curq_ = 0;
    curlen_ = 0;

    // initialize q_curlen_.
    for (int i = 0; i <= LSTF_NUM_QUEUES; i++) {
        q_curlen_[i] = 0;
    } 
        
    // initialize q_curq_.
    for (int i = 0; i <= LSTF_NUM_QUEUES; i++) {
        q_curq_[i] = 0;
    }

    last_rotation_time = 0;

    Queue::reset();
}

double LstfQueue::txtime(Packet* p)
{
    return (8. * hdr_cmn::access(p)->size() / bandwidth_);
}

void LstfQueue::rotateQueues(){
    for (int i = 0; i < LSTF_NUM_QUEUES; ++i){
        while ((bin_[i+1].q_)->length()){
	    (bin_[i].q_)->enque((bin_[i+1].q_)->deque());
	}
    }
}

// Add a new packet to the queue. If the entire buffer space is full, drop highest slack packet
void LstfQueue::enque(Packet* pkt)
{
    // If delta time has passed since last rotation and queue 0 is empty, rotate the queues.
    long long int time_since_last_rotate = (long long int)(Scheduler::instance().clock() * kTime_) - last_rotation_time;
    if (time_since_last_rotate > delta && !((bin_[0].q_)->length())){
	rotateQueues();
	last_rotation_time = (long long int)(Scheduler::instance().clock() * kTime_);
	fprintf(stderr, "Rotating queues %lld past delta = %lld\n", time_since_last_rotate - delta, delta);
    }

    // Get slack value of incoming packet.
    hdr_ip* iph = hdr_ip::access(pkt);
    int seqNo = getSeqNo(pkt);
    long long int curSlack = iph->prio() + (long long int)(txtime(pkt) * kTime_);  

    // Find queue to which packet belongs.
    int i = 1;
    while (i < LSTF_NUM_QUEUES && q_bounds_[i] < curSlack) i++;
    assert(1 <= i && i <= LSTF_NUM_QUEUES);

    LstfQueue::ofs_usage << i << "\n";

    // Drop packet if the buffer is full. 
    if (q_curlen_[i] >= q_max_[i]){
         assert(0);         // should never drop packets
         drop(pkt);
         return;
    }

    // Increment (whole) queue count and buffer size.
    curq_ += HDR_CMN(pkt)->size();
    curlen_++;

    // Increment bin packet count and buffer size.
    q_curq_[i] += HDR_CMN(pkt)->size();
    q_curlen_[i]++;
     
    // Timestamp packet with arrival time.
    HDR_CMN(pkt)->ts_ = Scheduler::instance().clock(); 

    // Enqueue packet into queue.
    (bin_[i].q_)->enque(pkt);

    if (debug_)
        printf("%lf: Lstf: QueueID %d: Enqueuing packet from flow with id %d, seqno = %d, size = %d and slack = %lld \n", Scheduler::instance().clock(), queueid_, iph->flowid(), seqNo, HDR_CMN(pkt)->size(), iph->prio());

}

Packet* LstfQueue::deque()
{
    if (curlen_ > 0) {
        for (int i = 0; i <= LSTF_NUM_QUEUES; i++) {
            if ((bin_[i].q_)->length() > 0) {
		// Deque the packet.
                Packet* pkt;
                pkt = (bin_[i].q_)->deque();
                int seqNo = getSeqNo(pkt);
                hdr_ip* iph = hdr_ip::access(pkt);

		// Decrement (whole) queue count and buffer size.
                curlen_--;
                curq_ -= HDR_CMN(pkt)->size();

		// Decrement bin packet count and buffer size.
                q_curlen_[i]--;
                q_curq_[i] -= HDR_CMN(pkt)->size();

		// Assign new slack value to packet.
                long long int wait_time = (Scheduler::instance().clock() * kTime_) - (long long int)(HDR_CMN(pkt)->ts_ * kTime_);

                long long int new_slack = iph->prio() - wait_time;

                iph->prio() = new_slack;

                // If delta time has passed since last rotation and queue 0 is empty, rotate the queues.
                long long int time_since_last_rotate = (long long int)(Scheduler::instance().clock() * kTime_) - last_rotation_time;
                if (time_since_last_rotate > delta && !((bin_[0].q_)->length())){
                    rotateQueues();
                    last_rotation_time = (long long int)(Scheduler::instance().clock() * kTime_);
                    fprintf(stderr, "Rotating queues %lld past delta = %lld\n", time_since_last_rotate - delta, delta);
                }

                if (debug_)
                    printf("%lf: Lstf: QueueID %d: Dequing packet from flow with id %d, slack %lld, seqno = %d, size = %d \n", Scheduler::instance().clock(), queueid_, iph->flowid(), iph->prio(), seqNo, HDR_CMN(pkt)->size());

                return pkt;
            }
        }
    }
    return 0;
}

int LstfQueue::command(int argc, const char* const* argv)
{
    Tcl& tcl = Tcl::instance();

    if (argc == 2) {
        if (strcmp(argv[1], "reset") == 0) {
            reset();
            return (TCL_OK);
        }
    } else if (argc == 3) {
        // attach a file for variable tracing
        if (strcmp(argv[1], "attach") == 0) {
            int mode;
            const char* id = argv[2];
            tchan_ = Tcl_GetChannel(tcl.interp(), (char*)id, &mode);
            if (tchan_ == 0) {
                tcl.resultf("Lstf trace: can't attach %s for writing", id);
                return (TCL_ERROR);
            }
            return (TCL_OK);
        }
        // connect LSTF to the underlying queue
        if (!strcmp(argv[1], "packetqueue-attach")) {
            //            delete q_;
            //            if (!(q_ = (PacketQueue*) TclObject::lookup(argv[2])))
            printf("error in command\n");
            return (TCL_ERROR);
            //            else {
            //                pq_ = q_;
            //                return (TCL_OK);
            //            }
        }
    }
    return (Queue::command(argc, argv));
}

// Routine called by TracedVar facility when variables change values.
// Note that the tracing of each var must be enabled in tcl to work.
void LstfQueue::trace(TracedVar* v)
{
    const char* p;

    if ((p = strstr(v->name(), "curq")) == NULL) {
        fprintf(stderr, "Lstf: unknown trace var %s\n", v->name());
        return;
    }
    if (tchan_) {
        char wrk[500];
        double t = Scheduler::instance().clock();
        if (*p == 'c') {
            sprintf(wrk, "c %g %d", t, int(*((TracedInt*)v)));
        }
        int n = strlen(wrk);
        wrk[n] = '\n';
        wrk[n + 1] = 0;
        (void)Tcl_Write(tchan_, wrk, n + 1);
    }
}
