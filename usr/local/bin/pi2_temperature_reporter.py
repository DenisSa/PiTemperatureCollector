import subprocess
from datetime import datetime
import socket
import re
import time
import configparser
import argparse
from influxdb import InfluxDBClient
import pi2_sysstat_collector as sysstat


class pi2_temperature_reporter:
    __temperatureCommand = "vcgencmd measure_temp"
    __influxDB_db = "rpi_metrics"
    __reg = re.compile(r"(\d+.\d+)")
    __influxDB_host = "localhost"
    __influxDB_port = 8086
    __poll_interval = 60

    def __init__(self, configpath):
        config = configparser.ConfigParser()
        if configpath:
            config.read(configpath)
            self.__influxDB_db = config['DEFAULT']['influxDB_db']
            self.__influxDB_host = config['DEFAULT']['influxDB_host']
            self.__poll_interval = int(config['DEFAULT']['poll_interval'])
            print "Database: {0} Host: {1} Poll interval: {2}".format(self.__influxDB_db, self.__influxDB_host, self.__poll_interval)

    def run(self):
        while True:
            try:
                cpu_load = sysstat.getCPU()
                temperature = self.getTemperature()
                uid = self.getUID()
                self.submitData(db=self.__influxDB_db, uid=uid,
                                temperature=temperature, cpu_load=cpu_load)
            except Exception as e:
                print "Caught exception - {0}".format(e)
            finally:
                time.sleep(self.__poll_interval)

    def submitData(self, db, uid, temperature=None, cpu_load=None):
        client = InfluxDBClient(database=db, host=self.__influxDB_host,
                                port=self.__influxDB_port)
        client.create_database(db)
        json_body = [
            {
                "measurement": db,
                "tags": {
                    "host": uid
                },
                "fields": {
                    "cpu_temperature": float(temperature),
                    "cpu_load": float(cpu_load)
                }
            }
        ]
        print "Writing {0}".format(json_body)
        client.write_points(json_body)
        client.close()

    def getTemperature(self):
        p = subprocess.Popen(self.__temperatureCommand,
                             stdout=subprocess.PIPE,
                             shell=True)
        output = p.communicate()[0]
        result = p.wait()

        if(result != 0):
            raise
        regmatch = self.__reg.search(output)
        return regmatch.group(0)

    def getTimeUTC(self):
        return datetime.utcnow()

    def getUID(self):
        return socket.gethostname()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Report Internal Temperature')
    parser.add_argument('configpath', help="Path to config file")
    args = parser.parse_args()
    pi2_temperature_reporter(args.configpath).run()
