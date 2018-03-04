import subprocess
import re

__cpuCommand = """awk -v a="$(awk '/cpu /{print $2+$4,$2+$4+$5}' /proc/stat; sleep 1)" '/cpu /{split(a,b," "); print 100*($2+$4-b[1])/($2+$4+$5-b[2])}'  /proc/stat"""
__temperatureCommand = "vcgencmd measure_temp"
__reg = re.compile(r"(\d+.\d+)")


def getCPU():
    try:
        p = subprocess.Popen(__cpuCommand,
                             stdout=subprocess.PIPE,
                             shell=True)
        output = p.communicate()[0].decode('ascii').rstrip()
        result = p.wait()
        if result != 0:
            raise
    except Exception as e:
        print("Caught exception: {0}".format(str(e)))
        output = 0
    return output


def getTemperature():
    p = subprocess.Popen(__temperatureCommand,
                         stdout=subprocess.PIPE,
                         shell=True)
    output = p.communicate()[0].decode('ascii')
    result = p.wait()

    if(result != 0):
        raise
    regmatch = __reg.search(output)
    return regmatch.group(0)


def getMemory():
    pass
