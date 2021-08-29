from Task import Task
from Queue import Queue
from Parameter import para_test
from Parameter import para_fog1
from auxiliary import taskArrivePoisson

import random

class SimNoP:
    def __init__(self, para):
        self.para = para
        print(para)
        self.timer = 0
        self.generatedTask = 0
        self.Q = []
        self.W = [0 for _ in range(self.para.queueNum)]
        for i in range(self.para.queueNum):
            self.Q.append(Queue(i, self.para.delta, self.para.debug))
        self.A_set = [[] for _ in range(self.para.queueNum)]
        self.processCapability = []
        for i in range(self.para.queueNum):
            self.processCapability.append((self.para.E_aver[i]-self.para.energyStatic)/self.para.energyPerMCycle)
        self.acceptRate = []
        for i in range(self.para.queueNum):
            self.acceptRate.append(min(1, self.processCapability[i]/(self.para.arriveRate[i]*self.para.taskInfo['totalCycle']))*0.95)

    def start(self):
        while self.timer < self.para.maxTime and self.generatedTask < self.para.maxTask:
            self.arrive()
            self.decision()
            for i in range(self.para.queueNum):
                self.Q[i].statistics(self.timer)
            self.timer+=1
        if self.para.debug:
            for i in range(self.para.queueNum):
                print(self.W[i])
        self.show()

    def arrive(self):
        self.generatedTask, self.A_set = taskArrivePoisson(self.timer, self.generatedTask, self.Q, self.para)

    def show(self):
        print("-------------------- INFO:Simulation --------------------")
        print("NumOfQueue:%d, MaxTime:%d, MaxTask:%d" % (
                self.para.queueNum, self.para.maxTime, self.para.maxTask))
        print("Timer:%d, GeneratedTask:%d" % (self.timer, self.generatedTask))
        print("ArriveRate:", self.para.arriveRate)
        print("-------------------- INFO:Queue --------------------")
        # for i in range(self.para.queueNum):
            # self.Q[i].show()
        print(self.W)
        print(self.acceptRate)

    def decision(self):
        random.seed()
        N = self.para.queueNum
        # accept
        a_set = [[] for _ in range(N)] # accept set
        for i in range(N):
            for task in self.A_set[i]:
                if random.random() < self.acceptRate[i]:
                    a_set[i].append(task)
                else:
                    self.Q[i].totalBlockedWorkload += task.totalCycle
        for i in range(N):
            self.Q[i].accept(a_set[i])
        # process
        process = [0 for _ in range(N)]
        for i in range(N):
            if self.W[i] <= 3000: #self.Q[i].length >= self.para.B_max[i]:
                process[i] = min(self.para.B_max[i], self.Q[i].length)
                self.Q[i].serveByCycle(process[i], self.timer)
        # update
        for i in range(N):
            self.W[i] = max(0, self.W[i] + self.para.efunc[i](process[i]) - self.para.E_aver[i])

# sim = SimNoP(para_fog1)
# sim.start()
