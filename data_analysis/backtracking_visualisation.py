from datetime import datetime, time

from anytree import Node, RenderTree
from anytree.exporter import DotExporter


class Structure:
    def __init__(self, structure_id):
        self.id = structure_id
        self.connected_structures = []

    def add_connection(self, structure):
        if isinstance(structure, Structure) and structure not in self.connected_structures:
            self.connected_structures.append(structure)

    def get_connected_ids(self):
        return [structure.id for structure in self.connected_structures]

    def __str__(self):
        return f"Structure ID: {self.id}, Connected IDs: {self.get_connected_ids()}"


def is_unvisited(structure, visited):
    return structure not in visited


def connect_structures_in_chain(structures, start_structure_id, visited=None, parent_node=None):
    if visited is None:
        visited = set()

    if parent_node is None:
        root_node = Node(name=str(structures[start_structure_id - 1].id))

    start_structure = structures[start_structure_id - 1]
    current_node = Node(name=str(start_structure.id), parent=parent_node)

    unvisited_connections = [s for s in start_structure.connected_structures if is_unvisited(s, visited)]

    if unvisited_connections:
        next_structure = unvisited_connections[0]  # Choose the first unvisited connection
        start_structure.add_connection(next_structure)
        visited.add(next_structure)
        connect_structures_in_chain(structures, next_structure.id, visited, current_node)


# Usage example:
if __name__ == "__main__":
    structures = [Structure(i) for i in range(1, 16)]

    # Define the connections (semi-random values)
    connections = {
        1: [2, 3, 4],
        2: [1, 3, 5],
        3: [1, 2, 4],
        4: [1, 3],
        5: [2],
        6: [],
        7: [2],
        8: [3],
        9: [4, 5],
        10: [1, 3],
        11: [2, 12],
        12: [],
        13: [12, 14],
        14: [13, 15],
        15: [14],
    }

    # Add connections based on the defined values
    for structure_id, connected_ids in connections.items():
        for connected_id in connected_ids:
            structure = structures[structure_id - 1]
            connected_structure = structures[connected_id - 1]
            structure.add_connection(connected_structure)

    # Connect structures in a long chain with the starting structure ID set to 1
    start_structure_id = 1
    connect_structures_in_chain(structures, start_structure_id)

    # Print the details of all structures after connecting
    for structure in structures:
        print(structure)

    # Create the tree structure
    root_node = Node(name="Root")
    for structure in structures:
        current_node = Node(name=str(structure.id), parent=root_node)
        for connected_structure in structure.connected_structures:
            Node(name=str(connected_structure.id), parent=current_node)

    # Print the tree structure
    print("Tree Structure:")
    for pre, _, node in RenderTree(root_node):
        print(f"{pre}{node.name}")

    # Save the pretty print result to a file
    with open("./output/trees/tree.txt", "w", encoding="utf-8") as file:
        for pre, _, node in RenderTree(root_node):
            file.write(f"{pre}{node.name}\n")

    # Visualize the tree using DotExporter
    DotExporter(root_node).to_dotfile(f"./output/trees/tree.dot")
    print("Tree structure visualized with DotExporter.")