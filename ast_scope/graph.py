from typing import Iterable


class DiGraph:
    def __init__(self):
        self.__adjacency_list: dict[str, set[str]] = {}

    def add_nodes_from(self, iterable: Iterable[str]):
        for node in iterable:
            self.add_node(node)

    def add_node(self, node: str):
        if node not in self.__adjacency_list:
            self.__adjacency_list[node] = set()

    def add_edge(self, source: str, target: str):
        self.__adjacency_list[source].add(target)

    def nodes(self):
        return list(self.__adjacency_list)

    def edges(self):
        return list(
            (source, target)
            for source, targets in self.__adjacency_list.items()
            for target in targets
        )

    def neighbors(self, node: str):
        return list(self.__adjacency_list[node])
