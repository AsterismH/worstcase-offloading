# This module contains auxiliary functions
import numpy as np
import random
from Task import Task

from butools.map import *
from butools.dmap import *

def workloadOfSet(taskSet): # remain workload
    if len(taskSet) == 0:
        return 0
    else:
        if isinstance(taskSet[0], list):
            result = []
            for i in taskSet:
                result.append(workloadOfSet(i))
            return result
        else:
            totalWorkload = 0
            for i in taskSet:
                totalWorkload += i.remainCycle
            return totalWorkload
def totalWorkloadOfSet(task_list): # total workload
    if len(task_list) == 0:
        return 0
    else:
        if isinstance(task_list[0], list):
            ret = []
            for task in task_list:
                ret.append(totalWorkloadOfSet(task))
            return ret
        else:
            total_workload = 0
            for task in task_list:
                total_workload += task.totalCycle
            return total_workload
def indexAfterTime(time, queue):
    index = -1
    for i in range(len(queue)):
        if queue[i].arriveTime >= time:
            index = i
            break
    return index
def notInSet(task, queue):
    taskSet = set()
    for i in queue:
        for j in i:
            taskSet.add(j)
    if task in taskSet:
        return 0
    else:
        return 1
def takeArriveTime(task):
    #return task.arriveTime
    return task.index
def takeIndex(task):
    return task.index
def sumByCol(matrix):
    ret = np.array(matrix)
    return (np.sum(ret, axis=0)).tolist()
def sumCol(m, col):
    ret = 0
    row_num = len(m)
    for i in range(row_num):
        ret += m[i][col]
    return ret
def sumRow(m, row):
    return sum(m[row])
def pickFirstMTasks(task_list, max_workload):
    ret = []
    picked_workload = 0
    for task in task_list:
        if picked_workload + task.totalCycle <= max_workload:
            ret.append(task)
            picked_workload += task.totalCycle
        else:
            break
    return ret
def addtodict2(thedict, key_a, key_b, val):
    if key_a in thedict:
        thedict[key_a].update({key_b: val})
    else:
        thedict.update({key_a:{key_b: val}})

def taskArriveBurst(timer, generatedTask, Q, para):
    A_set = [[] for _ in range(para.queueNum)]
    if generatedTask == 0:
        generateArriveSeq(para.maxTime)
    # arrive_seq =
    for i in range(para.queueNum):
        newNum = round(np.random.poisson(para.arriveRate[i]*arrive_rate_coef[timer]))
        if newNum > para.maxArriveRate:
            newNum = para.maxArriveRate
        if newNum > 0:
            for j in range(int(newNum)):
                generatedTask+=1
                datasize = 1 # we do not use datasize in this simulation
                totalCycle = round((random.random()*(para.taskInfo['totalCycleMax']-para.taskInfo['totalCycleMin']) +
                                    para.taskInfo['totalCycleMin'])*10.0)/10.0
                tempTask = Task(generatedTask, timer, datasize, \
                        totalCycle, Q[i])
                A_set[i].append(tempTask)
    return generatedTask, A_set

arrive_rate_coef = None
def generateArriveSeq(max_time):
    random.seed()
    global arrive_rate_coef
    D_0, D_1 = RandomMAP(4, 1.0)
    arrive_rate_coef = SamplesFromMAP(D_0, D_1, max_time)
    # for i in range(N):
        # arrive_rate = arrive_rate_list[i]
        # D_0, D_1 = RandomDMAP(4, aver_inter_arrival)
        # inter_seq = SamplesFromDMAP(D_0, D_1, int(3*arrive_rate*max_time))
        # index = 0
        # for t in range(max_time):
            # num_task = 0
            # remain_time = arrive_rate*aver_inter_arrival
            # while remain_time >= inter_seq[index]:
                # remain_time -= inter_seq[index]
                # index += 1
                # num_task += 1
            # inter_seq[index] -= remain_time
            # arrive_seq[i].append(num_task)

def taskArrivePoisson(timer, generatedTask, Q, para):
    if para.bursty == 1:
        return taskArriveBurst(timer, generatedTask, Q, para)
    random.seed()
    A_set = [[] for _ in range(para.queueNum)]
    for i in range(para.queueNum):
        newNum = round(np.random.poisson(para.arriveRate[i]))
        if newNum > para.maxArriveRate:
            newNum = para.maxArriveRate
        if newNum > 0:
            for j in range(int(newNum)):
                generatedTask+=1
                datasize = 1 # we do not use datasize in this simulation
                """ we will use uniform distribution instead of normal distribution
                totalCycle = round(np.random.normal(para.taskInfo['totalCycle'],\
                                                    para.taskInfo['totalCycleVar'])*10.0)/10.0
                totalCycle = min(max(totalCycle, para.taskInfo['totalCycleMin']),\
                                    para.taskInfo['totalCycleMax'])
                """
                totalCycle = round((random.random()*(para.taskInfo['totalCycleMax']-para.taskInfo['totalCycleMin']) +
                                    para.taskInfo['totalCycleMin'])*10.0)/10.0
                offloadingTime = genOffloadingTime(para);
                tempTask = Task(generatedTask, timer, datasize, \
                        totalCycle, offloadingTime, Q[i])
                A_set[i].append(tempTask)
    return generatedTask, A_set

def genOffloadingTime(para):
    time = 0
    mu = para.offloadingTimeAver # mu = 20
    sigma = para.offloadingTimeVar # sigma = 5
    lb = para.offloadingTimeLb # 10
    ub = para.offloadingTimeUb # 30
    if para.offloadingTimeDist == 1: # fix
        time = para.offloadingTimeAver
    if para.offloadingTimeDist == 2: # normal
        time = round(np.random.normal(mu, sigma))
    if para.offloadingTimeDist == 3: # uniform
        time = round(random.random() * (ub - lb) + lb)
    if para.offloadingTimeDist == 4: # two points
        if random.random() >= 0.5:
            time = 30
        else:
            time = 10
    return time

def listDiff(li1, li2):
    assert len(li1) == len(li2)
    li = []
    for i in range(len(li1)):
        li.append(li1[i] - li2[i])
    return li

def listMaxDiff2D(li1, li2):
    assert len(li1) == len(li2)
    li = []
    for i in range(len(li1)):
        li.append(max(listDiff(li1[i], li2[i])))
    return max(li)


def throughput(self):
    throughput = 0
    for i in range(self.para.queueNum):
        throughput += self.para.gfunc[i](self.Q[i].throughput / self.timer)
    return throughput



