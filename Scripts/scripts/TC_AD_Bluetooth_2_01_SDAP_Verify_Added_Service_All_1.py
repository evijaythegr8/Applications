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


class TC_AD_Bluetooth_2_01_SDAP_Verify_Added_Service_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Register a service
        serviceIndex = self.SendAndWaitForEvent(ComponentOne, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='Service1;%s'%BluetoothConstants.SERVICE_UUID1, timeout=30)
        self.log.info('serviceIndex %s' %serviceIndex)
        time.sleep(10)

        #Send a service request from ComponentTwo to ComponentOne
        self.EmptyQueue()
        self.SendCommand(ComponentTwo, OpCodes.FETCH_UUIDS_WITH_SDP, message=deviceOneAddress)
        foundUUIDs = []
        foundUUIDs = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_UUID, OpCodes.UUID_FOUND, timeout=30)

        # search for the UUID previously registered.
        targetString = BluetoothConstants.SERVICE_UUID1

        targetFound = self.MatchStringInList(foundUUIDs, targetString)
        if not targetFound:
            self.log.info("Target service UUID not found")
            raise Failure('Target service UUID not found')
        else:
            self.log.info("Service UUID found")

        #Remove service
        self.SendAndWaitForEvent(ComponentOne, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message=serviceIndex, timeout=10)
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
        tc = TC_AD_Bluetooth_2_01_SDAP_Verify_Added_Service_All_1("TC_AD_Bluetooth_2_01_SDAP_Verify_Added_Service_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
