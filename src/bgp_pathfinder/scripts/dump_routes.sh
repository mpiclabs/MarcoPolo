#!/bin/bash
# -*- coding: utf-8 -*-



SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR/..

./send_cmd.py "birdc6 show route for 2604:4540:80:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes80.txt
./send_cmd.py "birdc6 show route for 2604:4540:81:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes81.txt
./send_cmd.py "birdc6 show route for 2604:4540:82:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes82.txt
./send_cmd.py "birdc6 show route for 2604:4540:83:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes83.txt
./send_cmd.py "birdc6 show route for 2604:4540:84:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes84.txt
./send_cmd.py "birdc6 show route for 2604:4540:85:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes85.txt
./send_cmd.py "birdc6 show route for 2604:4540:86:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes86.txt
./send_cmd.py "birdc6 show route for 2604:4540:87:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes87.txt
./send_cmd.py "birdc6 show route for 2604:4540:88:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes88.txt
./send_cmd.py "birdc6 show route for 2604:4540:89:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes89.txt
./send_cmd.py "birdc6 show route for 2604:4540:8a:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes8a.txt
./send_cmd.py "birdc6 show route for 2604:4540:8b:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes8b.txt
./send_cmd.py "birdc6 show route for 2604:4540:8c:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes8c.txt
./send_cmd.py "birdc6 show route for 2604:4540:8d:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes8d.txt
./send_cmd.py "birdc6 show route for 2604:4540:8e:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes8e.txt
./send_cmd.py "birdc6 show route for 2604:4540:8f:: all protocol vultr" > ~/My\ Drive/Documents/school/ele\ 297/technical/tango/control-plane/routes8f.txt