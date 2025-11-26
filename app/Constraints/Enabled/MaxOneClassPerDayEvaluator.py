from app.Constraints.BaseEvaluator import BaseEvaluator
from collections import defaultdict

def groupByDayAndCommission(allocation):
        resourcesByDayAndCommission = defaultdict(lambda: defaultdict(list))
        for resource, commission in allocation.items():
            if commission is None:
                continue
            resourcesByDayAndCommission[resource.day][commission].append(resource)
        return resourcesByDayAndCommission

def countClasses(sortedResources):
    classes = 1
    for i in range(1,len(sortedResources)):
        if sortedResources[i].hour != sortedResources[i-1].hour + 1 or sortedResources[i].classroom.name != sortedResources[i-1].classroom.name:
            classes += 1
    return classes

class MaxOneClassPerDayEvaluator(BaseEvaluator): 
    def evaluate(self,allocation):
        resourcesByDayAndCommission = groupByDayAndCommission(allocation) 
        penalty = 0 
        for day, commissions in resourcesByDayAndCommission.items(): 
            for commission, resources in commissions.items(): 
                sortedResources = sorted(resources, key=lambda x: x.hour) 
                penalty += countClasses(sortedResources) - 1
        return penalty
    
    
