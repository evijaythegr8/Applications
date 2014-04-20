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


class TC_AD_Bluetooth_1_25_GAP_General_Incoming_Bonding_Just_Works_Accepted_All_1(BluetoothTestCase):

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
        serverId = self.SendAndWaitForEvent(ComponentOne, OpCodes.LISTEN_USING_RFCOMM, OpCodes.LISTEN_USING_RFCOMM, message=BTC.CHANNEL_ID, timeout=30)
        clientId = self.SendAndWaitForEvent(ComponentTwo, OpCodes.CREATE_RFCOMM_SOCKET, OpCodes.CREATE_RFCOMM_SOCKET, message='%s;%s'%(deviceOneAddress,BTC.CHANNEL_ID), timeout=30)
        self.SendCommand(ComponentOne, OpCodes.RFCOMM_ACCEPT, message='0;%s'%serverId)
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.RFCOMM_CONNECT, OpCodes.ACTION_ACL_CONNECTED, message=clientId)
        time.sleep(3)

        # Verify that the devices are bonded
        state = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_BOND_STATE, OpCodes.GET_BOND_STATE, message=deviceTwoAddress, timeout=10)
        if state != "BOND_BONDED":
            raise Failure("Devices not bonded")

        state = self.SendAndWaitForEvent(ComponentTwo, OpCodes.GET_BOND_STATE, OpCodes.GET_BOND_STATE, message=deviceOneAddress, timeout=10)
        if state != "BOND_BONDED":
            raise Failure("Devices not bonded")

        # Close connection
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.CLOSE_CONNECTION_CLIENT, OpCodes.CLOSE_CONNECTION_CLIENT, message=clientId, timeout=10)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message=serverId, timeout=10)

        # Verify that the devices are bonded
        state = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_BOND_STATE, OpCodes.GET_BOND_STATE, message=deviceTwoAddress, timeout=10)
        if state != "BOND_BONDED":
            raise Failure("Devices not bonded")

        state = self.SendAndWaitForEvent(ComponentTwo, OpCodes.GET_BOND_STATE, OpCodes.GET_BOND_STATE, message=deviceOneAddress, timeout=10)
        if state != "BOND_BONDED":
            raise Failure("Devices not bonded")

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
        tc = TC_AD_Bluetooth_1_25_GAP_General_Incoming_Bonding_Just_Works_Accepted_All_1("TC_AD_Bluetooth_1_25_GAP_General_Incoming_Bonding_Just_Works_Accepted_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
