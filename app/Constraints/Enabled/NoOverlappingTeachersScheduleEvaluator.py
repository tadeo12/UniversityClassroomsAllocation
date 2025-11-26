from collections import defaultdict
from app.Constraints.BaseEvaluator import BaseEvaluator


def groupByDayHourAndTeacher(allocation):
    resourcesByDayHourAndTeacher = defaultdict(list)
    for resource, commission in allocation.items():
        if commission is None:
            continue
        resourcesByDayHourAndTeacher[(resource.day,resource.hour,commission.teacher)].append(resource)
    return resourcesByDayHourAndTeacher

class NoOverlappingTeachersScheduleEvaluator(BaseEvaluator):

    def evaluate(self, allocation):
        resourcesByDayHourAndTeacher= groupByDayHourAndTeacher(allocation)
        penalty = 0
        for resources in resourcesByDayHourAndTeacher.values():
            if len(resources)>1:
                for i in range(len(resources)):
                    for j in range(i+1,len(resources)):
                        if resources[i].classroom != resources[j].classroom:
                            penalty+= 1
        return penalty