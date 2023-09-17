from json_uuid import getdataName, getprefixName

# os copy
import os
import shutil


uuid_List = ["4e25"]
for uuid in uuid_List:
    dataName = getdataName(uuid)
    prefixName = getprefixName(uuid)
    shutil.copy(
        src=dataName + "_transmission.txt",
        dst=os.path.join(
            "./grating_sweep_released_1", prefixName + "_transmission.txt"
        ),
    )
