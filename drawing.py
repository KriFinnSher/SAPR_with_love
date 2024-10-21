from PIL import Image, ImageTk
from tkinter import messagebox
import matplotlib.pyplot as plt
from io import BytesIO
import warnings


def draw_scheme(lengths, heights, bars, nodes, conc_loads, dist_loads, left_z, right_z):
    fig, scheme = plt.subplots()
    max_height = max(heights)
    sl = sum(lengths)
    sh = sum(heights)
    x = 0
    hly = []

    for length, height in zip(lengths, heights):
        y = max_height / 2 - height / 2 + max_height * 2.5
        scheme.add_patch(plt.Rectangle((x, y), length, height, edgecolor='black', facecolor='white'))
        hly.append((height, length, y))
        x += length

    if left_z[0]:
        try:
            vert_line_height = max_height / 2
            max_bar_y = max(hly, key=lambda h: h[0])[2]
            vert_line_y = max_bar_y + max_height / 2 - vert_line_height / 2
            scheme.arrow(0, vert_line_y, 0, vert_line_height, head_width=0, head_length=0, fc='black', ec='black')
            line_length = vert_line_height * 0.113

            for i in range(8):
                start_x = 0
                start_y = vert_line_y + i * vert_line_height / 7
                dx = -line_length
                dy = -line_length
                plt.arrow(start_x, start_y, dx, dy,
                          color='black', head_width=0,
                          head_length=0, width=0.01)
        except ValueError:
            messagebox.showwarning("Ошибка ввода данных", "Присутствуют пустые поля в окне стержней")
    if right_z[0]:
        vert_line_height = max_height / 2
        last_bar_x = sum(lengths)
        max_bar_y = max(hly, key=lambda h: h[0])[2]
        vert_line_y = max_bar_y + max_height / 2 - vert_line_height / 2
        scheme.arrow(last_bar_x, vert_line_y, 0, vert_line_height, head_width=0, head_length=0, fc='black', ec='black')
        line_length = vert_line_height * 0.113

        for i in range(8):
            start_x = last_bar_x
            start_y = vert_line_y + i * vert_line_height / 7
            dx = line_length
            dy = line_length
            plt.arrow(start_x, start_y, dx, dy,
                      color='black', head_width=0,
                      head_length=0, width=0.01)

    try:
        for dist_load in dist_loads:
            i = int(dist_load['bar_num']) - 2
            y_base = hly[i][2]
            height = hly[i][0]

            if float(dist_load['dist_load']) > 0:
                destination = 1
            elif float(dist_load['dist_load']) == 0:
                destination = 0
            else:
                destination = -1

            if destination > 0:
                x_start = float(nodes[min(int(bars[int(dist_load['bar_num']) - 1]['first_node']) - 1,
                                          int(bars[int(dist_load['bar_num']) - 1]['second_node']) - 1)])
                x_end = float(nodes[max(int(bars[int(dist_load['bar_num']) - 1]['first_node']) - 1,
                                        int(bars[int(dist_load['bar_num']) - 1]['second_node']) - 1)])

                bar_len = abs(x_end - x_start)
                arrow_len = bar_len / 5
                x_temp = x_start
                for k in range(5):
                    plt.arrow(x_temp, y_base + height / 2, abs(arrow_len * destination - sl / 100), 0,
                              color='b', head_width=sh / 35,
                              head_length=sl / 100, width=0.0001)
                    x_temp += arrow_len
            elif destination == 0:
                continue
            else:
                x_start = float(nodes[max(int(bars[int(dist_load['bar_num']) - 1]['first_node']) - 1,
                                          int(bars[int(dist_load['bar_num']) - 1]['second_node']) - 1)])
                x_end = float(nodes[min(int(bars[int(dist_load['bar_num']) - 1]['first_node']) - 1,
                                        int(bars[int(dist_load['bar_num']) - 1]['second_node']) - 1)])

                bar_len = abs(x_end - x_start)
                arrow_len = bar_len / 5
                x_temp = x_start
                for k in range(5):
                    a = arrow_len * destination + sl / 100
                    a = -a if a > 0 else a
                    plt.arrow(x_temp, y_base + height / 2, a, 0,
                              color='b', head_width=sh / 35,
                              head_length=sl / 100, width=0.0001)
                    x_temp -= arrow_len
    except ValueError:
        messagebox.showwarning("Ошибка ввода данных", "Присутствуют пустые поля в окне распределенных нагрузок")

    try:
        for conc_load in conc_loads:
            i = int(conc_load['node_num']) - 2

            if float(conc_load['conc_load']) > 0:
                destination = 1
            elif float(conc_load['conc_load']) == 0:
                destination = 0
            else:
                destination = -1

            x_node = nodes[int(conc_load['node_num']) - 1]
            y_base = hly[i][2]
            height = hly[i][0]

            if destination > 0:
                length = hly[i + 1][1] if (i + 1) < len(hly) else sl / 4
            elif destination == 0:
                continue
            else:
                length = -hly[i][1] if x_node != 0 else -sl / 4
            length = length / 3

            plt.arrow(x_node, y_base + height / 2, length, 0,
                      color='r', head_width=sh / 30,
                      head_length=sl / 50, width=0.0001)
    except ValueError:
        messagebox.showwarning("Ошибка ввода данных", "Присутствуют пустые поля в окне сосредоточенных нагрузок")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        scheme.set_xlim(-sum(lengths) * 0.15, sum(lengths) * 1.15)
        scheme.set_ylim(0, max_height * 4)

    scheme.axis('off')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf


def display_scheme(canvas, lengths, heights, bars, nodes, conc_loads, dist_loads, left_z, right_z):
    buf = draw_scheme(lengths, heights, bars, nodes, conc_loads, dist_loads, left_z, right_z)
    img = Image.open(buf)
    img = ImageTk.PhotoImage(img)

    canvas.delete("all")
    canvas.image = img
    canvas.create_image(0, 0, anchor='nw', image=img)
