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
from includes.BluetoothOpCodes import OpCodes
from includes.BluetoothTestComponent import BluetoothTestComponent
from includes.BluetoothConstants import BluetoothConstants as BTC
from string import find
import re,time


class TC_AD_Bluetooth_9_17_SPP_Long_Duration_Idle_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        DataAmountKb = int(Session.getSetupFileParam('bt', 'spptransferdataamount')) #KiloBytes
        Duration = int(Session.getSetupFileParam('bt', 'spplongduration')) #Minutes
        nbrOfKbToSend = int(Session.getSetupFileParam('bt', 'sppbuffersize'))
        bufferSize = int(Session.getSetupFileParam('bt', 'sppbuffersize'))

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Bond devices
        self.PairDevices(ComponentOne, ComponentTwo, deviceOneAddress, deviceTwoAddress, timeout=30)

        time.sleep(5)

        serverId = self.SendAndWaitForEvent(ComponentOne, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='SPP;%s'%BTC.SERVICE_SERIAL_PORT_PROFILE, timeout=10)
        clientId = self.SendAndWaitForEvent(ComponentTwo, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, message='%s;%s'%(deviceOneAddress,BTC.SERVICE_SERIAL_PORT_PROFILE), timeout=10)

        self.SendCommand(ComponentOne, OpCodes.RFCOMM_ACCEPT, message='60000;%s'%serverId)
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.RFCOMM_CONNECT, OpCodes.RFCOMM_CONNECT, message=clientId, timeout=20)

        # wait the time defined in setup_local.ini

        self.log.info('Label:   Waiting for: %s minutes'%(Duration))
        time.sleep(Duration*60)

        # send data to check that connection is still alive and healthy
        self.SendCommand(ComponentOne, OpCodes.RECEIVE_DATA_SERVER, message='%s;%s;%s'%(serverId, BTC.RFCOMM_CHECK_DATA, bufferSize))
        time.sleep(1)
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.DATA_PUMP_CLIENT, OpCodes.DATA_PUMP_CLIENT, message='%s;%s;%s'%(clientId, (nbrOfKbToSend*1024), bufferSize), timeout=180)
        time.sleep(5)

        #Close connection
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.CLOSE_CONNECTION_CLIENT, OpCodes.CLOSE_CONNECTION_CLIENT, message=clientId, timeout=30)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message=serverId, timeout=30)

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
        tc = TC_AD_Bluetooth_9_17_SPP_Long_Duration_Idle_All_1("TC_AD_Bluetooth_9_17_SPP_Long_Duration_Idle_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
