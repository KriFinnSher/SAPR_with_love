def scale_to_k(arr, k):
    arr = [float(val) for val in arr]
    min_val = min(arr)
    max_val = max(arr)

    if max_val <= min_val * k:
        return arr

    new_max_val = min_val * k
    scaling_factor = (new_max_val - min_val) / (max_val - min_val)

    new_arr = [min_val + (x - min_val) * scaling_factor for x in arr]
    return new_arr