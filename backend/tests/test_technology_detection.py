import pytest
from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph, GraphNode
from app.services.analysis.technology_detection import TechnologyDetection

def create_mock_graph(nodes_data):
    graph = RepositoryKnowledgeGraph()
    for nd in nodes_data:
        graph.nodes.append(GraphNode(
            label=nd["label"],
            properties=nd["properties"]
        ))
    return graph

def test_technology_detection_python_imports():
    detector = TechnologyDetection()
    graph = create_mock_graph([
        {"label": "Import", "properties": {"name": "pandas", "file_path": "test.py"}},
        {"label": "Import", "properties": {"name": "fastapi", "file_path": "main.py"}}
    ])
    result = detector.detect(graph)
    assert "Pandas" in result["technologies"]
    assert "FastAPI" in result["technologies"]
    
def test_technology_detection_java_annotations():
    detector = TechnologyDetection()
    graph = create_mock_graph([
        {"label": "Annotation", "properties": {"name": "RestController", "file_path": "Controller.java"}}
    ])
    result = detector.detect(graph)
    assert "Spring MVC" in result["technologies"]
    
def test_technology_detection_js_imports():
    detector = TechnologyDetection()
    graph = create_mock_graph([
        {"label": "Import", "properties": {"name": "react", "file_path": "app.js"}},
        {"label": "Import", "properties": {"name": "express", "file_path": "server.js"}}
    ])
    result = detector.detect(graph)
    assert "React" in result["technologies"]
    assert "Express.js" in result["technologies"]

def test_technology_detection_mixed_repo():
    detector = TechnologyDetection()
    graph = create_mock_graph([
        {"label": "Import", "properties": {"name": "pandas", "file_path": "test.py"}},
        {"label": "Annotation", "properties": {"name": "SpringBootApplication", "file_path": "App.java"}}
    ])
    result = detector.detect(graph)
    assert "Pandas" in result["technologies"]
    assert "Spring Boot" in result["technologies"]

def test_technology_detection_no_dependencies():
    detector = TechnologyDetection()
    graph = create_mock_graph([
        {"label": "Class", "properties": {"name": "MyClass", "file_path": "test.py"}}
    ])
    result = detector.detect(graph)
    assert len(result["technologies"]) == 0

def test_technology_detection_alias_imports():
    detector = TechnologyDetection()
    # E.g. import pandas as pd, PythonParser saves name as pandas
    graph = create_mock_graph([
        {"label": "Import", "properties": {"name": "pandas", "alias": "pd", "file_path": "test.py"}}
    ])
    result = detector.detect(graph)
    assert "Pandas" in result["technologies"]

def test_technology_detection_nested_packages():
    detector = TechnologyDetection()
    graph = create_mock_graph([
        {"label": "Import", "properties": {"name": "plotly.express.colors", "file_path": "test.py"}}
    ])
    result = detector.detect(graph)
    # resolve_technology should match plotly.express -> Plotly Express
    assert "Plotly Express" in result["technologies"]
