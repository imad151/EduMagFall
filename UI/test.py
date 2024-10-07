import numpy as np

nodes = np.zeros((1,2))

for _ in range(5):
    phi = np.random.uniform(0, 2 * np.pi)
    r = np.random.uniform(20, 50)

    node_x = 150 + (r * np.cos(phi))
    node_y = 150 + (r * np.sin(phi))

    nodes = np.vstack([nodes, [int(node_x), int(node_y)]])

nodes = nodes[1:]
print(nodes)
