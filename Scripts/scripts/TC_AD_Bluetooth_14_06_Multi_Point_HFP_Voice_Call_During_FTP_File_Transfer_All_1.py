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


class TC_AD_Bluetooth_14_06_Multi_Point_HFP_Voice_Call_During_FTP_File_Transfer_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        handsfreeAddress = Session.getSetupFileParam('bt', 'addressheadset')
        number = Session.getSetupFileParam('DUT2', 'phonenumber')
        FTPDongleAddress = Session.getSetupFileParam('bt', 'addressPCDongle')

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Set Handsfree Headset to discoverable
        BluetoothDialogInput('Set Headset in discoverable then press Enter')

        #Bond with Headset
        try:
            self.InitiateAndAcceptPairing(ComponentOne, handsfreeAddress)
        except:
            #Android handled the pairing without user interaction
            self.log.debug('Already paired?')

        #Connect Handsfree
        handsfreeConnected = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_HEADSET_CONNECTED, OpCodes.GET_IS_HEADSET_CONNECTED, message=handsfreeAddress, timeout=10)
        if handsfreeConnected == 'false':
            self.SendAndWaitForEvent(ComponentOne, OpCodes.CONNECT_HEADSET, OpCodes.CONNECT_HEADSET, message=handsfreeAddress, timeout=30)
        
        handsfreeConnected = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_HEADSET_CONNECTED, OpCodes.GET_IS_HEADSET_CONNECTED, message=handsfreeAddress, timeout=10)
        if handsfreeConnected == "false":
             self.log.info("Handsfree not connected")
             raise Failure('Handsfree not connected')

        # Establish FTP connection and start sending a file

        #Get device one out of sleep mode
        self.Wakeup(ComponentOne, timeout=30)
        time.sleep(2)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_DISCOVERABLE, OpCodes.SET_DISCOVERABLE, message='300', timeout=10)
        time.sleep(4)
        self.pressYes(ComponentOne)
        BluetoothDialogInput('Initiate a passkey pairing from the PC to the platform with PIN 0000 then press Enter')

        # Accept incoming pairing request from remote device
        self.AcceptIncomingPairing(ComponentOne, FTPDongleAddress, timeout=30)
        BluetoothDialogInput('Allow FTP request from PC and establish a FTP connection between the PC and Platform device')
        time.sleep(1)
        BluetoothDialogInput('Start sending a large file from the PC to the platform device, then press Enter')
        time.sleep(2)

        # Call setup
        self.Wakeup(ComponentTwo, timeout=30)
        time.sleep(2)
        self.SendCommand(ComponentOne, OpCodes.MAKE_CALL, message=number)
        time.sleep(5)
        BluetoothDialogInput("Verify that call in progress can be heard in the headset. Yes/No", option="TEST")
        self.SendCommand(ComponentTwo, OpCodes.ANSWER_CALL, message='Answer Call')
        time.sleep(2)
        BluetoothDialogInput("Verify that the call is setup correctly. Yes/No", option="TEST")
        time.sleep(1)
        BluetoothDialogInput('Wait for file transfer to finish then press Enter')
        time.sleep(1)
        BluetoothDialogInput("Verify that the file has been transferred correctly and that sound has good quality. Yes/No", option="TEST")
        self.SendCommand(ComponentOne, OpCodes.END_CALL, message='End Call')
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
        tc = TC_AD_Bluetooth_14_06_Multi_Point_HFP_Voice_Call_During_FTP_File_Transfer_All_1("TC_AD_Bluetooth_14_06_Multi_Point_HFP_Voice_Call_During_FTP_File_Transfer_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
