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


class TC_AD_Bluetooth_7_01_OPP_Outgoing_Transfer_Single_Small_File_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        contactName = 'Test Testsson'
        contactNumber = '+46123456'
        contactMail = 'test.test@test.se'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Remove old vcf files (make sure you don't have any other vcf files in another location since that will make the test fail)
        self.RunShellCommand(ComponentOne, "rm /sdcard/*.vcf")
        self.RunShellCommand(ComponentTwo, "rm /sdcard/*.vcf")
        self.RunShellCommand(ComponentTwo, "rm /sdcard/bluetooth/*.vcf")

        #Bond devices
        self.PairDevices(ComponentOne, ComponentTwo, deviceOneAddress, deviceTwoAddress, timeout=30)
        time.sleep(2)

        #Perform OBEX
        self.Wakeup(ComponentTwo, timeout=10)
        self.EmptyNotificationsList(ComponentTwo)

        #Send Contacts via OPP
        self.ClearContacts(ComponentOne)
        self.ClearContacts(ComponentTwo)
        self.CreateContact(ComponentOne, contactName, contactNumber, contactMail)
        time.sleep(2)
        self.Wakeup(ComponentOne, timeout=20)
        self.SendContactListViaOPP(ComponentOne)

        #Wait for incoming toast noting an incoming transfer request then accept it
        self.WaitForEvent(ComponentTwo, OpCodes.ACTION_ACL_CONNECTED, timeout=40)
        self.Wakeup(ComponentTwo, timeout=20)
        self.AcceptIncomingNotification(ComponentTwo)

        #Wait for transfer to finish
        self.WaitForEvent(ComponentTwo, OpCodes.ACTION_ACL_DISCONNECTED, timeout=40)
        time.sleep(2)

        #Import contacts
        self.Wakeup(ComponentTwo, timeout=10)
        self.ImportSingleContact(ComponentTwo)
        time.sleep(5)

        #Retreive contacts
        self.SendCommand(ComponentTwo, OpCodes.GET_CONTACTS, message='Getting contacts')
        foundContacts = []
        foundContacts = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_CONTACTS, OpCodes.CONTACT_FOUND, timeout=120)

        #Verify file transfer OK i.e correct contact received
        self.log.info('%s \n %s',len(foundContacts), foundContacts)
        targetString = "%s;%s;%s"%(contactName, contactNumber, contactMail)
        targetFound = self.MatchStringInList(foundContacts,targetString)
        if not targetFound:
            self.log.info("Sent contact not found")
            raise Failure('Sent contact not found')
        else:
            self.log.info("Sent contact found")

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
        tc = TC_AD_Bluetooth_7_01_OPP_Outgoing_Transfer_Single_Small_File_All_1("TC_AD_Bluetooth_7_01_OPP_Outgoing_Transfer_Single_Small_File_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
