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
from string import find
from array import array
import time
import re


class TC_AD_Bluetooth_1_42_GAP_Unsuccessful_OOB_Bonding_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Request OOB data from local and remote devices.
        oob1 = self.SendAndWaitForEvent(ComponentOne, OpCodes.READ_OUT_OF_BAND_DATA, OpCodes.READ_OUT_OF_BAND_DATA, message='Read out of bond data')
        time.sleep(2)
        print "OOB1: %s"%oob1
        oob2 = self.SendAndWaitForEvent(ComponentTwo, OpCodes.READ_OUT_OF_BAND_DATA, OpCodes.READ_OUT_OF_BAND_DATA, message='Read out of bond data')
        time.sleep(2)
        print "OOB2: %s"%oob2

        #Wake up devices so they can accept pairing
        self.Wakeup(ComponentOne, timeout=30)
        self.Wakeup(ComponentTwo, timeout=30)

        #Set device 2 out of band data
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.SET_DEVICE_OUT_OF_BAND_DATA, OpCodes.SET_DEVICE_OUT_OF_BAND_DATA, message='%s;%s'%(deviceOneAddress,oob1))
        time.sleep(5)

        #Reget OOB data from device 2
        oob2_new = self.SendAndWaitForEvent(ComponentTwo, OpCodes.READ_OUT_OF_BAND_DATA, OpCodes.READ_OUT_OF_BAND_DATA, message='Read out of bond data from remote device')
        time.sleep(2)
        print "OOB2 new: %s"%oob2_new
        time.sleep(5)

        #Try to bond devices with old OOB data
        self.SendAndWaitForEvent(ComponentOne, OpCodes.CREATE_BOND_OUT_OF_BAND, OpCodes.CREATE_BOND_OUT_OF_BAND, message='%s;%s'%(deviceTwoAddress,oob2), timeout=60)
        time.sleep(2)

        # Accept pairing request on both devices
        self.AcceptIncomingNotification(ComponentOne)
        self.AcceptIncomingNotification(ComponentTwo)
        time.sleep(5)

        # Verify that the devices are not bonded
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_BOND_STATE, OpCodes.GET_BOND_STATE, message=deviceTwoAddress, timeout=10)
        if returnData != "BOND_NONE":
            print "Devices are bonded"
            raise Failure('Devices are bonded')

        # Verify that the devices are not bonded
        returnData = self.SendAndWaitForEvent(ComponentTwo, OpCodes.GET_BOND_STATE, OpCodes.GET_BOND_STATE, message=deviceOneAddress, timeout=10)
        if returnData != "BOND_NONE":
            print "Devices are bonded"
            raise Failure('Devices are bonded')

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
        tc = TC_AD_Bluetooth_1_42_GAP_Unsuccessful_OOB_Bonding_All_1("TC_AD_Bluetooth_1_42_GAP_Unsuccessful_OOB_Bonding_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
