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


class TC_AD_Bluetooth_7_04_OPP_Outgoing_Transfer_Multiple_Large_Files_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        images = []
        images.append('pic_1.8_Mpix_WSXGA+_16x10_JFIF_1.02_Exif_2.21_Progressive_Q11.jpg')
        images.append('pic_2.3_Mpix_WUXGA_16x10_JFIF_1.02_Exif_2.21_BaselineStd_Q11.jpg')
        images.append('pic_2.3_Mpix_WUXGA_16x10_JFIF_1.02_Exif_2.21_Progressive_Q11.jpg')
        images.append('pic_3.1_Mpix_QXGA_4x3_Exif_2.21_BaselineStd_Q11.jpg')
        images.append('pic_3.1_Mpix_QXGA_4x3_JFIF_1.02_Exif_2.21_BaselineStd_Q9.jpg')
        mediaPaths = []
        for i in images:
            mediaPaths.append('/sdcard/%s'%i)
        targetPaths = []
        for i in images:
            targetPaths.append('/sdcard/bluetooth/%s'%i)

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
        self.Wakeup(ComponentTwo, timeout=10)
        self.EmptyNotificationsList(ComponentTwo)

        #Remove and re-upload reference files
        index = 0
        while index < len(images):
            self.RunShellCommand(ComponentTwo, "rm %s"%mediaPaths[index])
            self.RunShellCommand(ComponentTwo, "rm %s"%targetPaths[index])
            self.RunShellCommand(ComponentOne, "rm %s"%mediaPaths[index])
            self.pushFileFromContentDatabase(ComponentOne, images[index], mediaPaths[index])
            self.pushFileFromContentDatabase(ComponentTwo, images[index], mediaPaths[index])
            time.sleep(2)
            index +=1

        #Send image with Bluetooth
        collectedMediaPaths = mediaPaths[0]
        for i in range(1, len(mediaPaths)):
            collectedMediaPaths = "%s;%s"%(collectedMediaPaths, mediaPaths[i])
        self.Wakeup(ComponentOne, timeout=10)
        self.SendImages(ComponentOne, collectedMediaPaths)

        #Wait for incoming transfer request then accept it
        self.WaitForEvent(ComponentTwo, OpCodes.ACTION_ACL_CONNECTED, timeout=240)
        self.Wakeup(ComponentTwo, timeout=10)
        self.AcceptIncomingNotification(ComponentTwo)

        # Wait for transfer to finish
        self.WaitForEvent(ComponentTwo, OpCodes.ACTION_ACL_DISCONNECTED, timeout=240)
        time.sleep(2)

        # Verify file transfer OK
        index = 0
        while index < len(images):
            result = self.VerifyFileTransfer(ComponentTwo, images[index])
            if result == 'False':
                raise Failure("File was not transferred correctly")
            index +=1

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
        tc = TC_AD_Bluetooth_7_04_OPP_Outgoing_Transfer_Multiple_Large_Files_All_1("TC_AD_Bluetooth_7_04_OPP_Outgoing_Transfer_Multiple_Large_Files_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
