from json_uuid import getdataName, getprefixName

# os copy
import os
import shutil

uuid_List=[
"0918", 
"caa4", 
"e71b", 
"498d", 
"b920", 
"0003", 
"7241", 
"e0f9", 
"315c", 
"aa10", 
"0ce5",
"fb22",
"c951",
"ae7c",
"baaf",
"792d",
"b1c2",
"9f91",
"b415",
"9acb",
"6b48",
"b7b6",
"0759",
"c541",
"8b48",
"7d44",
"b151",
"f504",
"3616",
"2a88",
"0022",
"39b9",
"32fc",
"4c2c",
"93ea",
"1332",
"ec72",
"209f",
"50b3",
"a596",
"0a0b",
"48bb",
"1859",
"df5e",
"dbd6",
"a668"]

# uuid_List = ["4e25"]
for uuid in uuid_List:
    dataName = getdataName(uuid)
    prefixName = getprefixName(uuid)
    shutil.copy(
        src=dataName + "_transmission.txt",
        dst=os.path.join(
            "./grating_sweep_released_2_fiber27", prefixName + "_transmission.txt"
        ),
    )
