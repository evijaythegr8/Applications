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


class TC_AD_Bluetooth_1_15_GAP_Dedicated_Outgoing_Bonding_Pincode_Reject_All_1(BluetoothTestCase):

    def execute(self):

        # Initial setup
        ComponentOne = '1'
        LegacyDeviceAddress = Session.getSetupFileParam('bt', 'addresslegacy')

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        # Enable Bluetooth on the remote legacy device.
        BluetoothDialogInput('Enable Bluetooth on the remote device then press Enter')

        # From the local device initiate a pairing request to the remote device.
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.CREATE_BOND, OpCodes.PAIRING_VARIANT_PIN, message=LegacyDeviceAddress, timeout=30)

        # On remote side reject the pairing request
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_PAIRING_CONFIRMATION, OpCodes.UNBOND_REASON_AUTH_REJECTED, message='%s;false'%LegacyDeviceAddress, timeout=10)

        # Verify that the devices are not bonded
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_BOND_STATE, OpCodes.GET_BOND_STATE, message=LegacyDeviceAddress, timeout=10)
        if returnData != "BOND_NONE":
            self.log.info("Devices are bonded")
            raise Failure('Devices are bonded')

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
        tc = TC_AD_Bluetooth_1_15_GAP_Dedicated_Outgoing_Bonding_Pincode_Reject_All_1("TC_AD_Bluetooth_1_15_GAP_Dedicated_Outgoing_Bonding_Pincode_Reject_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
