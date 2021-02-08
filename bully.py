
from multiprocessing import Process, Value, Array
import os
import math
import time
import zmq
import numpy as np
from abc import ABC, abstractmethod
import re
import sys, getopt
import threading
import sys
from random import randrange
from random import sample 


def responder(id):
    global stop_thread
    pid=os.getpid()
    ctx = zmq.Context()
    sock = ctx.socket(zmq.SUB)
    print("Responder Starts "+(str(id)))
    global starts
    global responses
    
    for alive in alive_list:
        sock.connect("tcp://127.0.0.1:"+str(5500+alive))

    sock.setsockopt_string(zmq.SUBSCRIBE, "LEADER") # subscribe to time topic
    sock.setsockopt_string(zmq.SUBSCRIBE, "TERMINATION") # subscribe to time topic

    while True:
        msg = sock.recv_string()
        new_mes=msg.split("+")
        new_mes_cur=new_mes[1]
        responses[id].append(int(new_mes_cur))
        if int(new_mes_cur)<id:
            starts[id]=True
            print("RESPONDER RESPONDS "+str(id)+" " +new_mes_cur)
        if "TERMINATION" in msg:
            stop_thread=True
        if stop_thread==True:
            break


    print("End of listening thread",id)
    sock.close()
    ctx.term()

    
 
    





def Leader(id):
    global starts

    start=starts[id]
    send_check=False

    pid = os.getpid()
    ctx = zmq.Context()
    sock = ctx.socket(zmq.PUB)
    sock.bind("tcp://127.0.0.1:"+str(5500+id))
    global stop_thread

    print("Process Starts: "+str(pid)+" "+str(id)+" "+str(start))
    listener_thread=threading.Thread(target=responder ,args=(id,))
    listener_thread.start()
    time.sleep(3)
    termination=False
    while termination==False:
        start=starts[id]
        if start and not send_check:
            msg = "LEADER +"+str(id)
            sock.send_string(msg)
            print("PROCESS MULTICAST LEADER MSG:"+str(id))
            time.sleep(1)
            send_check=True
            max_val=max(responses[id])
            if max_val==id:
                msg = "TERMINATION +"+str(id)
                sock.send_string(msg)
                print("PROCESS BROADCAST TERMINATE MSG:"+str(id))
                termination=True
                stop_thread=True


            
        if stop_thread==True:
            break




            
    print("End of the Leader Process",pid)
    sock.close()
    ctx.term()
 





termination=False
stop_thread=False
numProc=range(0,int(sys.argv[1]))
alive_list=sample(numProc,int(sys.argv[2]))
starter_list=sample(alive_list,int(sys.argv[3]))

responses= [ [-1] for i in range(int(sys.argv[1]))]


print(alive_list,"alive")
print(starter_list,"starter")

starts=[]
starts= [ False for i in range(int(sys.argv[1]))]
for starter in starter_list:
    starts[starter]=True

for current_node in alive_list:
    if current_node in starter_list:
        p = Process(target=Leader, args=(current_node, ))
        p.start()
    else:
        p=Process(target=Leader,args=(current_node,))
        p.start() 
 









    