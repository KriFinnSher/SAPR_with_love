import matplotlib.pyplot as plt
import numpy as np
from Processor import MainProcessing

def draw_epur_n_sigma(x_coords, y_coords, epur_type):
    plt.clf()
    size = len(y_coords)

    main_lne = [0] * size

    plt.plot(x_coords, main_lne, color='red')
    plt.plot(x_coords, y_coords, color='red')
    plt.fill_between(x_coords, main_lne, y_coords, color='red', alpha=0.5, hatch='||')
    plt.title(f"Эпюра {epur_type}(x)")

    for i, (xi, y2i) in enumerate(zip(x_coords, y_coords)):
        plt.annotate(f'{abs(y2i)}', (xi, y2i), textcoords="offset points", xytext=(-7, 0), color='black')

    k = 0
    for i in range(0, len(x_coords) - 1, 2):
        k += 1
        if i + 2 >= len(x_coords):
            plt.annotate(f'({k})', ((x_coords[i] + x_coords[-1]) / 2, 0), textcoords="offset points", xytext=(0, 4),
                         color='black', weight='bold')
        else:
            plt.annotate(f'({k})', ((x_coords[i] + x_coords[i+2]) / 2, 0), textcoords="offset points", xytext=(0, 4), color='black', weight='bold')

    for i in range(1, len(x_coords) - 1, 2):
        plt.vlines(x=x_coords[i], ymin=0, ymax=y_coords[i], color='red', linewidth=1)

    plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.axis('off')

def draw_epur_u(data):
    t = 0
    k = 0
    plt.clf()
    for bar in data['bars']:
        k += 1
        bar_num = min(int(bar['first_node']), int(bar['second_node']))
        l = float(data['nodes'][bar_num])
        e = float(bar['e'])
        a = float(bar['a'])
        q = next((float(load['dist_load']) for load in data['dist_loads'] if int(load['bar_num']) == bar_num), 0)

        d0 = MainProcessing.calculate_deltas(data)[bar_num - 1]
        dl = MainProcessing.calculate_deltas(data)[bar_num]

        x = np.linspace(0, l, 100)
        y = [MainProcessing.calc_u(xi, d0, dl, l, q, e, a) for xi in x]

        plt.plot(x + t, y, color='red')
        plt.fill_between(x + t, [0] * len(x), y, color='red', alpha=0.5, hatch='||')


        plt.annotate(f'{round(abs(y[0]), 4)}', (t, y[0]), textcoords="offset points", xytext=(-7, 2), color='black')
        plt.annotate(f'{round(abs(y[-1]), 4)}', (t + l, y[-1]), textcoords="offset points", xytext=(-7, 2), color='black')

        plt.annotate(f'({k})', (t + l / 2, 0), textcoords="offset points", xytext=(0, 4), color='black', weight='bold')

        t += l

    plt.title("Эпюра U(x)")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.axis('off')
