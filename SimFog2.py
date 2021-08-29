import numpy as np
from scipy.optimize import minimize
from scipy.optimize import linear_sum_assignment

import random
import math
import matplotlib.pyplot as plt

from Task import Task
from Queue import Queue
from auxiliary import workloadOfSet
from auxiliary import totalWorkloadOfSet
from auxiliary import notInSet
from auxiliary import takeArriveTime
from auxiliary import sumCol
from auxiliary import sumRow
from auxiliary import pickFirstMTasks
from auxiliary import taskArrivePoisson
from Parameter import para_test
from Parameter import para_fog1

class SimFog2:
    def __init__(self, para):
        #copy parameter
        self.para = para
        self.v = [] # intial deriv value, used to calculate theoretical bound; TODO: put other place
        for i in range(self.para.queueNum):
            self.v.append(self.para.gfunc_deriv[i](0))

        #init local variables
        self.timer = 0
        self.generatedTask = 0
        self.Q = []
        for i in range(self.para.queueNum):
            self.Q.append(Queue(i, self.para.delta, self.para.debug, 1))
        self.H = [0]*self.para.queueNum
        self.Z = [0]*self.para.queueNum
        self.G = [0]*self.para.queueNum
        self.W = [0]*self.para.queueNum
        # Q_w[i] = Q[i].length + owe[*][i] - owe[i][*]
        self.Q_w = [0]*self.para.queueNum
        self.gamma = [0]*self.para.queueNum #no combinatorial constraint for gamma
        self.A_set = [[] for _ in range(self.para.queueNum)]
        self.a_set = [[] for _ in range(self.para.queueNum)]
        self.b = [0]*self.para.queueNum
        self.b_actual = [0]*self.para.queueNum
        self.c_set = [[[] for i in range(self.para.queueNum)] for j in range(self.para.queueNum)]
        self.d_set = [[] for _ in range(self.para.queueNum)]
        self.process = [0]*self.para.queueNum
        self.totalProcess = [0]*self.para.queueNum
        self.owe = [[0 for i in range(self.para.queueNum)] for j in range(self.para.queueNum)]
        self.theoryThroughput = self._optThroughput()

    def _optThroughput(self):
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
        totalServe = sum([(self.para.E_aver[i]-self.para.efunc[i](0))/self.para.efunc_deriv[i](0) \
                          for i in range(self.para.queueNum)]) #total process ability
        cons = ({'type' : 'ineq',
                 'fun'  : lambda x: np.array([totalServe - sum(x)]),
                 'jac'  : lambda x: np.array([-1.0]*self.para.queueNum)})
        bnds = []
        for i in self.para.arriveRate:
            bnds.append((0, i*self.para.taskInfo['totalCycle']))
        bnds = tuple(bnds)
        res = minimize(objfunc, [0]*self.para.queueNum, args=(-1.0), jac=objfunc_deriv, constraints=cons,\
                       bounds=bnds, method='SLSQP')
        return -res.fun

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

    def arrive(self):
        self.generatedTask, self.A_set = taskArrivePoisson(self.timer, self.generatedTask, self.Q, self.para)

    def show(self):
        print("-------------------- INFO:Simulation --------------------")
        print("Algorithm: ULG")
        print("NumOfQueue:%d, MaxTime:%d, MaxTask:%d" % (
                self.para.queueNum, self.para.maxTime, self.para.maxTask))
        print("Timer:%d, GeneratedTask:%d" % (self.timer, self.generatedTask))
        print("ArriveRate:", self.para.arriveRate)
        print("-------------------- INFO:Queue --------------------")
        for i in self.Q:
            i.show()

    def throughput(self):
        performance = 0
        for i in range(self.para.queueNum):
            performance += self.para.gfunc[i](self.Q[i].accepted / self.timer)
            performance -= self.para.beta * self.v[i] * (self.Q[i].dropped / self.timer)
        return performance

    def decision(self):
        N = self.para.queueNum
        self.gamma = [0]*self.para.queueNum #no combinatorial constraint for gamma
        self.a_set = [[] for _ in range(self.para.queueNum)]
        self.b = [0]*self.para.queueNum
        self.b_actual = [0]*self.para.queueNum
        self.c_set = [[[] for i in range(self.para.queueNum)] for j in range(self.para.queueNum)]
        self.d_set = [[] for _ in range(self.para.queueNum)]
        if self.para.debug:
            print("The beginning of time %d" % self.timer)
            for i in range(self.para.queueNum):
                print("Q[%d]:%f, G[%d]:%f, W[%d]:%f, Z[%d]:%f, %f" % (i, self.Q_w[i], \
                    i, self.G[i], i, self.W[i], i, self.Z[i], self.Q[i].length))

        #step 1;
        #we consider separable utility function, so the optimization problem in step 1
        #can be decomposed into N single-variable problems
        for i in range(self.para.queueNum):
            def objfunc(gamma, sign=1.0):
                return sign*(self.para.V*self.para.gfunc[i](gamma) - self.G[i]*gamma)
            def objfunc_deriv(gamma, sign=1.0):
                return sign*(self.para.V*self.para.gfunc_deriv[i](gamma) - self.G[i])
            res = minimize(objfunc, 0.5, args=(-1.0,), jac=objfunc_deriv, \
                           bounds=((0,self.para.A_max),), method='SLSQP', options={'disp':False})
            self.gamma[i] = np.asscalar(res.x)
        if self.para.debug:
            for i in range(self.para.queueNum):
                print('gamma[%d]:%f' % (i, self.gamma[i]), end=' ')
            print('')

        #step 2;
        # Choose $\widehat{a}_n(t)$
        # NOTE: we leave the implement of a_n(t) in the last because
        #           the newly arried task can only be processed in the next time slot
        for i in range(self.para.queueNum):
            if self.Q_w[i] >= self.G[i]:
                self.a_set[i] = []
            else:
                self.a_set[i] = pickFirstMTasks(self.A_set[i], self.para.A_max)
        #step 3;
        # Choose $b_n(t)$
        for i in range(self.para.queueNum):
            def objfunc(gamma, sign=1.0):
                return sign*((self.Q_w[i]+self.Z[i])*gamma - self.W[i]*self.para.efunc[i](gamma))
            def objfunc_deriv(gamma, sign=1.0):
                return sign*(self.Q[i].length+self.Z[i] - self.W[i]*self.para.efunc_deriv[i](gamma))
            res = minimize(objfunc, 0.5, args=(-1.0,), jac=objfunc_deriv, bounds=((0,self.para.B_max[i]),),\
                    method='SLSQP', options={'disp':False})
            self.b[i] = np.asscalar(res.x) # The cpu cycle should be int
        if self.para.debug:
            for i in range(self.para.queueNum):
                print('b[%d]:%f' % (i, self.b[i]), end=' ')
            print('')
        # implement b_n(t)
        eta = [[] for i in range(N)] # tasks processed by BS i
        rec = [[] for _ in range(N)] # tasks transferred to BS i
        br_n = [0 for i in range(N)]
        Qo_set = []
        for i in range(N):
            Qo_set.extend(self.Q[i].taskArray)
        Qo_set.sort(key=takeArriveTime)
        for i in range(N):
            br_n[i] = self.b[i]
        # TODO: technique mentioned in the remark
        while max(br_n) > 1.0e-9 and len(Qo_set) > 0:
            tempTask = Qo_set.pop(0)
            if br_n[tempTask.arriveQueue.index] > 1.0e-9:
                m = tempTask.arriveQueue.index
            else:
                m = br_n.index(max(br_n))
            if m != tempTask.currentQueue.index:
                self.owe[m][tempTask.currentQueue.index] += tempTask.totalCycle # how much workload BS i owed BS j
                self.Q[tempTask.currentQueue.index].offload(tempTask)
                tempTask.currentQueue = self.Q[m]
                rec[m].append(tempTask)
            eta[m].append(tempTask)
            br_n[m] = br_n[m]-tempTask.totalCycle
        for i in range(N):
            if len(eta[i]) > 0:
                self.Q[i].receiveByTaskList(rec[i])
                self.Q[i].serveByTaskList(eta[i], self.timer)
                self.b_actual[i] = totalWorkloadOfSet(eta[i])
        # update self.owe
        # clear debt cycles
        """
        balances = [0 for _ in range(N)]
        for i in range(N):
            # how much workload i owes other bs
            balances[i] = sumRow(self.owe, i) - sumCol(self.owe, i)
        assert math.isclose(sum(balances), 0, abs_tol=0.01)
        self.owe = [[0 for _ in range(N)] for _ in range(N)]
        while max(balances) > 1.0e-9:
            source = balances.index(max(balances))
            destination = balances.index(min(balances))
            amount = min(balances[source], -balances[destination])
            balances[source] -= amount
            balances[destination] += amount
            self.owe[source][destination] += amount
        assert math.isclose(sum(balances), 0, abs_tol=0.01)
        assert math.isclose(max(balances), 0, abs_tol=0.01)
        # clear debt by offloading tasks
        for i in range(N):
            for j in range(N):
                if len(self.Q[i].taskArray) <= 0:
                    break
                else:
                    tempTask = self.Q[i].taskArray[0]
                    while self.owe[i][j] - tempTask.totalCycle >= 1.0e-9:
                        tempTask.currentQueue = self.Q[j]
                        self.Q[i].offload(tempTask)
                        self.Q[j].receive(tempTask)
                        self.owe[i][j] -= tempTask.totalCycle
                        if len(self.Q[i].taskArray) <= 0:
                            break
                        else:
                            tempTask = self.Q[i].taskArray[0]
            self.Q[i].sortQueue()
        """

        #step 4; choose c
        # sort by the length of Q_n(t)+Z_n(t)
        for i in range(self.para.queueNum):
            self.H[i] = self.Z[i] + self.Q_w[i]
        arrayH = np.array(self.H)
        pi = np.argsort(-arrayH).tolist() # The index of H with dscending order
        i = 0
        j = N - 1
        offloaded_workload = [[0 for _ in range(N)] for _ in range(N)]
        balances = [0 for _ in range(N)]
        for i in range(N):
            # how much workload i owes other bs (send out)
            balances[i] = sumRow(self.owe, i) - sumCol(self.owe, i)
        # clear debt
        for i in range(N//2):
            for j in range(N-1, N//2-1, -1):
                temp = min(self.para.p - sumRow(offloaded_workload, pi[i]),
                        self.para.p - sumCol(offloaded_workload, pi[j]),
                        max(min(-balances[pi[i]], balances[pi[j]]), 0))
                balances[pi[j]] -= temp
                balances[pi[i]] += temp
                offloaded_workload[pi[i]][pi[j]] += temp
                if math.isclose(self.para.p, sumRow(offloaded_workload, pi[i]), abs_tol=0.01):
                    break
        for i in range(N):
            assert sumRow(offloaded_workload, i) <= self.para.p + 0.01
            assert sumCol(offloaded_workload, i) <= self.para.p + 0.01
        i = 0
        j = N - 1
        # offload task
        while i <= N//2-1:
            if len(self.Q[pi[i]].taskArray) <= 0:
                i += 1
                continue
            else:
                tempTask = self.Q[pi[i]].taskArray[0]
                if sumCol(offloaded_workload, pi[j]) + tempTask.totalCycle > self.para.p:
                    j -= 1
                    if j <= N//2 - 1:
                        break
                    continue
                elif sumRow(offloaded_workload, pi[i]) + tempTask.totalCycle > self.para.p:
                    i += 1
                    continue
                else:
                    self.Q[pi[i]].offload(tempTask)
                    self.c_set[pi[i]][pi[j]].append(tempTask)
                    offloaded_workload[pi[i]][pi[j]] += tempTask.totalCycle
        # implement c
        for i in range(N):
            for j in range(N):
                self.Q[j].receiveByTaskList(self.c_set[i][j])
        # reconstruct owe form balances
        self.owe = [[0 for _ in range(N)] for _ in range(N)]
        while max(balances) > 1.0e-9:
            source = balances.index(max(balances))
            destination = balances.index(min(balances))
            amount = min(balances[source], -balances[destination])
            balances[source] -= amount
            balances[destination] += amount
            self.owe[source][destination] += amount
        assert math.isclose(sum(balances), 0, abs_tol=0.01)
        assert math.isclose(max(balances), 0, abs_tol=0.01)
        if self.para.debug:
            print("owe:", end='')
            print(self.owe)

        #step 5;
        # Choose $\widehat{d}_n(t)$
        # TODO: explain average d is 0 in the paper
        # a little different to what written in paper, we pick tasks to exceed A^{max}
        for i in range(self.para.queueNum):
            # $\widehat{d}_n(t)$ is not empty only when $Q_n(t)+Z_n(t) > \beta*V*v_n$
            if self.Q_w[i]+self.Z[i] > self.para.beta*self.para.V*self.v[i]:
                currentWorkload = 0
                j = 1 # start from index 1 to skip the HOL task
                while currentWorkload < self.para.A_max and j < len(self.Q[i].taskArray):
                    nextTask = self.Q[i].taskArray[j]
                    # avoid tasks designated to be offloaded
                    if notInSet(nextTask, self.c_set[i]):
                        self.d_set[i].append(nextTask)
                        currentWorkload += nextTask.totalCycle
                    j += 1
            else:
                self.d_set[i] = []
        if self.para.debug:
            for i in range(self.para.queueNum):
                print('d[%d]:%f' % (i, workloadOfSet(self.d_set[i])), end=' ')
            print('')
        # implement d_n(t)
        for i in range(N):
            self.Q[i].drop(self.d_set[i])
        # implement a_n(t)
        for i in range(N):
            self.Q[i].accept(self.a_set[i])
            self.Q[i].totalBlockedWorkload += (workloadOfSet(self.A_set[i]) - workloadOfSet(self.a_set[i]))
        if self.para.debug:
            print("------------------------------ Accept ------------------------------")
            for i in range(N):
                print("Accept on Queue %d:" % (i), end='')
                for task in self.a_set[i]:
                    print(" %d," % (task.index), end='')
                print("")
            for i in range(N):
                print("Queue %d:" % (i), end='')
                for task in self.Q[i].taskArray:
                    print(" %d," % (task.index), end='')
                print("")
            print("--------------------------------------------------------------------")
        #step 6;
        # Update queues
        for i in range(N):
            # changeWorkload = self.b_actual[i] + workloadOfSet(self.d_set[i]) + sum(totalWorkloadOfSet(self.c_set[i])) - sum(totalWorkloadOfSet([row[i] for row in self.c_set]))
            changeWorkload = self.b_actual[i] + workloadOfSet(self.d_set[i]) + sumRow(offloaded_workload, i) - sumCol(offloaded_workload, i)
            if self.para.debug:
                print(changeWorkload)
                print(self.Q[i].length)
                print(self.Q_w[i])
            if self.Q_w[i] > changeWorkload:
                self.Z[i] = max(self.Z[i] - changeWorkload + self.para.epsilon, 0)
            else:
                self.Z[i] = 0
            self.Q_w[i] = self.Q_w[i] - changeWorkload + totalWorkloadOfSet(self.a_set[i])
            # if self.para.debug:
                # print(self.Q[i].length)
            assert math.isclose(self.Q_w[i], self.Q[i].length + sumCol(self.owe, i) - sumRow(self.owe, i), abs_tol=0.01)
            self.G[i] = max(self.G[i] - totalWorkloadOfSet(self.a_set[i]) + self.gamma[i], 0)
            self.W[i] = max(self.W[i] - self.para.E_aver[i] + self.para.efunc[i](self.b_actual[i]), 0)

# sim = SimFog2(para_fog1)
# sim.start()
