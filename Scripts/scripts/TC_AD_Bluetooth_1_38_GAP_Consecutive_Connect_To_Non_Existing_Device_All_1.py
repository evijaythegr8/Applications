#
#=BEGIN
#
# This file is part of the Bluetooth use-case verification
#
# Copyright (C) ST-Ericsson SA 2010. All rights reserved.
#
# This code is ST-Ericsson proprietary and confidential.
# Any use of the code for whatever purpose is subject to
# specific written permission of ST-Ericsson SA.
#
#=END
#
import setup_paths
import sys, os
curdir = os.path.realpath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(curdir + "/.."))

from includes.BluetoothTestCase import BluetoothTestCase

from core.session.Session import Session
from core.general.Exceptions import Error, Failure
from includes.BluetoothOpCodes import OpCodes
from includes.BluetoothTestComponent import BluetoothTestComponent
from includes.BluetoothConstants import BluetoothConstants as BTC
from string import find
import time,re


class TC_AD_Bluetooth_1_38_GAP_Consecutive_Connect_To_Non_Existing_Device_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        iterations = int(Session.getSetupFileParam('bt', 'gapiterations'))

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)
        time.sleep(5)

        #Check the bond state
        self.SendCommand(ComponentOne, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 1')
        foundDevices = self.WaitForEventAndStore(ComponentOne, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        if len(foundDevices) != 0:
            TestException("Paired device list not empty for ComponentOne")
        self.SendCommand(ComponentTwo, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 2')
        foundDevices = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        if len(foundDevices) != 0:
            TestException("Paired device list not empty for ComponentTwo")

        #Bond devices
        self.PairDevices(ComponentOne, ComponentTwo, deviceOneAddress, deviceTwoAddress, timeout=30)
        time.sleep(2)

        #Check the bond state
        self.SendCommand(ComponentOne, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 1')
        foundDevices = self.WaitForEventAndStore(ComponentOne, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        targetString = "%s;%s"%(deviceTwoName,deviceTwoAddress)
        targetFound = self.MatchStringInList(foundDevices, targetString)
        if not targetFound:
            self.log.info("Target device not found")
            raise Failure('Target device not found')
        else:
            self.log.info("Device found")
            self.log.info(foundDevices)

        #Check the bond state
        self.SendCommand(ComponentTwo, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 2')
        foundDevices = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        targetString = "%s;%s"%(deviceOneName,deviceOneAddress)
        targetFound = self.MatchStringInList(foundDevices, targetString)
        if not targetFound:
            self.log.info("Target device not found")
            raise Failure('Target device not found')
        else:
            self.log.info("Device found")
            self.log.info(foundDevices)

        #Create BluetoothServerSocket on Server (create service) "00001101-0000-1000-8000-00805F9B34FB" = SPP
        serverId = self.SendAndWaitForEvent(ComponentTwo, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='SPP;%s'%BTC.SERVICE_SERIAL_PORT_PROFILE, timeout=30)

        #Create BluetoothSocket on Client
        clientId = self.SendAndWaitForEvent(ComponentOne, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, message='%s;%s'%(deviceTwoAddress,BTC.SERVICE_SERIAL_PORT_PROFILE), timeout=30)
        time.sleep(5)

        #Disable BT on device 2
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.DISABLE_BT, OpCodes.CURR_STATE_OFF, message='Disable BT App %s'%ComponentTwo, timeout=30)

        #repeat Connect
        for i in range(0,iterations):
            self.log.info('Iteration: %s of %s'%(i+1,iterations))
            self.log.info('Iteration %s'%(i+1))

            #Try to connec to the disabled device 2 (should fail)
            try:
                self.SendAndWaitForEvent(ComponentOne, OpCodes.RFCOMM_CONNECT, OpCodes.RFCOMM_CONNECT, message=clientId, timeout=20)
                time.sleep(2)
                self.log.info("Connected which should not occur")
                raise Failure('Connected which should not occur')
            except:
                self.log.info("Failed to connect as it should")
                time.sleep(2)

        #Enable BT on device 2
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.ENABLE_BT_API, OpCodes.CURR_STATE_ON, message='Enable BT App %s'%ComponentTwo, timeout=30)

        #Close connection
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message=serverId, timeout=30)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.CLOSE_CONNECTION_CLIENT, OpCodes.CLOSE_CONNECTION_CLIENT, message=clientId, timeout=30)

        #Do a proper connect

        #Create BluetoothServerSocket on Server (create service) "00001101-0000-1000-8000-00805F9B34FB" = SPP
        serverId = self.SendAndWaitForEvent(ComponentTwo, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='SPP;%s'%BTC.SERVICE_SERIAL_PORT_PROFILE, timeout=30)

        #Create BluetoothSocket on Client
        clientId = self.SendAndWaitForEvent(ComponentOne, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, message='%s;%s'%(deviceTwoAddress,BTC.SERVICE_SERIAL_PORT_PROFILE), timeout=30)

        #Connect the service
        self.SendCommand(ComponentTwo, OpCodes.RFCOMM_ACCEPT, message='60000;%s'%serverId)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.RFCOMM_CONNECT, OpCodes.RFCOMM_CONNECT, message=clientId)
        time.sleep(5)

        #Close connection
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.CLOSE_CONNECTION_SERVER, OpCodes.CLOSE_CONNECTION_SERVER, message=serverId, timeout=30)
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message=serverId, timeout=30)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.CLOSE_CONNECTION_CLIENT, OpCodes.CLOSE_CONNECTION_CLIENT, message=clientId, timeout=30)

        #Clean up
        self.RestoreApplication(ComponentOne)
        self.RestoreApplication(ComponentTwo)
        self.CloseDownExecution()


if __name__ == '__main__':
    from core.script.Script                   import Script
    from core.setup.Environment               import Environment
    from plugins.android.device.AndroidDevice import AndroidDevice

    Session.init(Script(__file__))

    duts = []
    dut1 = AndroidDevice('DUT1', connection=1)
    dut2 = AndroidDevice('DUT2', connection=1)
    duts.append(dut1)
    duts.append(dut2)

    env = Environment()
    env.addEquipment(dut1)
    env.addEquipment(dut2)

    if(env.setup()):
        tc = TC_AD_Bluetooth_1_38_GAP_Consecutive_Connect_To_Non_Existing_Device_All_1("TC_AD_Bluetooth_1_38_GAP_Consecutive_Connect_To_Non_Existing_Device_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
