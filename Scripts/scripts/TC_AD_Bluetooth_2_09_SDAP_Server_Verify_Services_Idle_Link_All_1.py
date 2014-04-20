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
from includes.BluetoothOpCodes import OpCodes
from includes.BluetoothTestComponent import BluetoothTestComponent
from includes.BluetoothConstants import BluetoothConstants as BTC
from string import find
import re,time


class TC_AD_Bluetooth_2_09_SDAP_Server_Verify_Services_Idle_Link_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        bufferSize = int(Session.getSetupFileParam('bt', 'sppbuffersize'))

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Bond devices
        self.PairDevices(ComponentOne, ComponentTwo, deviceOneAddress, deviceTwoAddress, timeout=30)
        time.sleep(5)

        #Create service
        serverId = self.SendAndWaitForEvent(ComponentOne, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='SPP;%s'%BTC.SERVICE_SERIAL_PORT_PROFILE, timeout=30)
        clientId = self.SendAndWaitForEvent(ComponentTwo, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, message='%s;%s'%(deviceOneAddress,BTC.SERVICE_SERIAL_PORT_PROFILE), timeout=30)

        #Connect service
        self.SendCommand(ComponentOne, OpCodes.RFCOMM_ACCEPT, message='60000;%s'%serverId)
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.RFCOMM_CONNECT, OpCodes.RFCOMM_CONNECT, message=clientId)
        time.sleep(5)

        #VERIFY SERVICES

        #Fetch remote device services
        self.SendCommand(ComponentTwo, OpCodes.FETCH_UUIDS_WITH_SDP, message=deviceOneAddress)
        foundUUIDs = []
        foundUUIDs = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_UUID, OpCodes.UUID_FOUND, timeout=45)

        # compare answer with expected service response
        myList = {}
        for i in foundUUIDs:
            myList[i] = i

        if myList.has_key(BTC.SERVICE_OBJECT_PUSH_PROFILE):
            self.log.info("SERVICE_OBJECT_PUSH_PROFILE found")
        else:
            raise Failure("SERVICE_OBJECT_PUSH_PROFILE not found")

        if myList.has_key(BTC.SERVICE_AUDIO_VIDEO_SOURCE):
            self.log.info("SERVICE_AUDIO_VIDEO_SOURCE found")
        else:
            raise Failure("SERVICE_AUDIO_VIDEO_SOURCE not found")

        if myList.has_key(BTC.SERVICE_AUDIO_VIDEO_REMOTE_CONTROL_TARGET):
            self.log.info("SERVICE_AUDIO_VIDEO_REMOTE_CONTROL_TARGET found")
        else:
            raise Failure("SERVICE_AUDIO_VIDEO_REMOTE_CONTROL_TARGET not found")

        if myList.has_key(BTC.SERVICE_HEADSET_AUDIO_VIDEO_GATEWAY):
            self.log.info("SERVICE_HEADSET_AUDIO_VIDEO_GATEWAY found")
        else:
            raise Failure("SERVICE_HEADSET_AUDIO_VIDEO_GATEWAY not found")

        if myList.has_key(BTC.SERVICE_HANDSFREE_AUDIO_GATEWAY):
            self.log.info("SERVICE_HANDSFREE_AUDIO_GATEWAY found")
        else:
            raise Failure("SERVICE_HANDSFREE_AUDIO_GATEWAY not found")

        if myList.has_key(BTC.SERVICE_PHONE_BOOK_ACCESS_PROFILE):
            self.log.info("SERVICE_PHONE_BOOK_ACCESS_PROFILE found")
        else:
            raise Failure("SERVICE_PHONE_BOOK_ACCESS_PROFILE not found")

        if myList.has_key(BTC.SERVICE_PNP_DEVICE_ID):
            self.log.info("SERVICE_PNP_DEVICE_ID found")
        else:
            raise Failure("SERVICE_PNP_DEVICE_ID not found")

        #Close connections
        self.SendAndWaitForEvent(ComponentOne, OpCodes.CLOSE_CONNECTION_SERVER, OpCodes.CLOSE_CONNECTION_SERVER, message=serverId, timeout=30)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message=serverId, timeout=30)
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.CLOSE_CONNECTION_CLIENT, OpCodes.CLOSE_CONNECTION_CLIENT, message=clientId, timeout=30)

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
        tc = TC_AD_Bluetooth_2_09_SDAP_Server_Verify_Services_Idle_Link_All_1("TC_AD_Bluetooth_2_09_SDAP_Server_Verify_Services_Idle_Link_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
