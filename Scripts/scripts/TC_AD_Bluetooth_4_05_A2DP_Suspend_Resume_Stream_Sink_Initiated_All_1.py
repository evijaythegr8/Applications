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


class TC_AD_Bluetooth_4_05_A2DP_Suspend_Resume_Stream_Sink_Initiated_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        handsfreeAddress = Session.getSetupFileParam('bt', 'addressheadset')
        track = 'MP3_MPEG25_Music_RegalBaroque_169sec_Stereo_11kHz_CBR_64kbps.mp3'
        mediaPath = '/sdcard/%s'%track

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

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

        #Set A2DP Headset to discoverable
        BluetoothDialogInput('Set A2DP Headset in discoverable then press Enter')

        #Bond with A2DP Headset
        try:
            self.InitiateAndAcceptPairing(ComponentOne, handsfreeAddress)
        except:
            #Android handled the pairing without user interaction
            self.log.debug('Already paired?')

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

        #Suspend streaming audio
        time.sleep(2)
        BluetoothDialogInput('Press PAUSE on AVRCP Headset and verify that audio is paused. Yes/No',option='TEST')
        time.sleep(2)

        #Resume streaming audio
        time.sleep(2)
        BluetoothDialogInput('Press PLAY on AVRCP Headset and verify that audio is played. Yes/No',option='TEST')
        time.sleep(2)

        #Stop streaming audio
        self.Wakeup(ComponentOne, timeout=10)
        time.sleep(2)
        self.pressKey(ComponentOne,BTC.KEY_MEDIA_STOP)
        time.sleep(3)

        #Return to home
        self.pressKey(ComponentOne,BTC.KEY_HOME)

        #Remove files from SDcard
        self.RunShellCommand(ComponentOne, "rm %s"%mediaPath)

        #Disconnect A2DP
        self.SendAndWaitForEvent(ComponentOne, OpCodes.DISCONNECT_SINK, OpCodes.DISCONNECT_SINK, message=handsfreeAddress, timeout=10)
        time.sleep(2)

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
        tc = TC_AD_Bluetooth_4_05_A2DP_Suspend_Resume_Stream_Sink_Initiated_All_1("TC_AD_Bluetooth_4_05_A2DP_Suspend_Resume_Stream_Sink_Initiated_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
