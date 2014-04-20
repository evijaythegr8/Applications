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


class TC_AD_Bluetooth_4_09_A2DP_Incoming_Voice_Call_During_Streaming_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        handsfreeAddress = Session.getSetupFileParam('bt', 'addressheadset')
        track = 'MP3_MPEG25_Music_RegalBaroque_169sec_Stereo_11kHz_CBR_64kbps.mp3'
        mediaPath = '/sdcard/%s'%track
        number = Session.getSetupFileParam('DUT1', 'phonenumber')

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Empty SDcard
        self.RunShellCommand(ComponentOne, "rm %s"%mediaPath)

        #Push audio files
        self.pushFileFromContentDatabase(ComponentOne, track, mediaPath)
        time.sleep(2)

        #Trigger sdcard mounted broadcast
        self.RunShellCommand(ComponentOne, "am broadcast -a android.intent.action.MEDIA_MOUNTED --ez read-only false -d file:///sdcard")
        time.sleep(2)

        #Trigger sdcard mounted broadcast
        self.TriggerMediaScanner(ComponentOne)
        time.sleep(2)

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

        #Connect A2DP
        sinkState = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_SINK_STATE, OpCodes.GET_SINK_STATE, handsfreeAddress, timeout=10)
        if sinkState == BTC.STATE_DISCONNECTED:
            self.SendCommand(ComponentOne, OpCodes.CONNECT_SINK, message=handsfreeAddress)

        time.sleep(5)
        sinkState = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_SINK_STATE, OpCodes.GET_SINK_STATE, handsfreeAddress, timeout=10)
        if sinkState != BTC.STATE_CONNECTED:
            self.log.info('A2DP not connected')
            raise Failure('A2DP not connected')

        #Play music using Android GUI
        self.playMusicUsingGUI(ComponentOne)
        time.sleep(2)
        BluetoothDialogInput("Verify that music is playing. Yes/No", option="TEST")

        #Get device one out of sleep mode
        self.Wakeup(ComponentOne, timeout=30)
        time.sleep(2)
        self.SendCommand(ComponentTwo, OpCodes.MAKE_CALL, message=number)
        time.sleep(2)
        BluetoothDialogInput("Verify that music is paused and that incoming call can be heard in the headset. Yes/No", option="TEST")
        BluetoothDialogInput("Answer call using the headset then press Enter")
        BluetoothDialogInput("Verify that the call is setup correctly. Yes/No", option="TEST")
        self.SendCommand(ComponentOne, OpCodes.END_CALL, message='End Call')
        BluetoothDialogInput("Verify that the music is resumed. Yes/No", option="TEST")
        time.sleep(3)

        #Stop streaming audio
        self.Wakeup(ComponentOne, timeout=10)
        time.sleep(2)
        self.pressKey(ComponentOne,BTC.KEY_MEDIA_STOP)
        time.sleep(3)

        #Return to home
        self.pressKey(ComponentOne,BTC.KEY_HOME)
        self.pressKey(ComponentTwo,BTC.KEY_HOME)

        #Remove files from SDcard
        self.RunShellCommand(ComponentOne, "rm %s"%mediaPath)

        #Disconnect Handsfree
        self.SendAndWaitForEvent(ComponentOne, OpCodes.DISCONNECT_HEADSET, OpCodes.DISCONNECT_HEADSET, message=handsfreeAddress, timeout=10)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.DISCONNECT_SINK, OpCodes.DISCONNECT_SINK, message=handsfreeAddress, timeout=10)
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
        tc = TC_AD_Bluetooth_4_09_A2DP_Incoming_Voice_Call_During_Streaming_All_1("TC_AD_Bluetooth_4_09_A2DP_Incoming_Voice_Call_During_Streaming_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
