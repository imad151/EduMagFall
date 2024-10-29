import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

# Generate random points in clusters
def GenerateNodes():
    num_nodes = 13
    num_clusters = np.random.randint(2, 5)
    cluster_centre = np.random.uniform(100, 200, (num_clusters, 2))
    max_distance = 40
    min_distance = 20

    nodes = []
    for _ in range(num_nodes):
        while True:
            if np.random.rand() < 0.5:
                x = np.random.normal(150, max_distance)
                y = np.random.normal(150, max_distance)
            else:
                curr_cluster_idx = np.random.choice(num_clusters)
                curr_cluster = cluster_centre[curr_cluster_idx]

                x = np.random.normal(curr_cluster[0], max_distance)
                y = np.random.normal(curr_cluster[1], max_distance)

            if len(nodes) == 0 or np.all(np.linalg.norm(np.array(nodes) - np.array([x, y]), axis=1) >= min_distance) and 100<=x<=200 and 100<=y<=200:
                nodes.append([x, y])
                break
    return np.array(nodes)

# Greedy approach to arrange points by minimum distance
def arrange_points_min_distance(points, dist_matrix):
    num_points = len(points)
    visited = [False] * num_points
    order = [0]  # Start from the first point
    visited[0] = True
    current_point = 0

    for _ in range(1, num_points):
        # Find the nearest unvisited point
        next_point = np.argmin([dist_matrix[current_point][j] if not visited[j] else np.inf for j in range(num_points)])
        visited[next_point] = True
        order.append(next_point)
        current_point = next_point

    return points[order]

# Generate nodes and calculate distance matrix
import time
for _ in range(100):
    t1 = time.time()
    points = GenerateNodes()
    print(time.time()-t1)
dist_matrix = sp.spatial.distance.cdist(points, points, 'euclidean')
ordered_points = arrange_points_min_distance(points, dist_matrix)

# Calculate the MST
mst = sp.sparse.csgraph.minimum_spanning_tree(dist_matrix).toarray().astype(float)

# Plot MST
plt.figure()
for i in range(len(points)):
    for j in range(len(points)):
        if mst[i, j] > 0:
            print(int(points[i][0]), int(points[j][0]))
            plt.plot([points[i][0], points[j][0]], [points[i][1], points[j][1]], 'g-o', alpha=0.7)

# Plot original points
for point in points:
    plt.scatter(point[0], point[1], color='blue')

plt.title("Minimum Spanning Tree (MST) of Points")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)

# Plot ordered path by minimum distance
plt.figure()
for point in points:
    plt.scatter(point[0], point[1], color='blue')

x = [point[0] for point in ordered_points]
y = [point[1] for point in ordered_points]
plt.plot(x, y, '-o', color='red')

plt.title("Path of Points Ordered by Minimum Distance")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)

plt.show()
