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
from core.runtime.TestCase        import TestCase
from includes.BluetoothDialogInput import BluetoothDialogInput
from includes.BluetoothOpCodes          import OpCodes
from includes.BluetoothTestComponent    import BluetoothTestComponent
import time,re
from string import find


class TC_AD_Bluetooth_10_07_SAP_Server_Connection_Termination_Immediate_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        PTS_TC='TC_SERVER_DCN_BV_03_I '
        PTS = Session.getSetupFileParam('bt', 'addresspts')

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        # Setup HREF for immediate disconnect
        self.SendAndWaitForEvent(ComponentOne, OpCodes.DISABLE_BT, OpCodes.CURR_STATE_OFF, message='Disable BT App %s'%ComponentOne, timeout=30)
        self.runAdbCommand(ComponentOne, 'remount')
        self.RunShellCommand(ComponentOne, '". ./data/busybox/setup.sh;mv /system/lib/bluez-plugin/sap.so /system/lib/bluez-plugin/libbackup_sap.so"')
        self.RunShellCommand(ComponentOne, '". ./data/busybox/setup.sh;cp /system/lib/bluez-plugin/libsap_pts.so /system/lib/bluez-plugin/sap.so"')
        self.SendAndWaitForEvent(ComponentOne, OpCodes.ENABLE_BT_API, OpCodes.CURR_STATE_ON, message='Enable BT App %s'%ComponentOne, timeout=30)
        #Restart of board is needed here for the moment

        # Make local device discoverable
        self.setDiscoverable(ComponentOne)

        # From the remote device initiate a pairing request to the local device.
        BluetoothDialogInput('Press Enter then start the testcase: %s in PTS' % PTS_TC)

        # Accept incoming pairing request
        self.acceptIncomingSapPairing(ComponentOne, PTS, timeout=60)

        # Accept incoming SAP notification
        self.acceptIncomingSapConnection(ComponentOne)
        time.sleep(4)

        # Immediate disconnect
        BluetoothDialogInput('Disconnect')
        self.RunShellCommand(ComponentOne, 'dbus-send --system --dest=org.bluez --print-reply --type=method_call /org/bluez/test org.bluez.SimAccessTest.DisconnectImmediate')
        time.sleep(3)


    def postRun(self):
        TestCase.postRun(self)
        ComponentOne = '1'

        # Restore to normal state
        isEnabled = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_ISENABLED, OpCodes.GET_ISENABLED, message='Check state App %s'%ComponentOne, timeout=10)
        if isEnabled == "true":
            self.SendAndWaitForEvent(ComponentOne, OpCodes.DISABLE_BT, OpCodes.CURR_STATE_OFF, message='Disable BT App %s'%ComponentOne, timeout=30)
        self.RunShellCommand(ComponentOne, 'mv /system/lib/bluez-plugin/libbackup_sap.so /system/lib/bluez-plugin/sap.so')

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
        tc = TC_AD_Bluetooth_10_07_SAP_Server_Connection_Termination_Immediate_All_1("TC_AD_Bluetooth_10_07_SAP_Server_Connection_Termination_Immediate_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
