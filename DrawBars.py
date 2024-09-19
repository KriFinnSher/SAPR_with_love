import matplotlib.pyplot as plt


def draw_sticks(lengths, heights):
    fig, ax = plt.subplots()
    max_height = max(heights)
    x = 0
    for (length, height) in zip(lengths, heights):
        y = max_height / 2 - height / 2 + max_height
        ax.add_patch(plt.Rectangle((x, y), length, height, edgecolor='black', facecolor='white'))
        x += length

    ax.set_xlim(0, sum(lengths))
    ax.set_ylim(0, max_height*4)

    ax.axis('off')
    plt.show()


lengths = [12, 13, 14, 21]
heights = [12, 24, 21, 12]

draw_sticks(lengths, heights)