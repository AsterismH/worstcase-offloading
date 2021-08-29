import numpy as np
from scipy.optimize import minimize
from scipy.optimize import linear_sum_assignment

import random
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import sys
import pickle

from Task import Task
from Queue import Queue
from auxiliary import taskArrivePoisson
from auxiliary import takeArriveTime
from Parameter import para_fog1
from Parameter import para_test
import copy

class Simulation:
    def __init__(self, para):
        self.para = para
        self.timer = 0
        self.generatedTask = 0
        self.Q = []
        for i in range(self.para.queueNum):
            self.Q.append(Queue(i, self.para.delta, self.para.debug, sort=1))
        self.H = [0]*self.para.queueNum
        self.Z = [0]*self.para.queueNum
        self.W = [0]*self.para.queueNum
        self.A_set =[[] for _ in range(self.para.queueNum)]
        self.taskList = []
        self.dropList = []
        self.gamma = [0]*self.para.queueNum
        self.mu = [0]*self.para.queueNum
        self.b = [[0 for i in range(self.para.queueNum)] for j in range(self.para.queueNum)]
        self.e = [[self.para.energyStatic, self.para.taskInfo['totalCycle']*self.para.energyPerMCycle] for i in range(self.para.queueNum)]
        self.d = [0]*self.para.queueNum
        self.process = [0]*self.para.queueNum
        self.totalProcess = [0]*self.para.queueNum
        self.processWorkload = [0]*self.para.queueNum
        # self.dropLine = self.para.L_max - max(delta)
        # self.dropLine = 4500
        self.dropLine = 40
        self.blockedTask = [0 for _ in range(self.para.queueNum)]
        self.blockRate = [0 for _ in range(self.para.queueNum)]
        self.blockedWorkload = [0 for _ in range(self.para.queueNum)]
        # self.taskArrivalSeq = [0]*self.para.maxTime
        self.constW = 4*self.para.V+2
        # E_aver is the average energy consumption
        # processCapability is the average number of tasks that can be served per slot under the E_aver constraint
        self.processCapability = []
        for i in range(self.para.queueNum):
            self.processCapability.append((self.para.E_aver[i]-self.para.energyStatic)/self.para.energyPerMCycle)
        #compute theoretically maxmium throughput
        def objfunc(y, sign = 1.0):
            result = 0
            for i in range(self.para.queueNum):
                result += self.para.gfunc[i](y[i])
            return sign*result
        def objfunc_deriv(y, sign = 1.0):
            result = []
            for i in range(self.para.queueNum):
                result.append(sign*self.para.gfunc_deriv[i](y[i]))
            return np.array(result)
        totalServe = sum(self.processCapability) #total process ability
        cons = ({'type' : 'ineq',
                 'fun'  : lambda x: np.array([totalServe - sum(x)]),
                 'jac'  : lambda x: np.array([-1.0]*self.para.queueNum)})
        bnds = []
        for i in self.para.arriveRate:
            bnds.append((0, i))
        bnds = tuple(bnds)
        res = minimize(objfunc, [0]*self.para.queueNum, args=(-1.0), jac=objfunc_deriv, constraints=cons,
                       bounds=bnds, method='SLSQP')
        self.theoryThroughput = -res.fun
        #compute maxmium throughput for non-cooperation situation
        temp = 0
        for i in range(self.para.queueNum):
            temp += self.para.gfunc[i](min(self.para.arriveRate[i], self.processCapability[i]))
        self.nonCoTheoryThroughput = temp

    def start(self, slots=-1): #slots specifies the duration of a single run, mainly for debug
        if slots == -1:
            slots=self.para.maxTime-self.timer
        self.currentRoundTime = 0
        while(self.timer < self.para.maxTime and self.generatedTask < self.para.maxTask \
                and self.currentRoundTime < slots):
            self.arrive()
            self.decision()
            for i in self.Q:
                i.statistics(self.timer)
            self.timer+=1
        self.show()

    def show(self):
        print("-------------------- INFO:Simulation --------------------")
        print("NumOfQueue:%d, MaxTime:%d, MaxTask:%d" % (
                self.para.queueNum, self.para.maxTime, self.para.maxTask))
        print("Timer:%d, GeneratedTask:%d" % (self.timer, self.generatedTask))
        print("ArriveRate:", self.para.arriveRate)
        print("TotalProcess:", self.totalProcess)
        print("TotalBlockedWorkload:", self.blockedWorkload)
        print("-------------------- INFO:Queue --------------------")
        # for i in self.Q:
            # i.show()
        print(self.W)

    def arrive(self):
        self.generatedTask, self.A_set = taskArrivePoisson(self.timer, self.generatedTask, self.Q, self.para)

    def decision(self, availServeCycle = -1):
        if availServeCycle == -1:
            availServeCycle = [1000000 for _ in range(self.para.queueNum)]
        self.gamma = [0]*self.para.queueNum
        self.mu = [0]*self.para.queueNum
        self.b = [[0 for i in range(self.para.queueNum)] for j in range(self.para.queueNum)]
        self.d = [0]*self.para.queueNum
        self.process = [0]*self.para.queueNum
        self.processWorkload = [0]*self.para.queueNum
        if self.para.debug:
            print("The beginning of time %d" % self.timer)
        for i in range(self.para.queueNum):
            if self.para.debug:
                print("Q[%d]:%f, H[%d]:%f, W[%d]:%f, Z[%d]:%f" % (i, self.Q[i].length, \
                  i, self.H[i], i, self.W[i], i, self.Z[i]))
        # if self.para.debug:
            # for i in range(self.para.queueNum):
                # print('Q[%d]:' % (i), end='')
                # for j in self.Q[i].taskArray:
                    # print(j.index, end=' ')
                # print('')
        #step 1;
        #we consider separable utility function, so the optimization problem in step 1
        #can be decomposed into N single-variable problems
        for i in range(self.para.queueNum):
            def objfunc(gamma, sign=1.0):
                return sign*(self.para.V*self.para.gfunc[i](gamma) - self.Z[i]*gamma)
            def objfunc_deriv(gamma, sign=1.0):
                return sign*(self.para.V*self.para.gfunc_deriv[i](gamma) - self.Z[i])
