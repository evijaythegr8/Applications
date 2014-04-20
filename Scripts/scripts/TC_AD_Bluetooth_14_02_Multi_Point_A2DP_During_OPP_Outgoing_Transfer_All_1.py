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


class TC_AD_Bluetooth_14_02_Multi_Point_A2DP_During_OPP_Outgoing_Transfer_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        handsfreeAddress = Session.getSetupFileParam('bt', 'addressheadset')
        track = 'MP3_MPEG25_Music_RegalBaroque_169sec_Stereo_11kHz_CBR_64kbps.mp3'
        mediaPathAudio = '/data/local/com.stericsson.test.bluetooth.app/files/%s'%track
        musicPath = '/data/local/com.stericsson.test.bluetooth.app/files/test_mp3.mp3'
        image = 'pic_1.8_Mpix_WSXGA+_16x10_JFIF_1.02_Exif_2.21_BaselineStd_Q11.jpg'
        mediaPath = '/sdcard/%s'%image
        targetPath = '/sdcard/bluetooth/%s'%image

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #A2DP related

        #Push audio files
        self.pushFileFromContentDatabase(ComponentOne, track, mediaPathAudio)
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
        self.SendAndWaitForEvent(ComponentOne, OpCodes.PLAY_AUDIO, OpCodes.PLAY_AUDIO, message=mediaPathAudio, timeout=30)
        time.sleep(3)
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_AUDIO_PLAYING, OpCodes.GET_IS_AUDIO_PLAYING, message='Is Audio Playing app 1', timeout=30)
        if returnData == "false":
            self.log.info("Audio is not playing")
            raise Failure('Audio is not playing')

        #OPP related

        #Bond devices
        self.PairDevices(ComponentOne, ComponentTwo, deviceOneAddress, deviceTwoAddress, timeout=30)
        time.sleep(2)

        #Perform OBEX

        #Clear notifications on target device
        self.Wakeup(ComponentOne, timeout=10)
        self.EmptyNotificationsList(ComponentOne)

        #Remove and re-upload reference files
        self.RunShellCommand(ComponentOne, "rm %s"%mediaPath)
        self.RunShellCommand(ComponentOne, "rm %s"%targetPath)
        self.RunShellCommand(ComponentTwo, "rm %s"%mediaPath)
        self.pushFileFromContentDatabase(ComponentTwo, image, mediaPath)
        self.pushFileFromContentDatabase(ComponentOne, image, mediaPath)
        time.sleep(2)

        #Send image with Bluetooth
        self.Wakeup(ComponentTwo, timeout=10)
        self.SendImages(ComponentTwo, mediaPath)

        #Wait for incoming transfer request then accept it
        self.WaitForEvent(ComponentOne, OpCodes.ACTION_ACL_CONNECTED, timeout=240)
        self.Wakeup(ComponentOne, timeout=10)
        self.AcceptIncomingNotification(ComponentOne)

        # Wait for transfer to finish
        self.WaitForEvent(ComponentOne, OpCodes.ACTION_ACL_DISCONNECTED, timeout=240)
        time.sleep(2)

        BluetoothDialogInput('Verify that the audio is playing with good quality during OPP transfer. Yes/No', option="TEST")

        # Verify file transfer OK
        result = self.VerifyFileTransfer(ComponentOne, image)
        if result == 'False':
            raise Failure("File was not transferred correctly")

        # Close A2DP

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
        tc = TC_AD_Bluetooth_14_02_Multi_Point_A2DP_During_OPP_Outgoing_Transfer_All_1("TC_AD_Bluetooth_14_02_Multi_Point_A2DP_During_OPP_Outgoing_Transfer_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
