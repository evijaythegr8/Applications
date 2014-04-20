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


class TC_AD_Bluetooth_14_07_Multi_Point_HFP_Voice_Call_During_OPP_Outgoing_Transfer_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        handsfreeAddress = Session.getSetupFileParam('bt', 'addressheadset')
        number = Session.getSetupFileParam('DUT2', 'phonenumber')
        transferFile = 'pic_18.0_Mpix_NoName_3x2_Exif_2.21_BaselineStd_Q11.jpg'
        mediaPathTransfer = '/sdcard/%s'%transferFile
        targetPathTransfer = '/sdcard/bluetooth/%s'%transferFile

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

        #Perform OBEX

        #Bond devices
        self.PairDevices(ComponentOne, ComponentTwo, deviceOneAddress, deviceTwoAddress, timeout=30)
        time.sleep(2)

        #Perform OBEX

        #Get device two out of sleep mode
        self.Wakeup(ComponentTwo, timeout=40)
        time.sleep(4)

        #Clear notifications on target device
        self.EmptyNotificationsList(ComponentTwo)

        #Remove and re-upload reference files
        self.RunShellCommand(ComponentTwo, "rm %s"%mediaPathTransfer)
        self.RunShellCommand(ComponentTwo, "rm %s"%targetPathTransfer)
        self.RunShellCommand(ComponentOne, "rm %s"%mediaPathTransfer)
        self.pushFileFromContentDatabase(ComponentOne, transferFile, mediaPathTransfer)
        self.pushFileFromContentDatabase(ComponentTwo, transferFile, mediaPathTransfer)
        time.sleep(2)

        #Send image with Bluetooth
        self.Wakeup(ComponentOne, timeout=40)
        time.sleep(4)
        self.SendImages(ComponentOne, mediaPathTransfer)

        #Wait for incoming transfer request then accept it
        self.WaitForEvent(ComponentTwo, OpCodes.ACTION_ACL_CONNECTED, timeout=240)
        self.Wakeup(ComponentTwo, timeout=40)
        self.AcceptIncomingNotification(ComponentTwo)
        time.sleep(2)

        # Call setup
        self.Wakeup(ComponentTwo, timeout=30)
        time.sleep(2)
        self.SendCommand(ComponentOne, OpCodes.MAKE_CALL, message=number)
        time.sleep(5)
        BluetoothDialogInput("Verify that call in progress can be heard in the headset. Yes/No", option="TEST")
        self.SendCommand(ComponentTwo, OpCodes.ANSWER_CALL, message='Answer Call')
        time.sleep(2)
        BluetoothDialogInput("Verify that the call is setup correctly and with good quality. Yes/No", option="TEST")
        time.sleep(3)
        self.SendCommand(ComponentOne, OpCodes.END_CALL, message='End Call')

        #Wait for exchanges to finish, link goes down
        self.WaitForEvent(ComponentOne, OpCodes.ACTION_ACL_DISCONNECTED, timeout=300)

        #Return to home
        self.pressKey(ComponentOne,BTC.KEY_HOME)

        # Verify file transfer OK
        result = self.VerifyFileTransfer(ComponentTwo, transferFile)
        if result == 'False':
            raise Failure("File was not transferred correctly")

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
        tc = TC_AD_Bluetooth_14_07_Multi_Point_HFP_Voice_Call_During_OPP_Outgoing_Transfer_All_1("TC_AD_Bluetooth_14_07_Multi_Point_HFP_Voice_Call_During_OPP_Outgoing_Transfer_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()