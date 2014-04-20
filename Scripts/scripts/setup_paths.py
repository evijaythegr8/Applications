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
import os, sys

path = os.path.realpath(os.path.join(os.path.dirname( __file__ ), ".."))

if(path not in sys.path):
    sys.path.append(path)

import setup_external_paths
