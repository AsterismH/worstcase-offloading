from Simulation import Simulation
import math
import matplotlib.pyplot as plt
import random
import numpy as np


para = {
        'maxslots': 1000000,
        'maxpackets': 5000000,
        'debug': 0,
        'V': 100,
        'queueNum': 4,
        'arriveRate': [[1,0.6], [1,0.8], [1,0.4], [1,0.3]],
        'taskInfo': {'datasize':0, 'totalCycle':1},
        'e_aver': [0.3, 0.6, 0.8, 0.2], 
        'roundTrip': [[0,10,10,20], [10,0,10,20], [10,10,0,20], [20,20,20,0]],
        'gfunc': [lambda x: math.log(5.0+x), lambda x: math.log(5.0+2*x), \
                   lambda x: math.log(5.0+3*x), lambda x: math.log(5.0+4*x)],
        'gfunc_deriv': [lambda x: 1.0/(5+x), lambda x: 2.0/(5+2*x), \
                        lambda x: 3.0/(5+3*x), lambda x: 4.0/(5+4*x)]
        }


para_v1 = para.copy()
rounds = 10
averResTime = []
worstResTime = []
optPerm = []
algPerm = []
temp = 0
random.seed()
for j in range(rounds):
    temp = 0
    temp2 = 0
    for i in range(para_v1['queueNum']):
        para_v1['arriveRate'][i][1] = random.random()
    sim_v1 = Simulation(0,para_v1,para_v1['maxslots'],para_v1['maxpackets'])
    sim_v1.start()
    optPerm.append(sim_v1.theoryThroughput)
    algPerm.append(sim_v1.throughput())
    for k in range(para_v1['queueNum']):
        temp += sim_v1.Q[k].statAverDelay[-1]*(para['arriveRate'][k][1] - sim_v1.Q[k].statAverDrop[-1])
        temp2 += para['arriveRate'][k][1] - sim_v1.Q[k].statAverDrop[-1]
    averResTime.append(temp/temp2)
    worstResTime.append(sim_v1.Q[3].worstDelayIM)
    print(j)
    
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
X = np.arange(10)+1
l1, = ax2.plot(X,optPerm, marker = 's', markerfacecolor = 'none', markersize = 5, lw = 1, c = "#b58900", label = 'Optimal performance')
l2, = ax2.plot(X,algPerm, marker = '^', markerfacecolor = 'none', markersize = 5, lw = 1, ls = '--', c = "#EA4614", label = 'Algorithm performance')
#l3 = ax2.plot(averResTime, marker = 'o', markerfacecolor = 'none', markersize = 5, lw = 1, c = '#268BD2', label = 'Time-average response time')
#l4 = ax2.plot(worstResTime, marker = 'x', markerfacecolor = 'none', markersize = 5, lw = 1, ls = '-.', c = '#6C71C4', label = 'Worst case response time')
l3 = ax1.bar(X-0.15,worstResTime, width = 0.3, color = '#268BD2', edgecolor = 'k', hatch = "//", label = 'Worst-case response time')
l4 = ax1.bar(X+0.15,averResTime, width = 0.3, color = '#7C509D', edgecolor = 'k', hatch = "\\\\", label = 'Time-average response time')
ax1.set_xlabel("Simulation rounds")
ax2.set_ylabel("System performance")
ax1.set_ylabel("Response time")
               
ax2.set_ylim(5,8)
ax1.set_ylim(0,100)
               
#lns = [l1,l2,l3,l4]
#labs = [l.get_label() for l in lns]
#labs = [l1.get_label(), l2.get_label(), l3.get_label(), l4.get_label()]
ax1.legend((l1,l2,l3,l4), ('Optimal performance', 'Algorithm performance', 'Worst-case response time', 'Time-average response time'), ncol = 2, fontsize = 9)
#plt.legend()
#ax1.legend()
#ax2.legend()
plt.grid(True)
ax1.tick_params(direction="in", top = True)
ax1.tick_params(axis = 'y')
ax2.tick_params(direction="in")
ax2.tick_params(axis = 'y')
plt.savefig("arrival", dpi = 300)
    
print(optPerm)
print(algPerm)
print(worstResTime)
print(averResTime)    
    
    
"""    
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
plt.figure(2)
plt.xlabel("Time slot $t$")
plt.ylabel("Time-average response time")
plt.legend()
plt.grid(True)
ax = plt.gca()
ax.tick_params(direction="in", top = True, right = True)
plt.savefig('v1_2', dpi = 300)
plt.figure(3)
plt.xlabel("Time slot $t$")
plt.ylabel("Worst-case response time")
plt.legend()
plt.grid(True)
ax = plt.gca()
ax.tick_params(direction="in", top = True, right = True)
plt.savefig('v1_3', dpi = 300)
plt.figure(4)
plt.xlabel("Time slot $t$")
plt.ylabel("Tasks offloaded to the cloud")
plt.legend()
plt.grid(True)
ax = plt.gca()
ax.tick_params(direction="in", top = True, right = True)
plt.savefig('v1_4', dpi = 300)
"""


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
