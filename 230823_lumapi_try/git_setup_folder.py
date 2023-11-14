uuid = "8a24"

# append /uuid,/uuid/* to .gitignore
import os

with open(".gitignore", "a") as f:
    f.write("\n")
    f.write("!/" + uuid + "\n")
    f.write("!/" + uuid + "/*\n")

# create .gitignore in uuid folder
with open(os.path.join(uuid, ".gitignore"), "w") as f:
    # write following lines to .gitignore
    # *_p0.log
    # *.fsp
    # *.m1v
    # *_unbox.gds
    f.write("*_p0.log\n")
    f.write("*.fsp\n")
    f.write("*.m1v\n")
    f.write("*_unbox.gds\n")
