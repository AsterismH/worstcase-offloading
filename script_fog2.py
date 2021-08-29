from SimFog2 import SimFog2
from SimCoR import SimCoR
from SimNoP import SimNoP
from SimOPEN import SimOPEN

from Parameter import para_fog1
from Parameter import para_test
from auxiliary import addtodict2

import copy
import matplotlib.pyplot as plt
import pickle
import random

def plotRunTime(para):
    data_fog2 = run(SimFog2, para)
    data_nop = run(SimNoP, para)
    data_cor = run(SimCoR, para)
    data_open = run(SimOPEN, para)
    # plot
    # block rate
    data = [data_fog2['block_rate'], data_nop['block_rate'], data_cor['block_rate'], data_open['block_rate']]
    data_label = ['ULG', 'NoP', 'CoR', 'OPEN']
    xlabel = 'Time slot $t$'
    ylabel = 'Time-average block rate'
    savefig_name = 'aver_block_rate'
    mark_list = ['s', '^', 'o', 'x']
    lc_list = ['#396AB1', '#DA7C30', '#CC2529', '#535154']
    draw_y(data, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list)
    # plot satisfaction ratio
    data = [data_fog2['satis_ratio'], data_nop['satis_ratio'], data_cor['satis_ratio'], data_open['satis_ratio']]
    ylabel = 'Time-average satisfaction ratio'
    savefig_name = 'aver_satis_ratio'
    draw_y(data, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list)
    # plot aver utility
    data = [data_fog2['utility'], data_nop['utility'], data_cor['utility'], data_open['utility']]
    ylabel = 'Time-average system utility'
    savefig_name = 'aver_utility'
    draw_y(data, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list)
    # plot aver delay
    data = [data_fog2['delay'], data_nop['delay'], data_cor['delay'], data_open['delay']]
    ylabel = 'Time-average latency (ms)'
    savefig_name = 'aver_delay'
    draw_y(data, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list)

def tableDiffLoad(para):
    # coefs = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
    # worst_delay = {'wog':[], 'nop':[], 'cor':[], 'open':[]}
    # alg_list = ['wog', 'nop', 'cor', 'open']
    # sim_list = {'wog':SimFog2, 'nop':SimNoP, 'cor':SimCoR, 'open':SimOPEN}
    # for multi_coef in coefs:
        # new_para = copy.deepcopy(para)
        # new_para.arriveRate = [multi_coef*v for v in para.arriveRate]
        # for alg in alg_list:
            # data = run(sim_list[alg], new_para)
            # worst_delay[alg].append(data['worst_delay'][-1])
    # print(worst_delay)
    # block rate
    savefig_name = 'load_aver_block'
    data_file = open('./fog2_data_backup/'+savefig_name, 'rb')
    data = pickle.load(data_file)
    print(data)
    # satis ratio
    savefig_name = 'load_aver_satis_ratio'
    data_file = open('./fog2_data_backup/'+savefig_name, 'rb')
    data = pickle.load(data_file)
    print(data)

def scale(para):
    #queueNum_list = [50, 100, 150, 200, 250, 300]
    queueNum_list = [50]
    data_scale = {'utility':[], 'delay':[], 'block_rate':[], 'satis_ratio':[]}
    for queueNum in queueNum_list:
        new_para = copy.deepcopy(para)
        new_para.queueNum = queueNum
        delta = [[0 for _ in range(queueNum)] for _ in range(queueNum)]
        for i in range(queueNum):
            for j in range(i+1, queueNum):
                val = random.randrange(3,6)
                delta[i][j] = val
                delta[j][i] = val
        new_para.delta = delta
        print(delta)
        new_para.arriveRate = [random.randrange(1,8)*0.25 for _ in range(queueNum)]
        new_para.E_aver = [new_para.energyPerMCycle*5+new_para.energyStatic for _ in range(queueNum)]
        new_para.B_max = [20 for _ in range(queueNum)]
        new_para.gfunc = []
        new_para.gfunc_deriv = []
        new_para.efunc = []
        new_para.efunc_deriv = []
        for i in range(queueNum):
            new_para.gfunc.append(lambda x: x)
            new_para.gfunc_deriv.append(lambda x: 1)
            new_para.efunc.append(lambda x: para_fog1.energyStatic + para_fog1.energyPerMCycle*x)
            new_para.efunc_deriv.append(lambda x: para_fog1.energyPerMCycle)
        data = run(SimFog2, new_para)
        data_scale['utility'].append(data['utility'][-1])
        data_scale['delay'].append(data['delay'][-1])
        data_scale['block_rate'].append(data['block_rate'][-1])
        data_scale['satis_ratio'].append(data['satis_ratio'][-1])
    print(data_scale['delay'])
    """
    data_label = [['Utility'], ['Latency']]
    ylabel = ['Time-average system utility', 'Time-average latency (ms)']
    xlabel = 'Number of BSs'
    xdata = queueNum_list
    ydata1 = data_scale['utility']
    ydata2 = data_scale['delay']
    mark_list = [['o'], ['x']]
    ls_list = [['-'], ['-']]
    lc_list = [['#396AB1'], ['#DA7C30']]
    savefig_name = 'scale'
    draw_twinx(xdata, [[ydata1], [ydata2]], data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list, sample_point = len(xdata), mark_num = len(xdata))
    """

