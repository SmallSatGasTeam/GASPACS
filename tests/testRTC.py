import sys
sys.path.append('../')
from Drivers.rtc import RTC
rtc = RTC()
print(rtc.read())
