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


class TC_AD_Bluetooth_17_13_HFP_WBS_Incoming_Connection_During_Active_Call_All_1(BluetoothTestCase):

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

        BluetoothDialogInput("Turn off the headset. Press Enter")

        #Get device one out of sleep mode
        self.Wakeup(ComponentOne, timeout=30)
        time.sleep(2)

        self.SendCommand(ComponentTwo, OpCodes.MAKE_CALL, message=number)

        BluetoothDialogInput("Verify that there is an incoming call. Yes/No", option="TEST")

        self.SendCommand(ComponentOne, OpCodes.ANSWER_CALL, message=number)

        time.sleep(5)

        BluetoothDialogInput("Verify that the call is active. Yes/No", option="TEST")

        time.sleep(3)

        BluetoothDialogInput("Turn on the headset. Press Enter")

        time.sleep(5)

        BluetoothDialogInput("Verify that call was transferred to the headset and that audio is routed there. Yes/No", option="TEST")

        #Check if WB is setup
        time.sleep(3)
        if (!self.CheckIfWB(ComponentOne)):
            self.log.info("WB not setup")
            raise Failure('WB not setup')

        BluetoothDialogInput("Hang-up the call. Press Enter")

        #Return to home
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
        tc = TC_AD_Bluetooth_17_13_HFP_WBS_Incoming_Connection_During_Active_Call_All_1("TC_AD_Bluetooth_17_13_HFP_WBS_Incoming_Connection_During_Active_Call_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
