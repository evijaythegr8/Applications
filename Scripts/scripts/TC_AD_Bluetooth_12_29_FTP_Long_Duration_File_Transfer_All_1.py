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


class TC_AD_Bluetooth_12_29_FTP_Long_Duration_File_Transfer_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        FTPAddress = Session.getSetupFileParam('bt', 'addressPCDongle')
        Duration = int(Session.getSetupFileParam('bt', 'ftplongduration'))

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        # Create folder and file structure

        #self.generateFtpStructure(ComponentOne)

        # Make local device discoverable
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_DISCOVERABLE, OpCodes.SET_DISCOVERABLE, message='300', timeout=10)
        time.sleep(4)
        self.pressYes(ComponentOne)
        BluetoothDialogInput('Initiate a passkey pairing from the PC to the platform with 0000 then press Enter')

        # Accept incoming pairing request from remote device
        self.AcceptIncomingPairing(ComponentOne, FTPAddress, timeout=30)
        BluetoothDialogInput('Establish a FTP connection between from PC to the platform device and press Enter')

        # Accept incoming FTP connection
        self.acceptIncomingFTPConnection(ComponentOne)
        BluetoothDialogInput('Send a large file to the platform device over the FTP connection, then retrieve the same file and verify that the transmission was OK. Yes/No.')

        # Wait for disconnect

        #self.WaitForEvent(ComponentOne, OpCodes.ACTION_ACL_DISCONNECTED, timeout=30)

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
        tc = TC_AD_Bluetooth_12_29_FTP_Long_Duration_File_Transfer_All_1("TC_AD_Bluetooth_12_29_FTP_Long_Duration_File_Transfer_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
