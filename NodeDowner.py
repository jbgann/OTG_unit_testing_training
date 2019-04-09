from threading import Thread
import time
import subprocess
import nid_tools
import nagios_tools
import sys

def verify_and_report(nid):
    time.sleep(90)
    if "down" in nid_tools.get_state(nid):
      nagios.make_alarm(host=nid,state=critical,
                        message="Node refused to go down")

def down_and_follow_up(nid,reason="Stuck in a completing state"):
    subprocess.call("scontrol update NodeName='%s' state=down reason='%s'" %
                    (nid,message))
    followup = Thread(verify_and_report,args=(nid,))
    return followup

#This line is useful for several different reasons
#What it does is makes sure all the code under the if statement
#is run if, and only if, the module was invoked directly
#The indented code will not run if the module is merely imported,
#as the module will take the name "NodeDowner"
#Consider adding this to all your code, as importing happens in a
#wide variety of circumstances, such as unittesting, borrowing features
#from a command line tool without using the tool itself, multiprocessing
#and unpickling. In this example, run from the command line, this module is a
#simple untility that tries to down a node, spawns a daemon to followup, and
#returns control to the user. However, if you wanted to automate the node downing
#process, this module could be imported (and the code below would not run),
#and the importing code would be responsible for managing the followup threads
if __name__ == "__main__":
    node_to_down = sys.ARGV[1]
    wait_thread = down_and_follow_up(node_to_down)
    wait_thread.daemon = True
    wait_thread.start()
