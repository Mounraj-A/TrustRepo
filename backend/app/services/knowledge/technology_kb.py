from typing import List, Dict
from app.models.knowledge.technology import Technology
from app.models.knowledge.capability import Capability

TECHNOLOGY_KB: Dict[str, Technology] = {}


def _add_tech(tech: Technology):
    TECHNOLOGY_KB[tech.id] = tech


# ── Java / Spring ───────────────────────────────────────────────────────
_add_tech(Technology(
    id="spring",
    display_name="Spring Framework",
    aliases=["org.springframework", "spring"],
    languages=["Java"],
    category="Backend Framework",
    homepage="https://spring.io/",
    description="The Spring Framework provides a comprehensive programming and configuration model for modern Java-based enterprise applications."
))
_add_tech(Technology(
    id="spring_boot",
    display_name="Spring Boot",
    aliases=["org.springframework.boot", "spring-boot", "spring_boot"],
    languages=["Java"],
    category="Backend Framework",
    parent="spring",
    homepage="https://spring.io/projects/spring-boot",
    description="Spring Boot makes it easy to create stand-alone, production-grade Spring based Applications."
))
_add_tech(Technology(
    id="spring_security",
    display_name="Spring Security",
    aliases=["org.springframework.security", "spring-security"],
    languages=["Java"],
    category="Authentication",
    parent="spring"
))
_add_tech(Technology(
    id="spring_data_jpa",
    display_name="Spring Data JPA",
    aliases=["org.springframework.data.jpa", "spring-data-jpa"],
    languages=["Java"],
    category="Database",
    parent="spring"
))
_add_tech(Technology(
    id="hibernate",
    display_name="Hibernate ORM",
    aliases=["org.hibernate", "hibernate"],
    languages=["Java"],
    category="Database"
))
_add_tech(Technology(
    id="spring_web",
    display_name="Spring MVC",
    aliases=["org.springframework.web", "spring-webmvc"],
    languages=["Java"],
    category="Backend Framework",
    parent="spring"
))
_add_tech(Technology(
    id="spring_amqp",
    display_name="RabbitMQ (Spring AMQP)",
    aliases=["org.springframework.amqp", "spring-rabbit"],
    languages=["Java"],
    category="Messaging",
    parent="spring"
))
_add_tech(Technology(
    id="spring_kafka",
    display_name="Apache Kafka (Spring)",
    aliases=["org.springframework.kafka", "spring-kafka"],
    languages=["Java"],
    category="Messaging",
    parent="spring"
))
_add_tech(Technology(
    id="spring_data_neo4j",
    display_name="Neo4j (Spring Data)",
    aliases=["org.springframework.data.neo4j", "spring-data-neo4j"],
    languages=["Java"],
    category="Database",
    parent="spring"
))
_add_tech(Technology(
    id="jwt_java",
    display_name="JWT (Java)",
    aliases=["io.jsonwebtoken", "com.auth0.jwt"],
    languages=["Java"],
    category="Authentication"
))
_add_tech(Technology(
    id="keycloak",
    display_name="Keycloak",
    aliases=["org.keycloak"],
    languages=["Java"],
    category="Authentication"
))
_add_tech(Technology(
    id="swagger",
    display_name="Swagger / OpenAPI",
    aliases=["io.swagger", "org.springdoc", "springdoc-openapi"],
    languages=["Java"],
    category="API Documentation"
))
_add_tech(Technology(
    id="jackson",
    display_name="Jackson (JSON)",
    aliases=["com.fasterxml.jackson"],
    languages=["Java"],
    category="Serialization"
))
_add_tech(Technology(
    id="jpa",
    display_name="JPA",
    aliases=["javax.persistence", "jakarta.persistence"],
    languages=["Java"],
    category="Database"
))
_add_tech(Technology(
    id="mapstruct",
    display_name="MapStruct",
    aliases=["org.mapstruct"],
    languages=["Java"],
    category="Mapping"
))
_add_tech(Technology(
    id="mysql_java",
    display_name="MySQL (Java)",
    aliases=["com.mysql", "mysql-connector-java"],
    languages=["Java"],
    category="Database"
))
_add_tech(Technology(
    id="mongodb_java",
    display_name="MongoDB (Java)",
    aliases=["org.mongodb"],
    languages=["Java"],
    category="Database"
))
_add_tech(Technology(
    id="redis_java",
    display_name="Redis (Java)",
    aliases=["io.lettuce", "org.redisson"],
    languages=["Java"],
    category="Caching"
))

