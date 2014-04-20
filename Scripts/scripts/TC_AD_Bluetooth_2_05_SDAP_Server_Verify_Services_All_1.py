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
from includes.BluetoothOpCodes import OpCodes
from includes.BluetoothTestComponent import BluetoothTestComponent
from includes.BluetoothConstants import BluetoothConstants
from string import find
import re,time


class TC_AD_Bluetooth_2_05_SDAP_Server_Verify_Services_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Enable PAN to find PAN NAP service
        self.SendAndWaitForEvent(ComponentOne, OpCodes.ENABLE_PAN, OpCodes.ENABLE_PAN, message='Enable PAN', timeout=10)
        time.sleep(5)

        #Fetch remote device services
        self.EmptyQueue()
        self.SendCommand(ComponentTwo, OpCodes.FETCH_UUIDS_WITH_SDP, message=deviceOneAddress)

        foundUUIDs = []
        foundUUIDs = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_UUID, OpCodes.UUID_FOUND, timeout=45)

        # compare answer with expected service response
        myList = {}
        for i in foundUUIDs:
            myList[i] = i

        if myList.has_key(BluetoothConstants.SERVICE_OBJECT_PUSH_PROFILE):
            self.log.info("SERVICE_OBJECT_PUSH_PROFILE found")
        else:
            raise Failure("SERVICE_OBJECT_PUSH_PROFILE not found")

        if myList.has_key(BluetoothConstants.SERVICE_AUDIO_VIDEO_SOURCE):
            self.log.info("SERVICE_AUDIO_VIDEO_SOURCE found")
        else:
            raise Failure("SERVICE_AUDIO_VIDEO_SOURCE not found")

        if myList.has_key(BluetoothConstants.SERVICE_AUDIO_VIDEO_REMOTE_CONTROL_TARGET):
            self.log.info("SERVICE_AUDIO_VIDEO_REMOTE_CONTROL_TARGET found")
        else:
            raise Failure("SERVICE_AUDIO_VIDEO_REMOTE_CONTROL_TARGET not found")

        if myList.has_key(BluetoothConstants.SERVICE_HEADSET_AUDIO_VIDEO_GATEWAY):
            self.log.info("SERVICE_HEADSET_AUDIO_VIDEO_GATEWAY found")
        else:
            raise Failure("SERVICE_HEADSET_AUDIO_VIDEO_GATEWAY not found")

        if myList.has_key(BluetoothConstants.SERVICE_HANDSFREE_AUDIO_GATEWAY):
            self.log.info("SERVICE_HANDSFREE_AUDIO_GATEWAY found")
        else:
            raise Failure("SERVICE_HANDSFREE_AUDIO_GATEWAY not found")

        if myList.has_key(BluetoothConstants.SERVICE_PHONE_BOOK_ACCESS_PROFILE):
            self.log.info("SERVICE_PHONE_BOOK_ACCESS_PROFILE found")
        else:
            raise Failure("SERVICE_PHONE_BOOK_ACCESS_PROFILE not found")

        if myList.has_key(BluetoothConstants.SERVICE_PNP_DEVICE_ID):
            self.log.info("SERVICE_PNP_DEVICE_ID found")
        else:
            raise Failure("SERVICE_PNP_DEVICE_ID not found")

        if myList.has_key(BluetoothConstants.SERVICE_PAN_NAP):
            self.log.info("SERVICE_PAN_NAP found")
        else:
            raise Failure("SERVICE_PAN_NAP not found")

        #Disable PAN
        self.SendAndWaitForEvent(ComponentOne, OpCodes.DISABLE_PAN, OpCodes.DISABLE_PAN, message='Disable PAN', timeout=10)

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
        tc = TC_AD_Bluetooth_2_05_SDAP_Server_Verify_Services_All_1("TC_AD_Bluetooth_2_05_SDAP_Server_Verify_Services_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
