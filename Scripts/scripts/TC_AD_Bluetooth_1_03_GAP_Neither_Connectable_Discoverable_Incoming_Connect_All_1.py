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
from includes.BluetoothOpCodes          import OpCodes
from includes.BluetoothTestComponent    import BluetoothTestComponent
from includes.BluetoothConstants import BluetoothConstants as BTC
import time,re
from includes.BluetoothConstants import BluetoothConstants
from string import find


class TC_AD_Bluetooth_1_03_GAP_Neither_Connectable_Discoverable_Incoming_Connect_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        # Change discoverable timeout
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_DISCOVERABLE_TIMEOUT, OpCodes.SET_DISCOVERABLE_TIMEOUT, message='30', timeout=10)

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        # Perform a dedicated bonding
        self.PairDevices(ComponentOne, ComponentTwo, deviceOneAddress, deviceTwoAddress, timeout=30)
        time.sleep(10)

        # Create service
        serverId = self.SendAndWaitForEvent(ComponentOne, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='SPP;%s'%BTC.SERVICE_SERIAL_PORT_PROFILE, timeout=30)
        time.sleep(2)

        # Verify that the local device is disabled
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_ISENABLED, OpCodes.GET_ISENABLED, message='Check state app 1', timeout=10)
        if returnData == "true":
            self.SendAndWaitForEvent(ComponentOne, OpCodes.DISABLE_BT, OpCodes.DISABLE_BT, message='Disable BT app 1', timeout=30)
            self.WaitForEvent(ComponentOne, OpCodes.CURR_STATE_OFF, timeout=30)
            time.sleep(2)

        # Verify that the local device is not discoverable
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.START_DEVICE_DISCOVERY, OpCodes.START_DEVICE_DISCOVERY, message='Discover devices app 2', timeout=10)
        time.sleep(2)
        foundDevices = []
        foundDevices = self.WaitForEventAndStore(ComponentTwo, OpCodes.ACTION_DISCOVERY_FINISHED, OpCodes.ACTION_FOUND, timeout=60)
        targetString = "%s;%s"%(deviceOneName,deviceOneAddress)
        targetFound = self.MatchStringInList(foundDevices, targetString)

        if not targetFound:
            self.log.info("Local device not found")
        else:
            self.log.info("Device found")
            raise Failure('Local device found')

        # From the remote device initiate a link request
        clientId = self.SendAndWaitForEvent(ComponentTwo, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, message='%s;%s'%(deviceOneAddress,BTC.SERVICE_SERIAL_PORT_PROFILE), timeout=30)
        try:
            self.SendAndWaitForEvent(ComponentTwo, OpCodes.RFCOMM_CONNECT, OpCodes.ACTION_ACL_CONNECTED, message=clientId)
            raise Failure("Connect didn't fail")
        except:
            self.log.info("Connect failed as expected")

        # Remove client
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.CLOSE_CONNECTION_CLIENT, OpCodes.CLOSE_CONNECTION_CLIENT, message=clientId, timeout=10)

        # Reenable Bluetooth for cleanup
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_ISENABLED, OpCodes.GET_ISENABLED, message='Check state app 1', timeout=10)
        if returnData == "false":
            self.SendAndWaitForEvent(ComponentOne, OpCodes.ENABLE_BT_API, OpCodes.CURR_STATE_ON, message='Enable BT app 1', timeout=30)

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
        tc = TC_AD_Bluetooth_1_03_GAP_Neither_Connectable_Discoverable_Incoming_Connect_All_1("TC_AD_Bluetooth_1_03_GAP_Neither_Connectable_Discoverable_Incoming_Connect_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