def plotScale():
    savefig_name = 'scale'
    data_file = open('./fog2_data/'+savefig_name, 'rb')
    data_scale = pickle.load(data_file)
    print(data_scale)
    data_scale = [[[248.17629999999994, 530.2736000000001, 734.0061, 1010.2188000000003, 1231.2182000000003, 1503.7816999999993]], [[5.472665198087006, 5.489438471008171, 5.261455729046395, 5.778879090351518, 5.291007881462439, 5.588321363400022]]]
    data_file = open('./fog2_data/'+savefig_name, 'wb')
    pickle.dump(data_scale, data_file)
    data_label = [['Utility'], ['Latency']]
    ylabel = ['Time-average system utility', 'Time-average latency (ms)']
    xlabel = 'Number of BSs'
    queueNum_list = [50, 100, 150, 200, 250, 300]
    xdata = queueNum_list
    ydata1 = data_scale[0][0]
    ydata2 = data_scale[1][0]
    mark_list = [['o'], ['x']]
    ls_list = [['-'], ['-']]
    lc_list = [['#396AB1'], ['#CC2529']]
    draw_twinx_(xdata, [[ydata1], [ydata2]], data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list, sample_point = len(xdata), mark_num = len(xdata))

def nop(para): 
    # we have revised SimNoP, so we need to update the data associated with NoP
    # run-time
    data_nop = run(SimNoP, para)
    savefig_name_list = ['aver_block_rate', 'aver_satis_ratio', 'aver_utility', 'aver_delay']
    property_name_list = ['block_rate', 'satis_ratio', 'utility', 'delay']
    for i in range(4):
        savefig_name = savefig_name_list[i]
        property_name = property_name_list[i]
        data_file = open('./fog2_data_backup/'+savefig_name, 'rb')
        data = pickle.load(data_file)
        data[1] = data_nop[property_name]
        data_file = open('./fog2_data_backup/'+savefig_name, 'wb')
        pickle.dump(data, data_file)
    # different load
    # coefs = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
    # worst_delay = []
    # aver_delay = []
    # utility = []
    # satis_ratio = []
    # block_rate = []
    # for multi_coef in coefs:
        # new_para = copy.deepcopy(para)
        # new_para.arriveRate = [multi_coef*v for v in para.arriveRate]
        # # new_para.maxTime = 5000
        # data = run(SimNoP, new_para)
        # utility.append(data['utility'][-1])
        # aver_delay.append(data['delay'][-1])
        # worst_delay.append(data['worst_delay'][-1])
        # block_rate.append(data['block_rate'][-1])
        # satis_ratio.append(data['satis_ratio'][-1])
    # savefig_name_list = ['load_aver_delay', 'load_aver_utility', 'load_aver_block', 'load_aver_satis_ratio']
    # print(worst_delay)
    # print(aver_delay)
    # for i in range(4):
        # savefig_name = savefig_name_list[i]
        # data_file = open('./fog2_data_backup/'+savefig_name, 'rb')
        # data = pickle.load(data_file)
        # if i == 0:
            # data[1] = aver_delay
        # elif i == 1:
            # data[1] = utility
        # elif i == 2:
            # data[1] = block_rate
        # elif i == 3:
            # data[1] = satis_ratio
        # data_file = open('./fog2_data_backup/'+savefig_name, 'wb')
        # pickle.dump(data, data_file)
    # different V, light load
    # nopDiffV(para, 'light_')
    # para.arriveRate = [1.5*v for v in para.arriveRate]
    # nopDiffV(para, 'heavy_')

