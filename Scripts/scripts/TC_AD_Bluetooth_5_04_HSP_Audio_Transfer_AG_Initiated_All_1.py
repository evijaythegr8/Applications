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


class TC_AD_Bluetooth_5_04_HSP_Audio_Transfer_AG_Initiated_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        ptsAddress = Session.getSetupFileParam('bt', 'addresspts')
        ptsTestCase = 'TC_AG_ACT_BV_02_I'
        UE1_SIM_umber = self.Configuration.getSectionKeyValue('UE1', 'phonenumber')

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentTwo)		
        BluetoothDialogInput('Start the test case: %s in PTS, then press Enter'%ptsTestCase)
        time.sleep(5)

        #Bond with PTS dongle
        try:
            self.InitiateAndAcceptPairing(ComponentOne, ptsAddress, timeout=30)
        except:
            #Android handled the pairing without user interaction
            self.log.info("Auto pairing?")
            #Check it to make sure
            time.sleep(10)
            self.SendAndWaitForEvent(ComponentOne, OpCodes.CONNECT_HEADSET, OpCodes.CONNECT_HEADSET, message=handsfreeAddress, timeout=30)
            time.sleep(6)
            isHeadsetConnected = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_HEADSET_CONNECTED, OpCodes.GET_IS_HEADSET_CONNECTED, message=ptsAddress, timeout=10)
            if isHeadsetConnected == "false":
                self.log.info("HSP not connected")
                raise Failure('HSP not connected')

        #Place, answer and end the call		
        self.SendCommand(ComponentTwo, OpCodes.MAKE_CALL, message=UE1_SIM_umber)
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
             raise Failure('Handsfree still connected')

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
        tc = TC_AD_Bluetooth_5_04_HSP_Audio_Transfer_AG_Initiated_All_1("TC_AD_Bluetooth_5_04_HSP_Audio_Transfer_AG_Initiated_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
