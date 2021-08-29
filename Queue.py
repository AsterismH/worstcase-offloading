from Task import Task
from auxiliary import takeArriveTime
from auxiliary import workloadOfSet
import math

class Queue:
    def __init__(self, index, delta, debug, sort = 0):
        self.debug = debug
        self.delta = delta # transmission time between different nodes
        self.taskArray = []
        self.index = index
        self.length = 0 # NOTE: the length is not the actual workload and is maintained manually
        self.currentTask = None
        self.throughput = 0
        self.dropped = 0
        self.accepted = 0
        self.totalDelay = 0
        self.worstDelay = 0
        self.L_max = 50
        self.totalBlockedWorkload = 0
        self.sort = sort
        #we can't simply add rtt for each transmitted task, because the rtt among
        #different nodes are different. we must delay fix time(max rtt) to guarantee no collision
        # In practive, instead of always waiting for the maximum transmission time, we can process task as long as
        # they are ready. The actual serving time depend on the actual transmission time and cpu activity level, as
        # the maximum amout of workload that can be served during one slot is bounded. However, this time is always
        # before the maximum transmission time, so the average response time is reduced.
        self.statLength = []
        self.statAverDrop = []
        self.statAverDelay = []
        self.statWorstDelay = []
        self.statAverBlocked = []
        self.statTotalDelay = []
        self.statTotalThroughput = []
    def checkForLmax(self, timer):
        for task in self.taskArray:
            tmpDelay = timer - task.arriveTime + \
                self.delta[self.index][task.arriveQueue.index] + 1
            if tmpDelay > self.L_max:
                task.arriveQueue.dropped += task.totalCycle
                self.length -= task.remainCycle
                self.taskArray.remove(task)
        if len(self.taskArray) > 0:
            self.currentTask = self.taskArray[0]
        else:
            self.currentTask = None
    def _rountineForServedTask(self, task, timer):
        task.remainCycle = 0
        task.status = 'SERVED'
        if self.debug:
            print("TaskServe: Task %d on Queue %d" % (task.index, self.index))
        task.arriveQueue.throughput += task.totalCycle
        tmpDelay = timer - task.arriveTime + \
            self.delta[self.index][task.arriveQueue.index] + 1
        if tmpDelay > self.L_max:
            task.arriveQueue.dropped += task.totalCycle
        else:
            if tmpDelay > task.arriveQueue.worstDelay:
                task.arriveQueue.worstDelay = tmpDelay
            task.arriveQueue.totalDelay += tmpDelay*task.totalCycle
        self.taskArray.remove(task)
    def _serve(self, serveCycle, timer): # this function only process current HOL task; it does not pick next task when HOL is served;
        assert serveCycle > 0
        assert self.currentTask != None
        assert self.currentTask.remainCycle > 0
        assert serveCycle <= self.currentTask.remainCycle
        if serveCycle < self.currentTask.remainCycle:
            self.currentTask.remainCycle -= serveCycle
            self.length -= serveCycle
        else:
            self.length -= serveCycle
            self._rountineForServedTask(self.currentTask, timer)
    def serveByTaskNum(self, num, timer):
        # self.checkForLmax(timer)
        # return the actual served workload
        if num == 0:
            return 0
        workload = 0
        while len(self.taskArray) > 0 and num > 0:
            num -= 1
            self.length -= self.currentTask.remainCycle
            workload += self.currentTask.remainCycle
            self._rountineForServedTask(self.currentTask, timer)
            if len(self.taskArray) > 0:
                self.currentTask = self.taskArray[0]
            else:
                self.currentTask = None
        return workload
    def serveByTaskList(self, taskList, timer):
        self.checkForLmax(timer)
        if taskList == []:
            return
        # first serve current HOL task
        assert self.currentTask != None
        assert self.currentTask.remainCycle > 0
        if len(self.taskArray) > 1:
            assert math.isclose(self.length, self.currentTask.remainCycle + workloadOfSet(self.taskArray[1:]), abs_tol=0.01)
        if len(self.taskArray) == 1:
            assert math.isclose(self.length, self.currentTask.remainCycle, abs_tol=0.01)
        # serve out all tasks in taskList
        self.length -= workloadOfSet(taskList)
        for i in taskList:
            self._rountineForServedTask(i, timer)
        self.pickTask()
    def serveByCycle(self, totalCycle, timer):
        self.checkForLmax(timer)
        if totalCycle == 0:
            return
        if math.isclose(self.length, 0, abs_tol=0.01):
            return
        assert self.currentTask != None
        if len(self.taskArray) > 1:
            assert math.isclose(self.length, self.currentTask.remainCycle + workloadOfSet(self.taskArray[1:]), abs_tol=0.01)
        if len(self.taskArray) == 1:
            assert math.isclose(self.length, self.currentTask.remainCycle, abs_tol=0.01)
        if totalCycle < self.currentTask.remainCycle:
            self._serve(totalCycle, timer)
        else:
            while totalCycle >= self.currentTask.remainCycle:
                totalCycle -= self.currentTask.remainCycle
                self.length -= self.currentTask.remainCycle
                self._rountineForServedTask(self.currentTask, timer)
                if len(self.taskArray) > 0:
                    self.currentTask = self.taskArray[0]
                else:
                    self.currentTask = None
                    return
            assert totalCycle < self.currentTask.remainCycle
            if totalCycle > 0:
                self._serve(totalCycle, timer)
    def virtualDropHOL(self):
        if len(self.taskArray) == 0:
            return
        task = self.currentTask
        self.taskArray.remove(task)
        self.length -= task.remainCycle
        if len(self.taskArray) > 0:
            self.currentTask = self.taskArray[0]
        else:
            self.currentTask = None
        return task
    def dropHOL(self):
        if len(self.taskArray) == 0:
            return
        task = self.currentTask
        self.taskArray.remove(task)
        self.length -= task.remainCycle
        task.arriveQueue.dropped += task.totalCycle
        if len(self.taskArray) > 0:
            self.currentTask = self.taskArray[0]
        else:
            self.currentTask = None
        return task
    def setHOL(self, task):
        assert task in self.taskArray
        self.taskArray.remove(task)
        self.taskArray.insert(0, task)
        self.currentTask = task
    def drop(self, taskList):
        for i in taskList:
            self.taskArray.remove(i)
            self.length -= i.remainCycle
            i.arriveQueue.dropped += i.totalCycle
        if self.debug:
            print("Drop tasks in Queue %d:" % (self.index), end='')
            for i in taskList:
                print(" %d," % (i.index), end='')
            print("")
        self.sortQueue()
    def sortQueue(self):
        if len(self.taskArray) > 0:
            assert self.currentTask != None
        # Sort tasks of this queue according to the arrive time
        if len(self.taskArray) > 1:
            if self.sort == 0:
                self.taskArray[1:].sort(key=takeArriveTime)
            else:
                self.taskArray.sort(key=takeArriveTime)
                self.pickTask()
    def accept(self, taskList):
        if len(self.taskArray) > 1:
            assert math.isclose(self.length, self.currentTask.remainCycle + workloadOfSet(self.taskArray[1:]), abs_tol=0.01)
        if len(self.taskArray) == 1:
            assert math.isclose(self.length, self.currentTask.remainCycle, abs_tol=0.01)
        self.taskArray.extend(taskList)
        for task in taskList:
            task.currentQueue = self
        self.accepted += workloadOfSet(taskList)
        self.length += workloadOfSet(taskList)
        if self.currentTask == None and len(self.taskArray) > 0:
            self.currentTask = self.taskArray[0]
        self.sortQueue()
    def receive(self, task):
        if len(self.taskArray) > 1:
            assert math.isclose(self.length, self.currentTask.remainCycle + workloadOfSet(self.taskArray[1:]), abs_tol=0.01)
        if len(self.taskArray) == 1:
            assert math.isclose(self.length, self.currentTask.remainCycle, abs_tol=0.01)
        self.taskArray.append(task)
        task.currentQueue = self
        self.length += task.remainCycle
        if self.currentTask == None:
            self.currentTask = self.taskArray[0]
        self.sortQueue()
        if self.debug:
            print("Queue %d receive task %d with load %f, total length is %f" % (self.index, task.index, task.totalCycle, self.length))
    def receiveByTaskList(self, taskList):
        for task in taskList:
            self.receive(task)
    def offload(self, task):
        self.taskArray.remove(task)
        self.length -= task.remainCycle
        if len(self.taskArray) > 0:
            self.currentTask = self.taskArray[0]
        else:
            self.currentTask = None
    def offloadHOL(self):
        # ! this function will offload HOL
        assert len(self.taskArray) > 0
        task = self.taskArray[0]
        self.taskArray.remove(task)
        self.length -= task.remainCycle
        if len(self.taskArray) > 0:
            self.currentTask = self.taskArray[0]
        else:
            self.currentTask = None
        return task
    def offloadByCycle(self, cycle):
        if len(self.taskArray) > 1:
            assert math.isclose(self.length, self.currentTask.remainCycle + workloadOfSet(self.taskArray[1:]), abs_tol=0.01)
        if len(self.taskArray) == 1:
            assert math.isclose(self.length, self.currentTask.remainCycle, abs_tol=0.01)
        taskList = []
        if cycle == 0:
            return []
        while len(self.taskArray) > 1:
            if cycle > self.taskArray[-1].remainCycle:
                task = self.taskArray[-1]
                taskList.append(task)
                self.taskArray.remove(task)
                self.length -= task.remainCycle
                cycle -= task.remainCycle
            else:
                break
        return taskList
    def pickTask(self):
        if len(self.taskArray) == 0:
            self.currentTask = None
        else:
            self.currentTask = self.taskArray[0]
    def statistics(self, currentTime):
        self.statLength.append(self.length)
        self.statAverDrop.append(self.dropped/(currentTime+1))
        self.statAverDelay.append(self.totalDelay/(1 if self.throughput==0 else self.throughput))
        self.statWorstDelay.append(self.worstDelay)
        self.statAverBlocked.append(self.totalBlockedWorkload/(currentTime+1))
        self.statTotalDelay.append(self.totalDelay)
        self.statTotalThroughput.append(self.throughput)
    def show(self):
        print("Queue Index:%d, Queue Length:%d, Queue Throughput:%d, Queue Dropped:%d, Worst Delay:%d, Average Delay:%f, BlockedWorkload:%f"\
              % (self.index, self.length, self.throughput, self.dropped, \
                 self.worstDelay, self.totalDelay/(1 if self.throughput==0 else self.throughput), self.totalBlockedWorkload))