def nopDiffV(para, prefix = ''):
    V_list = [10, 30, 50, 70, 90, 110]
    savefig_name_list = ['V_aver_delay', 'V_aver_utility', 'V_aver_block_rate', 'V_aver_satis_ratio']
    property_list = ['delay', 'utility', 'block_rate', 'satis_ratio']
    data_nop = {'utility':[], 'delay':[], 'block_rate':[], 'satis_ratio':[]}
    for V in V_list:
        new_para = copy.deepcopy(para)
        new_para.V = V
        data = run(SimNoP, new_para)
        for property_name in property_list:
            data_nop[property_name].append(data[property_name][-1])
    for i in range(4):
        savefig_name = prefix + savefig_name_list[i]
        property_name = property_list[i]
        data_file = open('./fog2_data_backup/'+savefig_name, 'rb')
        data = pickle.load(data_file)
        data[1] = data_nop[property_name]
        data_file = open('./fog2_data_backup/'+savefig_name, 'wb')
        pickle.dump(data, data_file)

def plotDiffLoad(para):
    # utility and delay under different load (10%, 20%, 30%, 40% 50%)
    coefs = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
    utility = {'wog':[], 'nop':[], 'cor':[], 'open':[]}
    delay = {'wog':[], 'nop':[], 'cor':[], 'open':[]}
    block_rate = {'wog':[], 'nop':[], 'cor':[], 'open':[]}
    satis_ratio = {'wog':[], 'nop':[], 'cor':[], 'open':[]}
    alg_list = ['wog', 'nop', 'cor', 'open']
    sim_list = {'wog':SimFog2, 'nop':SimNoP, 'cor':SimCoR, 'open':SimOPEN}
    for multi_coef in coefs:
        new_para = copy.deepcopy(para)
        new_para.arriveRate = [multi_coef*v for v in para.arriveRate]
        for alg in alg_list:
            data = run(sim_list[alg], new_para)
            utility[alg].append(data['utility'][-1])
            delay[alg].append(data['delay'][-1])
            block_rate[alg].append(data['block_rate'][-1])
            satis_ratio[alg].append(data['satis_ratio'][-1])
    # plot
    # delay
    xdata = [(v-1.0)*100 for v in coefs]
    ydata = [delay['wog'], delay['nop'], delay['cor'], delay['open']]
    data_label = ['ULG', 'NoP', 'CoR', 'OPEN']
    xlabel = 'Increase of arrival rate ($\%$)'
    ylabel = 'Time-average latency (ms)'
    savefig_name = 'load_aver_delay'
    mark_list = ['s', '^', 'o', 'x']
    lc_list = ['#396AB1', '#DA7C30', '#CC2529', '#535154']
    draw(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, sample_point = len(xdata), mark_num = len(xdata))
    # utility
    ydata = [utility['wog'], utility['nop'], utility['cor'], utility['open']]
    ylabel = 'Time-average system utility'
    savefig_name = 'load_aver_utility'
    draw(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, sample_point = len(xdata), mark_num = len(xdata))
    # block rate
    ydata = [block_rate['wog'], block_rate['nop'], block_rate['cor'], block_rate['open']]
    ylabel = 'Time-average block rate'
    savefig_name = 'load_aver_block'
    draw(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, sample_point = len(xdata), mark_num = len(xdata))
    # satis ratio
    ydata = [satis_ratio['wog'], satis_ratio['nop'], satis_ratio['cor'], satis_ratio['open']]
    ylabel = 'Time-average satisfaction ratio'
    savefig_name = 'load_aver_satis_ratio'
    draw(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, sample_point = len(xdata), mark_num = len(xdata))

def plotDiffV(para):
    # light loaded
    _plotDiffV(para, 'light_')
    # heavy loaded
    para.arriveRate = [1.5*v for v in para.arriveRate]
    _plotDiffV(para, 'heavy_')

