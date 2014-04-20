#
#=BEGIN
#
# This file is part of the bluetooth use-case verification
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


class TC_AD_Bluetooth_14_15_Multi_Point_A2DP_AVRCP_HFP_To_Device_One_SPP_To_Device_Two_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'

        handsfreeAddress = Session.getSetupFileParam('bt', 'addressheadset')
        number = Session.getSetupFileParam('DUT1', 'phonenumber')
        file = '118c_a_MU.mp3'
        mediaPath = '/data/local/com.stericsson.test.bluetooth.app/files/%s'%file
        bufferSize = int(Session.getSetupFileParam('bt', 'sppbuffersize'))

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        self.pushFileFromContentDatabase(ComponentOne, file, mediaPath)

        #Set Handsfree Headset to discoverable
        BluetoothDialogInput('Set Handsfree Headset %s in discoverable then press OK'%handsfreeAddress)

        #Bond with Handsfree
        try:
            self.InitiateAndAcceptPairing(ComponentOne, handsfreeAddress, timeout=30)
            time.sleep(1)
            #Connect A2DP and HFP
            self.SendCommand(ComponentOne, OpCodes.CONNECT_SINK, message=handsfreeAddress)
            time.sleep(2)
            self.SendAndWaitForEvent(ComponentOne, OpCodes.CONNECT_HEADSET, OpCodes.CONNECT_HEADSET, message=handsfreeAddress, timeout=30)
        except:
            #Android handled the pairing without user interaction
            self.log.info("Auto pairing?")
            time.sleep(15)
            #Connect A2DP and HFP
            self.SendCommand(ComponentOne, OpCodes.CONNECT_SINK, message=handsfreeAddress)
            time.sleep(2)
            self.SendAndWaitForEvent(ComponentOne, OpCodes.CONNECT_HEADSET, OpCodes.CONNECT_HEADSET, message=handsfreeAddress, timeout=30)
            time.sleep(10)
            sinkState = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_SINK_STATE, OpCodes.GET_SINK_STATE, message=handsfreeAddress, timeout=10)
            if sinkState != BTC.STATE_CONNECTED:
                self.log.info("A2DP not connected")
                raise Failure('A2DP not connected')
            HandsfreeConnected = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_HEADSET_CONNECTED, OpCodes.GET_IS_HEADSET_CONNECTED, message=handsfreeAddress, timeout=10)
            if HandsfreeConnected == "false":
                self.log.info("Handsfree not connected")
                raise Failure('Handsfree not connected')
        time.sleep(5)

        #Bond devices
        self.PairDevices(ComponentOne, ComponentTwo, deviceOneAddress, deviceTwoAddress, timeout=30)
        time.sleep(2)

        #Start streaming audio
        self.SendAndWaitForEvent(ComponentOne, OpCodes.PLAY_AUDIO, OpCodes.PLAY_AUDIO, message=mediaPath, timeout=30)
        time.sleep(3)
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_AUDIO_PLAYING, OpCodes.GET_IS_AUDIO_PLAYING, message='Is Audio Playing app 1', timeout=30)
        if returnData == "false":
            self.log.info("Audio is not playing")
            raise Failure('Audio is not playing')
        time.sleep(5)

        # SPP

        #Create BluetoothServerSocket on Server (create service) "00001101-0000-1000-8000-00805f9b34fb" = SPP
        serverId = self.SendAndWaitForEvent(ComponentOne, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='SPP;%s'%BTC.SERVICE_SERIAL_PORT_PROFILE, timeout=10)

        #Create BluetoothSocket on Client
        clientId = self.SendAndWaitForEvent(ComponentTwo, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, message='%s;%s'%(deviceOneAddress,BTC.SERVICE_SERIAL_PORT_PROFILE), timeout=10)

        #Connect the service
        self.SendCommand(ComponentOne, OpCodes.RFCOMM_ACCEPT, message='60000;%s'%serverId)
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.RFCOMM_CONNECT, OpCodes.RFCOMM_CONNECT, message=clientId)
        time.sleep(8)

        #Send Data Server to Client
        self.SendCommand(ComponentTwo, OpCodes.RECEIVE_DATA_CLIENT, message='%s;%s;%s'%(clientId, BTC.RFCOMM_THREAD_CHECK, bufferSize))
        time.sleep(1)
        self.SendCommand(ComponentOne, OpCodes.SEND_CONTINUOUS_DATA_SERVER, message=serverId)
        time.sleep(6)

        #Verify Audio is not disrupted and that data is still being sent
        BluetoothDialogInput("Verify that music is playing with good quality. Yes/No", option="TEST")
        isSending = self.SendAndWaitForEvent(ComponentOne, OpCodes.IS_CONTINUOUS_DATA_SENDING, OpCodes.IS_CONTINUOUS_DATA_SENDING, timeout=30)
        if isSending == "false":
                self.log.info("Data is not sending")
                raise Failure('Data is not sending')

        #Send AVRCP pause
        BluetoothDialogInput("Press pause on Headset and verify that audio track is paused. Yes/No", option="TEST")
        time.sleep(4)

        #Send AVRCP play
        BluetoothDialogInput("Press play on Headset and verify that audio track is played. Yes/No", option="TEST")
        time.sleep(4)

        # Call setup
        self.Wakeup(ComponentOne, timeout=50)
        time.sleep(2)
        self.SendCommand(ComponentTwo, OpCodes.MAKE_CALL, message=number)
        time.sleep(5)
        BluetoothDialogInput("Verify that call in progress can be heard in the headset, then press Answer on Headset. Yes/No", option="TEST")
        time.sleep(2)
        BluetoothDialogInput("Verify that the call is setup correctly and with good quality and that music is paused. Yes/No", option="TEST")
        time.sleep(3)

        #Data still sending?
        time.sleep(10)
        isSending = self.SendAndWaitForEvent(ComponentOne, OpCodes.IS_CONTINUOUS_DATA_SENDING, OpCodes.IS_CONTINUOUS_DATA_SENDING, timeout=30)
        if isSending == "false":
                self.log.info("Data is not sending")
                raise Failure('Data is not sending')

        BluetoothDialogInput("Terminate call from Headset and verify that music is resumed. Yes/No", option="TEST")

        #Data still sending?
        isSending = self.SendAndWaitForEvent(ComponentOne, OpCodes.IS_CONTINUOUS_DATA_SENDING, OpCodes.IS_CONTINUOUS_DATA_SENDING, timeout=30)
        if isSending == "false":
                self.log.info("Data is not sending")
                raise Failure('Data is not sending')

        #Abort data sending
        self.SendCommand(ComponentOne, OpCodes.STOP_SEND_CONTINUOUS_DATA)

        isSending = self.SendAndWaitForEvent(ComponentOne, OpCodes.IS_CONTINUOUS_DATA_SENDING, OpCodes.IS_CONTINUOUS_DATA_SENDING, timeout=30)
        if isSending == "true":
            self.log.info("Data is still sending")
            raise Failure('Data is still sending')

        #Stop streaming audio
        time.sleep(4)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.STOP_AUDIO, OpCodes.STOP_AUDIO, message='Stop Audio app 1', timeout=30)
        time.sleep(3)
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_IS_AUDIO_PLAYING, OpCodes.GET_IS_AUDIO_PLAYING, message='Is Audio Playing app 1', timeout=30)
        if returnData == "true":
            self.log.info("Audio is still playing")
            raise Failure('Audio is still playing')

        #Return to home
        self.pressKey(ComponentOne,BTC.KEY_HOME)
        self.pressKey(ComponentTwo,BTC.KEY_HOME)
        time.sleep(2)

        #Close connection
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.CLOSE_CONNECTION_CLIENT, OpCodes.CLOSE_CONNECTION_CLIENT, message=clientId, timeout=30)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message=serverId, timeout=30)

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
        tc = TC_AD_Bluetooth_14_15_Multi_Point_A2DP_AVRCP_HFP_To_Device_One_SPP_To_Device_Two_All_1("TC_AD_Bluetooth_14_15_Multi_Point_A2DP_AVRCP_HFP_To_Device_One_SPP_To_Device_Two_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
