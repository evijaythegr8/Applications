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
from includes.BluetoothOpCodes import OpCodes
from includes.BluetoothTestComponent import BluetoothTestComponent
from includes.BluetoothConstants import BluetoothConstants as BTC
from string import find
import time,re


class TC_AD_Bluetooth_7_12_OPP_Incoming_Transfer_Rejected_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        image = 'pic_1.8_Mpix_WSXGA+_16x10_JFIF_1.02_Exif_2.21_BaselineStd_Q11.jpg'
        mediaPath = '/sdcard/%s'%image
        targetPath = '/sdcard/bluetooth/%s'%image

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Bond devices
        self.PairDevices(ComponentOne, ComponentTwo, deviceOneAddress, deviceTwoAddress, timeout=30)
        time.sleep(2)

        #Perform OBEX

        #Clear notifications on target device
        self.Wakeup(ComponentOne, timeout=10)
        self.EmptyNotificationsList(ComponentOne)

        #Remove and re-upload reference files
        self.RunShellCommand(ComponentOne, "rm %s"%targetPath)
        self.RunShellCommand(ComponentTwo, "rm %s"%mediaPath)
        self.pushFileFromContentDatabase(ComponentTwo, image, mediaPath)
        time.sleep(2)

        #Send image with Bluetooth
        self.Wakeup(ComponentTwo, timeout=10)
        self.SendImages(ComponentTwo, mediaPath)

        #Wait for incoming transfer request then reject it
        self.WaitForEvent(ComponentOne, OpCodes.ACTION_ACL_CONNECTED, timeout=240)
        self.Wakeup(ComponentOne, timeout=10)
        self.RejectIncomingNotification(ComponentOne)

        #Wait for transfer to finish
        self.WaitForEvent(ComponentOne, OpCodes.ACTION_ACL_DISCONNECTED, timeout=20)
        time.sleep(2)

        # Verify that the file was not transfered OK
        result = self.RunShellCommand(ComponentOne, "ls %s"%(targetPath))
        if find(result, 'No such file or directory') != -1:
            pass
        else:
            raise Failure("File was created, and not removed")

        #Clean up
        self.RestoreApplication(ComponentOne)
        self.RestoreApplication(ComponentTwo)
        self.CloseDownExecution()


if __name__ == '__main__':
    from core.script.Script                   import Script
    from core.setup.Environment               import Environment
    from plugins.android.device.AndroidDevice import AndroidDevice

    Session.init(Script(__file__))

    duts = []
    dut1 = AndroidDevice('DUT1', connection=1)
    dut2 = AndroidDevice('DUT2', connection=1)
    duts.append(dut1)
    duts.append(dut2)

    env = Environment()
    env.addEquipment(dut1)
    env.addEquipment(dut2)

    if(env.setup()):
        tc = TC_AD_Bluetooth_7_12_OPP_Incoming_Transfer_Rejected_All_1("TC_AD_Bluetooth_7_12_OPP_Incoming_Transfer_Rejected_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
