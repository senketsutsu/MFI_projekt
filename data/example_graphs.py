from typing import Dict, List, Tuple

Edge = Tuple[str, str]
GraphEdges = List[Edge]

EXAMPLE_GRAPHS: Dict[str, GraphEdges] = {
    "Cykl prosty": [
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),
    ],
    "Gwiazda": [
        ("A", "B"),
        ("A", "C"),
        ("A", "D"),
        ("A", "E"),
        ("B", "A"),
        ("C", "A"),
        ("D", "A"),
        ("E", "A"),
    ],
    "Graf z dangling node (no outlinks)": [
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),
        ("C", "D"),
    ],
    "Mały graf testowy": [
        ("A", "B"),
        ("A", "C"),
        ("B", "C"),
        ("C", "A"),
        ("D", "C"),
    ],
    "Średni graf testowy": [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("C", "D"),
        ("C", "E"),
        ("D", "A"),
        ("E", "D"),
        ("F", "C"),
        ("F", "E"),
    ],
}