#            cons = ({'type' : 'ineq',
#                'fun' : lambda gamma: np.array([gamma + 1]),
#                'jac' : lambda gamma: np.array([1.0])},
#                {'type' : 'ineq',
#                    'fun' : lambda gamma: np.array([-gamma + 1]),
#                    'jac' : lambda gamma: np.array([-1.0])})
            #res = minimize(objfunc, 0, args=(-1.0), jac=objfunc_deriv, constraints=cons, method='SLSQP', options={'disp':True})
            res = minimize(objfunc, 0, args=(-1.0), jac=objfunc_deriv, bounds=((-1,1),), method='SLSQP', options={'disp':False})
            #self.gamma[i] = res.x
            self.gamma[i] = np.asscalar(res.x)
        #step 2;
        # We turn all negative coefficient into 0 and acquire that every row and column be chosen at least once
        # This can be proved equivalent to the original problem
        auxMat = [] #auxiliary matrix
        for i in range(self.para.queueNum):
            auxMat.append([])
            for j in range(self.para.queueNum):
                auxVal = min(self.H[i],self.Z[i]) - self.W[j]*(self.e[j][1]-self.e[j][0])
                auxMat[i].append( -max(0, auxVal) )
        if self.para.debug:
            print(auxMat)
        costMat = np.array(auxMat)
        rowInd, colInd = linear_sum_assignment(costMat)
        for i in range(self.para.queueNum):
            if costMat[rowInd[i]][colInd[i]] == 0:
                self.b[rowInd[i]][colInd[i]] = 0
            else:
                self.b[rowInd[i]][colInd[i]] = 1
        if self.para.debug:
            print(self.b)
        #step 3;
        # we should note that in this algorithm, the unit of b and mu is the number of tasks, not workload
        for i in range(self.para.queueNum):
            self.mu[i] = sum(self.b[i])
        for i in range(self.para.queueNum):
            for j in range(self.para.queueNum):
                self.process[i] += self.b[j][i]
            self.totalProcess[i] += self.process[i]
        for i in range(self.para.queueNum):
            # if self.mu[i] == 0:
            if self.Q[i].length > 0.01 and self.H[i] >= self.Z[i]:
                self.d[i] = 1
        for i in range(self.para.queueNum):
            if self.para.debug:
                print("gamma[%d]:%f, mu[%d]:%f, d[%d]:%f, p[%d]:%f" % (i,self.gamma[i],i,self.mu[i],i,self.d[i],i,self.process[i]))
        #step 4;
        # for i in range(self.para.queueNum):
            # self.Q[i].serve(self.mu[i], self.timer)
            # if self.d[i] == 1:
                # self.Q[i].drop(self.Q[i].currentTask)
            # self.taskArrive(self.Q[i], self.para.arriveRate[i])
            # # update H
            # if self.Q[i].length == 0:
                # self.H[i] = 0
            # else:
                # #if the head-of-line task arrives in slot t(self.timer), it is designated to have a waiting
                # #time of 1 at slot t+1. Therefore, we should add an extra 1
                # self.H[i] = self.timer-self.Q[i].currentTask.arriveTime+1
            # if self.timer < self.constW:
                # self.Z[i] = max(0, self.Z[i]+self.d[i]+self.gamma[i])
            # else:
                # self.Z[i] = max(0, self.Z[i]-self.taskArrivalSeq[self.timer-self.constW]+self.d[i]+self.gamma[i])
            # #self.Z[i] = max(0, self.Z[i]-self.para.arriveRate[i][1]+self.d[i]+self.gamma[i])
            # self.W[i] = max(0, self.W[i]-self.para.E_aver[i]+self.e[i][self.process[i]])

        # block
        """
        for i in range(self.para.queueNum):
            while len(self.A_set[i]) > 0 and self.blockedTask[i] > 0:
                task = self.A_set[i][0]
                self.A_set[i].remove(task)
                self.blockedTask[i] -= 1
                self.blockedWorkload[i] += task.totalCycle
                self.Q[i].totalBlockedWorkload += task.totalCycle
        """
        random.seed()
        self.blockRate = [i*0.995 for i in self.blockRate]
        for i in range(self.para.queueNum):
            for task in self.A_set[i]:
                if random.random() < self.blockRate[i]:
                    task = self.A_set[i][0]
                    self.A_set[i].remove(task)
                    self.blockedWorkload[i] += task.totalCycle
                    self.Q[i].totalBlockedWorkload += task.totalCycle
        for i in range(self.para.queueNum):
            self.Q[i].accept(self.A_set[i])
        for i in range(self.para.queueNum):
            for j in range(self.para.queueNum):
                if self.b[i][j] == 1 and i != j and self.b[j][i] == 0:
                    task = self.Q[i].offloadHOL()
                    self.Q[j].receive(task)
        for i in range(self.para.queueNum):
            if self.process[i] > 0:
                assert self.process[i] == 1
                self.processWorkload[i] = self.Q[i].serveByTaskNum(self.process[i], self.timer)
        for i in range(self.para.queueNum):
            if self.d[i] == 1 or self.H[i] > self.Z[i]:
                self.d[i] == 0
                # TODO: drop tasks if their response time is about to exceed the worst-case guarantee
                while len(self.Q[i].taskArray) > 0 and self.timer-self.Q[i].currentTask.arriveTime+1 > self.Z[i]:
                    task = self.Q[i].virtualDropHOL()
                    self.dropList.append(task)
                    # self.blockedTask[i] += 5
                    self.blockRate[i] += 0.3
                    self.d[i] += 1
        # for i in range(self.para.queueNum):
            # self.taskArrive(self.Q[i], self.para.arriveRate[i])
            # update H
            if math.isclose(self.Q[i].length, 0, abs_tol=0.01):
                self.H[i] = 0
            else:
                #if the head-of-line task arrives in slot t(self.timer), it is designated to have a waiting
                #time of 1 at slot t+1. Therefore, we should add an extra 1
                # self.H[i] = 3*(self.timer-self.Q[i].currentTask.arriveTime+1)
                self.H[i] = (self.timer-self.Q[i].currentTask.arriveTime+1)
            """
            if self.timer < self.constW:
                self.Z[i] = max(0, self.Z[i]+self.d[i]+self.gamma[i])
            else:
                self.Z[i] = max(0, self.Z[i]-self.taskArrivalSeq[self.timer-self.constW]+self.d[i]+self.gamma[i])
            """
            self.Z[i] = max(0, self.Z[i]-self.para.arriveRate[i]+self.d[i]+self.gamma[i])
            # self.W[i] = max(0, self.W[i]-self.para.E_aver[i]+self.e[i][self.process[i]])
            # self.W[i] = max(0, self.W[i]-self.para.E_aver[i]+self.para.efunc[i](self.processWorkload[i]))

