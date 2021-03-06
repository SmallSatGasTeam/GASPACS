import sys
sys.path.append('../../')
import time
from Drivers.backupAntennaDeployer import BackupAntennaDeployer
from Drivers.antennaDoor import AntennaDoor
import Drivers.eps.EPS as EPS
import asyncio
from flightLogic.missionModes import safe
import flightLogic.getDriverData as getDriverData
from TXISR import pythonInterrupt


class antennaMode:

	def __init__(self, saveObject, safeModeObject):
		self.deployVoltage = 3 #Threshold voltage to deploy
		self.maximumWaitTime = 30 #Maximum time to wait for deployment before going to SAFE
		self.timeWaited = 0 #Time already waited - zero
		self.__getTTNCData = getDriverData.TTNCData(saveObject)
		self.__getAttitudeData = getDriverData.AttitudeData(saveObject)
		self.__tasks = [] #List will be populated with background tasks to cancel them
		self.__safeMode = safeModeObject
		self.__antennaDeployer = BackupAntennaDeployer()
		self.__antennaDoor = AntennaDoor()


	async def run(self):
		print('Antenna Deploy Running!')
		self.__tasks.append(asyncio.create_task(pythonInterrupt.interrupt()))
		self.__tasks.append(asyncio.create_task(self.__getTTNCData.collectTTNCData(1))) #Antenna deploy is mission mode 1
		self.__tasks.append(asyncio.create_task(self.__getAttitudeData.collectAttitudeData()))
		self.__tasks.append(asyncio.create_task(self.__safeMode.thresholdCheck())) #Check battery conditions, run safe mode if battery drops below safe level
		eps=EPS()
		while True: #Runs antenna deploy loop
			if (eps.getBusVoltage()>self.deployVoltage):
				await asyncio.gather(self.__antennaDeployer.deployPrimary()) #Fire Primary Backup Resistor
				doorStatus = self.__antennaDoor.readDoorStatus() #Check Door status
				if doorStatus == (1,1,1,1): #probably need to change this to actually work
					self.cancelAllTasks(self.__tasks)
					print('Doors are open, returning true')
					return True
				else:
					print('Firing secondary, primary did not work. Returning True')
					await asyncio.gather(self.__antennaDeployer.deploySecondary())
					self.cancelAllTasks(self.__tasks)
					return True
			else:
				if(self.timeWaited > self.maximumWaitTime):
					self.__safeMode.run(10) #1 hour
					await asyncio.sleep(5) #This is an artifact of testing, and will not matter for the actual flight software
				else:
					#Wait 1 minute
					print('Waiting 1 minute until battery status resolves')
					self.timeWaited = self.timeWaited+1
					await asyncio.sleep(60)



	def cancelAllTasks(self, taskList):
		try:
			for t in taskList:
				t.cancel()
		except asyncio.exceptions.CancelledException:
			print("Caught thrown exception in cancelling background task")
