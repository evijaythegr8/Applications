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


class TC_AD_Bluetooth_12_27_FTP_Consecutive_Send_Receive_File_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        FTPAddress = Session.getSetupFileParam('bt', 'addressPCDongle')
        iterations = int(Session.getSetupFileParam('bt', 'ftpiterations'))

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        #Create folder and file structure
        self.generateFtpStructure(ComponentOne)

        # Make local device discoverable
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_DISCOVERABLE, OpCodes.SET_DISCOVERABLE, message='300', timeout=10)
        time.sleep(4)
        self.pressYes(ComponentOne)
        BluetoothDialogInput('Initiate a pairing to %s with pin code 0000 from the PC then press Enter'%deviceOneName)

        # Accept incoming pairing request from remote device
        self.AcceptIncomingPairing(ComponentOne, FTPAddress, timeout=60)
        BluetoothDialogInput('Enter OBEX File Transfer on the device in PC then press Enter')

        # Accept incoming FTP connection
        self.acceptIncomingFTPConnection(ComponentOne)

        #repeat Connect and Disconnect
        BluetoothDialogInput('Send a file from computer to DUT, then from DUT to computer %s times and verify that it works. Yes/No.'%iterations, option='TEST')
        BluetoothDialogInput('Unpair the DUT from PC then press Enter')

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
        tc = TC_AD_Bluetooth_12_27_FTP_Consecutive_Send_Receive_File_All_1("TC_AD_Bluetooth_12_27_FTP_Consecutive_Send_Receive_File_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
