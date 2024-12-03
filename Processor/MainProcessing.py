import numpy as np
from PreProcessor.Service import InputChecker


def calc_b(f, q, l, lz, rz):
    size = len(l) + 2
    ex_q = [0] * size
    ex_f = [0] * size
    b = [0] * size

    for ql in q:
        ex_q[ql] += q[ql] * l[ql] / 2
        ex_q[ql+1] += q[ql] * l[ql] / 2

    for fl in f:
        ex_f[fl] = f[fl]

    for i in range(size):
        b[i] = ex_f[i] + ex_q[i]

    if lz:
        b[1] = 0
    if rz:
        b[-1] = 0
    return b[1:]


def calc_a(ks, lz, rz):
    size = len(ks) + 1
    A = [[0] * size for _ in range(size)]

    for k in range(size - 1):
        for i in range(2):
            for j in range(2):
                A[i+k][j+k] += ks[k][i][j]

    if lz:
        A[0][0] = 1
        for i in range(1, size):
            A[0][i] = 0
            A[i][0] = 0
    if rz:
        A[-1][-1] = 1
        for i in range(0, size-1):
            A[-1][i] = 0
            A[i][-1] = 0

    return A

def calc_deltas(A, b):
    A = np.array(A)
    b = np.array(b)

    delta = np.linalg.solve(A, b)
    delta_rounded = np.round(delta, 4).tolist()

    return delta_rounded


def calc_u(x, d0, dl, l, q, e, a):
    return round(d0 + (x / l) * (dl - d0) + (q * l**2) / (2 * e * a) * (x / l) * (1 - x / l), 4)


def calc_n(x, d0, dl, l, q, e, a):
    return round((e * a / l) * (dl - d0) + (q * l / 2) * (1 - 2 * x / l), 4)


def calc_sigma(n, a):
    return round(n / a, 4)


def get_ks(data):
    ks = []

    l = {min(int(bar['first_node']), int(bar['second_node'])): float(
        data['nodes'][min(int(bar['first_node']), int(bar['second_node']))]) for bar in data['bars']}
    e = {min(int(bar['first_node']), int(bar['second_node'])): float(bar['e']) for bar in data['bars']}
    a = {min(int(bar['first_node']), int(bar['second_node'])): float(bar['a']) for bar in data['bars']}

    for k in range(1, len(data['bars']) + 1):
        tk = [[e[k] * a[k] / l[k], -e[k] * a[k] / l[k]], [-e[k] * a[k] / l[k], e[k] * a[k] / l[k]]]
        ks.append(tk)

    return ks


def calculate_deltas(data):

    if InputChecker.input_is_correct(data):
        q = {int(bar['bar_num']): float(bar['dist_load']) for bar in data['dist_loads']}
        f = {int(node['node_num']): float(node['conc_load']) for node in data['conc_loads']}
        l = {min(int(bar['first_node']), int(bar['second_node'])): float(
            data['nodes'][min(int(bar['first_node']), int(bar['second_node']))]) for bar in data['bars']}
        b = calc_b(f, q, l, data['left_zadelka'][0], data['right_zadelka'][0])
        A = calc_a(get_ks(data), data['left_zadelka'][0], data['right_zadelka'][0])

        return calc_deltas(A, b)


def section_calc(data, bar_num, x):

    d0 = calculate_deltas(data)[bar_num - 1]
    dl = calculate_deltas(data)[bar_num]

    l = float(data['nodes'][bar_num])
    e = next((float(bar['e']) for bar in data['bars'] if min(int(bar['first_node']), int(bar['second_node'])) == bar_num), 0)
    a = next((float(bar['a']) for bar in data['bars'] if min(int(bar['first_node']), int(bar['second_node'])) == bar_num), 0)
    q = next((float(bar['dist_load']) for bar in data['dist_loads'] if int(bar['bar_num']) == bar_num), 0)

    u = round(calc_u(x, d0, dl, l, q, e, a), 4)
    n = round(calc_n(x, d0, dl, l, q, e, a), 4)
    sigma = round(calc_sigma(n, a), 4)

    return u, n, sigma

def section_calc_for_window(root):
    root.refresh()
    data = root.user_input

    x = float(root.x.get())
    bar_num = int(root.bar_num.get())

    return section_calc(data, bar_num, x)


def section_calc_for_nx_epur(data):
    bars = data['bars']
    x_coords, y_coords_nx, y_coords_sigma = [], [], []

    t = 0
    for bar in bars:
        bar_num = min(int(bar['first_node']), int(bar['second_node']))
        l = float(data['nodes'][bar_num])

        x_coords.append(t)
        x_coords.append(l + t)

        y_coords_nx.append(section_calc(data, bar_num, 0)[1])
        y_coords_nx.append(section_calc(data, bar_num, l)[1])

        y_coords_sigma.append(section_calc(data, bar_num, 0)[2])
        y_coords_sigma.append(section_calc(data, bar_num, l)[2])

        t += l

    return x_coords, y_coords_nx, y_coords_sigma
