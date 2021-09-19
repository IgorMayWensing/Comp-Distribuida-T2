import os

os.system("gnome-terminal --geometry=50x20+460+0 -- bash -c \'python3 node.py 9000; exec bash\'")
os.system("gnome-terminal --geometry=50x20+920+0 -- bash -c \'python3 node.py 9001; exec bash\'")
os.system("gnome-terminal --geometry=106x10+460+410 -- bash -c \'python3 node.py 9002; exec bash\'")
os.system("gnome-terminal --geometry=50x20+460+900 -- bash -c \'python3 node.py 9003; exec bash\'")
os.system("gnome-terminal --geometry=50x20+920+900 -- bash -c \'python3 node.py 9004; exec bash\'")
