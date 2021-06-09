# This Python script will run on every boot.
# When executed, the root filesystem will be mounted so that CircuitPython can write to it.
# This script file allows files to be saved to the flash drive through CircuitPython code.
# The Pi Pico LCARS code will save a list of historic atmospheric pressure readings in order
# to allow the pressure trend graph to be drawn.
# This can only be done if the filesystem is writable.
# If you do not wish to save these readings, this boot.py script file is not required.
#
# ###########################
# #-------- HOWEVER --------#
# ###########################
#
# Allowing the CircuitPython code to write to the filesystem means that USB write
# access will be disabled. Thus, you will no longer be able to edit the code using
# the CircuitPython editor or by other means.
# Furthermore, you will be unable to delete or rename the boot.py file using file
# manager.
#
# In order to regain write access to the filesystem through USB, carry out the
# following.
#
# Use REPL to execute the following commands:-
#
# >>> import os
# >>> os.listdir("/")
# >>> os.rename("/boot.py", "/boot.bak")
#
# This will rename the 'boot.py' script to 'boot.bak'
#
# After rebooting the device, the filesystem will again be writeable, so you
# will be able to edit via USB as normal.
#

import storage

storage.remount("/", False)