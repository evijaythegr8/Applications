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
from string import find
from includes.BluetoothConstants import BluetoothConstants
import re,time


class TC_AD_Bluetooth_2_07_SDAP_Server_Create_Same_UUID_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        time.sleep(5)

        # register a service
        serviceIndex = self.SendAndWaitForEvent(ComponentOne, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='Service1;%s'%BluetoothConstants.SERVICE_UUID1, timeout=30)
        time.sleep(3)
        self.SendCommand(ComponentTwo, OpCodes.FETCH_UUIDS_WITH_SDP, message=deviceOneAddress)
        foundUUIDs = []
        foundUUIDs = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_UUID, OpCodes.UUID_FOUND, timeout=45)

        # search for the UUID previously registered.
        targetString = BluetoothConstants.SERVICE_UUID1

        targetFound = self.MatchStringInList(foundUUIDs, targetString)
        if not targetFound:
            self.log.info("SERVICE_UUID1 not found ")
            raise Failure('SERVICE_UUID1 not found')
        else:
            self.log.info("found SERVICE_UUID1")

        # try to register with the same UUID, should generate a failure
        try:
            serviceIndex2 = self.SendAndWaitForEvent(ComponentOne, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='Service2;%s'%BluetoothConstants.SERVICE_UUID1, timeout=30)
            self.log.info('serviceIndex2 %s' %serviceIndex2)
            raise Failure("Failure no exception thrown, when trying to register with same SERVICE_UUID1")
        except:
            self.log.info("OK Exception raised from trying to register with same UUID twice")

        # register with new UUID, this should work
        serviceIndex3 = self.SendAndWaitForEvent(ComponentOne, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='Service3;%s'%BluetoothConstants.SERVICE_UUID2, timeout=30)
        time.sleep(3)

        self.SendCommand(ComponentTwo, OpCodes.FETCH_UUIDS_WITH_SDP, message=deviceOneAddress)
        foundUUIDs = []
        foundUUIDs = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_UUID, OpCodes.UUID_FOUND, 45)

        targetString = BluetoothConstants.SERVICE_UUID2

        targetFound = self.MatchStringInList(foundUUIDs, targetString)

        if not targetFound:
            self.log.info("SERVICE_UUID2 not found")
            raise Failure('SERVICE_UUID2 not found ')
        else:
            self.log.info("found SERVICE_UUID2")

        #Remove services
        self.SendAndWaitForEvent(ComponentOne, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message='%s'%serviceIndex, timeout=30)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message='%s'%serviceIndex3, timeout=30)

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
        tc = TC_AD_Bluetooth_2_07_SDAP_Server_Create_Same_UUID_All_1("TC_AD_Bluetooth_2_07_SDAP_Server_Create_Same_UUID_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