class SimFog1:
    def __init__(self, para):
        self.para = para
        self.timer = 0
        self.generatedTask = 0
        self.numOfInstances = 5
        self.W = [0 for _ in range(para.queueNum)]
        self.workloadInterval = [[] for _ in range(self.numOfInstances)]
        self.lengthOfInterval = (self.para.taskInfo['totalCycleMax']-self.para.taskInfo['totalCycleMin'])/self.numOfInstances
        for i in range(self.numOfInstances):
            self.workloadInterval[i].append(self.para.taskInfo['totalCycleMin']+i*self.lengthOfInterval)
            self.workloadInterval[i].append(self.para.taskInfo['totalCycleMin']+(i+1)*self.lengthOfInterval)
        self.instances = []
        for i in range(self.numOfInstances):
            paraNew = copy.deepcopy(para)
            paraNew.arriveRate = [j/self.numOfInstances for j in para.arriveRate]
            paraNew.taskInfo['totalCycle'] = sum(self.workloadInterval[i])/2
            paraNew.taskInfo['totalCycleMin'] = self.workloadInterval[i][0]
            paraNew.taskInfo['totalCycleMax'] = self.workloadInterval[i][1]
            paraNew.E_aver = [(paraNew.taskInfo['totalCycle']/para.taskInfo['totalCycle'])*(para.E_aver[j]/self.numOfInstances) for j in range(para.queueNum)]
            paraNew.energyStatic = para.energyStatic/self.numOfInstances
            paraNew.efunc = []
            paraNew.efunc_deriv = []
            for j in range(paraNew.queueNum):
                paraNew.efunc.append(lambda x: paraNew.energyStatic + paraNew.energyPerMCycle*x)
                paraNew.efunc_deriv.append(lambda x: paraNew.energyPerMCycle)
            self.instances.append(Simulation(paraNew))
        # self.A_set[i][j] is the task list in instance i of BS j
        self.A_set_inst = [[[] for _ in range(self.para.queueNum)] for _ in range(self.numOfInstances)]
        self.A_set = [[] for _ in range(self.para.queueNum)]

    def start(self):
        while self.timer < self.para.maxTime and self.generatedTask < self.para.maxTask:
            self.arrive()
            for i in range(self.numOfInstances):
                self.instances[i].A_set = self.A_set_inst[i]
                for j in range(self.para.queueNum):
                    self.instances[i].generatedTask += len(self.A_set_inst[i][j])
            for i in range(self.numOfInstances):
                self.instances[i].decision()
            pw = [0 for _ in range(self.para.queueNum)]
            for i in range(self.para.queueNum):
                for inst in self.instances:
                    pw[i] += inst.processWorkload[i]
            for i in range(self.para.queueNum):
                self.W[i] = max(0, (self.W[i]+self.para.efunc[i](pw[i])-self.para.E_aver[i]))
                # self.W[i] = self.W[i]+self.para.efunc[i](pw[i])-self.para.E_aver[i]
            for inst in self.instances:
                inst.W = [max(0,i) for i in self.W]
            # calculate how much computing cycles left in each bs
            remain_cpu = self.para.B_max
            for inst in self.instances:
                for j in range(self.para.queueNum):
                    remain_cpu[j] -= inst.processWorkload[j]
            for i in range(self.para.queueNum):
                remain_cpu[i] = max(0, remain_cpu[i])
            # find bs with smallest W to serve dropped tasks
            # first discard tasks whose response time exceed L^max-2*delta^max
            for inst in self.instances:
                for task in inst.dropList:
                    if self.timer - task.arriveTime > inst.dropLine:
                        inst.dropList.remove(task)
                        # inst.blockedTask[task.arriveQueue.index] += 10
                        task.arriveQueue.dropped += task.totalCycle
                if len(inst.dropList) > 1:
                    inst.dropList.sort(key=takeArriveTime)
            for inst in self.instances:
                while len(inst.dropList) > 0 and max(remain_cpu) >= inst.dropList[0].totalCycle:
                    task = inst.dropList[0]
                    inst.dropList.remove(task)
                    bs_index = remain_cpu.index(max(remain_cpu))
                    remain_cpu[bs_index] -= task.totalCycle
                    inst.Q[bs_index].receive(task)
                    inst.Q[bs_index].setHOL(task)
                    inst.Q[bs_index].serveByTaskNum(1, self.timer)
                    # need to update W queue
                    # inst.W[bs_index] += inst.para.efunc[bs_index](task.totalCycle)
                    self.W[bs_index] += self.para.energyPerMCycle*task.totalCycle
            for i in range(self.numOfInstances):
                for j in range(self.para.queueNum):
                    self.instances[i].Q[j].statistics(self.timer)
            self.timer+=1
            for i in range(self.numOfInstances):
                self.instances[i].timer = self.timer
        for i in range(self.numOfInstances):
            self.instances[i].show()
        print(self.W)

    def arrive(self):
        fakeQueue = [None for _ in range(self.para.queueNum)]
        self.generatedTask, self.A_set = taskArrivePoisson(self.timer, self.generatedTask, fakeQueue, self.para)
        # assign tasks to different instances and set their actual arive queue
        self.A_set_inst = [[[] for _ in range(self.para.queueNum)] for _ in range(self.numOfInstances)]
        for j in range(self.para.queueNum):
            for task in self.A_set[j]:
                index = math.floor((task.totalCycle-self.para.taskInfo['totalCycleMin'])/self.lengthOfInterval)
                # if the task's workload is the maxCycle, we may result in a index that is out of list scope
                if index == self.numOfInstances:
                    index = self.numOfInstances-1
                assert task.totalCycle >= self.workloadInterval[index][0] and task.totalCycle <= self.workloadInterval[index][1]
                task.arriveQueue = self.instances[index].Q[j]
                self.A_set_inst[index][j].append(task)

    def show(self):
        print("-------------------- INFO:Simulation --------------------")
        print("NumOfQueue:%d, MaxTime:%d, MaxTask:%d" % (
                self.para.queueNum, self.para.maxTime, self.para.maxTask))
        print("Timer:%d, GeneratedTask:%d" % (self.timer, self.generatedTask))
        print("ArriveRate:", self.para.arriveRate)
        # print("-------------------- INFO:Queue --------------------")
        # for i in range(self.para.queueNum):
            # self.Q[i].show()

# para = para_test
# # para.arriveRate = [i/10 for i in para.arriveRate]
# # para.maxArriveRate /= 10
# # para.energyStatic /= 10
# # para.E_aver = [i/10 for i in para.E_aver]
# # para.B_max = [i/10 for i in para.B_max]
# # sim = Simulation(para)
#sim = SimFog1(para_fog1)
#sim.start()