def _plotDiffV(para, prefix = ''):
    # utility and delay under different V
    V_list = [10, 30, 50, 70, 90, 110]
    alg_list = ['wog', 'nop', 'cor', 'open']
    sim_list = {'wog':SimFog2, 'nop':SimNoP, 'cor':SimCoR, 'open':SimOPEN}
    metric_list = ['delay', 'utility', 'block_rate', 'satis_ratio']
    data_dict = dict()
    for alg in alg_list:
        for metric in metric_list:
            addtodict2(data_dict, alg, metric, [])
    for V in V_list:
        new_para = copy.deepcopy(para)
        new_para.V = V
        for alg in alg_list:
            data = run(sim_list[alg], new_para)
            for metric in metric_list:
                data_dict[alg][metric].append(data[metric][-1])
    # plot
    # delay
    xdata = V_list
    ydata = [data_dict[alg]['delay'] for alg in alg_list]
    data_label = ['ULG', 'NoP', 'CoR', 'OPEN']
    xlabel = 'V'
    ylabel = 'Time-average latency (ms)'
    savefig_name = prefix + 'V_aver_delay'
    mark_list = ['s', '^', 'o', 'x']
    lc_list = ['#396AB1', '#DA7C30', '#CC2529', '#535154']
    draw(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, sample_point = len(xdata), mark_num = len(xdata))
    # utility
    ydata = [data_dict[alg]['utility'] for alg in alg_list]
    ylabel = 'Time-average system utility'
    savefig_name = prefix + 'V_aver_utility'
    draw(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, sample_point = len(xdata), mark_num = len(xdata))
    # block rate
    ydata = [data_dict[alg]['block_rate'] for alg in alg_list]
    ylabel = 'Time-average block rate'
    savefig_name = prefix + 'V_aver_block_rate'
    draw(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, sample_point = len(xdata), mark_num = len(xdata))
    # satis ratio
    ydata = [data_dict[alg]['satis_ratio'] for alg in alg_list]
    ylabel = 'Time-average satisfaction ratio'
    savefig_name = prefix + 'V_aver_satis_ratio'
    draw(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, sample_point = len(xdata), mark_num = len(xdata))

def plotBusrty(para):
    para.bursty = 0
    data_nonbursty = _runAllAlg(para)
    para.bursty = 1
    data_bursty = _runAllAlg(para)
    # plot
    # delay
    data = [data_nonbursty['wog']['delay'], data_bursty['wog']['delay'], data_nonbursty['cor']['delay'], data_bursty['cor']['delay'], data_nonbursty['open']['delay'], data_bursty['open']['delay']]
    data_label = ['ULG(Poisson)', 'ULG(Bursty)', 'CoR(Poisson)', 'CoR(Bursty)', 'OPEN(Poisson)', 'OPEN(Bursty)']
    xlabel = 'Time slot $t$'
    ylabel = 'Time-average latency (ms)'
    savefig_name = 'bursty_delay'
    mark_list = ['o', 'o', '^', '^', 'x', 'x']
    lc_list = ['#396AB1', '#396AB1', '#CC2529', '#CC2529', '#535154', '#535154']
    ls_list = ['-', '--', '-', '--', '-', '--']
    draw_y(data, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list)
    # utility
    data = [data_nonbursty['wog']['utility'], data_bursty['wog']['utility'], data_nonbursty['cor']['utility'], data_bursty['cor']['utility'], data_nonbursty['open']['utility'], data_bursty['open']['utility']]
    ylabel = 'Time-average system utility'
    savefig_name = 'bursty_utility'
    draw_y(data, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list)

