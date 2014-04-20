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
from includes.BluetoothOpCodes              import OpCodes
from includes.BluetoothTestComponent        import BluetoothTestComponent
from includes.BluetoothConstants            import BluetoothConstants
from includes.BluetoothConstants            import BluetoothConstants as BTC
import time, re


class TC_AD_Bluetooth_12_21_FTP_Push_Different_File_Formats_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        PTSDongleAddress = Session.getSetupFileParam('bt', 'addresspts')
        ptsTestCase = 'TC_SERVER_OTR_BV_15_I'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        #Create folder and file structure
        self.generateFtpStructure(ComponentOne)

        #Empty notifications list
        self.Wakeup(ComponentOne, timeout=300)
        self.EmptyNotificationsList(ComponentOne)

        # Start PTS test case
        BluetoothDialogInput('Press Enter and then start test case %s in PTS '%ptsTestCase)

        # Accept incoming pairing request from remote device
        self.AcceptIncomingPairing(ComponentOne, PTSDongleAddress, timeout=30)

        # Accept incoming FTP connection
        self.acceptIncomingFTPConnection(ComponentOne)

        #Wait for exchanges to finish, link goes down
        self.WaitForEvent(ComponentOne, OpCodes.ACTION_ACL_DISCONNECTED, timeout=120)

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
        tc = TC_AD_Bluetooth_12_21_FTP_Push_Different_File_Formats_All_1("TC_AD_Bluetooth_12_21_FTP_Push_Different_File_Formats_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
