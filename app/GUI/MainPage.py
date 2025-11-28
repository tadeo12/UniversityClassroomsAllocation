import os
from streamlit_ace import st_ace
import streamlit as st
import json
from ConfigManager import ConfigManager
from app.Logic.ExecutionHandler import executionButtonHandler
from app.Logic.EntititiesInitializer import createEntitiesFromJson
from app.GUI.EntitiesDataInputInterface import entitiesDataInput
from app.GUI.PredefiniedAllocationInput import showPredefiniedAllocationInput
from app.GUI.Graphs import initializeGraphsPanel, updateProgress

def mainPage():
    loadSessionStateVariables()
    st.title("Generación de distribución de aulas")

    col1, col2 = st.columns([st.session_state.colWidth, 10 - st.session_state.colWidth])
    with col1:
        leftColumnContent()
    with col2:
        rigthColumnContent()


def loadSessionStateVariables():
    st.session_state.setdefault("colWidth", 7)
    st.session_state.setdefault("entities", loadEntities())
    st.session_state.setdefault("entitiesJsonText", json.dumps(loadEntitiesJson(), indent=4, ensure_ascii=False))


def loadEntities():
    entities = createEntitiesFromJson(loadEntitiesJson())
    st.session_state.entities = entities
    return entities

def loadEntitiesJson():
    inputDataFilePath = ConfigManager().getConfig()["input_data_file_path"]
    if os.path.exists(inputDataFilePath):
        with open(inputDataFilePath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def leftColumnContent():
    entitiesDataInput()


def rigthColumnContent():
    st.subheader("Distribución inicial")
    initialOptionSelector = st.radio(
        "selección de distribución inicial",
        ["Predefinida", "Aleatoria"],
        index=1,
        key="allocation_type"
    )

    if "finishedAlgorithm" not in st.session_state:
        st.session_state.finishedAlgorithm = False
    if "algorithmRunning" not in st.session_state:
        st.session_state.algorithmRunning = False
    if "colWidth" not in st.session_state:
        st.session_state.colWidth = 8

    if initialOptionSelector == "Predefinida":
        newWidth = 5
    elif  st.session_state.get("algorithmRunning", False) or st.session_state.get("finishedAlgorithm", False):
        newWidth = 2
    else:
        newWidth = 8

    if st.session_state.get("colWidth", None) != newWidth:
        st.session_state.colWidth = newWidth
        if not st.session_state.get("algorithmRunning", False):
            st.rerun()

    if initialOptionSelector == "Predefinida":
        showPredefiniedAllocationInput()

    overlayPlaceholder = st.empty()
    #progressPlaceholder = st.empty()

    def blockUserInteraction():
        overlayPlaceholder.markdown(
             """
             <style>
             .overlay {
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background: rgba(0,0,0,0.15);
                z-index: 9998;
             }
             .overlay-text {
                position: fixed
                top: 80px;       /* bajamos el texto (ajustá este valor si querés más espacio) */
                right: 20px;     /* lo pegamos a la derecha */
                color: black;
                font-size: 26px;
                font-weight: bold;
                z-index: 9999; 
             }
             </style>
             <div class="overlay"></div>
             <div class="overlay-text">🚀 Ejecutando algoritmo...</div>

             """,
             unsafe_allow_html=True,
        )

    if st.button("Ejecutar") and not st.session_state.algorithmRunning:
        st.session_state.algorithmRunning = True
        st.session_state.colWidth = 2  
        st.rerun()  

    if st.session_state.algorithmRunning:
        
        initializeGraphsPanel()
        blockUserInteraction()
        executionButtonHandler(updateProgress)
        st.session_state.progressBar.empty()
        overlayPlaceholder.empty()
        st.success("El algoritmo finalizó")
        st.session_state.algorithmRunning = False
        st.session_state.finishedAlgorith = True
        #st.rerun()