def plotOtherPara(para):
    # under heavy loaded case
    para.arriveRate = [1.5*v for v in para.arriveRate]
    # the impact of beta, epsilon, p, and A_max
    attr_list = ['beta', 'epsilon', 'p', 'A_max']
    # attr_list = ['p', 'epsilon']
    value_list = {}
    value_list['beta'] = [1, 2, 3, 4, 5, 6]
    value_list['epsilon'] = [6, 7, 8, 9, 10, 11]
    value_list['p'] = [10, 20, 30, 40, 50, 60]
    value_list['A_max'] = [15, 20, 25, 30, 35, 40]
    data = {}
    for attr in attr_list:
        data[attr] = _impactOfPara(copy.deepcopy(para), attr, value_list[attr])
    # plot
    attr_symbol = {
        'beta': r'$\beta$',
        'epsilon': r'$\epsilon$',
        'p': r'$p$',
        'A_max': r'$A^{max}$'
    }
    data_label = [['Utility'], ['Latency']]
    ylabel = ['Time-average system utility', 'Time-average latency (ms)']
    mark_list = [['o'], ['x']]
    ls_list = [['-'], ['-']]
    lc_list = [['#396AB1'], ['#DA7C30']]
    # lc_list = ['', '', '#CC2529', '#535154']
    for attr in attr_list:
        xdata = value_list[attr]
        ydata1 = data[attr]['utility']
        ydata2 = data[attr]['delay']
        xlabel = attr_symbol[attr]
        savefig_name = 'impact_of_' + attr
        draw_twinx(xdata, [[ydata1], [ydata2]], data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list, sample_point = len(xdata), mark_num = len(xdata))

def _impactOfPara(para, attr_name, value_list):
    utility = []
    delay = []
    for value in value_list:
        exec('para.'+attr_name+'=%s' % str(value))
        data = run(SimFog2, para)
        utility.append(data['utility'][-1])
        delay.append(data['delay'][-1])
    return {
        'utility': utility,
        'delay': delay
    }

def _runAllAlg(para):
    # run all algorithms and return their related data
    alg_list = ['wog', 'nop', 'cor', 'open']
    sim_list = {'wog':SimFog2, 'nop':SimNoP, 'cor':SimCoR, 'open':SimOPEN}
    metric_list = ['delay', 'utility', 'block_rate', 'satis_ratio']
    data_dict = dict()
    for alg in alg_list:
        data = run(sim_list[alg], para)
        for metric in metric_list:
            addtodict2(data_dict, alg, metric, data[metric])
    return data_dict

def run(sim_cls, para):
    sim = sim_cls(para)
    sim.start()
    averDrop = [0 for _ in range(para.maxTime)]
    averBlock = [0 for _ in range(para.maxTime)]
    totalDelay = [0 for _ in range(para.maxTime)]
    totalThroughput = [0 for _ in range(para.maxTime)]
    worstDelay = [0 for _ in range(para.maxTime)]
    for t in range(para.maxTime):
        for i in range(para.queueNum):
            if sim_cls == SimCoR:
                for j in range(para.queueNum):
                    averDrop[t] += sim.Q[i][j].statAverDrop[t]
                    averBlock[t] += sim.Q[i][j].statAverBlocked[t]
                    totalDelay[t] += sim.Q[i][j].statTotalDelay[t]
                    totalThroughput[t] += sim.Q[i][j].statTotalThroughput[t]
                    if sim.Q[i][j].statWorstDelay[t] > worstDelay[t]:
                        worstDelay[t] = sim.Q[i][j].statWorstDelay[t]
            else:
                averDrop[t] += sim.Q[i].statAverDrop[t]
                averBlock[t] += sim.Q[i].statAverBlocked[t]
                totalDelay[t] += sim.Q[i].statTotalDelay[t]
                totalThroughput[t] += sim.Q[i].statTotalThroughput[t]
                if sim.Q[i].statWorstDelay[t] > worstDelay[t]:
                    worstDelay[t] = sim.Q[i].statWorstDelay[t]
    averDropRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in averDrop]
    averSatisRatio = [1-v for v in averDropRate]
    averBlockRate = [v/(sum(para.arriveRate)*para.taskInfo['totalCycle']) for v in averBlock]
    averBlockRate[0] = 0
    averDelay = [totalDelay[t]/(1 if totalThroughput[t]==0 else totalThroughput[t]) for t in range(para.maxTime)]
    averUtility = [(totalThroughput[t]-para.beta*averDrop[t]*(t+1))/(t+1) for t in range(para.maxTime)]
    # save_data(worstDelay, './fog2_data/table_worst_delay')
    return {
        'satis_ratio': averSatisRatio,
        'block_rate': averBlockRate,
        'delay': averDelay,
        'utility': averUtility,
        'worst_delay': worstDelay
    }

