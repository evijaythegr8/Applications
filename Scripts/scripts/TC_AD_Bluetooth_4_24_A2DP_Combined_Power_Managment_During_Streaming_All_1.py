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
from lib.power_management.SuspendResume import SuspendResume
from lib.power_management.CpuIdle import CpuIdle
from string import find
import time,re


class TC_AD_Bluetooth_4_24_A2DP_Combined_Power_Managment_During_Streaming_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        handsfreeAddress = Session.getSetupFileParam('bt', 'addressheadset')
        track = 'MP3_MPEG25_Music_RegalBaroque_169sec_Stereo_11kHz_CBR_64kbps.mp3'
        mediaPath = '/data/local/com.stericsson.test.bluetooth.app/files/%s'%track

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        #Startup for Power managment
        self.sr = SuspendResume(SuspendResume.POWER_MANAGEMENT_TYPE_DEEPSLEEP, self.logFileNameBase, self.Devices[Phone].ID)
        self.sr.cmd = self.Devices[Phone].StelpCommand
        self.cpu = CpuIdle(self.logFileNameBase, self.Devices[Phone].ID)
        self.cpu.cmd = self.Devices[Phone].StelpCommand

        #Power Managment start test
        self.log.info("Running combined power managment 1st part...")
        self.cpu.testRunBefore()
        self.log.info("Done.")
        self.log.info("Starting test case...")

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
        BluetoothDialogInput("Verify that audio can be heard in the headset. Yes/No", option="TEST")

        #Wait a while
        time.sleep(60)
        BluetoothDialogInput("Verify that audio still can be heard in the headset. Yes/No", option="TEST")

        #Stop streaming audio
        self.SendAndWaitForEvent(ComponentOne, OpCodes.STOP_AUDIO, OpCodes.STOP_AUDIO, message='Stop Audio app 1', timeout=30)
        time.sleep(3)
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_AUDIO_PLAYING, OpCodes.GET_IS_AUDIO_PLAYING, message='Is Audio Playing app 1', timeout=30)
        if returnData == "true":
          self.log.info("Audio is still playing")
          raise Failure('Audio is still playing')

        #Test Done, Cleanup

        #Disconnect A2DP
        self.SendAndWaitForEvent(ComponentOne, OpCodes.DISCONNECT_SINK, OpCodes.DISCONNECT_SINK, message=handsfreeAddress, timeout=10)
        time.sleep(2)
        self.SendCommand(ComponentOne, OpCodes.GET_SINK_IN_CONNECTION_STATE, message='%s;%s;%s'%(BTC.STATE_CONNECTED, BTC.STATE_CONNECTING, BTC.STATE_DISCONNECTING))
        foundDevices = self.WaitForEventAndStore(ComponentOne, OpCodes.NO_MORE_SINK_IN_CONNECTION_STATE_FOUND, OpCodes.SINK_IN_CONNECTION_STATE_FOUND, timeout=60)
        self.log.info(foundDevices)

        #Clean up
        self.RestoreApplication(ComponentOne)
        self.CloseDownExecution()

        #Power Managment end test
        self.log.info("Done.")
        self.log.info("Running combined power managment 2nd part...")
        self.cpu.testRunAfter()
        self.sr.testRunBefore()
        self.sr.testRunAfter()
        self.cpu.initialize()
        self.cpu.testRunBefore()
        self.cpu.testRunAfter()
        self.log.info("Done.")


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
        tc = TC_AD_Bluetooth_4_24_A2DP_Combined_Power_Managment_During_Streaming_All_1("TC_AD_Bluetooth_4_24_A2DP_Combined_Power_Managment_During_Streaming_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
