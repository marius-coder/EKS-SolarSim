# -*- coding: latin-1 -*-
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from Sonnenstand import Sonne


sun = Sonne()
date = "2006-06-21 14:00:00"
sun.Init("nepal")
test = sun.CalcSonnenstand(date, debug = False)
sun.CalcGlobalstrahlung(hohenwinkel = test["Hohenwinkel"], debug = False)

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

inter = np.linspace(0, 2, 49)#[:-1]
theta = inter*np.pi
ax.set_rlim(bottom=90, top=0)
ax.plot(theta,sun.horizonList, color = "grey")
plt.fill_between(theta, 0, sun.horizonList, alpha=0.2)
#ticks neu setzen und Warning zu unterdr�cken
ticks_loc = ax.get_xticks().tolist()
ax.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
ax.set_theta_zero_location("N")
plt.show()