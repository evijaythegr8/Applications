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


class TC_AD_Bluetooth_11_15_AVRCP_Browsing_Virtual_File_System_Metadata_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ptsAddress = Session.getSetupFileParam('bt', 'addresspts')
        ptsTestCase_1='TC_TG_CEC_BV_01'
        ptsTestCase_2='TC_TG_MCN_CB_BV_06_I'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()
        time.sleep(15)

        #Enable BT
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_ISENABLED, OpCodes.GET_ISENABLED, message='Check state app 1', timeout=10)
        if returnData == "false":
            self.SendAndWaitForEvent(ComponentOne, OpCodes.ENABLE_BT_API, OpCodes.ENABLE_BT_API, message='Enable BT app 1', timeout=30)
            self.WaitForEvent(ComponentOne, OpCodes.CURR_STATE_ON, timeout=60)
            time.sleep(5)

        #Copy test-mediaplayer application to the local device
        self.RunShellCommand(ComponentOne, command='rm /test-mediaplayer')
        time.sleep(4)
        self.pushFullPath(ComponentOne, 'C:/test-mediaplayer', '/test-mediaplayer')
        time.sleep(4)
        self.RunShellCommand(ComponentOne, command='chmod 777 /test-mediaplayer')

        #Run test-mediaplayer
        BluetoothDialogInput('Run test-mediaplayer and press OK')
        time.sleep(5)

        # Make local device discoverable
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_DISCOVERABLE, OpCodes.SET_DISCOVERABLE, message='300', timeout=10)
        time.sleep(4)
        self.pressYes(ComponentOne)

        #Register test-mediaplayer

        # From the remote device initiate a pairing request to the local device.
        BluetoothDialogInput('Press OK, then start the test case: %s in PTS'%ptsTestCase_1)
        time.sleep(5)

        # Accept incoming pairing request
        try:
            self.AcceptIncomingPairing(ComponentOne, ptsAddress, timeout=30)
        except:
            print 'auto pairing'
        else:
            time.sleep(4)
            self.pressYes(ComponentOne)

        time.sleep(5)
        self.RunShellCommand(ComponentOne, command="./test-mediaplayer query NotifyAddressedPlayer")
        time.sleep(5)
        self.RunShellCommand(ComponentOne, command="./test-mediaplayer query NotifyEventMask")
        time.sleep(5)

        # Make sure device is still in discoverable mode
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_DISCOVERABLE, OpCodes.SET_DISCOVERABLE, message='300', timeout=10)
        time.sleep(4)
        self.pressYes(ComponentOne)

        # Run PTS test case
        BluetoothDialogInput('Press OK, then start the test case: %s in PTS'%ptsTestCase_2)
        time.sleep(5)

        # Accept incoming pairing request
        try:
            self.AcceptIncomingPairing(ComponentOne, ptsAddress, timeout=30)
        except:
            print 'auto pairing'

        time.sleep(10)

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
        tc = TC_AD_Bluetooth_11_15_AVRCP_Browsing_Virtual_File_System_Metadata_All_1("TC_AD_Bluetooth_11_15_AVRCP_Browsing_Virtual_File_System_Metadata_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