# ── Python ──────────────────────────────────────────────────────────────
_add_tech(Technology(
    id="fastapi",
    display_name="FastAPI",
    aliases=["fastapi"],
    languages=["Python"],
    category="Backend Framework",
    homepage="https://fastapi.tiangolo.com/",
    description="FastAPI is a modern, fast (high-performance), web framework for building APIs with Python."
))
_add_tech(Technology(
    id="flask",
    display_name="Flask",
    aliases=["flask"],
    languages=["Python"],
    category="Backend Framework"
))
_add_tech(Technology(
    id="django",
    display_name="Django",
    aliases=["django"],
    languages=["Python"],
    category="Backend Framework"
))
_add_tech(Technology(
    id="sqlalchemy",
    display_name="SQLAlchemy",
    aliases=["sqlalchemy"],
    languages=["Python"],
    category="ORM"
))
_add_tech(Technology(
    id="pydantic",
    display_name="Pydantic",
    aliases=["pydantic"],
    languages=["Python"],
    category="Validation"
))
_add_tech(Technology(
    id="plotly",
    display_name="Plotly",
    aliases=["plotly"],
    languages=["Python"],
    category="Visualization",
    homepage="https://plotly.com/python/",
    description="Interactive, open-source, and browser-based graphing library for Python."
))
_add_tech(Technology(
    id="plotly_express",
    display_name="Plotly Express",
    aliases=["plotly.express", "px"],
    languages=["Python"],
    category="Visualization",
    parent="plotly"
))
_add_tech(Technology(
    id="pandas",
    display_name="Pandas",
    aliases=["pandas", "pd"],
    languages=["Python"],
    category="Data Processing"
))
_add_tech(Technology(
    id="numpy",
    display_name="NumPy",
    aliases=["numpy", "np"],
    languages=["Python"],
    category="Scientific Computing"
))
_add_tech(Technology(
    id="streamlit",
    display_name="Streamlit",
    aliases=["streamlit", "st"],
    languages=["Python"],
    category="Dashboard"
))
_add_tech(Technology(
    id="jwt_python",
    display_name="PyJWT",
    aliases=["jwt", "PyJWT"],
    languages=["Python"],
    category="Authentication"
))
_add_tech(Technology(
    id="redis_python",
    display_name="Redis (Python)",
    aliases=["redis"],
    languages=["Python"],
    category="Caching"
))
_add_tech(Technology(
    id="celery",
    display_name="Celery",
    aliases=["celery"],
    languages=["Python"],
    category="Task Queue"
))
_add_tech(Technology(
    id="aiohttp",
    display_name="AIOHTTP",
    aliases=["aiohttp"],
    languages=["Python"],
    category="Backend Framework"
))
_add_tech(Technology(
    id="psycopg2",
    display_name="PostgreSQL (psycopg2)",
    aliases=["psycopg2"],
    languages=["Python"],
    category="Database"
))
_add_tech(Technology(
    id="pymongo",
    display_name="MongoDB (PyMongo)",
    aliases=["pymongo"],
    languages=["Python"],
    category="Database"
))
_add_tech(Technology(
    id="pymysql",
    display_name="MySQL (PyMySQL)",
    aliases=["pymysql"],
    languages=["Python"],
    category="Database"
))
_add_tech(Technology(
    id="scikit_learn",
    display_name="Scikit-Learn",
    aliases=["sklearn", "scikit-learn"],
    languages=["Python"],
    category="Machine Learning"
))
_add_tech(Technology(
    id="matplotlib",
    display_name="Matplotlib",
    aliases=["matplotlib"],
    languages=["Python"],
    category="Visualization"
))
_add_tech(Technology(
    id="seaborn",
    display_name="Seaborn",
    aliases=["seaborn", "sns"],
    languages=["Python"],
    category="Visualization"
))

