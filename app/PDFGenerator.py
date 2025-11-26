import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import timedelta, datetime
from ConfigManager import ConfigManager
from app.GUI.Graphs import generateFiguresForPdf
import streamlit as st


styles = getSampleStyleSheet()

def groupByClassroom(allocation):
    grouped = {}
    for resource, commission in allocation.items():
        classroom = resource.classroom.name
        if classroom not in grouped:
            grouped[classroom] = {}
        grouped[classroom][resource] = commission
    return grouped

def get_time_config():
    """Obtiene las configuraciones de horario desde ConfigManager."""
    config = ConfigManager().getConfig()
    start_hour = float(config.get("start_hour", 8))  # Por defecto 8
    hours_per_resource = float(config.get("hours_per_resource", 1))  # Por defecto 1h
    return start_hour, hours_per_resource


def format_hour(hour_float):
    """Convierte una hora decimal (ej: 8.5) a formato hh:mm."""
    base_time = datetime(2020, 1, 1, 0, 0)
    delta = timedelta(hours=hour_float)
    return (base_time + delta).strftime("%H:%M")


def get_real_hour(hour_index):
    """
    Convierte un índice horario (ej: 0, 1, 2, ...) en una hora real según la configuración.
    Retorna una tupla (hora_inicio, hora_fin).
    """
    start_hour, hours_per_resource = get_time_config()
    real_start = start_hour + hour_index * hours_per_resource
    real_end = real_start + hours_per_resource
    return real_start, real_end



def loadClassroomScheduleData(allocation):
    cellStyle = styles["BodyText"]
    cellStyle.wordWrap = 'CJK'
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

    start_hour, hours_per_resource = get_time_config()

    used_hour_indices = sorted(set(resource.hour for resource in allocation))
    schedule = {}

    for idx in used_hour_indices:
        real_hour, _ = get_real_hour(idx)
        for day in range(5):
            schedule[(real_hour, day)] = []

    # Rellenar schedule con info, incluyendo recursos existentes sin comision
    for resource, commission in allocation.items():
        day = resource.day
        real_start, real_end = get_real_hour(resource.hour)
        start_str = format_hour(real_start)
        end_str = format_hour(real_end)

        if commission is not None:
            info = f"{commission.name} - {commission.subject.name} - {commission.teacher.name} ({start_str}-{end_str})"
        else:
            # Marcador para recurso existente pero sin asignar
            info = ""

        # Asegurarse de que la clave exista (por seguridad)
        key = (real_start, day)
        if key not in schedule:
            schedule[key] = []
        schedule[key].append(info)

    # Construir la tabla a partir de schedule
    data = [["Hora"] + days]
    real_hours_sorted = sorted(set(h for (h, _) in schedule))

    for hour in real_hours_sorted:
        hour_str = format_hour(hour)
        row = [Paragraph(f"{hour_str}", cellStyle)]
        for day in range(5):
            entries = schedule.get((hour, day), [])
            content = "<br/>".join(entries)
            row.append(Paragraph(content, cellStyle))
        data.append(row)

    return data


def loadData(allocation):
    cellStyle = styles["BodyText"]
    cellStyle.wordWrap = 'CJK'

    data = [["Materia", "Profesor", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]]
    table = {}

    # 1) Acumular horarios crudos
    for resource, commission in allocation.items():
        if commission is None:
            continue

        subject = commission.subject.name
        teacher = commission.teacher.name
        day = resource.day
        classroom = resource.classroom.name
        key = (commission.name, subject, teacher)

        if key not in table:
            table[key] = {0: [], 1: [], 2: [], 3: [], 4: []}

        table[key][day].append({
            "slot": resource.hour,
            "classroom": classroom
        })

    # 2) Construcción de las filas ordenadas y mergeadas
    for (commission, subject, teacher), schedules in table.items():
        row = [Paragraph(subject, cellStyle), Paragraph(teacher, cellStyle)]

        for day in range(5):
            blocks = schedules[day]

            if not blocks:
                row.append(Paragraph("", cellStyle))
                continue

            # ORDENAR POR slot
            blocks.sort(key=lambda x: x["slot"])

            # 3) MERGE de bloques contiguos
            merged = []
            current = {
                "start": blocks[0]["slot"],
                "end": blocks[0]["slot"] + 1,
                "classroom": blocks[0]["classroom"]
            }

            for b in blocks[1:]:
                if (
                    b["slot"] == current["end"] and
                    b["classroom"] == current["classroom"]
                ):
                    # extender bloque
                    current["end"] += 1
                else:
                    merged.append(current)
                    current = {
                        "start": b["slot"],
                        "end": b["slot"] + 1,
                        "classroom": b["classroom"]
                    }

            merged.append(current)

            # 4) Convertir bloques a texto
            texts = []
            for m in merged:
                start_real, _ = get_real_hour(m["start"])
                end_real, _ = get_real_hour(m["end"])
                start_str = format_hour(start_real)
                end_str = format_hour(end_real)

                texts.append(f"{start_str}-{end_str} hs<br/>{m['classroom']}")

            # Juntar
            final_text = "<br/><br/>".join(texts)
            row.append(Paragraph(final_text, cellStyle))

        data.append(row)

    return data

