from auxiliary import *
from Parameter import para_test

generatedTask = 0
arrive_seq = []
for t in range(100):
    print(t)
    generatedTask, A_set = taskArriveBurst(t, generatedTask, [None for _ in range(4)], para_test)
    arrive_seq.append(len(A_set[0]))

print(arrive_seq)
print(sum(arrive_seq)/100)

