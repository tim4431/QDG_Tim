from json_uuid import getdataName, getprefixName

# os copy
import os
import shutil

uuid_List=["82d5", 
"0a7a", 
"8e24", 
"d491", 
"61a5", 
"f38f", 
"d6b1", 
"e00e", 
"cf31", 
"a67d", 
"f855",
"98f0",
"45ec",
"686a",
"92da",
"cde0",
"c62e",
"c2bc",
"4901",
"8572",
"3442",
"de6b",
"8977",
"c158",
"71de",
"8cfd",
"7081",
"6184",
"b2a6",
"bae3",
"3140",
"c4e5",
"7e80",
"1574",
"f951",
"224e",
"231c",
"fdb9",
"3d59",
"6469",
"ea47",
"1074",
"e435",
"1920",
"f1f8"]

# uuid_List = ["4e25"]
for uuid in uuid_List:
    dataName = getdataName(uuid)
    prefixName = getprefixName(uuid)
    shutil.copy(
        src=dataName + "_transmission.txt",
        dst=os.path.join(
            "./grating_sweep_airclad_1", prefixName + "_transmission.txt"
        ),
    )
