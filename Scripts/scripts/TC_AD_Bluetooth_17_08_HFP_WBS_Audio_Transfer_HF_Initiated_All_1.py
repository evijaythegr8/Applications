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
from includes.BluetoothConstants import BluetoothConstants as BTC
import time,re
from includes.BluetoothConstants import BluetoothConstants
from string import find


class TC_AD_Bluetooth_17_08_HFP_WBS_Audio_Transfer_HF_Initiated_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        handsfreeAddress = Session.getSetupFileParam('bt', 'addressWBSheadset')
        number = Session.getSetupFileParam('DUT2', 'phonenumber')

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Enable WB in platform
        self.EnableWB(ComponentOne)

        #Set Handsfree Headset to discoverable
        BluetoothDialogInput('Set WBS in discoverable then press Enter')

        #Bond with Handsfree
        try:
            self.InitiateAndAcceptPairing(ComponentOne, handsfreeAddress, timeout=30)
        except:
            #Android handled the pairing without user interaction
            self.log.info("Auto pairing?")
            #Check it to make sure
            time.sleep(15)
            self.SendAndWaitForEvent(ComponentOne, OpCodes.CONNECT_HEADSET, OpCodes.CONNECT_HEADSET, message=handsfreeAddress, timeout=30)
            time.sleep(6)
            HandsfreeConnected = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_HEADSET_CONNECTED, OpCodes.GET_IS_HEADSET_CONNECTED, message=handsfreeAddress, timeout=10)
            if HandsfreeConnected == "false":
                self.log.info("Handsfree not connected")
                raise Failure('Handsfree not connected')
        time.sleep(5)

        #Get device two out of sleep mode
        self.Wakeup(ComponentTwo, timeout=30)
        time.sleep(2)

        self.SendCommand(ComponentOne, OpCodes.MAKE_CALL, message=number)
        BluetoothDialogInput("Verify that call in progress can be heard in the headset. Yes/No", option="TEST")

        self.SendCommand(ComponentTwo, OpCodes.ANSWER_CALL, message='Answer Call. Press Enter.')

        #Check if WB is setup
        time.sleep(3)
        if (!self.CheckIfWB(ComponentOne)):
            self.log.info("WB not setup")
            raise Failure('WB not setup')

        BluetoothDialogInput("Verify that the call is setup correctly and audio is routed to the headset. Yes/No", option="TEST")

        BluetoothDialogInput("In Phone Menu untick Bluetooth to transfer sound to phone then press Enter")

        BluetoothDialogInput("Verify that the audio is in the phone. Yes/No", option="TEST")

        BluetoothDialogInput("Press the answer call/multi-purpose button on the headset to transfer audio. then press Enter")

        BluetoothDialogInput("Verify that the audio is in the headset. Yes/No", option="TEST")

        #Check if WB is setup
        time.sleep(3)
        if (!self.CheckIfWB(ComponentOne)):
            self.log.info("WB not setup")
            raise Failure('WB not setup')

        self.SendCommand(ComponentOne, OpCodes.END_CALL, message='End Call. Press Enter.')

        time.sleep(3)

        #Return to home
        self.pressKey(ComponentOne,BTC.KEY_HOME)

        #Disconnect Handsfree
        self.SendAndWaitForEvent(ComponentOne, OpCodes.DISCONNECT_HEADSET, OpCodes.DISCONNECT_HEADSET, message=handsfreeAddress, timeout=10)
        time.sleep(2)

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
        tc = TC_AD_Bluetooth_17_08_HFP_WBS_Audio_Transfer_HF_Initiated_All_1("TC_AD_Bluetooth_17_08_HFP_WBS_Audio_Transfer_HF_Initiated_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
