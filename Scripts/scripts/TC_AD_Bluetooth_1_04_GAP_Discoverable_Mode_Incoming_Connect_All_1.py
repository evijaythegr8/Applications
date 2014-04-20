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


class TC_AD_Bluetooth_1_04_GAP_Discoverable_Mode_Incoming_Connect_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        # Make local device discoverable
        self.Wakeup(ComponentOne, timeout=10)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_DISCOVERABLE, OpCodes.SET_DISCOVERABLE, message='300', timeout=10)
        time.sleep(4)
        self.pressYes(ComponentOne)

        # Perform a dedicated bonding
        self.PairDevices(ComponentOne, ComponentTwo, deviceOneAddress, deviceTwoAddress, timeout=30)
        time.sleep(5)

        # Verify that the local device is discoverable
        scanMode = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_SCAN_MODE, OpCodes.GET_SCAN_MODE, message='Get Scan Mode app 1', timeout=30)
        if scanMode != BluetoothConstants.SCAN_MODE_CONNECTABLE_DISCOVERABLE_STRING:
            self.log.info("Scan mode is not discoverable. It is %s"%scanMode)
            raise Failure('Scan mode is not discoverable')

        # Verify that the local device is discoverable
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.START_DEVICE_DISCOVERY, OpCodes.START_DEVICE_DISCOVERY, message='Discover devices app 2', timeout=10)
        time.sleep(2)
        foundDevices = []
        foundDevices = self.WaitForEventAndStore(ComponentTwo, OpCodes.ACTION_DISCOVERY_FINISHED, OpCodes.ACTION_FOUND, timeout=120)
        targetString = "%s;%s"%(deviceOneName,deviceOneAddress)
        targetFound = self.MatchStringInList(foundDevices, targetString)

        if not targetFound:
            self.log.info("Local device not found")
            raise Failure('Local device not found')
        else:
            self.log.info("Device found")

        # From the remote device initiate a link request
        serverId = self.SendAndWaitForEvent(ComponentOne, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='SPP;%s'%BTC.SERVICE_SERIAL_PORT_PROFILE, timeout=30)
        clientId = self.SendAndWaitForEvent(ComponentTwo, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, message='%s;%s'%(deviceOneAddress,BTC.SERVICE_SERIAL_PORT_PROFILE), timeout=30)
        self.SendCommand(ComponentOne, OpCodes.RFCOMM_ACCEPT, message='60000;%s'%serverId)
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.RFCOMM_CONNECT, OpCodes.RFCOMM_CONNECT, message=clientId)

        # Disconnect and remove service
        time.sleep(5)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.CLOSE_CONNECTION_SERVER, OpCodes.ACTION_ACL_DISCONNECTED, message=serverId, timeout=10)
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.CLOSE_CONNECTION_CLIENT, OpCodes.CLOSE_CONNECTION_CLIENT, message=clientId, timeout=10)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message=serverId, timeout=10)

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
        tc = TC_AD_Bluetooth_1_04_GAP_Discoverable_Mode_Incoming_Connect_All_1("TC_AD_Bluetooth_1_04_GAP_Discoverable_Mode_Incoming_Connect_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
