import numpy as np
from scipy.optimize import minimize
from scipy.optimize import linear_sum_assignment

import random
import math
import matplotlib.pyplot as plt

from Task import Task
from Queue import Queue
from auxiliary import workloadOfSet
from auxiliary import notInSet
from auxiliary import takeArriveTime
from auxiliary import sumByCol
from auxiliary import taskArrivePoisson
from Parameter import para_test
from Parameter import para_fog1

class SimOPEN:
    def __init__(self, para):
        self.para = para
        self.Q = []
        for i in range(self.para.queueNum):
            self.Q.append(Queue(i, self.para.delta, self.para.debug))
        self.W = [0 for _ in range(self.para.queueNum)] # energy deficit queues q in the literature
        self.beta = [[0 for _ in range(self.para.queueNum)] for i in range(self.para.queueNum)] # offloading decisions
        self.A_set = [[] for _ in range(self.para.queueNum)]
        self.mu = [] # mu is the expected service rate with regard to the number of tasks (e.g. tasks per second)
        # mu = f/h, f is the cpu cycle and h is the expected workload of each task
        for i in range(self.para.queueNum):
            #self.mu.append(self.para.B_max[i]/self.para.taskInfo['totalCycle'])
            self.mu.append(self.para.maxArriveRate)
        # E_tx is the energy consumption for wireless transmission
        self.E_tx = [0 for _ in range(self.para.queueNum)]
        self.func_E = []
        for i in range(self.para.queueNum):
            self.func_E.append(lambda x: self.E_tx[i]+self.para.efunc[i](sumByCol(x)[i]))
        # phi the expected task arrival computed from history data
        self.phi = [1.0 for _ in range(self.para.queueNum)]
        self.timer = 0
        self.generatedTask = 0
        temp = 0
        for i in range(self.para.queueNum):
            temp += sum(self.para.delta[i])
        self.tau = temp/(self.para.queueNum*(self.para.queueNum-1))
        self.k = self.para.energyPerMCycle*self.para.taskInfo['totalCycle']
        self.epsilon = 0.05

    def start(self):
        while self.timer < self.para.maxTime and self.generatedTask < self.para.maxTask:
            self.arrive()
            self.decision()
            for i in self.Q:
                i.statistics(self.timer)
            self.timer+=1
        if self.para.debug:
            for i in range(self.para.queueNum):
                print(self.W[i])
        self.show()

    def arrive(self): # compute arrived tasks; maybe blocked;
        self.generatedTask, self.A_set = taskArrivePoisson(self.timer, self.generatedTask, self.Q, self.para)

    def show(self):
        print("-------------------- INFO:Simulation --------------------")
        print("NumOfQueue:%d, MaxTime:%d, MaxTask:%d" % (
                self.para.queueNum, self.para.maxTime, self.para.maxTask))
        print("Timer:%d, GeneratedTask:%d" % (self.timer, self.generatedTask))
        print("ArriveRate:", self.para.arriveRate)
        print("-------------------- INFO:Queue --------------------")
        # for i in self.Q:
            # i.show()
        print(self.W)

    def _OPEN_C(self, mu, phi, tau):
        # mu: SBS services rate
        # phi: SBS workload arrival rate
        # tau: Network mean communication time
        # define marginal computation delay function d_i
        beta = [[0 for _ in range(self.para.queueNum)] for _ in range(self.para.queueNum)]
        func_d = []
        func_d_reverse = []
        for i in range(self.para.queueNum):
            func_d.append(lambda x: mu[i]/((mu[i]-min(mu[i]-0.5, x))*(mu[i]-min(mu[i]-0.5, x))))
            func_d_reverse.append(lambda x: mu[i] - math.sqrt(mu[i]/x))
            #func_d.append(lambda x: 2*x/mu[i])
            #func_d_reverse.append(lambda x: mu[i]*x/2)
        # define marginal congestion delay function g_i
        func_g = lambda x: 0
        # self.k is the energy consumption for executing h CPU cycles
        xi = []
        for i in range(self.para.queueNum):
            xi.append(self.para.V*func_d[i](phi[i])+self.k*self.W[i])
        xi_max = max(xi)
        xi_min = min(xi)
        if xi_min+self.para.V*func_g(0) >= xi_max:
            return beta
        a = xi_min
        b = xi_max
        lam_S = 0
        lam_R = 1
        alpha = 0
        omega = [0 for _ in range(self.para.queueNum)]
        inbound = [0 for _ in range(self.para.queueNum)]
        outbound = [0 for _ in range(self.para.queueNum)]
        while abs(lam_S - lam_R) >= self.epsilon:
            # print(abs(lam_S-lam_R))
            inbound = [0 for _ in range(self.para.queueNum)]
            outbound = [0 for _ in range(self.para.queueNum)]
            alpha = (a+b)/2
            # compute sink SBS list and lam_S
            sink_list = []
            lam_S = 0
            for i in range(self.para.queueNum):
                if xi[i] < alpha:
                    sink_list.append(i)
                    omega[i] = func_d_reverse[i]((alpha-(self.k*self.W[i]))/self.para.V)
                    # assert omega[i] >= phi[i]
                    lam_S += omega[i] - phi[i]
                    inbound[i] = omega[i] - phi[i]
            # compute neutral and source SBS list and lam_R
            neutral_list = []
            source_list= []
            lam_R = 0
            for i in range(self.para.queueNum):
                if xi[i] >= alpha and xi[i] <= alpha+self.para.V*func_g(lam_S):
                    neutral_list.append(i)
                    omega[i] = phi[i]
                elif xi[i] > alpha+self.para.V*func_g(lam_S):
                    source_list.append(i)
                    y = (alpha+self.para.V*func_g(lam_S)-self.k*self.W[i])/self.para.V
                    if y <= 1/mu[i]:
                        omega[i] = 0
                    else:
                        omega[i] = func_d_reverse[i]((alpha+self.para.V*func_g(lam_S)-self.k*self.W[i])/self.para.V)
                    # assert phi[i] >= omega[i]
                    lam_R += phi[i] - omega[i]
                    outbound[i] = phi[i] - omega[i]
            if lam_S > lam_R:
                b = alpha
            else:
                a = alpha
        assert math.isclose(lam_S, lam_R, abs_tol=0.1)
        for i in range(self.para.queueNum):
            if outbound[i] < 0:
                inbound[i] += -outbound[i]
                outbound[i] = 0
            if inbound[i] < 0:
                outbound[i] += -inbound[i]
                inbound[i] = 0
        assert math.isclose(sum(inbound), sum(outbound), abs_tol=0.1)
        assert min(inbound) >= 0 and min(outbound) >= 0
        # compute decision variable beta
        for i in range(self.para.queueNum):
            for j in range(self.para.queueNum):
                if outbound[i] == 0:
                    break
                if inbound[j] == 0:
                    continue
                if inbound[j] <= outbound[i]:
                    beta[i][j] += inbound[j]
                    outbound[i] -= inbound[j]
                    inbound[j] = 0
                    continue
                else:
                    beta[i][j] += outbound[i]
                    inbound[j] -= outbound[i]
                    outbound[i] = 0
                    break
        assert math.isclose(max(inbound), 0, abs_tol=0.1) and math.isclose(max(outbound), 0, abs_tol=0.1)
        return beta

    def decision(self):
        # obeserve workload arrival phi(t) and feasible offloading set B(t)
        # solving P2 to get optimal beta(t)
        self.beta = self._OPEN_C(self.mu, self.phi, self.tau)
        for i in range(self.para.queueNum):
            self.beta[i][i] = self.phi[i] - sum(self.beta[i])
        # we offload newly arrived tasks according to beta
        for i in range(self.para.queueNum):
            offloadingRate = [0 for _ in range(self.para.queueNum)]
            sumOfLoad = sum(self.beta[i])
            for j in range(self.para.queueNum):
                if j == 0:
                    offloadingRate[j] = self.beta[i][j]/sumOfLoad
                else:
                    offloadingRate[j] = offloadingRate[j-1]+self.beta[i][j]/sumOfLoad
            assert math.isclose(offloadingRate[-1], 1)
            for task in self.A_set[i]:
                prob = random.random()
                for index, p in enumerate(offloadingRate):
                    if prob < p:
                        self.Q[index].receive(task)
                        break
        # process if the length is enough
        process = [0 for _ in range(self.para.queueNum)]
        for i in range(self.para.queueNum):
            self.Q[i].checkForLmax(self.timer)
            if self.Q[i].length >= self.para.B_max[i]+5 and self.W[i] < self.para.V:
                self.Q[i].serveByCycle(self.para.B_max[i], self.timer)
                process[i] = self.para.B_max[i]
        # update queues
        for i in range(self.para.queueNum):
            self.W[i] = max(0, self.W[i] + self.para.efunc[i](process[i]) - self.para.E_aver[i])

        for i in range(self.para.queueNum):
            self.phi[i] = (self.phi[i]*(self.timer+1) + workloadOfSet(self.A_set[i])/self.para.taskInfo['totalCycle'])/(self.timer+2)

# sim = SimOPEN(para_fog1)
# sim.start()
