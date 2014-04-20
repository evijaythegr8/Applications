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


class TC_AD_Bluetooth_1_12_GAP_Dedicated_Incoming_Bonding_Pincode_Accepted_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        LegacyDeviceAddress = Session.getSetupFileParam('bt', 'addresslegacy')

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        # Make local device discoverable
        self.Wakeup(ComponentOne, timeout=10)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_DISCOVERABLE, OpCodes.SET_DISCOVERABLE, message='Set Discoverable app 1', timeout=10)
        time.sleep(4)
        self.pressYes(ComponentOne)

        BluetoothDialogInput('Initiate a pairing request from the remote device to the device with friendly name: %s. Pin code is 0000. then press Enter'%deviceOneName)

        # Accept incoming pairing request
        self.WaitForEvent(ComponentOne, OpCodes.PAIRING_VARIANT_PIN, timeout=30)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_PIN, OpCodes.CURR_BOND_STATE_BONDED, message='%s;0000'%LegacyDeviceAddress)
        time.sleep(2)

        # Verify that the pairing is successful.
        result = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_BOND_STATE, OpCodes.GET_BOND_STATE, message=LegacyDeviceAddress, timeout=10)
        if result != "BOND_BONDED":
            raise Failure("Device not bonded")

        time.sleep(2)
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
        tc = TC_AD_Bluetooth_1_12_GAP_Dedicated_Incoming_Bonding_Pincode_Accepted_All_1("TC_AD_Bluetooth_1_12_GAP_Dedicated_Incoming_Bonding_Pincode_Accepted_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