# ── JavaScript / Node ───────────────────────────────────────────────────
_add_tech(Technology(
    id="express",
    display_name="Express.js",
    aliases=["express"],
    languages=["JavaScript", "TypeScript"],
    category="Backend Framework",
    homepage="https://expressjs.com/",
    description="Fast, unopinionated, minimalist web framework for Node.js"
))
_add_tech(Technology(
    id="react",
    display_name="React",
    aliases=["react"],
    languages=["JavaScript", "TypeScript"],
    category="Frontend Framework"
))
_add_tech(Technology(
    id="mongoose",
    display_name="Mongoose",
    aliases=["mongoose"],
    languages=["JavaScript", "TypeScript"],
    category="ORM"
))
_add_tech(Technology(
    id="jsonwebtoken",
    display_name="JSON Web Token",
    aliases=["jsonwebtoken"],
    languages=["JavaScript", "TypeScript"],
    category="Authentication"
))
_add_tech(Technology(
    id="plotly_js",
    display_name="Plotly.js",
    aliases=["plotly.js"],
    languages=["JavaScript", "TypeScript"],
    category="Visualization",
    parent="plotly"
))

# ── Universal / Language Independent ────────────────────────────────────
_add_tech(Technology(
    id="docker",
    display_name="Docker",
    aliases=["docker"],
    languages=[],  # Empty implies universal
    category="Containerization"
))
_add_tech(Technology(
    id="neo4j",
    display_name="Neo4j",
    aliases=["neo4j", "org.neo4j", "spring-data-neo4j"],
    languages=[],  # Usually matches neo4j driver across languages
    category="Database"
))
_add_tech(Technology(
    id="postgresql",
    display_name="PostgreSQL",
    aliases=["postgresql", "psycopg2", "pg", "org.postgresql"],
    languages=[],
    category="Database"
))


# ── Capabilities Mapping ────────────────────────────────────────────────
CAPABILITY_KB: Dict[str, Capability] = {}


def _add_cap(cap: Capability):
    CAPABILITY_KB[cap.id] = cap


_add_cap(
    Capability(
        "database", "Database Management", [
            "Database", "ORM"], "Data persistence and database communication layer."))
_add_cap(
    Capability(
        "visualization", "Data Visualization", [
            "Visualization", "Dashboard"], "Graphical representation of data and metrics."))
_add_cap(Capability("analytics",
                    "Data Analytics",
                    ["Data Processing",
                     "Scientific Computing",
                     "Machine Learning"],
                    "Processing and analyzing structured or unstructured data."))
_add_cap(Capability("authentication", "Authentication & Security", [
         "Authentication", "Security"], "User identity verification and access control."))
_add_cap(
    Capability(
        "api",
        "API Infrastructure",
        ["Backend Framework"],
        "Exposes endpoints for external systems or frontends."))
_add_cap(Capability("messaging",
                    "Messaging & Events",
                    ["Messaging",
                     "Task Queue"],
                    "Asynchronous inter-service communication via queues or event buses."))
_add_cap(
    Capability(
        "caching",
        "Caching Layer",
        ["Caching"],
        "In-memory or distributed caching for performance optimization."))
_add_cap(
    Capability(
        "frontend",
        "Frontend / UI",
        ["Frontend Framework"],
        "User-facing UI layer and component rendering."))
_add_cap(Capability("containerization",
                    "Containerization",
                    ["Containerization",
                     "Orchestration"],
                    "Container-based deployment and orchestration infrastructure."))


def resolve_technology(import_path: str,
                       file_languages: List[str]) -> List[Technology]:
    """
    Given an import path (e.g. plotly.express.colors) and file languages,
    returns all matching Technologies from longest path to shortest.
    Example: plotly.express.colors -> matches plotly.express -> matches plotly.
    """
    results = []

    # Simple strategy: generate paths from longest to shortest
    # e.g., ['plotly.express.colors', 'plotly.express', 'plotly']
    parts = import_path.split('.')
    paths = []
    for i in range(len(parts), 0, -1):
        paths.append('.'.join(parts[:i]))

    for p in paths:
        # Check against aliases
        for tech in TECHNOLOGY_KB.values():
            if tech.languages and not any(
                    lang in tech.languages for lang in file_languages):
                continue

            if p in tech.aliases or import_path == tech.id:
                if tech not in results:
                    results.append(tech)

    # Also attempt reverse-lookup by alias for common shortnames (e.g., 'px')
    # but only if it's an exact match
    for tech in TECHNOLOGY_KB.values():
        if tech.languages and not any(
                lang in tech.languages for lang in file_languages):
            continue
        if import_path in tech.aliases and tech not in results:
            results.append(tech)

    return results


def get_capabilities_for_tech(tech: Technology) -> List[Capability]:
    return [cap for cap in CAPABILITY_KB.values(
    ) if tech.category in cap.category_triggers]
