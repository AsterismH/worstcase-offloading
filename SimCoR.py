import random
from math import floor
import copy


from Task import Task
from Queue import Queue
from auxiliary import workloadOfSet
from auxiliary import notInSet
from auxiliary import takeArriveTime
from auxiliary import taskArrivePoisson
from auxiliary import listMaxDiff2D
from Parameter import para_test
from Parameter import para_fog1

class SimCoR:
    def __init__(self, para):
        self.para = para
        self.para.p = 6
        self.timer = 0
        self.generatedTask = 0
        self.expandedDelta = [[0 for _ in range(self.para.queueNum*self.para.queueNum)] for _ in range(self.para.queueNum*self.para.queueNum)]
        for i in range(self.para.queueNum*self.para.queueNum):
            for j in range(self.para.queueNum*self.para.queueNum):
                self.expandedDelta[i][j] = self.para.delta[floor(i/self.para.queueNum)][floor(j/self.para.queueNum)]
        # Q[i][j] is Q_i^j in the paper
        self.Q = [[] for _ in range(self.para.queueNum)]
        for i in range(self.para.queueNum):
            for j in range(self.para.queueNum):
                self.Q[i].append(Queue(i*self.para.queueNum+j, self.expandedDelta, self.para.debug))
        # the computing cost per MCycle zeta_i = W_i*energyCostCoef
        self.W = [0 for _ in range(self.para.queueNum)]
        self.energyCostCoef = 1
        self.A_set = [[] for _ in range(self.para.queueNum)]
        # workload of accepted tasks
        self.a = [0 for _ in range(self.para.queueNum)]
        self.k = [[0 for _ in range(self.para.queueNum)] for _ in range(self.para.queueNum)]
        self.epsilon = 1.0/self.para.V
        self.Q_0, self.Q_max = self._computePlaceHolder()

    def start(self):
        while self.timer < self.para.maxTime and self.generatedTask < self.para.maxTask:
            self.arrive()
            self.decision()
            for i in range(self.para.queueNum):
                for s in range(self.para.queueNum):
                    self.Q[i][s].statistics(self.timer)
            self.timer+=1
        if self.para.debug:
            for i in range(self.para.queueNum):
                print(self.W[i])
        self.show()

    def arrive(self):
        Q_local = []
        for i in range(self.para.queueNum):
            Q_local.append(self.Q[i][i])
        self.generatedTask, self.A_set = taskArrivePoisson(self.timer, self.generatedTask, Q_local, self.para)

    def show(self):
        print("-------------------- INFO:Simulation --------------------")
        print("NumOfQueue:%d, MaxTime:%d, MaxTask:%d" % (
                self.para.queueNum, self.para.maxTime, self.para.maxTask))
        print("Timer:%d, GeneratedTask:%d" % (self.timer, self.generatedTask))
        print("ArriveRate:", self.para.arriveRate)
        print("-------------------- INFO:Queue --------------------")
        # for i in range(self.para.queueNum):
            # self.Q[i][i].show()
        print(self.W)

    def decision(self):
        N = self.para.queueNum
        # Algorithm 1
        # line 3. compute self.a according to eq (12)
        self.a = [0 for _ in range(N)]
        for i in range(N):
            # self.para.gfunc_deriv[i](0) is the alpha_i in the paper
            if self.Q_0[i][i] + self.Q[i][i].length < self.para.gfunc_deriv[i](0)/self.epsilon:
                self.a[i] = self.A_set[i]
            else:
                self.a[i] = []
                self.Q[i][i].totalBlockedWorkload += workloadOfSet(self.A_set[i])
        # line 4. compute f_i^s according to eq (13)
        # first compute k
        self.k = [[0 for _ in range(N)] for _ in range(N)]
        for i in range(N):
            for j in range(N):
                self.k[i][j] = self.epsilon*(self.Q_0[i][j]+self.Q[i][j].length) - self.energyCostCoef*self.W[i]
        # compute f
        f = [[0 for _ in range(N)] for _ in range(N)]
        for i in range(N):
            index = self.k[i].index(max(self.k[i]))
            if self.k[i][index] > 0:
                f[i][index] = self.para.B_max[i]
        # line 5. schedule the offloading and routing based on (14)
        # b_{ij}^s: the tasks of server s offloaded from i to j
        b = [[[0 for _ in range(N)] for _ in range(N)] for _ in range(N)]
        beta = [[[0 for _ in range(N)] for _ in range(N)] for _ in range(N)]
        for i in range(N):
            for j in range(N):
                for s in range(N):
                    beta[i][j][s] = self.epsilon * (self.Q_0[i][s]+self.Q[i][s].length-self.Q[j][s].length-self.Q_0[j][s])
        for i in range(N):
            for j in range(N):
                s = beta[i][j].index(max(beta[i][j]))
                b[i][j][s] = self.para.p
        # execute offloading decision, then process decision
        for i in range(N):
            for j in range(N):
                for s in range(N):
                    taskList = self.Q[i][s].offloadByCycle(b[i][j][s])
                    self.Q[j][j].receiveByTaskList(taskList)
        for i in range(N):
            self.Q[i][i].receiveByTaskList(self.a[i])
        true_f = [[0 for _ in range(N)] for _ in range(N)]
        for i in range(N):
            for s in range(N):
                self.Q[i][s].checkForLmax(self.timer)
                task_num = 0
                total_workload = 0
                for task in self.Q[i][s].taskArray:
                    if total_workload + task.totalCycle > f[i][s]:
                        break
                    else:
                        total_workload += task.totalCycle
                        true_f[i][s] += task.totalCycle
                        task_num += 1
                # self.Q[i][s].serveByCycle(f[i][s], self.timer)
                self.Q[i][s].serveByTaskNum(task_num, self.timer)
        # update energy consumption queue
        for i in range(N):
            self.W[i] = max(0, self.W[i] + self.para.efunc[i](sum(true_f[i])) - self.para.E_aver[i])

    def _computePlaceHolder(self):
        # init
        N = self.para.queueNum
        Q_0_new = [[1000000 for _ in range(N)] for _ in range(N)]
        Q_max_new = [[-1000000 for _ in range(N)] for _ in range(N)]
        Q_max = [0 for _ in range(N)]
        for i in range(N):
            Q_max[i] = self.para.gfunc_deriv[i](0)/self.epsilon + self.para.maxArriveRate*self.para.taskInfo['totalCycleMax'] + (self.para.queueNum-1)*self.para.p
            Q_max_new[i][i] = Q_max[i]
        w = [[0 for _ in range(N)] for _ in range(N)]
        for i in range(N):
            for j in range(N):
                w[i][j] = -self.para.p
        phi = [[0 for _ in range(N)] for _ in range(N)]
        for i in range(N):
            for s in range(N):
                phi[i][s] = self.W[i]*self.energyCostCoef - self.para.B_max[i]
        # recursively computing
        while True:
            Q_0_old = copy.deepcopy(Q_0_new)
            Q_max_old = copy.deepcopy(Q_max_new)
            for i in range(N):
                for s in range(N):
                    li = []
                    li.append(Q_0_old[i][s])
                    for j in range(N):
                        li.append(Q_0_old[j][s]-w[i][j])
                    li.append(phi[i][s])
                    Q_0_new[i][s] = max(0, min(li))
                    li = []
                    li.append(Q_max_old[i][s])
                    for j in range(N):
                        li.append(Q_max_old[j][s]-w[i][j])
                    Q_max_new[i][s] = min(Q_max[s], max(li))
            if listMaxDiff2D(Q_0_new, Q_0_old) < 0.01 or listMaxDiff2D(Q_max_new, Q_max_old) < 0.01:
                break
        return Q_0_new, Q_max_new

# sim = SimCoR(para_fog1)
# sim.start()
