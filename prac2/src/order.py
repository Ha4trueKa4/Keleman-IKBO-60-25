def load_order(edges, root):
    order = []
    _place(root, edges, {}, order)
    return order


def _place(node, edges, state, order):
    state[node] = "active"
    for dep in edges.get(node, []):
        if dep not in state:
            _place(dep, edges, state, order)
    state[node] = "done"
    order.append(node)
