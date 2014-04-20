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
from includes.BluetoothOpCodes          import OpCodes
from includes.BluetoothTestComponent    import BluetoothTestComponent
import time,re


class TC_AD_Bluetooth_1_33_GAP_Dedicated_Incoming_Bonding_Pincode_Remote_Reject_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        LegacyDeviceAddress = Session.getSetupFileParam('bt', 'addresslegacy')

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        BluetoothDialogInput('Enable Bluetooth on the remote device then press Enter')

        # Make local device discoverable
        self.Wakeup(ComponentOne, timeout=10)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_DISCOVERABLE, OpCodes.SET_DISCOVERABLE, message='Set Discoverable app 1', timeout=10)
        time.sleep(4)
        self.pressYes(ComponentOne)

        BluetoothDialogInput('Initiate a pairing request from the remote device to the device with friendly name: %s. then press Enter'%deviceOneName)

        # Reject incoming pairing request
        BluetoothDialogInput('Cancel the paring from the remote device when enter pincode request is visible. then press Enter')

        self.WaitForEvent(ComponentOne, OpCodes.ACTION_PAIRING_CANCEL, timeout=50)
        time.sleep(5)

        # Verify that the pairing is unsuccessful.
        self.SendCommand(ComponentOne, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 1')
        foundDevices = self.WaitForEventAndStore(ComponentOne, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        targetFound = self.MatchStringInList(foundDevices, LegacyDeviceAddress)
        if not targetFound:
            self.log.info("Target device not found")
        else:
            self.log.info("Device found")
            self.log.info(foundDevices)
            raise Failure('Target device found')

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
        tc = TC_AD_Bluetooth_1_33_GAP_Dedicated_Incoming_Bonding_Pincode_Remote_Reject_All_1("TC_AD_Bluetooth_1_33_GAP_Dedicated_Incoming_Bonding_Pincode_Remote_Reject_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
