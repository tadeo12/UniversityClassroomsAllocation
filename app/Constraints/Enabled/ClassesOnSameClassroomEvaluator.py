from collections import defaultdict
from app.Constraints.BaseEvaluator import BaseEvaluator
from ConfigManager import ConfigManager
import streamlit as st


def groupByCommission(allocation):
        resourcesByCommission = defaultdict(list)
        for resource, commission in allocation.items():
            if commission is None:
                continue
            resourcesByCommission[commission].append(resource)
        return resourcesByCommission

class ClassesOnSameClassroomEvaluator(BaseEvaluator):
        def evaluate(self, allocation):
            resourcesByCommission = groupByCommission(allocation)
            penalty = 0
            for commission, resources in resourcesByCommission.items():
                classrooms = {r.classroom for r in resources}
                penalty += len(classrooms) - 1
            return penalty
       
        def maxHappyValue(self):
            #asume que las clases son de 4 horas
            if not st.session_state.entities:
                raise Exception("No se definieron las entidades")
            commissions = st.session_state.entities["commissions"]
            count = 0
            for commission in commissions:
                count += (commission.hours / 4) - 1
            return count 
            
        def maxValue(self):
            if not st.session_state.entities:
                raise Exception("No se definieron las entidades")
            commissions = st.session_state.entities["commissions"]
            numberOfClassrooms = len(st.session_state.entities["classrooms"])
            hoursPerResource = ConfigManager().getConfig()["hours_per_resource"]
            count = 0
            for commission in commissions:
                count += min(numberOfClassrooms, commission.hours / hoursPerResource ) - 1
            return count 
       
        
