import streamlit as st
from app.Logic.AllocationValidation import validate
from app.Logic.RandomInitialAllocationGenerator import generateRandomInitialAllocation
from app.Logic.SimulatedAnnealing import simulatedAnnealing
from app.Logic.Evaluator import evaluate


def executionButtonHandler(progressCallback = None):
    commissions = st.session_state.entities["commissions"]
    resources = st.session_state.entities["resources"]
    print('num de recursos: ', len(resources))
    print('num de comisiones: ', len(commissions))
    if st.session_state.allocation_type == "Aleatoria":
        initialAllocation = generateRandomInitialAllocation(commissions, resources)
    else:  # "Predefinida"
        if "initialAllocation" not in st.session_state or st.session_state.initialAllocation is None:
            st.error("Debe cargar una asignación predefinida antes de ejecutar el algoritmo.")
            return
        validate(st.session_state.initialAllocation)

        completeAllocation = dict(st.session_state.initialAllocation)
        for r in resources:
            if r not in completeAllocation:
                completeAllocation[r] = None
        initialAllocation = completeAllocation

    print(str(evaluate(initialAllocation)))    

    st.session_state["finalAllocation"] = simulatedAnnealing(initialAllocation, progressCallback)
    st.session_state["evaluation"] = evaluate(st.session_state["finalAllocation"])




    