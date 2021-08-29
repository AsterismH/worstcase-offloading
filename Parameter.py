import pickle

delta = [[0 for i in range(4)] for i in range(4)]
for i in range(4):
    for j in range(4):
        if i == j:
            delta[i][j] = 0
        elif i == 3 or j == 3:
            delta[i][j] = 10
        else:
            delta[i][j] = 10

class Parameter:
    def __init__(self):
        self.maxTime = 1000
        self.maxTask = 50000000
        self.debug = 0
        self.V = 30
        self.beta = 3
        self.queueNum = 4
        self.userNum = 0
        self.delta = delta
        self.arriveRate = [3, 3, 1, 2]
        # self.arriveRate = [4.5, 4.5, 1.5, 3]
        self.maxArriveRate = 15 # max number of tasks
        self.taskInfo = {'datasize':0, 'totalCycle':1, 'totalCycleVar':1, 'totalCycleMin':0.1, \
                    'totalCycleMax':1.9}
        self.energyStatic = 1
        self.energyPerMCycle = 1
        self.E_aver = [3, 5, 4, 3]
        # self.E_aver = [2, 2, 1, 1]
        self.A_max = 20 # max workload
        self.B_max = [10, 10, 10, 10] # max workload
        self.epsilon = 3
        self.p = 10
        self.bursty = 0
        self.offloadingTimeDist = 1
        self.offloadingTimeAver = 20
        self.offloadingTimeVar = 5
        self.offloadingTimeLb = 10
        self.offloadingTimeUb = 30
        self.gfunc = [lambda x: x, lambda x: x, lambda x: x, lambda x:x]
        self.gfunc_deriv = [lambda x:1, lambda x:1, lambda x:1, lambda x:1]
        self.efunc = [lambda x: self.energyStatic+x, lambda x: self.energyStatic+x, \
                   lambda x: self.energyStatic+x, lambda x: self.energyStatic+x]
        self.efunc_deriv = [lambda x: 1.0, lambda x: 1.0, \
                        lambda x: 1.0, lambda x: 1.0]

para_test = Parameter()
paraOPEN = Parameter()
paraOPEN.queueNum = 10 # Expected number of SBSs, N = 10
# Expected number of UEs, M = 400 ~ [200, 600]
# Task arrival rate of UE m, \pi^t_m = [0, 4] task/sec
# Expected number of CPU cycles per task, h = 40M
# CPU frequency of edge server at SBS n, f_n = 3G Hz
# Expected input data size per task, s = 0.2 Mb
# Transmission delay for one task in LAN, \tau = 200 ms
# Wireless transmission frequency, f^{TX} = 900M Hz
# Distance power loss coefficient, N_L = 20
# Wireless channel bandwidth, W = 20M Hz
# Noise power, \sigma^2 = -174 dBm/Hz
# Transmission power of UEs, P^u_m = 10 dBm
# Expected energy consumption per task, k_n = 9*10^{-5} W*h
# Long term energy constraint, E_aver[n] = 22 W*h

para_fog1 = Parameter()
para_fog1.maxTime = 1000
para_fog1.debug = 0
para_fog1.V = 50
para_fog1.beta = 3
para_fog1.queueNum = 36
para_fog1.userNum = 126
with open('aux/delta', 'rb') as fread:
    para_fog1.delta = pickle.load(fread)
    assert len(para_fog1.delta[0]) == para_fog1.queueNum
# the arriveRate records the average arrival of each BS and can be computed from the number of users that linked to each BS. e.g. if each user post 0.5 task per slot, and a BS links to 6 users, then the arrival rate of this BS is 0.5*6=3.
para_fog1.arriveRate = []
averageArriveOfUser = 0.25
with open('aux/iUserOfBS', 'rb') as fread:
    iUserOfBS = pickle.load(fread)
    assert len(iUserOfBS) == para_fog1.queueNum
for i in iUserOfBS:
    if i == 0:
        i = 1
    para_fog1.arriveRate.append(i*averageArriveOfUser)
para_fog1.maxArriveRate = 20*max(para_fog1.arriveRate)
para_fog1.taskInfo = {'data_size':0, 'totalCycle':5, 'totalCycleVar':1, 'totalCycleMin':2.5, 'totalCycleMax':7.5}
para_fog1.energyPerMCycle = 8.2*2.78*0.1*0.2 # uW*h
para_fog1.energyStatic = 4.17*0.2  # 15w per hour  # 2.22 # uWh per slot
# para_fog1.E_aver = [para_fog1.energyPerMCycle*9+para_fog1.energyStatic for _ in range(para_fog1.queueNum)] # process 10M (2 tasks) per slot
# para_fog1.E_aver = [25 for _ in range(para_fog1.queueNum)] # process 10M (2 tasks) per slot
para_fog1.E_aver = [para_fog1.energyPerMCycle*5+para_fog1.energyStatic for _ in range(para_fog1.queueNum)]
para_fog1.A_max = 30
para_fog1.B_max = [20 for _ in range(para_fog1.queueNum)]
para_fog1.epsilon = 8
para_fog1.p = 30 # will be used in CoR
para_fog1.bursty = 0
para_fog1.gfunc = []
para_fog1.gfunc_deriv = []
para_fog1.efunc = []
para_fog1.efunc_deriv = []
for i in range(para_fog1.queueNum):
    para_fog1.gfunc.append(lambda x: x)
    para_fog1.gfunc_deriv.append(lambda x: 1)
    para_fog1.efunc.append(lambda x: para_fog1.energyStatic + para_fog1.energyPerMCycle*x)
    para_fog1.efunc_deriv.append(lambda x: para_fog1.energyPerMCycle)


