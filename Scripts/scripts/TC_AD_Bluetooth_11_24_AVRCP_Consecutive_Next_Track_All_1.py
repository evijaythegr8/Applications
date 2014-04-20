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


class TC_AD_Bluetooth_11_24_AVRCP_Consecutive_Next_Track_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        handsfreeAddress = Session.getSetupFileParam('bt', 'addressheadset')
        track1 = '118c_a_MU.mp3'
        mediaPath1 = '/data/local/com.stericsson.test.bluetooth.app/files/%s'%track1
        track2 = 'MP3_MPEG25_Music_RegalBaroque_169sec_Stereo_11kHz_CBR_64kbps.mp3'
        mediaPath2 = '/data/local/com.stericsson.test.bluetooth.app/files/%s'%track2
        iterations = int(Session.getSetupFileParam('bt', 'avrcpiterations'))

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        #Push audio files
        self.pushFileFromContentDatabase(ComponentOne, track1, mediaPath1)
        self.pushFileFromContentDatabase(ComponentOne, track2, mediaPath2)
        time.sleep(2)

        #Setup BT testapp mediaplayer with the two paths
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SETUP_MULTIPLE_AUDIO_TRACKS, OpCodes.SETUP_MULTIPLE_AUDIO_TRACKS, message=mediaPath1, timeout=10)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SETUP_MULTIPLE_AUDIO_TRACKS, OpCodes.SETUP_MULTIPLE_AUDIO_TRACKS, message=mediaPath2, timeout=10)

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

        #Start streaming audio
        self.SendAndWaitForEvent(ComponentOne, OpCodes.PLAY_AUDIO, OpCodes.PLAY_AUDIO, message=mediaPath1, timeout=30)
        time.sleep(3)
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_AUDIO_PLAYING, OpCodes.GET_IS_AUDIO_PLAYING, message='Is Audio Playing app 1', timeout=30)
        if returnData == "false":
            self.log.info("Audio is not playing")
            raise Failure('Audio is not playing')
        time.sleep(5)

        #repeat next track
        for i in range(0,iterations):
            self.log.info('Iteration: %s of %s'%(i+1,iterations))
            self.log.info('Iteration %s'%(i+1))
            #Next track
            time.sleep(2)
            BluetoothDialogInput('Press Next track on AVRCP Headset and verify that new track is played, Yes/No',option='TEST')
            time.sleep(3)

        #Stop streaming audio
        time.sleep(2)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.STOP_AUDIO, OpCodes.STOP_AUDIO, message='Stop Audio app 1', timeout=30)
        time.sleep(3)
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_AUDIO_PLAYING, OpCodes.GET_IS_AUDIO_PLAYING, message='Is Audio Playing app 1', timeout=30)
        if returnData == "true":
            self.log.info("Audio is still playing")
            raise Failure('Audio is still playing')

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
        tc = TC_AD_Bluetooth_11_24_AVRCP_Consecutive_Next_Track_All_1("TC_AD_Bluetooth_11_24_AVRCP_Consecutive_Next_Track_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
