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
from string import find


class TC_AD_Bluetooth_1_21_GAP_General_Outgoing_Bonding_Just_Works_Accepted_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        # From the local device initiate a link request with low security enough to trigger a just works pairing request from the remote device.
        serverId = self.SendAndWaitForEvent(ComponentTwo, OpCodes.LISTEN_USING_RFCOMM, OpCodes.LISTEN_USING_RFCOMM, message=BTC.CHANNEL_ID, timeout=30)
        clientId = self.SendAndWaitForEvent(ComponentOne, OpCodes.CREATE_RFCOMM_SOCKET, OpCodes.CREATE_RFCOMM_SOCKET, message='%s;%s'%(deviceTwoAddress,BTC.CHANNEL_ID), timeout=30)
        self.SendCommand(ComponentTwo, OpCodes.RFCOMM_ACCEPT, message='0;%s'%serverId)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.RFCOMM_CONNECT, OpCodes.ACTION_ACL_CONNECTED, message=clientId)
        time.sleep(3)

        # Verify that the devices are bonded
        state = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_BOND_STATE, OpCodes.GET_BOND_STATE, message=deviceTwoAddress, timeout=10)
        if state != "BOND_BONDED":
            raise Failure("Devices not bonded")

        state = self.SendAndWaitForEvent(ComponentTwo, OpCodes.GET_BOND_STATE, OpCodes.GET_BOND_STATE, message=deviceOneAddress, timeout=10)
        if state != "BOND_BONDED":
            raise Failure("Devices not bonded")

        #Disconnect
        self.SendAndWaitForEvent(ComponentOne, OpCodes.CLOSE_CONNECTION_CLIENT, OpCodes.ACTION_ACL_DISCONNECTED, message=clientId, timeout=10)
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message=serverId, timeout=10)
        time.sleep(4)

        # Verify that the devices are not bonded (since it will be a no bonding the linkkeys should be removed after disconnect)
        self.SendCommand(ComponentOne, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 1')
        foundDevices = self.WaitForEventAndStore(ComponentOne, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        targetString = "%s;%s"%(deviceTwoName,deviceTwoAddress)
        targetFound = self.MatchStringInList(foundDevices, targetString)
        if targetFound:
            self.log.info("Target device found")
        else:
            self.log.info("Device not found")
            raise Failure('Target device not found')

        # Verify that the devices are not bonded
        self.SendCommand(ComponentTwo, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 2')
        foundDevices = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        targetString = "%s;%s"%(deviceOneName,deviceOneAddress)
        targetFound = self.MatchStringInList(foundDevices, targetString)
        if targetFound:
            self.log.info("Target device found")
        else:
            self.log.info("Device not found")
            raise Failure('Target device not found')

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
        tc = TC_AD_Bluetooth_1_21_GAP_General_Outgoing_Bonding_Just_Works_Accepted_All_1("TC_AD_Bluetooth_1_21_GAP_General_Outgoing_Bonding_Just_Works_Accepted_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
