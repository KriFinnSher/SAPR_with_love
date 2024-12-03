from Processor import MainProcessing


def get_all(data, steps):
    iter_nums = steps

    size = len(data['bars']) + 1
    bar_tables = [[] * size for _ in range(size)]
    bars = sorted(data['bars'], key=lambda x: x['first_node'])

    deltas = MainProcessing.calculate_deltas(data)


    for bar in bars:
        bar_num = min(int(bar['first_node']), int(bar['second_node']))

        l = float(data['nodes'][bar_num])
        d0, dl = deltas[bar_num - 1], deltas[bar_num]

        e = next((float(bar['e']) for bar in data['bars'] if
                  min(int(bar['first_node']), int(bar['second_node'])) == bar_num), 0)
        a = next((float(bar['a']) for bar in data['bars'] if
                  min(int(bar['first_node']), int(bar['second_node'])) == bar_num), 0)
        q = next((float(bar['dist_load']) for bar in data['dist_loads'] if int(bar['bar_num']) == bar_num), 0)
        for i in range(iter_nums + 1):
            l_iter = round(l / iter_nums * i, 4)
            n, u = MainProcessing.calc_n(l_iter, d0, dl, l, q, e, a), MainProcessing.calc_u(l_iter, d0, dl, l, q, e, a)
            sigma = MainProcessing.calc_sigma(n, a)

            sigma_max = next((float(bar['max_load']) for bar in data['bars'] if min(int(bar['first_node']), int(bar['second_node'])) == bar_num), 0)
            bar_tables[bar_num].append((l_iter, n, u, sigma, sigma_max))

    return bar_tables[1:]