def generateClassroomTable(allocation, pageWidth):
    colWidths = [pageWidth * 0.1] + [pageWidth * 0.18] * 5  # Hora + 5 días
    data = loadClassroomScheduleData(allocation)
    table = Table(data, colWidths)

    existing_slots = set()
    for resource, commission in allocation.items():
        real_start, _ = get_real_hour(resource.hour)
        existing_slots.add((real_start, resource.day))

    styleTable = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ])

    num_rows = len(data)
    for row_idx in range(1, num_rows):
        hour_str = data[row_idx][0].text
        real_hour = float(hour_str.split(":")[0]) + float(hour_str.split(":")[1]) / 60

        for col_idx in range(1, 6):  # solo días (Lunes a Viernes)
            day = col_idx - 1

            if (real_hour, day) in existing_slots:
                # Existe recurso → asignado o disponible → color A
                styleTable.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.lightcyan)
            else:
                # NO existe recurso → mostrar como celda inexistente → color B
                styleTable.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.whitesmoke)
    table.setStyle(styleTable)
    return table

def generateTable(allocation, pageWidth):
    colWidths = [pageWidth * 0.2, pageWidth * 0.2] + [pageWidth * 0.12] * 5

    data = loadData(allocation)

    table = Table(data, colWidths)
    styleTable= TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),         # Fondo de la cabecera
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),    # Color del texto de la cabecera
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),                # Centrar todo el texto
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),               # Centrar verticalmente
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),      # Negrita en la cabecera
        ('FONTSIZE', (0, 0), (-1, 0), 10),                    # Tamaño de letra de la cabecera
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),                # Espaciado de la cabecera
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),       # Fondo de las celdas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),        # Bordes de las celdas
    ])
    table.setStyle(styleTable)

    return table

def createPdf(allocation, fileName="horarios_clase.pdf"):
    doc = SimpleDocTemplate(fileName, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []

    pageWidth = A4[0] - 40

    elements.append(Paragraph("Distribución de aulas", styles["h1"]))
    table = generateTable(allocation, pageWidth)
    elements.append(table)

    grouped_alloc = groupByClassroom(allocation)
    for classroom, alloc in grouped_alloc.items():
        elements.append(Paragraph(f"Aula: {classroom}", styles["Heading2"]))
        table = generateClassroomTable(alloc, pageWidth)
        elements.append(table)
        elements.append(Paragraph("<br/><br/>", styles["BodyText"]))

    config = ConfigManager().getConfig()
    elements.append(Paragraph("Información de ejecución del algoritmo", styles["h1"]))
    elements.append(Paragraph("Configuraciones:", styles["h2"]))
    for key, value in config.items():
        elements.append(Paragraph(f"<b>{key}</b>: {value}", styles["BodyText"]))
        elements.append(Spacer(1, 20))

    # Gráficos
    if "statsHistory" in st.session_state and st.session_state.statsHistory:
        elements.append(Paragraph("Estadísticas del algoritmo", styles["h2"]))
        figures = generateFiguresForPdf(st.session_state.statsHistory)
        imgs = [Image(buf, width=250, height=180) for buf in figures]
        rows = [imgs[i:i+2] for i in range(0, len(imgs), 2)]
        table = Table(rows, colWidths=[260, 260])
        table.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ]))
        elements.append(table)

    elements.append(Paragraph("Asignación (JSON copiable)", styles["h1"]))

    clean_alloc = {
        f"({key.day}, {key.hour}, '{key.classroom.name}')": value.name
        for key, value in allocation.items()
        if value not in (None, -1)
    }

    json_str = json.dumps(clean_alloc, indent=4, ensure_ascii=False)

    for line in json_str.splitlines():
        elements.append(Paragraph(line.replace(" ", "&nbsp;"), styles["Code"]))

    # Evaluación
    if "evaluation" in st.session_state and st.session_state.evaluation:
        elements.append(Paragraph("Evaluación de restricciones", styles["h1"]))
        eval_json = json.dumps(st.session_state.evaluation, indent=4, ensure_ascii=False)
        for line in eval_json.splitlines():
            elements.append(Paragraph(line.replace(" ", "&nbsp;"), styles["Code"]))

    doc.build(elements)
    print(f"PDF generado con éxito en: {fileName}")