def draw_y(ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list = None):
    xdata = range(len(ydata[0]))
    draw(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list)

def draw(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list = None, sample_point = 300, mark_num = 10):
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
        plt.plot(xdata[::sample_interval], ydata[i][::sample_interval], marker = mark, markevery = int(sample_point/mark_num), markerfacecolor = 'none', c = lc, ls = ls, label = data_label[i])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    ax = plt.gca()
    ax.tick_params(direction='in', top = True, right = True)
    plt.savefig('./fog2_pic/'+savefig_name+'_300', bbox_inches='tight', dpi = 300)
    plt.savefig('./fog2_pic/'+savefig_name+'_600', bbox_inches='tight', dpi = 600)
    plt.savefig('./fog2_pic/'+savefig_name+'.eps', bbox_inches='tight', format='eps', dpi = 900)
    save_data(ydata, './fog2_data/'+savefig_name)
    plt.show()
    plt.close()

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
            l = axs[i].plot(xdata[::sample_interval], ydata[i][j][::sample_interval], marker = mark, markevery = int(sample_point/mark_num), markerfacecolor = 'none', c = lc, ls = ls, label = data_label[i][j])
            lns.append(l)
        axs[i].set_ylabel(ylabel[i])
    temp_lns = lns[0]
    for i in range(len(lns)-1):
        temp_lns += lns[i+1]
    labs = [l.get_label() for l in (temp_lns)]
    ax1.legend(temp_lns, labs)
    plt.grid(True)
    plt.savefig('./fog2_pic/'+savefig_name+'_300', bbox_inches='tight', dpi = 300)
    plt.savefig('./fog2_pic/'+savefig_name+'_600', bbox_inches='tight', dpi = 600)
    plt.savefig('./fog2_pic/'+savefig_name+'.eps', bbox_inches='tight', format='eps', dpi = 900)
    save_data(ydata, './fog2_data/'+savefig_name)
    plt.show()
    plt.close()

def draw_twinx_(xdata, ydata, data_label, xlabel, ylabel, savefig_name, mark_list, lc_list, ls_list, sample_point = 100, mark_num = 10):
    assert len(ydata) == 2 # ydata[0] is the data of lines belong to the first ax
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax2.set_ylim(0, 10)
    axs = [ax1, ax2]
    sample_interval = int(len(xdata)/sample_point)
    lns = []
    ax1.set_xlabel(xlabel, fontsize="x-large")
    ax1.tick_params(direction = 'in', top = True)
    # plot lines of ax1
    for i in range(len(ydata)):
        for j in range(len(ydata[i])):
            mark = mark_list[i][j]
            lc = lc_list[i][j]
            ls = ls_list[i][j]
            l = axs[i].plot(xdata[::sample_interval], ydata[i][j][::sample_interval], marker = mark, markevery = int(sample_point/mark_num), markerfacecolor = 'none', c = lc, ls = ls, label = data_label[i][j])
            lns.append(l)
        axs[i].set_ylabel(ylabel[i], fontsize="x-large")
    temp_lns = lns[0]
    for i in range(len(lns)-1):
        temp_lns += lns[i+1]
    labs = [l.get_label() for l in (temp_lns)]
    ax1.legend(temp_lns, labs, fontsize="large")
    plt.grid(True, color='gainsboro', linewidth=0.5)
    plt.savefig('./fog2_pic/'+savefig_name+'_300', bbox_inches='tight', dpi = 300)
    plt.savefig('./fog2_pic/'+savefig_name+'_600', bbox_inches='tight', dpi = 600)
    plt.savefig('./fog2_pic/'+savefig_name+'.eps', bbox_inches='tight', format='eps', dpi = 900)
    save_data(ydata, './fog2_data/'+savefig_name)
    plt.show()
    plt.close()

def save_data(data, file_name):
    with open(file_name, 'wb') as fwrite:
        pickle.dump(data, fwrite)

# plotRunTime(para_fog1)
# plotDiffLoad(para_fog1)
# plotDiffV(para_fog1)
# plotBusrty(para_fog1)
# plotOtherPara(para_fog1)
# tableDiffLoad(para_fog1)
# nopDiffLoad(para_fog1)
# nop(para_fog1)
#scale(para_fog1)
plotScale()
