from app.Constraints.BaseEvaluator import BaseEvaluator
from ConfigManager import ConfigManager
import streamlit as st


class EnoughCapacityEvaluator(BaseEvaluator):
    def evaluate(self, allocation):
        penalty = 0
        for resource, commission in allocation.items():
            if commission is None:
                continue
            penalty += max(0, commission.students - resource.classroom.capacity)
        return penalty
    
    def maxValue(self):
        if not st.session_state.entities:
            raise Exception("No se definieron las entidades")
        
        if not st.session_state.entities["classrooms"][0]:
            raise Exception("No se definio ninguna aula")

        minCapacity =  st.session_state.entities["classrooms"][0].capacity
        for classroom in st.session_state.entities["classrooms"]:
            if classroom.capacity < minCapacity:
                minCapacity = classroom.capacity

        hoursPerResource = ConfigManager().getConfig()["hours_per_resource"]
        maxValue = 0
        for commision in st.session_state.entities["commissions"]:
            maxValue += max(0, commision.students - minCapacity) * (commision.hours/ hoursPerResource)


        return maxValue
    
    def maxHappyValue(self):
        return self.maxValue()