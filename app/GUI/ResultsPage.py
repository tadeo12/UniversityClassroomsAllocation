import streamlit as st

from app.PDFGenerator import createPdf

def resultsPage():
    st.title("Resultados de la Ejecución")
    if "finalAllocation" in st.session_state and "evaluation" in st.session_state:
        st.subheader("Final Allocation")


        finalAllocation = {key.id: value for key, value in st.session_state.finalAllocation.items() if value != -1}
        if st.radio("Mostrar asignación detallada", ("Sí", "No")) == "Sí":
            detailedFinalAllocation = {str(key): str(value) for key, value in st.session_state.finalAllocation.items()}
            st.json(detailedFinalAllocation)
        else:
            finalAllocation = {
                key: value for key, value in st.session_state.finalAllocation.items() if value != -1
            }
            formatted_allocation = {
                f"({key.day}, {key.hour}, '{key.classroom.name}')": value.name
                for key, value in finalAllocation.items()
                if value not in (None, -1)
            }
            st.json(formatted_allocation)

        
        st.subheader("Evaluation")
        st.json(st.session_state.evaluation)


        createPdf(st.session_state.finalAllocation)
        with open("horarios_clase.pdf", "rb") as f:
            pdf_data = f.read()
        
        st.download_button(label="Descargar PDF",data=pdf_data,file_name="horarios_clase.pdf",mime="aplication/pdf")
                    
    else:
        st.write("No hay resultados disponibles. Por favor, ejecute el algoritmo primero.")