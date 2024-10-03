from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from io import BytesIO


def draw_scheme(lengths, heights, nodes, conc_loads, dist_loads):
    fig, scheme = plt.subplots()
    max_height = max(heights)
    x = 0
    hly = []

    for length, height in zip(lengths, heights):
        y = max_height / 2 - height / 2 + max_height * 2.5
        scheme.add_patch(plt.Rectangle((x, y), length, height, edgecolor='black', facecolor='white'))
        hly.append((height, length, y))
        x += length

    for conc_load in conc_loads:
        i = int(conc_load[0]) - 2
        load_magnitude = conc_load[1]
        x_node = nodes[i + 1]
        y_base = hly[i][2]
        height = hly[i][0]
        sl = sum(lengths)
        sh = sum(heights)

        if load_magnitude > 0:
            length = hly[i + 1][1] if (i + 1) < len(hly) else sl / 4
        else:
            length = -hly[i][1] if x_node != 0 else -sl / 4
        length = length / 3

        plt.arrow(x_node, y_base + height / 2, length, 0,
                  color='r', head_width=sh / 40,
                  head_length=sl / 50, width=0.0001)

    scheme.set_xlim(-sum(lengths)*0.15, sum(lengths)*1.15)
    scheme.set_ylim(0, max_height * 4)
    scheme.axis('off')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf


def display_scheme(canvas, lengths, heights, nodes, conc_loads, dist_loads):
    buf = draw_scheme(lengths, heights, nodes, conc_loads, dist_loads)
    img = Image.open(buf)
    img = ImageTk.PhotoImage(img)

    canvas.delete("all")
    canvas.image = img
    canvas.create_image(0, 0, anchor='nw', image=img)

