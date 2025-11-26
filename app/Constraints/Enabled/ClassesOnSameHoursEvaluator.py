from collections import defaultdict
from ConfigManager import ConfigManager
from app.Constraints.BaseEvaluator import BaseEvaluator
import streamlit as st

def groupByCommissionAndDay(allocation):
        resourcesByDayAndCommission = defaultdict(lambda: defaultdict(list))
        for resource, commission in allocation.items():
            if commission is None:
                continue
            resourcesByDayAndCommission[commission][resource.day].append(resource)
        return resourcesByDayAndCommission



class ClassesOnSameHoursEvaluator(BaseEvaluator):
    #En vez de tener el mismo horario exacto, considero que dos 
    #clases tiene el mismo horario si un horario es subconjunto de otro.
    #En casos donde haya mas de una clase por dia, la penalizacion puede ser baja o cero,
    #y no reflejar la simplicidad que se busca con esta restriccion. sin embargo
    #considero que en dichos casos pesará mas la restriccion de una clase por dia

    def evaluate(self, allocation):
        resourcesByCommissionsAndDay = groupByCommissionAndDay(allocation)
        penalty = 0
        for commission, resourcesByDay in resourcesByCommissionsAndDay.items():
            hoursByDay = {}
            for day, resources in resourcesByDay.items():
                hours = {r.hour for r in resources}
                hoursByDay[day] = hours

            for day1, hours1 in hoursByDay.items():
                for day2, hours2 in hoursByDay.items():
                    if day1 >= day2:
                        continue
                    if not (hours1.issubset(hours2) or hours2.issubset(hours1)):
                        penalty += 1

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
        
        ## TODO analizar peor caso, deje como cota superior comisiones * dias de la semana
        daysPerWeek = ConfigManager().getConfig()["days_per_week"]
        numCommissions = len(st.session_state.entities["commissions"])
        return numCommissions * daysPerWeek
    