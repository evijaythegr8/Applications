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
from includes.BluetoothDialogInput import BluetoothDialogInput
from includes.BluetoothOpCodes          import OpCodes
from includes.BluetoothTestComponent    import BluetoothTestComponent
import time,re
from string import find


class TC_AD_Bluetooth_10_05_SAP_Server_Connection_Termination_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        PTS_TC='TC_SERVER_DCN_BV_01_I '
        PTS = Session.getSetupFileParam('bt', 'addresspts')

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        # Make local device discoverable
        self.setDiscoverable(ComponentOne)

        # From the remote device initiate a pairing request to the local device.
        BluetoothDialogInput('Press Enter then start the testcase: %s in PTS' % PTS_TC)

        # Accept incoming pairing request
        self.acceptIncomingSapPairing(ComponentOne, PTS, timeout=60)

        # Accept incoming SAP notification
        self.acceptIncomingSapConnection(ComponentOne)

        self.WaitForEvent(ComponentOne, OpCodes.ACTION_ACL_DISCONNECTED, timeout=60)

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
        tc = TC_AD_Bluetooth_10_05_SAP_Server_Connection_Termination_All_1("TC_AD_Bluetooth_10_05_SAP_Server_Connection_Termination_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
