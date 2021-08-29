from SimFog1 import SimFog1
from SimCoR import SimCoR
from SimNoP import SimNoP
from SimOPEN import SimOPEN

from Parameter import para_fog1
from Parameter import para_test

import copy
import matplotlib.pyplot as plt
import pickle

"""
all time average statistics are with comparison
need drop, block, delay history
"""

def plotRunTime(para):
    parameter = copy.deepcopy(para)
    simfog1 = SimFog1(parameter)
    simfog1.start()
    parameter = copy.deepcopy(para)
    simnop = SimNoP(parameter)
    simnop.start()
    parameter = copy.deepcopy(para)
    simopen = SimOPEN(parameter)
    simopen.start()
    parameter = copy.deepcopy(para)
    simcor = SimCoR(parameter)
    simcor.start()
    # obtain time average throughput and drop rate
    # throughput = average_arrival*slot - total blocked workload - dropped workload
    # utility = throughput - 2*dropped workload
    # related data for simfog1
    simfog1_averDrop = [0 for _ in range(para.maxTime)]
    simfog1_averBlock = [0 for _ in range(para.maxTime)]
    simfog1_totalDelay = [0 for _ in range(para.maxTime)]
    simfog1_totalThroughput = [0 for _ in range(para.maxTime)]
    simfog1_averUtility = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for inst in simfog1.instances:
            for i in range(para.queueNum):
                simfog1_averDrop[t] += inst.Q[i].statAverDrop[t]
                simfog1_averBlock[t] += inst.Q[i].statAverBlocked[t]
                simfog1_totalDelay[t] += inst.Q[i].statTotalDelay[t]
                simfog1_totalThroughput[t] += inst.Q[i].statTotalThroughput[t]
    simfog1_averDropRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in simfog1_averDrop]
    simfog1_averBlockRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in simfog1_averBlock]
    simfog1_averDelay = [simfog1_totalDelay[t]/(1 if simfog1_totalThroughput[t]==0 else simfog1_totalThroughput[t]) for t in range(para.maxTime)]
    simfog1_averUtility = [(simfog1_totalThroughput[t]-2*simfog1_averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]
    # print(simfog1_averDropRate)
    # print(simfog1_averBlockRate)
    # print(simfog1_averDelay)
    # print(simfog1_averUtility)
    # related data for simcor
    simcor_averDrop = [0 for _ in range(para.maxTime)]
    simcor_averBlock = [0 for _ in range(para.maxTime)]
    simcor_totalDelay = [0 for _ in range(para.maxTime)]
    simcor_totalThroughput = [0 for _ in range(para.maxTime)]
    simcor_averUtility = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for i in range(para.queueNum):
            for j in range(para.queueNum):
                simcor_averDrop[t] += simcor.Q[i][j].statAverDrop[t]
                simcor_averBlock[t] += simcor.Q[i][j].statAverBlocked[t]
                simcor_totalDelay[t] += simcor.Q[i][j].statTotalDelay[t]
                simcor_totalThroughput[t] += simcor.Q[i][j].statTotalThroughput[t]
    simcor_averDropRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in simcor_averDrop]
    simcor_averBlockRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in simcor_averBlock]
    simcor_averDelay = [simcor_totalDelay[t]/(1 if simcor_totalThroughput[t]==0 else simcor_totalThroughput[t]) for t in range(para.maxTime)]
    simcor_averUtility = [(simcor_totalThroughput[t]-2*simcor_averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]
    # related data for simnop
    simnop_averDrop = [0 for _ in range(para.maxTime)]
    simnop_averBlock = [0 for _ in range(para.maxTime)]
    simnop_totalDelay = [0 for _ in range(para.maxTime)]
    simnop_totalThroughput = [0 for _ in range(para.maxTime)]
    simnop_averUtility = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for i in range(para.queueNum):
            simnop_averDrop[t] += simnop.Q[i].statAverDrop[t]
            simnop_averBlock[t] += simnop.Q[i].statAverBlocked[t]
            simnop_totalDelay[t] += simnop.Q[i].statTotalDelay[t]
            simnop_totalThroughput[t] += simnop.Q[i].statTotalThroughput[t]
    simnop_averDropRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in simnop_averDrop]
    simnop_averBlockRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in simnop_averBlock]
    simnop_averBlockRate[0] = 0
    simnop_averDelay = [simnop_totalDelay[t]/(1 if simnop_totalThroughput[t]==0 else simnop_totalThroughput[t]) for t in range(para.maxTime)]
    simnop_averUtility = [(simnop_totalThroughput[t]-2*simnop_averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]
    # related data for simopen
    simopen_averDrop = [0 for _ in range(para.maxTime)]
    simopen_averBlock = [0 for _ in range(para.maxTime)]
    simopen_totalDelay = [0 for _ in range(para.maxTime)]
    simopen_totalThroughput = [0 for _ in range(para.maxTime)]
    simopen_averUtility = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for i in range(para.queueNum):
            simopen_averDrop[t] += simopen.Q[i].statAverDrop[t]
            simopen_averBlock[t] += simopen.Q[i].statAverBlocked[t]
            simopen_totalDelay[t] += simopen.Q[i].statTotalDelay[t]
            simopen_totalThroughput[t] += simopen.Q[i].statTotalThroughput[t]
    simopen_averDropRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in simopen_averDrop]
    simopen_averBlockRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in simopen_averBlock]
    simopen_averDelay = [simopen_totalDelay[t]/(1 if simopen_totalThroughput[t]==0 else simopen_totalThroughput[t]) for t in range(para.maxTime)]
    simopen_averUtility = [(simopen_totalThroughput[t]-2*simopen_averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]
    # plot blockRate
    data = [simfog1_averBlockRate, simnop_averBlockRate, simcor_averBlockRate, simopen_averBlockRate]
    data_label = ['WoG', 'NoP', 'CoR', 'OPEN']
    xlabel = 'Time slot $t$'
    ylabel = 'Time-average block rate'
    savefig_name = 'aver_block_rate'
    mark_list = ['s', '^', 'o', 'x']
    lc_list = ['#EA4614', '#859900', '#268BD2', '#6C71C4']
    draw_y(data, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list)
    # plot satisfaction ratio
    data = [[1-i for i in simfog1_averDropRate], [1-i for i in simnop_averDropRate], [1-i for i in simcor_averDropRate], [1-i for i in simopen_averDropRate]]
    ylabel = 'Time-average satisfaction ratio'
    savefig_name = 'aver_satis_ratio'
    draw_y(data, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list)
    # plot aver utility
    data = [simfog1_averUtility, simnop_averUtility, simcor_averUtility, simopen_averUtility]
    ylabel = 'Time-average system utility'
    savefig_name = 'aver_utility'
    draw_y(data, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list)
    # plot aver delay
    data = [simfog1_averDelay, simnop_averDelay, simcor_averDelay, simopen_averDelay]
    ylabel = 'Time-average response time'
    savefig_name = 'aver_delay'
    draw_y(data, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list)



def draw_y(ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list = None):
    xdata = range(len(ydata[0]))
    draw(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list)

def draw(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list, sample_point = 300, mark_num = 10):
    assert len(xdata) == len(ydata[0])
    lines = len(ydata)
    if ls_list == None:
        ls_list = ['-' for _ in range(lines)]
    sample_interval = int(len(ydata[0])/sample_point)
    fig = plt.figure()
    for i in range(lines):
        mark = mark_list[i]
        lc = lc_list[i]
        ls = ls_list[i]
        plt.plot(xdata[::sample_interval], ydata[i][::sample_interval], marker = mark, markevery = int(sample_point/mark_num), markerfacecolor = 'none', markersize = 5, lw = 1, c = lc, ls = ls, label = data_label[i])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    ax = plt.gca()
    ax.tick_params(direction='in', top = True, right = True)
    plt.savefig('./pic/'+savefig_name+'_300', bbox_inches='tight', dpi = 300)
    plt.savefig('./pic/'+savefig_name+'_600', bbox_inches='tight', dpi = 600)
    plt.savefig('./pic/'+savefig_name+'.eps', bbox_inches='tight', format='eps', dpi = 900)
    save_data(ydata, './data/'+savefig_name)
    plt.show()
    plt.close()


def plotDiffV(para):
    # TODO: do not consider L^max here
    V_list = [2, 3, 5, 10, 15, 25, 40, 60]
    # V_list = [5, 10]
    aver_delay_list = [[] for _ in range(4)]
    aver_utility_list = [[] for _ in range(4)]
    aver_throughput_list = [[] for _ in range(4)]
    aver_backlog_list = [[] for _ in range(4)]
    totalTime = para.maxTime
    totalWorkload = sum(para.arriveRate)*para.taskInfo['totalCycle']
    for V in V_list:
        para.V = V
        simfog1 = SimFog1(copy.deepcopy(para))
        simfog1.start()
        simnop = SimNoP(copy.deepcopy(para))
        simnop.start()
        simopen = SimOPEN(copy.deepcopy(para))
        simopen.start()
        simcor = SimCoR(copy.deepcopy(para))
        simcor.start()
        # related data for simfog1
        totalDelay = 0
        totalThroughput = 0
        averDrop = 0
        averBacklog = 0
        for inst in simfog1.instances:
            for i in range(para.queueNum):
                averDrop += inst.Q[i].statAverDrop[-1]
                totalThroughput += inst.Q[i].statTotalThroughput[-1]
                totalDelay += inst.Q[i].statTotalDelay[-1]
                averBacklog += sum(inst.Q[i].statLength)/len(inst.Q[i].statLength)
        aver_delay_list[0].append(totalDelay/totalThroughput)
        aver_utility_list[0].append(totalThroughput/totalTime-2*averDrop)
        aver_throughput_list[0].append(totalThroughput/totalTime)
        aver_backlog_list[0].append(averBacklog/(para.queueNum))
        print(aver_delay_list[0])
        print(aver_utility_list[0])
        print(aver_throughput_list[0])
        print(aver_backlog_list[0])
        # related data for simcor
        totalDelay = 0
        totalThroughput = 0
        averDrop = 0
        averBacklog = 0
        for i in range(para.queueNum):
            for j in range(para.queueNum):
                averDrop += simcor.Q[i][j].statAverDrop[-1]
                totalThroughput += simcor.Q[i][j].statTotalThroughput[-1]
                totalDelay += simcor.Q[i][j].statTotalDelay[-1]
                averBacklog += sum(simcor.Q[i][j].statLength)/len(simcor.Q[i][j].statLength)
        aver_delay_list[2].append(totalDelay/totalThroughput)
        aver_utility_list[2].append(totalThroughput/totalTime-2*averDrop)
        aver_throughput_list[2].append(totalThroughput/totalTime)
        aver_backlog_list[2].append(averBacklog/(para.queueNum))
        # related data for simnop
        totalDelay = 0
        totalThroughput = 0
        averDrop = 0
        averBacklog = 0
        for i in range(para.queueNum):
            averDrop += simnop.Q[i].statAverDrop[-1]
            totalThroughput += simnop.Q[i].statTotalThroughput[-1]
            totalDelay += simnop.Q[i].statTotalDelay[-1]
            averBacklog += sum(simnop.Q[i].statLength)/len(simnop.Q[i].statLength)
        aver_delay_list[1].append(totalDelay/totalThroughput)
        aver_utility_list[1].append(totalThroughput/totalTime-2*averDrop)
        aver_throughput_list[1].append(totalThroughput/totalTime)
        aver_backlog_list[1].append(averBacklog/(para.queueNum))
        # related data for simopen
        totalDelay = 0
        totalThroughput = 0
        averDrop = 0
        averBacklog = 0
        for i in range(para.queueNum):
            averDrop += simopen.Q[i].statAverDrop[-1]
            totalThroughput += simopen.Q[i].statTotalThroughput[-1]
            totalDelay += simopen.Q[i].statTotalDelay[-1]
            averBacklog += sum(simopen.Q[i].statLength)/len(simopen.Q[i].statLength)
        aver_delay_list[3].append(totalDelay/totalThroughput)
        aver_utility_list[3].append(totalThroughput/totalTime-2*averDrop)
        aver_throughput_list[3].append(totalThroughput/totalTime)
        aver_backlog_list[3].append(averBacklog/(para.queueNum))
    # plot aver delay
    data_label = ['WoG', 'NoP', 'CoR', 'OPEN']
    xlabel = 'V'
    ylabel = 'Time-average response time'
    savefig_name = 'V_aver_delay'
    mark_list = ['s', '^', 'o', 'x']
    lc_list = ['#EA4614', '#859900', '#268BD2', '#6C71C4']
    draw(V_list, aver_delay_list, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, sample_point = len(V_list), mark_num = len(V_list))
    # plot aver utility
    ylabel = 'System utility'
    savefig_name = 'V_aver_utility'
    draw(V_list, aver_utility_list, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, sample_point = len(V_list), mark_num = len(V_list))
    # plot aver throughput
    ylabel = 'System throughput'
    savefig_name = 'V_aver_throughput'
    draw(V_list, aver_throughput_list, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, sample_point = len(V_list), mark_num = len(V_list))
    # plot aver backlog
    ylabel = 'Time-average backlog'
    savefig_name = 'V_aver_backlog'
    draw(V_list, aver_backlog_list, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, sample_point = len(V_list), mark_num = len(V_list))


def plotBurstyNew(para):
    para.bursty = 0
    simfog1_nonbursty = SimFog1(copy.deepcopy(para))
    simfog1_nonbursty.start()
    simopen_nonbursty = SimOPEN(copy.deepcopy(para))
    simopen_nonbursty.start()
    simcor_nonbursty = SimCoR(copy.deepcopy(para))
    simcor_nonbursty.start()
    # related data for non-bursty case
    simfog1_nonbursty_averDrop = [0 for _ in range(para.maxTime)]
    simfog1_nonbursty_totalDelay = [0 for _ in range(para.maxTime)]
    simfog1_nonbursty_totalThroughput = [0 for _ in range(para.maxTime)]
    simfog1_nonbursty_averBlock = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for inst in simfog1_nonbursty.instances:
            for i in range(para.queueNum):
                simfog1_nonbursty_averDrop[t] += inst.Q[i].statAverDrop[t]
                simfog1_nonbursty_totalDelay[t] += inst.Q[i].statTotalDelay[t]
                simfog1_nonbursty_totalThroughput[t] += inst.Q[i].statTotalThroughput[t]
                simfog1_nonbursty_averBlock[t] += inst.Q[i].statAverBlocked[t]
    simfog1_nonbursty_averDelay = [simfog1_nonbursty_totalDelay[t]/(1 if simfog1_nonbursty_totalThroughput[t]==0 else simfog1_nonbursty_totalThroughput[t]) for t in range(para.maxTime)]
    simfog1_nonbursty_averUtility = [(simfog1_nonbursty_totalThroughput[t]-2*simfog1_nonbursty_averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]
    simfog1_nonbursty_averDropRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in simfog1_nonbursty_averDrop]
    simfog1_nonbursty_averBlockRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in simfog1_nonbursty_averBlock]


    simopen_nonbursty_averDrop = [0 for _ in range(para.maxTime)]
    simopen_nonbursty_totalDelay = [0 for _ in range(para.maxTime)]
    simopen_nonbursty_totalThroughput = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for i in range(para.queueNum):
            simopen_nonbursty_averDrop[t] += simopen_nonbursty.Q[i].statAverDrop[t]
            simopen_nonbursty_totalDelay[t] += simopen_nonbursty.Q[i].statTotalDelay[t]
            simopen_nonbursty_totalThroughput[t] += simopen_nonbursty.Q[i].statTotalThroughput[t]
    simopen_nonbursty_averDelay = [simopen_nonbursty_totalDelay[t]/(1 if simopen_nonbursty_totalThroughput[t]==0 else simopen_nonbursty_totalThroughput[t]) for t in range(para.maxTime)]
    simopen_nonbursty_averUtility = [(simopen_nonbursty_totalThroughput[t]-2*simopen_nonbursty_averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]


    simcor_nonbursty_averDrop = [0 for _ in range(para.maxTime)]
    simcor_nonbursty_totalDelay = [0 for _ in range(para.maxTime)]
    simcor_nonbursty_totalThroughput = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for i in range(para.queueNum):
            for j in range(para.queueNum):
                simcor_nonbursty_averDrop[t] += simcor_nonbursty.Q[i][j].statAverDrop[t]
                simcor_nonbursty_totalDelay[t] += simcor_nonbursty.Q[i][j].statTotalDelay[t]
                simcor_nonbursty_totalThroughput[t] += simcor_nonbursty.Q[i][j].statTotalThroughput[t]
    simcor_nonbursty_averDelay = [simcor_nonbursty_totalDelay[t]/(1 if simcor_nonbursty_totalThroughput[t]==0 else simcor_nonbursty_totalThroughput[t]) for t in range(para.maxTime)]
    simcor_nonbursty_averUtility = [(simcor_nonbursty_totalThroughput[t]-2*simcor_nonbursty_averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]

    # bursty case
    para.bursty = 1
    simfog1_bursty = SimFog1(copy.deepcopy(para))
    simfog1_bursty.start()
    simopen_bursty = SimOPEN(copy.deepcopy(para))
    simopen_bursty.start()
    simcor_bursty = SimCoR(copy.deepcopy(para))
    simcor_bursty.start()
    # related data for non-bursty case
    simfog1_bursty_averDrop = [0 for _ in range(para.maxTime)]
    simfog1_bursty_totalDelay = [0 for _ in range(para.maxTime)]
    simfog1_bursty_totalThroughput = [0 for _ in range(para.maxTime)]
    simfog1_bursty_averBlock = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for inst in simfog1_bursty.instances:
            for i in range(para.queueNum):
                simfog1_bursty_averDrop[t] += inst.Q[i].statAverDrop[t]
                simfog1_bursty_totalDelay[t] += inst.Q[i].statTotalDelay[t]
                simfog1_bursty_totalThroughput[t] += inst.Q[i].statTotalThroughput[t]
                simfog1_bursty_averBlock[t] += inst.Q[i].statAverBlocked[t]
    simfog1_bursty_averDelay = [simfog1_bursty_totalDelay[t]/(1 if simfog1_bursty_totalThroughput[t]==0 else simfog1_bursty_totalThroughput[t]) for t in range(para.maxTime)]
    simfog1_bursty_averUtility = [(simfog1_bursty_totalThroughput[t]-2*simfog1_bursty_averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]
    simfog1_bursty_averDropRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in simfog1_bursty_averDrop]
    simfog1_bursty_averBlockRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in simfog1_bursty_averBlock]

    simopen_bursty_averDrop = [0 for _ in range(para.maxTime)]
    simopen_bursty_totalDelay = [0 for _ in range(para.maxTime)]
    simopen_bursty_totalThroughput = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for i in range(para.queueNum):
            simopen_bursty_averDrop[t] += simopen_bursty.Q[i].statAverDrop[t]
            simopen_bursty_totalDelay[t] += simopen_bursty.Q[i].statTotalDelay[t]
            simopen_bursty_totalThroughput[t] += simopen_bursty.Q[i].statTotalThroughput[t]
    simopen_bursty_averDelay = [simopen_bursty_totalDelay[t]/(1 if simopen_bursty_totalThroughput[t]==0 else simopen_bursty_totalThroughput[t]) for t in range(para.maxTime)]
    simopen_bursty_averUtility = [(simopen_bursty_totalThroughput[t]-2*simopen_bursty_averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]

    simcor_bursty_averDrop = [0 for _ in range(para.maxTime)]
    simcor_bursty_totalDelay = [0 for _ in range(para.maxTime)]
    simcor_bursty_totalThroughput = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for i in range(para.queueNum):
            for j in range(para.queueNum):
                simcor_bursty_averDrop[t] += simcor_bursty.Q[i][j].statAverDrop[t]
                simcor_bursty_totalDelay[t] += simcor_bursty.Q[i][j].statTotalDelay[t]
                simcor_bursty_totalThroughput[t] += simcor_bursty.Q[i][j].statTotalThroughput[t]
    simcor_bursty_averDelay = [simcor_bursty_totalDelay[t]/(1 if simcor_bursty_totalThroughput[t]==0 else simcor_bursty_totalThroughput[t]) for t in range(para.maxTime)]
    simcor_bursty_averUtility = [(simcor_bursty_totalThroughput[t]-2*simcor_bursty_averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]

    # plot
    data = [simfog1_nonbursty_averDelay, simfog1_bursty_averDelay, simopen_nonbursty_averDelay, simopen_bursty_averDelay, simcor_nonbursty_averDelay, simcor_bursty_averDelay]
    data_label = ['WoG(Poisson)', 'WoG(Bursty)', 'OPEN(Poisson)', 'OPEN(Bursty)', 'CoR(Poisson)', 'CoR(Bursty)']
    xlabel = 'Time slot $t$'
    ylabel = 'Time-average response time'
    savefig_name = 'bursty_delay'
    mark_list = ['o', 'o', '^', '^', 'x', 'x']
    # mark_list = ["" for _ in range(6)]
    lc_list = ['#EA4614', '#EA4614', '#6C71C4', '#6C71C4', '#859900', '#859900']
    ls_list = ['-', '--', '-', '--', '-', '--']
    draw_y(data, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list)
    data = [simfog1_nonbursty_averUtility, simfog1_bursty_averUtility, simopen_nonbursty_averUtility, simopen_bursty_averUtility, simcor_nonbursty_averUtility, simcor_bursty_averUtility]
    xlabel = 'Time slot $t$'
    ylabel = 'Time-average system utility'
    savefig_name = 'bursty_utility'
    draw_y(data, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list)
    print(simfog1_nonbursty_averBlockRate[-1])
    print(simfog1_bursty_averBlockRate[-1])
    print(simfog1_nonbursty_averDropRate[-1])
    print(simfog1_bursty_averDropRate[-1])


def plotBursty(para):
    para.bursty = 0
    simfog1_nonbursty = SimFog1(copy.deepcopy(para))
    simfog1_nonbursty.start()
    # related data for non-bursty case
    nonbursty_averDrop = [0 for _ in range(para.maxTime)]
    nonbursty_totalDelay = [0 for _ in range(para.maxTime)]
    nonbursty_totalThroughput = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for inst in simfog1_nonbursty.instances:
            for i in range(para.queueNum):
                nonbursty_averDrop[t] += inst.Q[i].statAverDrop[t]
                nonbursty_totalDelay[t] += inst.Q[i].statTotalDelay[t]
                nonbursty_totalThroughput[t] += inst.Q[i].statTotalThroughput[t]
    nonbursty_averDelay = [nonbursty_totalDelay[t]/(1 if nonbursty_totalThroughput[t]==0 else nonbursty_totalThroughput[t]) for t in range(para.maxTime)]
    nonbursty_averUtility = [(nonbursty_totalThroughput[t]-2*nonbursty_averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]
    # bursty case
    para.bursty = 1
    simfog1_bursty = SimFog1(copy.deepcopy(para))
    simfog1_bursty.start()
    # related data for non-bursty case
    bursty_averDrop = [0 for _ in range(para.maxTime)]
    bursty_totalDelay = [0 for _ in range(para.maxTime)]
    bursty_totalThroughput = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for inst in simfog1_bursty.instances:
            for i in range(para.queueNum):
                bursty_averDrop[t] += inst.Q[i].statAverDrop[t]
                bursty_totalDelay[t] += inst.Q[i].statTotalDelay[t]
                bursty_totalThroughput[t] += inst.Q[i].statTotalThroughput[t]
    bursty_averDelay = [bursty_totalDelay[t]/(1 if bursty_totalThroughput[t]==0 else bursty_totalThroughput[t]) for t in range(para.maxTime)]
    bursty_averUtility = [(bursty_totalThroughput[t]-2*bursty_averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]
    # plot
    xdata = range(para.maxTime)
    ydata = [[nonbursty_averUtility, bursty_averUtility], [nonbursty_averDelay, bursty_averDelay]]
    data_label = [['Utility(Poisson)', 'Utility(Bursty)'], ['Latency(Poisson)', 'Latency(Bursty)']]
    xlabel = 'Time slot $t$'
    ylabel = ['Time-average system utility', 'Time-average response time']
    savefig_name = 'bursty'
    mark_list = [['o', 'x'], ['o', 'x']]
    lc_list = [['#EA4614', '#EA4614'], ['#6C71C4', '#6C71C4']]
    ls_list = [['-', '--'], ['-', '--']]
    draw_twinx(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list)

def draw_twinx(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list, sample_point = 100, mark_num = 10):
    assert len(ydata) == 2 # ydata[0] is the data of lines belong to the first ax
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    axs = [ax1, ax2]
    sample_interval = int(len(xdata)/sample_point)
    lns = []
    ax1.set_xlabel(xlabel)
    ax1.tick_params(direction = 'in', top = True)
    # plot lines of ax1
    for i in range(len(ydata)):
        for j in range(len(ydata[i])):
            mark = mark_list[i][j]
            lc = lc_list[i][j]
            ls = ls_list[i][j]
            l = axs[i].plot(xdata[::sample_interval], ydata[i][j][::sample_interval], marker = mark, markevery = int(sample_point/mark_num), markerfacecolor = 'none', markersize = 5, lw = 1, c = lc, ls = ls, label = data_label[i][j])
            lns.append(l)
        axs[i].set_ylabel(ylabel[i])
    temp_lns = lns[0]
    for i in range(len(lns)-1):
        temp_lns += lns[i+1]
    labs = [l.get_label() for l in (temp_lns)]
    ax1.legend(temp_lns, labs, loc='right')
    plt.grid(True)
    plt.savefig('./pic/'+savefig_name+'_300', bbox_inches='tight', dpi = 300)
    plt.savefig('./pic/'+savefig_name+'_600', bbox_inches='tight', dpi = 600)
    plt.savefig('./pic/'+savefig_name+'.eps', bbox_inches='tight', format='eps', dpi = 900)
    save_data(ydata, './data/'+savefig_name)
    plt.show()
    plt.close()

def save_data(data, file_name):
    with open(file_name, 'wb') as fwrite:
        pickle.dump(data, fwrite)

# plotRunTime(para_fog1)
# plotDiffV(para_fog1)
plotBurstyNew(para_fog1)
