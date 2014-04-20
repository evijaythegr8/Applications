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


class TC_AD_Bluetooth_1_41_GAP_Successful_OOB_Bonding_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Empty notification list
        self.EmptyNotificationsList(ComponentOne)
        self.EmptyNotificationsList(ComponentTwo)

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

        #Set device 1 out of band data
        time.sleep(5)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_DEVICE_OUT_OF_BAND_DATA, OpCodes.SET_DEVICE_OUT_OF_BAND_DATA, message='%s;%s'%(deviceTwoAddress,oob2))

        #Bond devices
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.CREATE_BOND_OUT_OF_BAND, OpCodes.CREATE_BOND_OUT_OF_BAND, message='%s;%s'%(deviceOneAddress,oob1), timeout=20)
        time.sleep(2)

        # Accept pairing request on both devices
        self.AcceptIncomingNotification(ComponentOne)
        self.AcceptIncomingNotification(ComponentTwo)

        time.sleep(5)

        #Check the bond state
        self.SendCommand(ComponentOne, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 1')
        foundDevices = self.WaitForEventAndStore(ComponentOne, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        targetString = "%s;%s"%(deviceTwoName,deviceTwoAddress)
        targetFound = self.MatchStringInList(foundDevices, targetString)
        if not targetFound:
            self.log.info("Target device 2 not found")
            raise Failure('Target device 2 not found')
        else:
            self.log.info("Device found")
            self.log.info(foundDevices)

        #Check the bond state
        self.SendCommand(ComponentTwo, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 2')
        foundDevices = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        targetString = "%s;%s"%(deviceOneName,deviceOneAddress)
        targetFound = self.MatchStringInList(foundDevices, targetString)
        if not targetFound:
            self.log.info("Target device 1 not found")
            raise Failure('Target device 1 not found')
        else:
            self.log.info("Device found")
            self.log.info(foundDevices)

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
        tc = TC_AD_Bluetooth_1_41_GAP_Successful_OOB_Bonding_All_1("TC_AD_Bluetooth_1_41_GAP_Successful_OOB_Bonding_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
