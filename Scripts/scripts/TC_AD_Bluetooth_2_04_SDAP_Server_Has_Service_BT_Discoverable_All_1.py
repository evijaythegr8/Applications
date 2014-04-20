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
from string import find
import re,time
from includes.BluetoothConstants import BluetoothConstants


class TC_AD_Bluetooth_2_04_SDAP_Server_Has_Service_BT_Discoverable_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Bond devices
        self.PairDevices(ComponentTwo, ComponentOne, deviceTwoAddress, deviceOneAddress)
        time.sleep(5)

        #Enable PAN
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.ENABLE_PAN, OpCodes.ENABLE_PAN, message='Enable PAN', timeout=10)

        ##################################################################################################

        serviceInt = BluetoothConstants.LIMITED_DISCOVERABILITY
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.HAS_SERVICE, OpCodes.HAS_SERVICE, message="%s;%s"%(deviceTwoAddress, serviceInt) , timeout=10)

        if returnData == "true":
            self.log.info("Found service LIMITED_DISCOVERABILITY")
            raise Failure("Found service LIMITED_DISCOVERABILITY")
        else:
            self.log.info("Could not find service LIMITED_DISCOVERABILITY")

        ##################################################################################################

        serviceInt = BluetoothConstants.POSITIONING

        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.HAS_SERVICE, OpCodes.HAS_SERVICE, message="%s;%s"%(deviceTwoAddress, serviceInt) , timeout=10)

        if returnData == "true":
            self.log.info("Found service POSITIONING")
            raise Failure("Found service POSITIONING")
        else:
            self.log.info("Could not find service POSITIONING")

        ##################################################################################################

        serviceInt = BluetoothConstants.NETWORKING

        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.HAS_SERVICE, OpCodes.HAS_SERVICE, message="%s;%s"%(deviceTwoAddress, serviceInt) , timeout=10)

        if returnData == "true":
            self.log.info("Found service NETWORKING")
        else:
            self.log.info("Could not find service NETWORKING")
            raise Failure("Could not find service NETWORKING")

        ##################################################################################################

        serviceInt = BluetoothConstants.RENDER

        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.HAS_SERVICE, OpCodes.HAS_SERVICE, message="%s;%s"%(deviceTwoAddress, serviceInt) , timeout=10)

        if returnData == "true":
            self.log.info("Found service RENDER")
            raise Failure("Found service RENDER")
        else:
            self.log.info("Could not find service RENDER")

        ##################################################################################################

        serviceInt = BluetoothConstants.CAPTURE

        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.HAS_SERVICE, OpCodes.HAS_SERVICE, message="%s;%s"%(deviceTwoAddress, serviceInt) , timeout=10)

        if returnData == "true":
            self.log.info("Found service CAPTURE")
        else:
            self.log.info("Could not find service CAPTURE")
            raise Failure("Could not find service CAPTURE")

        ##################################################################################################

        serviceInt = BluetoothConstants.OBJECT_TRANSFER

        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.HAS_SERVICE, OpCodes.HAS_SERVICE, message="%s;%s"%(deviceTwoAddress, serviceInt) , timeout=10)

        if returnData == "true":
            self.log.info("Found service OBJECT_TRANSFER")
        else:
            self.log.info("Could not find service OBJECT_TRANSFER")
            raise Failure("Could not find service OBJECT_TRANSFER")

        ##################################################################################################

        serviceInt = BluetoothConstants.AUDIO

        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.HAS_SERVICE, OpCodes.HAS_SERVICE, message="%s;%s"%(deviceTwoAddress, serviceInt) , timeout=10)

        if returnData == "true":
            self.log.info("Found service AUDIO")
            raise Failure("Found service AUDIO")
        else:
            self.log.info("Could not find service AUDIO")

        ##################################################################################################

        serviceInt = BluetoothConstants.TELEPHONY

        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.HAS_SERVICE, OpCodes.HAS_SERVICE, message="%s;%s"%(deviceTwoAddress, serviceInt) , timeout=10)

        if returnData == "true":
            self.log.info("Found service TELEPHONY")
        else:
            self.log.info("Could not find service TELEPHONY")
            raise Failure("Could not find service TELEPHONY")

        ##################################################################################################

        serviceInt = BluetoothConstants.INFORMATION

        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.HAS_SERVICE, OpCodes.HAS_SERVICE, message="%s;%s"%(deviceTwoAddress, serviceInt) , timeout=10)

        if returnData == "true":
            self.log.info("Found service INFORMATION")
            raise Failure("Found service INFORMATION")
        else:
            self.log.info("Could not find service INFORMATION")

        ##################################################################################################

        # try a service that does not exist

        serviceInt = BluetoothConstants.NONEXISTING

        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.HAS_SERVICE, OpCodes.HAS_SERVICE, message="%s;%s"%(deviceTwoAddress, serviceInt) , timeout=10)

        if returnData == "false":
            self.log.info("HasService returned false = > OK")
        else:
            self.log.info("HasService returned true while false was expected")
            raise Failure("HasService returned true while false was expected")

        ##################################################################################################

        #Disable PAN
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.DISABLE_PAN, OpCodes.DISABLE_PAN, message='Disable PAN', timeout=10)

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
        tc = TC_AD_Bluetooth_2_04_SDAP_Server_Has_Service_BT_Discoverable_All_1("TC_AD_Bluetooth_2_04_SDAP_Server_Has_Service_BT_Discoverable_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
