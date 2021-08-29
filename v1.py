from Simulation import Simulation
from Simulation import para
import math
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import numpy as np


para_v1 = para.copy()
sim_v1 = Simulation(0,para_v1)
sim_v1.start()
for i in range(para_v1['queueNum']):
    lab = "Fog node " + str(i+1)
    if i == 0:
        mark = "s"
    elif i == 1:
        mark = "^"
    elif i == 2:
        mark = "o"
    elif i == 3:
        mark = "x"
    if i == 0:
        lc = "#EA4614"
    elif i == 1:
        lc = "#859900"
    elif i == 2:
        lc = "#268BD2"
    elif i == 3:
        lc = "#6C71C4"
#    if i == 0:
#        linestyle = "-"
#    elif i == 1:
#        linestyle = (0, (1, 3))
#    elif i == 2:
#        linestyle = (0, (5, 3))
#    elif i == 3:
#        linestyle = (0, (3, 3, 1, 3))
    plt.figure(1)
    plt.plot(range(len(sim_v1.Q[i].statLength))[:2000:100], sim_v1.Q[i].statLength[:2000:100], marker = mark, markevery = 2, markerfacecolor = 'none', markersize = 5, lw = 1, c = lc, label = lab)
    #plt.bar(np.arange(len(sim_v1.Q[i].statLength[0:50])), sim_v1.Q[i].statLength[0:50],  color = lc, label = lab)
    #bottom += np.array(sim_v1.Q[i].statLength)
    plt.figure(2)
    plt.plot(range(len(sim_v1.Q[i].statAverDelay))[::100], sim_v1.Q[i].statAverDelay[::100], marker = mark, markevery = 10, markerfacecolor = 'none', markersize = 5, lw = 1, c = lc, label = lab)
    plt.figure(3)
    plt.plot(range(len(sim_v1.Q[i].statWorstDelay))[::100], sim_v1.Q[i].statWorstDelay[::100], marker = mark, markevery = 10, markerfacecolor = 'none', markersize = 5, lw = 1, c = lc, label = lab)
    plt.figure(4)
    plt.plot(range(len(sim_v1.Q[i].statAverDrop))[::100], sim_v1.Q[i].statAverDrop[::100], marker = mark, markevery = 10, markerfacecolor = 'none', markersize = 5, lw = 1, c = lc, label = lab)
plt.figure(1)
plt.xlabel("Time slot $t$")
plt.ylabel("Length of $Q_n(t)$")
plt.legend()
plt.grid(True)
ax = plt.gca()
ax.tick_params(direction="in", top = True, right = True)
plt.savefig('v1_1',dpi = 300)
plt.savefig('v30_1.eps', format='eps', dpi=1200)
plt.figure(2)
plt.xlabel("Time slot $t$")
plt.ylabel("Time-average response time")
plt.legend()
plt.grid(True)
ax = plt.gca()
ax.tick_params(direction="in", top = True, right = True)
plt.savefig('v1_2', dpi = 300)
plt.savefig('v30_2.eps', format='eps', dpi=1200)
plt.figure(3)
plt.xlabel("Time slot $t$")
plt.ylabel("Worst-case response time")
plt.legend()
plt.grid(True)
ax = plt.gca()
ax.tick_params(direction="in", top = True, right = True)
plt.savefig('v1_3', dpi = 300)
plt.savefig('v30_3.eps', format='eps', dpi=1200)
plt.figure(4)
plt.xlabel("Time slot $t$")
plt.ylabel("Tasks offloaded to the cloud")
plt.legend()
plt.grid(True)
ax = plt.gca()
ax.tick_params(direction="in", top = True, right = True)
plt.savefig('v1_4', dpi = 300)
plt.savefig('v30_4.eps', format='eps', dpi=1200)



"""
fw = open('data/v1/datafile','wb')
for i in range(para_v1['queueNum']):
    pickle.dump(sim_v1.Q[i].statLength, fw)
    pickle.dump(sim_v1.Q[i].statAverDelay, fw)
    pickle.dump(sim_v1.Q[i].statWorstDelay, fw)
    pickle.dump(sim_v1.Q[i].statAverDrop, fw)
fw.close()

fr = open('data/v1/datafile','rb')
dataStatLength = []
dataStatAverDelay = []
dataStatWorstDelay = [] 
dataStatAverDrop = []
for i in range(para_v1['queueNum']):
    dataStatLength.append(pickle.load(fr))
    dataStatAverDelay.append(pickle.load(fr))
    dataStatWorstDelay.append(pickle.load(fr))
    dataStatAverDrop.append(pickle.load(fr))
fr.close()

for i in range(para_v1['queueNum']):
    plt.figure(1)
    plt.plot(dataStatLength[i])
    plt.figure(2)
    plt.plot(dataStatAverDelay[i])
    plt.figure(3)
    plt.plot(dataStatWorstDelay[i])
    plt.figure(4)
    plt.plot(dataStatAverDrop[i])
plt.figure(1)
plt.savefig('data/v1/1')
plt.close()
plt.figure(2)
plt.savefig('data/v1/2')
plt.close()
plt.figure(3)
plt.savefig('data/v1/3')
plt.close()
plt.figure(4)
plt.savefig('data/v1/4')
plt.close()
"""
