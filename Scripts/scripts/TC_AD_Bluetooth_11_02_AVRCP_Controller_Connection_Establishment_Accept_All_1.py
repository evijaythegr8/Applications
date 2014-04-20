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


class TC_AD_Bluetooth_11_02_AVRCP_Controller_Connection_Establishment_Accept_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ptsAddress = Session.getSetupFileParam('bt', 'addresspts')
        ptsTestCase='TC_TG_CEC_BV_02'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        # Make local device discoverable
        self.Wakeup(ComponentOne, timeout=240)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_DISCOVERABLE, OpCodes.SET_DISCOVERABLE, message='300', timeout=10)
        time.sleep(4)
        self.pressYes(ComponentOne)

        # From the remote device initiate a pairing request to the local device.
        BluetoothDialogInput('Press OK, then start the test case: %s in PTS'%ptsTestCase)
        time.sleep(15)

        self.pressKey(ComponentOne,'85')
        time.sleep(5)

        #Initiate outgoing connection
        try:
            self.InitiateAndAcceptPairing(ComponentOne, ptsAddress, timeout=30)
        except:
            self.log.info("Auto pairing?")
        self.SendCommand(ComponentOne, OpCodes.CONNECT_SINK, message=ptsAddress)
        time.sleep(5)

        #Disconnect devices
        self.SendCommand(ComponentOne, OpCodes.DISCONNECT_SINK, message=ptsAddress)

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
        tc = TC_AD_Bluetooth_11_02_AVRCP_Controller_Connection_Establishment_Accept_All_1("TC_AD_Bluetooth_11_02_AVRCP_Controller_Connection_Establishment_Accept_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
