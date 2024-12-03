from tkinter import filedialog

from Processor import MainProcessing
from . import BarsInfo
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Image
from io import BytesIO
import matplotlib.pyplot as plt
from .Epura import draw_epur_n_sigma, draw_epur_u

pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='RussianText', fontName='DejaVuSans', fontSize=12))
styles.add(ParagraphStyle(name='CenteredTitle', fontName='DejaVuSans', fontSize=14, alignment=TA_CENTER))
styles.add(ParagraphStyle(name='CenteredTitle1', fontName='DejaVuSans', fontSize=12, alignment=TA_CENTER))
styles.add(ParagraphStyle(name='CenteredTitle2', fontName='DejaVuSans', fontSize=10, alignment=TA_CENTER))


def get_data_for_file(data):
    nodes = data["nodes"]
    conc_loads = {int(item["node_num"]): item["conc_load"] for item in data["conc_loads"]}
    nodes_table = [["Узел", "S, м", "F, Па"]]
    for i, value in enumerate(nodes, start=1):
        nodes_table.append([i, value, conc_loads.get(i, "-")])

    bars = sorted(data["bars"], key=lambda x: x["first_node"])
    dist_loads = {int(item["bar_num"]): item["dist_load"] for item in data["dist_loads"]}
    bars_table = [["Узел 1", "Узел 2", "A", "E", "[σ], Па", "F, Па"]]
    for i, bar in enumerate(bars, start=1):
        bars_table.append([
            bar["first_node"],
            bar["second_node"],
            bar["a"],
            bar["e"],
            bar["max_load"],
            dist_loads.get(i, "-")
        ])

    table_data = BarsInfo.get_all(data, 10)

    return nodes_table, bars_table, table_data


def create_file(data, sheme):
    filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

    if filepath:
        nt, bt, td = get_data_for_file(data)
        x_coords, y_coords_nx, y_coords_sigma = MainProcessing.section_calc_for_nx_epur(data)

        pp = Paragraph("&nbsp;", styles["CenteredTitle"])
        doc = SimpleDocTemplate(filepath, pagesize=letter)

        elements = []

        main_title = Paragraph("Очет о расчете прямолинейной стержневой конструкции по допускаемым напряжениям", styles["CenteredTitle"])
        elements.append(main_title)
        elements.append(pp)

        title = Paragraph("Исходные данные конструкции", styles["CenteredTitle1"])
        elements.append(title)

        table1 = Table(nt)
        table1.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        table2 = Table(bt)
        table2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(pp)

        nodes_caption = Paragraph("Параметры узлов", styles["CenteredTitle2"])
        elements.append(nodes_caption)
        elements.append(pp)
        elements.append(table1)

        elements.append(pp)

        bars_caption = Paragraph("Параметры стержней", styles["CenteredTitle2"])
        elements.append(bars_caption)
        elements.append(pp)
        elements.append(table2)


        elements.append(pp)
        scheme_caption = Paragraph("Визуализация конструкции", styles["CenteredTitle1"])
        elements.append(scheme_caption)
        elements.append(pp)
        img = Image(sheme, width=400, height=270)
        elements.append(img)

        table_caption = Paragraph("Значения параметров стержней в напряженно-деформированном состоянии", styles["CenteredTitle1"])
        elements.append(table_caption)
        elements.append(pp)

        for i, table_data in enumerate(td):
            table = [['X', 'N(x)', 'U(x)', 'σ(x)', '[σ]']]

            for row in table_data:
                table.append([f"{row[0]}", f"{row[1]}", f"{row[2]}", f"{row[3]}", f"{row[4]}"])

            t = Table(table)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            for row_idx, row in enumerate(table[1:], start=1):
                if abs(float(row[3])) > float(row[4]):
                    t.setStyle([('TEXTCOLOR', (0, row_idx), (-1, row_idx), colors.red)])

            table_caption = Paragraph(f"Таблица {i+1}", styles["CenteredTitle2"])
            elements.append(table_caption)
            elements.append(pp)
            elements.append(t)
            elements.append(pp)

        epur_title = Paragraph("Графики эпюр заданной конструкции", styles["CenteredTitle1"])
        elements.append(epur_title)
        elements.append(pp)

        buf1 = save_plot_to_buffer(draw_epur_n_sigma, x_coords, y_coords_nx, "N")
        img1 = Image(buf1, width=400, height=300)
        elements.append(img1)
        elements.append(pp)

        buf2 = save_plot_to_buffer(draw_epur_n_sigma, x_coords, y_coords_sigma, "σ")
        img2 = Image(buf2, width=400, height=300)
        elements.append(img2)
        elements.append(pp)

        buf3 = save_plot_to_buffer(draw_epur_u, data)
        img3 = Image(buf3, width=400, height=300)
        elements.append(img3)
        elements.append(pp)

        doc.build(elements)


def save_plot_to_buffer(func, *args):
    buf = BytesIO()
    func(*args)
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

