#
# Send Sound Pressure Level to OVH IoT PaaS as OpenTSDB Metrics
#
# USB reverse-engineering of WENSN WS1361 SPL Meter courtesy of http://www.ebswift.com/reverse-engineering-spl-usb.html
# Python code to send to OpenTDSB courtesy of https://github.com/runabove/iot-push-examples/tree/master/Python
#
# sends the following metrics:
# moving average of sound level: soundLevel
# peak of sound level: soundLevel.peak
#
import sys
import usb.core #from pyusb
import time
import numpy
from array import array
import requests
import json

#these modules come from here: https://github.com/runabove/iot-push-examples/tree/master/Python
from OpenTSDBProfile import OpenTSDBProfile
from OpenTSDBPusherHttp import OpenTSDBPusherHttp
from Metric import Metric

#HTTP Proxy
proxies = {}
#proxies = {
#          'http': 'http://proxyhost:proxyport',
#          'https': 'http': 'http://proxyhost:proxyport'
#        }

#OpenTSDB write ID from https://cloud.runabove.com/#/iot/
writeID = "My_writeID"
#OpenTSDB key
key = "My_WriteKey"
#OpenTSDB URL
url = "https://opentsdb.iot.runabove.io/api/put"
#OpenTSDB port
port = 443


#5 minutes moving average window length (one sound pressure level scan per 2 seconds)
#the very first data point is sent after 10 minutes (2 times the interval)
movingAverageWindowLength = 150
count = 1
peak = 0

dev = usb.core.find(idVendor=0x16c0, idProduct=0x5dc)
assert dev is not None
print (dev)
print (hex(dev.idVendor) + ', ' + hex(dev.idProduct))


class RingBuffer():
    "A 1D ring buffer using numpy arrays"
    def __init__(self, length):
        self.data = numpy.zeros(length, dtype='f')
        self.index = 0

    def extend(self, x):
        "adds array x to ring buffer"
        x_index = (self.index + numpy.arange(x.size)) % self.data.size
        self.data[x_index] = x
        self.index = x_index[-1] + 1

    def get(self):
        "Returns the first-in-first-out data in the ring buffer"
        idx = (self.index + numpy.arange(self.data.size)) %self.data.size
        return self.data[idx]


def runningMeanFast(x, n):
    return numpy.convolve(x, numpy.ones((n,))/n, mode='valid')[(n-1):]

def sendMetricToOpenTSDB(metricName,value,writeID,key,url,port,proxies):
        profile = OpenTSDBProfile(writeID,key,url,port)
        pusher = OpenTSDBPusherHttp()
        timestamp = int(time.time())
        metric = Metric(metricName,value,timestamp,{})
        pusher.pushData(profile,metric,proxies);

buffer = RingBuffer(movingAverageWindowLength * 2)
a = array('f')



#Main loop, runs once every 2s
while True:
        #read Sound level from SPL Meter
	ret = dev.ctrl_transfer(0xC0, 4, 0, 0, 200)
	dB = (ret[0] + ((ret[1] & 3) * 256)) * 0.1 + 30

	if dB > peak:
		peak = dB

	#print ("dB= {}".format(dB))
	
	a.append(dB)
	mAvg = runningMeanFast(a,movingAverageWindowLength)

	if(count >= 2 * movingAverageWindowLength and (count % movingAverageWindowLength == 0)):
                mAvgDB = int(mAvg[-1])
                #print ("moving Avg= {}".format(mAvgDB))
                sendMetricToOpenTSDB("soundLevel",mAvgDB,writeID,key,url,port,proxies)
                sendMetricToOpenTSDB("soundLevel.peak",peak,writeID,key,url,port,proxies)
                count = 0
                peak = 0
        #no need to scan SPL Meter faster since it outputs a 2s moving average of SPL                
	time.sleep(2)
	count = count + 1

