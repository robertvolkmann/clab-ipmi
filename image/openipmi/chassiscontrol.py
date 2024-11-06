#!/usr/bin/python3
# Taken from https://raw.githubusercontent.com/cminyard/openipmi/refs/heads/master/lanserv/ipmi_sim_chassiscontrol
#
# An example script for handling external power control.

# It's parameters are:
#
#  ipmi_sim_chassiscontrol <device> get [parm [parm ...]]
#  ipmi_sim_chassiscontrol <device> set [parm val [parm val ...]]
#
# where <device> is the particular target to reset and parm is either
# "power", "reset", or "boot".
#
# The output of the "get" is "<parm>:<value>" for each listed parm,
# and only power is listed, you cannot fetch reset.
# The output of the "set" is empty on success.  Error output goes to
# standard out (so it can be captured in the simulator) and the program
# returns an error.
#
# The values for power and reset are either "1" or "0".  Note that
# reset does a pulse, it does not set the reset line level.
#
# The value for boot is either "none", "pxe" or "default".

import sys


def do_get(parameters):
    for param in parameters:
        if param == "power":
            val = "0"
        elif param == "boot":
            val = "default"
        else:
            print(f"Invalid parameter: {param}")
            sys.exit(1)

        print(f"{param}:{val}")


def do_set(parameters):
    if len(parameters) % 2 != 0:
        print("Parameter and value pairs are required.")
        sys.exit(1)

    i = 0
    while i < len(parameters):
        param = parameters[i]
        i += 1
        if i >= len(parameters):
            print(f"No value present for parameter {param}")
            sys.exit(1)

        val = parameters[i]
        i += 1

        if param == "power":
            # Handle power setting logic here if needed
            pass

        elif param == "reset":
            # Reset is a pulse action; no specific logic here
            pass

        elif param == "boot":
            if val not in ["none", "pxe", "cdrom", "bios", "default"]:
                print(f"Invalid boot value: {val}")
                sys.exit(1)

        elif param == "identify":
            interval = val
            if i < len(parameters):
                force = parameters[i]
                i += 1
            else:
                force = None  # Assume optional
            # Handle identify settings here if needed

        else:
            print(f"Invalid parameter: {param}")
            sys.exit(1)


def do_check():
    # Check is not supported for chassis control
    sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage: chassiscontrol.py <device> <operation> [parameters...]")
        sys.exit(1)

    device = sys.argv[1]
    operation = sys.argv[2]
    parameters = sys.argv[3:]

    if operation == "get":
        do_get(parameters)
    elif operation == "set":
        do_set(parameters)
    elif operation == "check":
        do_check()
    else:
        print(f"Unknown operation: {operation}")
        sys.exit(1)


if __name__ == "__main__":
    main()
