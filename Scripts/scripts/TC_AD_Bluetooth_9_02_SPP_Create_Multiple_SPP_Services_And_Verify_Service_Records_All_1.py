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
from includes.BluetoothConstants import BluetoothConstants as BTC
from string import find
from includes.uuid import *
import re,time


class TC_AD_Bluetooth_9_02_SPP_Create_Multiple_SPP_Services_And_Verify_Service_Records_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        nbrOfServices = int(Session.getSetupFileParam('bt', 'sppservices'))

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Create Bond
        self.PairDevices(ComponentOne, ComponentTwo, deviceOneAddress, deviceTwoAddress, timeout=30)
        time.sleep(5)

        #Create multiple BluetoothServerSocket on Server (create service)
        UUIDs = []
        serverIds = []
        for i in range(0,nbrOfServices):
            newUUID = uuid()
            UUIDs.append(newUUID) #Python uuidgen from 2.6 uuid.uuid4()
            serverIds.append(self.SendAndWaitForEvent(ComponentOne, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='MyService%s;%s'%(i,newUUID), timeout=30))

        #Check if services are added
        self.SendCommand(ComponentTwo, OpCodes.FETCH_UUIDS_WITH_SDP, message=deviceOneAddress)
        foundUUIDs = []
        foundUUIDs = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_UUID, OpCodes.UUID_FOUND, timeout=120)

        #Convert list to dictionary
        foundUUIDList = {}
        for i in foundUUIDs:
            foundUUIDList[i] = i

        #Search for all created UUIDs in found UUIDs list
        for i in UUIDs:
            if not foundUUIDList.has_key(i):
                self.log.info("UUID not found: %s"%i)
                raise Failure('UUID not found')
            else:
                self.log.info("UUID found")

        #Close BluetoothServerSockets
        for i in serverIds:
            self.SendAndWaitForEvent(ComponentOne, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message=i, timeout=30)

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
        tc = TC_AD_Bluetooth_9_02_SPP_Create_Multiple_SPP_Services_And_Verify_Service_Records_All_1("TC_AD_Bluetooth_9_02_SPP_Create_Multiple_SPP_Services_And_Verify_Service_Records_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
