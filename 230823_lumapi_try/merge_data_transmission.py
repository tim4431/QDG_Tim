from json_uuid import getdataName, getprefixName

# os copy
import os
import shutil


def merge_data_transmission(uuid_List, merge_dst: str):
    for uuid in uuid_List:
        dataName = getdataName(uuid)
        prefixName = getprefixName(uuid)
        shutil.copy(
            src=dataName + "_transmission.txt",
            dst=os.path.join(merge_dst, prefixName + "_transmission.txt"),
        )
