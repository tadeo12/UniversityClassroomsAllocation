from collections import Counter
from app.Models.Commission import Commission
from app.Models.Resource import Resource
from ConfigManager import ConfigManager



class InvalidAllocationError(Exception):
    """Excepción personalizada para asignaciones inválidas."""
    pass

def validate(Allocation: dict) -> None:
    if not isinstance(Allocation, dict):
        raise InvalidAllocationError("Allocation debe ser un diccionario.")

    commission_count = Counter()

    for key, value in Allocation.items():
        if not isinstance(key, Resource):
            raise InvalidAllocationError(f"La clave {key} no es una instancia de Resource.")
        if not isinstance(value, Commission):
            raise InvalidAllocationError(f"El valor {value} no es una instancia de Commission.")
        
        commission_count[value] += 1

    enoughtHoursValidation(commission_count)

def enoughtHoursValidation(commission_count):
    hoursPerResource = ConfigManager().getConfig()["hours_per_resource"]
    for commission, count in commission_count.items():
        if count * hoursPerResource != commission.hours:
            raise InvalidAllocationError(
                f"La comisión {commission} está asignada a {count} recursos, "
                f"pero requiere exactamente {commission.hours / hoursPerResource}."
            )

