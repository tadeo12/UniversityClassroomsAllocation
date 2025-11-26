from collections import defaultdict
from app.Constraints.BaseEvaluator import BaseEvaluator


def groupByDayAndHour(allocation):
    resourcesByCommission = defaultdict(list)
    for resource, commission in allocation.items():
        if commission is None:
            continue
        resourcesByCommission[(resource.day,resource.hour)].append(commission)
    return resourcesByCommission

def countGroupsInBothCommissions(commissionA, commissionB):
    return len(set(commissionA.groups) & set(commissionB.groups))

class NoGroupWithOverlappingScheduleEvaluator(BaseEvaluator):
    def evaluate(self, allocation):
        penalty = 0
        commissionsWithClassesAtTheSameTime = groupByDayAndHour(allocation)
        for (day,hour), commissions in commissionsWithClassesAtTheSameTime.items():
            for i in range(len(commissions)):
                for j in range(i+1,len(commissions)):
                    penalty += countGroupsInBothCommissions(commissions[i],commissions[j])
        return penalty