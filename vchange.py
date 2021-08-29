from Simulation import Simulation
from Simulation import para
import matplotlib.pyplot as plt


rounds = 1
statThroughput = []
statWorstDelay = [] # only for Q[0]
statAverDelay = []
V = []
i = 1
while i < 101:
    para['V'] = i
    tempThroughput = 0
    tempWorstDelay = 0
    tempAverDelay = 0
    for j in range(rounds):
        sim = Simulation(0,para)
        sim.start()
        tempThroughput += sim.throughput() # this is in fact the obj value, not throughput
        tempWorstDelay += sim.Q[3].worstDelay
        temp = 0
        temp2 = 0
        for k in range(para['queueNum']):
            temp += sim.Q[k].statAverDelay[-1]*(para['arriveRate'][k] - sim.Q[k].statAverDrop[-1])
            temp2 += para['arriveRate'][k] - sim.Q[k].statAverDrop[-1]
        tempAverDelay += temp/temp2
    tempThroughput = tempThroughput/rounds
    tempWorstDelay = tempWorstDelay/rounds
    tempAverDelay = tempAverDelay/rounds
    statThroughput.append(tempThroughput)
    statWorstDelay.append(tempWorstDelay)
    statAverDelay.append(tempAverDelay)
    V.append(i)
    print(i)
    if i < 10:
        i += 1
    elif i < 100:
        i += 5
    elif i < 301:
        i += 20

print(sim.theoryThroughput)
print(statThroughput)
print(statWorstDelay)
print(statAverDelay)

me = [0, 9, 11, 13, 15, 17, 19, 21, 23, 25, -1]
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
l1 = ax1.plot(V,statThroughput, marker = 's', markerfacecolor = 'none', markersize = 5, markevery = me, lw = 1, c = "#cb4b16", label = 'Algorithm performance')
ax1.plot(V,[sim.theoryThroughput for i in V], c = 'k', ls = '--')
plt.grid(True)

ax1.set_xlabel("V")
ax1.set_ylabel("System performance")

ax1.tick_params(direction="in", top = True)
ax1.annotate("Optimal system performance", xy = (60,7.222), xytext = (20, 7.20), arrowprops = dict(arrowstyle='->'))


l2 = ax2.plot(V,[20+(2*para['beta']*i*para['gfunc_deriv'][3](0)+2*para['A_max']+4*para['p'])/para['epsilon'] for i in V], marker = 'o', markerfacecolor = 'none', markersize = 5, markevery = me, lw = 1, c = "#268BD2", label = "Response time bound")
l3 = ax2.plot(V,statWorstDelay, marker = 'x', markerfacecolor = 'none', markersize = 5, markevery = me, lw = 1, c = "#6C71C4", ls = "-.", label = "Worst-case response time")
l4 = ax2.plot(V,statAverDelay, marker = '^', markerfacecolor = 'none', markersize = 5, markevery = me, lw = 1, c = "#b58900", ls = "--", label = "Time-average response time")


ax2.set_ylabel("Response time")
#ax2.set_ylim(0,120)
lns = l1 + l2 + l3 + l4
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc = 'right')

plt.savefig('vchange.eps', format='eps', dpi = 1200)
plt.savefig('vchange.png', format='png', dpi = 300)

f = open('vchange.txt', 'w')
f.write('theoryThroughpu, statThroughput, statWorstDelay, statAverDelay'+'\n')
f.write(str(sim.theoryThroughput)+'\n')
f.write(str(statThroughput)+'\n')
f.write(str(statWorstDelay)+'\n')
f.write(str(statAverDelay)+'\n')
f.close()



