# usbsplloop
Adaptation of the usbsplloop.py found here http://www.ebswift.com/reverse-engineering-spl-usb.html to send data to an OpenTSDB server

#Usage
The following variables need to be configured:

```
#OpenTSDB write ID from https://cloud.runabove.com/#/iot/
writeID = "My_writeID"
#OpenTSDB key
key = "My_WriteKey"
#OpenTSDB URL
url = "https://opentsdb.iot.runabove.io/api/put"
#OpenTSDB port
port = 443
```

You may also configure the data sending period:
```
#5 minutes moving average window length (one sound pressure level scan per 2 seconds)
#the very first data point is sent after 10 minutes (2 times the interval)
movingAverageWindowLength = 150
```

The script is run via
```
python usbsplloop.py
```

On Windows, to run without a console windows, the script is run via
```
pythonw usbsplloop.py
```


#Viewing Data
Data may be viewed via a tool such as Grafana for instance, connected to your OpenTSDB server:
![Alt text](images/screenshot.png?raw=true "Screenshot")
