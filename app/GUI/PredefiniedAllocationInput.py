import streamlit as st
from streamlit_ace import st_ace
import json
import pandas as pd
import ast

def showPredefiniedAllocationInput():
    inputOption = st.radio("¿cómo desea ingresar la distribución inicial?", ["Escribir Json", "Arrastrar archivo"], horizontal=True)
    if inputOption == "Escribir Json":
        AllocationJsonInput()
    else:
        AllocationFileInput()

def AllocationFileInput():
    st.subheader("Arrastre un archivo con la distribución predefinida")
    uploaded_file = st.file_uploader("Seleccione un archivo JSON", type=["json"])
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
        except json.JSONDecodeError:
            st.error("El archivo no contiene un JSON válido.")
            return
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            return

        try:
            generateInitialAllocationFromJson(data)
            st.success("Archivo cargado correctamente")
        except Exception as e:
            st.error(f"Error procesando la distribución: {e}")
            return

        if "show_allocation" not in st.session_state:
            st.session_state.show_allocation = False

        if st.button("Mostrar distribución cargada"):
            st.session_state.show_allocation = not st.session_state.show_allocation


        if st.session_state.get("show_allocation"):
            allocation_display = {
                str(resource): str(commission) 
                for resource, commission in st.session_state.initialAllocation.items()
            }
            st.json(allocation_display)


def AllocationJsonInput():
    st.subheader("Ingrese JSON para la distribución predefinida")
    predef_json = st_ace("{}", language='json', height=300)
    if st.button("Guardar distribución"):
        try:
            data = json.loads(predef_json)
        except json.JSONDecodeError:
            st.error("JSON inválido")
            return

        try:
            generateInitialAllocationFromJson(data)
            st.success("Distribución guardada")
        except Exception as e:
            st.error(f"Error procesando la distribución: {e}")

def generateInitialAllocationFromJson(data):
    allocation = {}
    resources = st.session_state.entities["resources"]
    commissions = st.session_state.entities["commissions"]
    resource_lookup = {(r.day, r.hour, r.classroom.name): r for r in resources}
    commission_lookup = {c.name: c for c in commissions}

    for keyString, commission_name in data.items():
        try:
            key = ast.literal_eval(keyString)
        except Exception:
            raise ValueError(f"Clave inválida (no se pudo interpretar): {keyString}")

        if not isinstance(key, tuple) or len(key) != 3:
            raise ValueError(f"Clave inválida (debe ser una tupla de 3 elementos): {keyString}")

        day, hour, classroom_name = key
        resource = resource_lookup.get((day, hour, classroom_name))
        if resource is None:
            raise ValueError(f"No se encontró el recurso para la clave: {key}")

        commission = commission_lookup.get(commission_name)
        if commission is None:
            raise ValueError(f"No se encontró la comisión: {commission_name}")

        allocation[resource] = commission

    st.session_state.initialAllocation = allocation
