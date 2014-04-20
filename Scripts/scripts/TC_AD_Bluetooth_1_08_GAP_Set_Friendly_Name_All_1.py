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
import time,re


class TC_AD_Bluetooth_1_08_GAP_Set_Friendly_Name_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        friendlyName = "BTTestFriendlyName"

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        #Set Friendly Name and verify
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_NAME, OpCodes.ACTION_LOCAL_NAME_CHANGED, message=friendlyName, timeout=10)
        time.sleep(2)
        newFriendlyName = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_NAME, OpCodes.GET_NAME, message='GetName app 1', timeout=10)
        if newFriendlyName != friendlyName:
            self.log.info("Name was not set properly")
            raise Failure('Name was not set properly')

        #Clean up
        self.RestoreApplication(ComponentOne)
        self.CloseDownExecution()


if __name__ == '__main__':
    from core.script.Script                   import Script
    from core.setup.Environment               import Environment
    from plugins.android.device.AndroidDevice import AndroidDevice

    Session.init(Script(__file__))

    duts = []
    dut1 = AndroidDevice('DUT1', connection=1)
    duts.append(dut1)

    env = Environment()
    env.addEquipment(dut1)

    if(env.setup()):
        tc = TC_AD_Bluetooth_1_08_GAP_Set_Friendly_Name_All_1("TC_AD_Bluetooth_1_08_GAP_Set_Friendly_Name_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
