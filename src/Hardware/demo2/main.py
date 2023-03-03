from motors import Motors
from devices import *
from gpioi import *

import time

mc = Motors()
f = FanGroup(mc, [])

m_start_sensor = Button(8)
m = Motor(mc, [0], forward_values=[-80], start_sensor=m_start_sensor)


def main():
    pass

if __name__ == "__main__":
    main()

