import json
from typing import List
import random
from app.Models.Commission import Commission
from app.Models.Resource import Resource
from ConfigManager import ConfigManager

def generateRandomInitialAllocation(commissions: List[Commission], resources: List[Resource]):
    allocation = {}
    available_resources = resources.copy()  # Hacemos una copia para gestionar los recursos disponibles
    hoursPerResource = ConfigManager().getConfig()["hours_per_resource"]
    for commission in commissions:
        required_blocks = int(commission.hours / hoursPerResource)
        for _ in range(required_blocks):
            if not available_resources:
                raise ValueError("No hay suficientes recursos disponibles para asignar las comisiones.")
            
            selected_resource = random.choice(available_resources)
            available_resources.remove(selected_resource)
            allocation[selected_resource] = commission


    for r in available_resources:
        allocation[r] = None


    return allocation