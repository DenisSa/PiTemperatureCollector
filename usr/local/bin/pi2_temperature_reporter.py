import subprocess
from datetime import datetime
import socket
import requests
import re
import time
import configparser
import argparse


class pi2_temperature_reporter:
    __temperatureCommand = "vcgencmd measure_temp"
    __influxDB_db = "rpi_temperature"
    __influxDB_write_url = "http://localhost:8086/write?"

    def __init__(self, configpath):
        config = configparser.ConfigParser()
        if configpath:
            config.read(configpath)
            self.__influxDB_db = config['DEFAULT']['influxDB_db']
            self.__influxDB_write_url = config['DEFAULT']['influxDB_write_url']

    def run(self):
        while True:
            try:
                temperature = self.getTemperature()
                timeUTC = self.getTimeUTC()
                uid = self.getUID()
                self.submitHtmlPost(uid, temperature, timeUTC)
            except Exception as e:
                print "Caught exception - {0}".format(e)
            finally:
                time.sleep(60)

    def getTemperature(self):
        reg = re.compile(r"(\d+.\d+)")
        p = subprocess.Popen(self.__temperatureCommand,
                             stdout=subprocess.PIPE,
                             shell=True)
        output = p.communicate()[0]
        result = p.wait()

        if(result != 0):
            raise
        regmatch = reg.search(output)
        return regmatch.group(0)

    def getTimeUTC(self):
        return datetime.utcnow()

    def getUID(self):
        return socket.gethostname()

    def submitHtmlPost(self, uid, temperature, timeUTC):
        url = "{0}db={1}".format(self.__influxDB_write_url, self.__influxDB_db)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = "internal_temperature,host={0} value={1}\n".format(uid, temperature)
        r = requests.post(url, data=payload, headers=headers)
        print "Got response: {0}".format(r.status_code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Report Internal Temperature')
    parser.add_argument('configpath', help="Path to config file")
    args = parser.parse_args()
    pi2_temperature_reporter(args.configpath).run()
