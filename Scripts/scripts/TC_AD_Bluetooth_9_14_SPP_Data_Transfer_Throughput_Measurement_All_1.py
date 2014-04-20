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
import re,time


class TC_AD_Bluetooth_9_14_SPP_Data_Transfer_Throughput_Measurement_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'
        DataAmountKb = int(Session.getSetupFileParam('bt', 'sppthroughputdataamount')) #KiloBytes
        TransferBuffer = int(Session.getSetupFileParam('bt', 'sppbuffersize'))
        requirement = float(Session.getSetupFileParam('bt', 'sppthroughput'))

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Bond devices
        self.PairDevices(ComponentOne, ComponentTwo, deviceOneAddress, deviceTwoAddress, timeout=30)
        time.sleep(5)

        #Create and connect the SPP service
        serverId = self.SendAndWaitForEvent(ComponentOne, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, OpCodes.LISTEN_USING_RFCOMM_WITH_SERVICE_RECORD, message='SPP;%s'%BTC.SERVICE_SERIAL_PORT_PROFILE, timeout=10)
        clientId = self.SendAndWaitForEvent(ComponentTwo, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, OpCodes.CREATE_SOCKET_TO_SERVICE_RECORD, message='%s;%s'%(deviceOneAddress,BTC.SERVICE_SERIAL_PORT_PROFILE), timeout=10)
        self.SendCommand(ComponentOne, OpCodes.RFCOMM_ACCEPT, message='60000;%s'%serverId)
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.RFCOMM_CONNECT, OpCodes.RFCOMM_CONNECT, message=clientId, timeout=20)
        time.sleep(3)

        #Start data transfer
        self.SendCommand(ComponentTwo, OpCodes.RECEIVE_DATA_CLIENT, message='%s;%s;%s'%(clientId, BTC.RFCOMM_IGNORE, TransferBuffer))
        time.sleep(1)
        transferTime = self.SendAndWaitForEvent(ComponentOne, OpCodes.DATA_PUMP_SERVER, OpCodes.DATA_PUMP_SERVER, message='%s;%s;%s'%(serverId, DataAmountKb*1024, TransferBuffer),timeout=2400)

        #Calculate Throughput
        transferTime = float(transferTime)
        DataAmountKb = float(DataAmountKb)
        tp = float()
        tp = ((DataAmountKb*8.0)/1024.0)/(transferTime/1000.0)
        time.sleep(3)
        self.log.info("ThroughPut = %s, tt = %s, da = %s, da/tt = %s"%(tp, transferTime, DataAmountKb,(DataAmountKb/transferTime)))

        #Close connections
        self.SendAndWaitForEvent(ComponentOne, OpCodes.CLOSE_CONNECTION_SERVER, OpCodes.CLOSE_CONNECTION_SERVER, message=serverId, timeout=30)
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.CLOSE_CONNECTION_CLIENT, OpCodes.CLOSE_CONNECTION_CLIENT, message=clientId, timeout=30)
        self.SendAndWaitForEvent(ComponentOne, OpCodes.REMOVE_RFCOMM_SERVICE, OpCodes.REMOVE_RFCOMM_SERVICE, message=serverId, timeout=30)

        #Clean up
        self.RestoreApplication(ComponentOne)
        self.RestoreApplication(ComponentTwo)
        if tp < requirement:
            raise Failure("Throughput of %s is lower then the requirement of %s"%(tp,requirement))
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
        tc = TC_AD_Bluetooth_9_14_SPP_Data_Transfer_Throughput_Measurement_All_1("TC_AD_Bluetooth_9_14_SPP_Data_Transfer_Throughput_Measurement_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
