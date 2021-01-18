import re


s = open("trex.py").read()

new_s = re.sub(r"([a-z])([A-Z])", "\1_" + "\2".lower(), s)

open("trex.py", "w").write(new_s)
