class Task:
    def __init__(self, index, currentTime, size, totalCycle, offloadingTime, arriveQueue):
        self.size = size # This is the data size, not the workload
        self.arriveQueue = arriveQueue
        self.currentQueue = arriveQueue
        self.index = index
        self.arriveTime = currentTime
        self.totalCycle = totalCycle # This is the workload
        self.offloadingTime = offloadingTime
        self.receiveTime = currentTime + offloadingTime
        self.remainCycle = totalCycle
        # We have the following status
        # ARRIVE, ACCEPTED, BLOCKED, PROCESSING, SERVED
        self.status = 'ARRIVE'
    def show(self):
        print("Task Index:%d, Task Status:%s" % (self.index, self.status))


