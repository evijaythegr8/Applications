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
from string import find
import time,re


class TC_AD_Bluetooth_17_34_HFP_WBS_Switch_NB_WB_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        WBShandsfreeAddress = Session.getSetupFileParam('bt', 'addressWBSheadset')
        handsfreeAddress = Session.getSetupFileParam('bt', 'addressheadset')
        number = Session.getSetupFileParam('DUT1', 'phonenumber')

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Enable WB in platform
        self.EnableWB(ComponentOne)

        #Set WBS Handsfree Headset to discoverable
        BluetoothDialogInput('Set WBS Headset in discoverable then press Enter')

        #Bond with Handsfree
        try:
            self.InitiateAndAcceptPairing(ComponentOne, WBShandsfreeAddress, timeout=30)
        except:
            #Android handled the pairing without user interaction
            self.log.info("Auto pairing?")
        time.sleep(5)

        #Set Handsfree Headset to discoverable
        BluetoothDialogInput('Set "Normal" Headset in discoverable then press Enter')

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

        #Make call
        self.SendCommand(ComponentTwo, OpCodes.MAKE_CALL, message=number)
        BluetoothDialogInput("Verify that ring tone can be heard in the headset. Yes/No", option="TEST")

        BluetoothDialogInput("Press Enter then answer call using the headset")

        #Check if WB is setup
        if self.CheckIfWB(ComponentOne, 120):
            self.log.info("WB setup")
            raise Failure('WB setup')

        BluetoothDialogInput("Verify that the call is setup correctly. Yes/No", option="TEST")

        BluetoothDialogInput("Press Enter then turn off Headset and and trigger connect on WBS Headset")

        #Check if WB is setup
        time.sleep(3)
        if not self.CheckIfWB(ComponentOne):
            self.log.info("WB not setup")
            raise Failure('WB not setup')

        BluetoothDialogInput("Verify that the audio is routed to WBS Headset. Yes/No", option="TEST")

        BluetoothDialogInput("Hang-up the call. Press OK")
        time.sleep(3)

        #Return to home
        self.pressKey(ComponentTwo,BTC.KEY_HOME)

        #Disconnect Handsfree
        self.SendAndWaitForEvent(ComponentOne, OpCodes.DISCONNECT_HEADSET, OpCodes.DISCONNECT_HEADSET, message=WBShandsfreeAddress, timeout=10)
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
        tc = TC_AD_Bluetooth_17_34_HFP_WBS_Switch_NB_WB_All_1("TC_AD_Bluetooth_17_34_HFP_WBS_Switch_NB_WB_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
