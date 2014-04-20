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


class TC_AD_Bluetooth_4_16_A2DP_Consecutive_Sink_Connect_Disconnect_During_Playing_Audio_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        iterations = int(Session.getSetupFileParam('bt', 'a2dpiterations'))
        handsfreeAddress = Session.getSetupFileParam('bt', 'addressheadset')
        track = 'MP3_MPEG25_Music_RegalBaroque_169sec_Stereo_11kHz_CBR_64kbps.mp3'
        mediaPath = '/data/local/com.stericsson.test.bluetooth.app/files/%s'%track

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        #Push audio files
        self.pushFileFromContentDatabase(ComponentOne, track, mediaPath)
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

        #Start streaming audio
        self.SendAndWaitForEvent(ComponentOne, OpCodes.PLAY_AUDIO, OpCodes.PLAY_AUDIO, message=mediaPath, timeout=30)
        time.sleep(3)
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_AUDIO_PLAYING, OpCodes.GET_IS_AUDIO_PLAYING, message='Is Audio Playing app 1', timeout=30)
        if returnData == "false":
          self.log.info("Audio is not playing")
          raise Failure('Audio is not playing')

        #repeat Disconnect and reconnect sink
        for i in range(0,iterations):
            self.log.info('Iteration:   %s of %s'%(i+1,iterations))
            self.SendAndWaitForEvent(ComponentOne, OpCodes.DISCONNECT_SINK, OpCodes.CURR_SINK_STATE_DISCONNECTED, message=handsfreeAddress, timeout=20)
            time.sleep(5)
            result = self.SendAndWaitForEvent(ComponentOne, OpCodes.IS_AUDIO_ROUTED_TO_A2DP, OpCodes.IS_AUDIO_ROUTED_TO_A2DP, message='check audio routing', timeout=10)
            if result == "true":
                raise Failure("Audio not routed correctly - Audio is playing in A2DP")
            time.sleep(2)
            self.SendAndWaitForEvent(ComponentOne, OpCodes.CONNECT_SINK, OpCodes.CURR_SINK_STATE_CONNECTED, message=handsfreeAddress, timeout=20)
            time.sleep(5)
            result = self.SendAndWaitForEvent(ComponentOne, OpCodes.IS_AUDIO_ROUTED_TO_A2DP, OpCodes.IS_AUDIO_ROUTED_TO_A2DP, message='check audio routing', timeout=10)
            if result == "false":
                raise Failure("Audio not routed correctly - Audio is not playing in A2DP")
            time.sleep(2)

        #Stop streaming audio
        time.sleep(2)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.STOP_AUDIO, OpCodes.STOP_AUDIO, message='Stop Audio app 1', timeout=30)
        time.sleep(3)
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_AUDIO_PLAYING, OpCodes.GET_IS_AUDIO_PLAYING, message='Is Audio Playing app 1', timeout=30)
        if returnData == "true":
          self.log.info("Audio is still playing")
          raise Failure('Audio is still playing')

        #Check sink state
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_SINK_STATE, OpCodes.GET_SINK_STATE, message=handsfreeAddress, timeout=30)
        self.log.info("State is: %s"%returnData)
        if returnData == "STATE_PLAYING":
          self.log.info("Sink State is Playing")
          raise Failure('Sink State is Playing')

        #Disconnect A2DP
        self.SendAndWaitForEvent(ComponentOne, OpCodes.DISCONNECT_SINK, OpCodes.DISCONNECT_SINK, message=handsfreeAddress, timeout=10)

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
        tc = TC_AD_Bluetooth_4_16_A2DP_Consecutive_Sink_Connect_Disconnect_During_Playing_Audio_All_1("TC_AD_Bluetooth_4_16_A2DP_Consecutive_Sink_Connect_Disconnect_During_Playing_Audio_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
