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
from includes.BluetoothDialogInput import BluetoothDialogInput
from includes.BluetoothOpCodes import OpCodes
from includes.BluetoothTestComponent import BluetoothTestComponent
from string import find
import time,re


class TC_AD_Bluetooth_5_05_HSP_Audio_Transfer_HS_Inititated_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        ptsAddress = Session.getSetupFileParam('bt', 'addresspts')
        ptsTestCase = 'TC_AG_ACT_BV_01_I'
        UE1_SIM_umber = self.Configuration.getSectionKeyValue('UE1', 'phonenumber')
        UE2_SIM_umber = self.Configuration.getSectionKeyValue('UE2', 'phonenumber')

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentTwo)

        # Make local device discoverable
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_DISCOVERABLE, OpCodes.SET_DISCOVERABLE, message='300', timeout=10)
        time.sleep(4)
        self.pressYes(ComponentOne)

        # Place and end call to add UE2 number to Call log. PTS will use first number from the Call log
        self.SendCommand(ComponentOne, OpCodes.MAKE_CALL, message=UE2_SIM_umber)
        time.sleep(2)
        self.SendCommand(ComponentOne, OpCodes. END_CALL, message='End Call')
        self.SendAndWaitForEvent(ComponentOne, OpCodes.CLEAR_NOTIFICATIONS, OpCodes.CLEAR_NOTIFICATIONS, message='Clear notifications', timeout=25)
        BluetoothDialogInput('Press OK, then start the test case: %s in PTS'%ptsTestCase)
        time.sleep(5)

        # Accept incoming pairing request
        self.WaitForEvent(ComponentOne, OpCodes.PAIRING_VARIANT_PIN, timeout=60)
        time.sleep(5)
        self.SendCommand(ComponentOne, OpCodes.SET_PIN, message='%s;0000'%ptsAddress)

        # UE2 answer call from UE1, then UE1 ends the call
        time.sleep(15)
        self.SendCommand(ComponentTwo, OpCodes.END_CALL, message='End Call')		
        time.sleep(2)

        #Disconnect Handsfree
        self.SendAndWaitForEvent(ComponentOne, OpCodes.DISCONNECT_HEADSET, OpCodes.DISCONNECT_HEADSET, message=ptsAddress, timeout=10)
        time.sleep(2)

        #Check Handsfree disconnected
        isHandsfreeConnected = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_HEADSET_CONNECTED, OpCodes.GET_IS_HEADSET_CONNECTED, message=ptsAddress, timeout=10)
        if isHandsfreeConnected == "true":
             self.log.info("Handsfree still connected")
             raise Failure('Handsfree2DP still connected')

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
        tc = TC_AD_Bluetooth_5_05_HSP_Audio_Transfer_HS_Inititated_All_1("TC_AD_Bluetooth_5_05_HSP_Audio_Transfer_HS_Inititated_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
