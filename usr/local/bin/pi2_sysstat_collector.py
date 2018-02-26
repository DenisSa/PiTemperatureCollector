import subprocess

_cpuCommand = """awk -v a="$(awk '/cpu /{print $2+$4,$2+$4+$5}' /proc/stat; sleep 1)" '/cpu /{split(a,b," "); print 100*($2+$4-b[1])/($2+$4+$5-b[2])}'  /proc/stat"""


def getCPU():
    try:
        p = subprocess.Popen(_cpuCommand,
                             stdout=subprocess.PIPE,
                             shell=True)
        output = p.communicate()[0].rstrip()
        result = p.wait()
        if result != 0:
            raise
    except Exception as e:
        print "Caught exception: {0}".format(str(e))
        output = 0
    return output


def getMemory():
    pass
