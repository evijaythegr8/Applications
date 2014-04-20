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


class TC_AD_Bluetooth_17_31_HFP_WBS_Disable_BT_During_Voice_Call_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        handsfreeAddress = Session.getSetupFileParam('bt', 'addressWBSheadset')
        number = Session.getSetupFileParam('DUT1', 'phonenumber')

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Enable WB in platform
        self.EnableWB(ComponentOne)

        #Set Handsfree Headset to discoverable
        BluetoothDialogInput('Set WBS Headset in discoverable then press Enter')

        #Bond with Handsfree
        try:
            self.InitiateAndAcceptPairing(ComponentOne, handsfreeAddress, timeout=30)
        except:
            #Android handled the pairing without user interaction
            self.log.info("Auto pairing?")
            #Check it to make sure
            time.sleep(10)
            self.SendAndWaitForEvent(ComponentOne, OpCodes.CONNECT_HEADSET, OpCodes.CONNECT_HEADSET, message=handsfreeAddress, timeout=30)
            time.sleep(12) #Remove when 10s connect delay is solved in headset
            time.sleep(4)
            HandsfreeConnected = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_HEADSET_CONNECTED, OpCodes.GET_IS_HEADSET_CONNECTED, message=handsfreeAddress, timeout=10)
            if HandsfreeConnected == "false":
                self.log.info("Handsfree not connected")
                raise Failure('Handsfree not connected')
        time.sleep(5)

        #Get device one out of sleep mode
        self.Wakeup(ComponentOne, timeout=30)
        time.sleep(2)

        self.SendCommand(ComponentTwo, OpCodes.MAKE_CALL, message=number)

        BluetoothDialogInput("Verify that ring tone can be heard in the headset. Yes/No", option="TEST")

        self.SendCommand(ComponentOne, OpCodes.ANSWER_CALL, message=number)

        #Check if WB is setup
        if not self.CheckIfWB(ComponentOne, 120):
            self.log.info("WB not setup")
            raise Failure('WB not setup')

        BluetoothDialogInput("Verify that the call is setup correctly and audio is routed to the headset. Yes/No", option="TEST")
        time.sleep(5)

        #Disable BT during call
        self.SendAndWaitForEvent(ComponentOne, OpCodes.DISABLE_BT, OpCodes.CURR_STATE_OFF, message='Disable BT App 1', timeout=30)

        BluetoothDialogInput("Verify that the audio is routed to the phone. Yes/No", option="TEST")

        #Re-enable BT
        self.SendAndWaitForEvent(ComponentOne, OpCodes.ENABLE_BT_API, OpCodes.CURR_STATE_ON, message='Enable BT App 1', timeout=30)
        time.sleep(10)

        #Check if WB is setup
        if not self.CheckIfWB(ComponentOne, 120):
            self.log.info("WB not setup")
            raise Failure('WB not setup')

        BluetoothDialogInput("Verify that the audio is routed to the headset. Yes/No", option="TEST")

        self.SendCommand(ComponentOne, OpCodes.END_CALL, message='End Call')

        time.sleep(3)

        #Return to home
        self.pressKey(ComponentOne,BTC.KEY_HOME)
        self.pressKey(ComponentTwo,BTC.KEY_HOME)

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
        tc = TC_AD_Bluetooth_17_31_HFP_WBS_Disable_BT_During_Voice_Call_All_1("TC_AD_Bluetooth_17_31_HFP_WBS_Disable_BT_During_Voice_Call_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
