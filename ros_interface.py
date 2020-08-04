import roslaunch
import rospy
import subprocess
import sys
import signal
import psutil
from time import sleep


def launch_turtlesim():
    global _uuid, _launch
    rospy.init_node('en_Mapping', anonymous=True)
    _uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
    roslaunch.configure_logging(_uuid)
    _launch = roslaunch.parent.ROSLaunchParent(_uuid, [
        "/home/will/PycharmProjects/turtlesim_webui/launch/launch_turtlesim.launch"])
    _launch.start()
    rospy.loginfo("turtlesim started")
    try:
        _launch.spin()
    finally:
        _launch.shutdown()

def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
        print(parent)
    except psutil.NoSuchProcess:
        print("parent process not existing")
        return
    children = parent.children(recursive=True)
    print(children)
    for process in children:
        print("try to kill child: " + str(process))
        process.send_signal(sig)


class Roscore(object):
    """
    roscore wrapped into a subprocess.
    Singleton implementation prevents from creating more than one instance.
    """
    __initialized = False

    def __init__(self):
        if Roscore.__initialized:
            raise Exception("You can't create more than 1 instance of Roscore.")
        Roscore.__initialized = True

    def run(self):
        try:
            self.roscore_process = subprocess.Popen(['roscore'])
            self.roscore_pid = self.roscore_process.pid  # pid of the roscore process (which has child processes)
        except OSError as e:
            sys.stderr.write('roscore could not be run')
            raise e

    def terminate(self):
        print("try to kill child pids of roscore pid: " + str(self.roscore_pid))
        kill_child_processes(self.roscore_pid)
        self.roscore_process.terminate()
        self.roscore_process.wait()  # important to prevent from zombie process
        Roscore.__initialized = False
