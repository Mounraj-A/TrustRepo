from database.neo4j import neo4j_conn

class GraphRepository:
    def __init__(self):
        self.conn = neo4j_conn

    def create_entity(self, label: str, properties: dict):
        prop_string = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        query = f"CREATE (n:{label} {{{prop_string}}}) RETURN n"
        return self.conn.query(query, properties)

    def clear_graph(self):
        query = "MATCH (n) DETACH DELETE n"
        return self.conn.query(query)

    def setup_indexes(self):
        # Create indexes for fast merging
        try:
            self.conn.query("CREATE INDEX IF NOT EXISTS FOR (n:Class) ON (n.qualname)")
            self.conn.query("CREATE INDEX IF NOT EXISTS FOR (n:Method) ON (n.qualname)")
            self.conn.query("CREATE INDEX IF NOT EXISTS FOR (n:File) ON (n.qualname)")
        except Exception:
            pass

    def save_graph(self, graph):
        self.clear_graph()
        self.setup_indexes()
        
        # Batch nodes by label
        nodes_by_label = {}
        for node in graph.nodes:
            if node.label not in nodes_by_label:
                nodes_by_label[node.label] = []
            nodes_by_label[node.label].append(node.properties)
            
        for label, properties_list in nodes_by_label.items():
            query = f"""
            UNWIND $batch AS props
            CREATE (n:{label})
            SET n = props
            """
            self.conn.query(query, {"batch": properties_list})
            
        # Batch edges by type
        edges_by_type = {}
        for edge in graph.edges:
            if edge.rel_type not in edges_by_type:
                edges_by_type[edge.rel_type] = []
            
            edge_data = {
                "from_qualname": edge.source_qualname,
                "to_qualname": edge.target_qualname,
                **edge.properties
            }
            edges_by_type[edge.rel_type].append(edge_data)
            
        for rel_type, data_list in edges_by_type.items():
            query = f"""
            UNWIND $batch AS data
            MATCH (a), (b)
            WHERE a.qualname = data.from_qualname AND b.qualname = data.to_qualname
            MERGE (a)-[r:{rel_type}]->(b)
            SET r = data
            """
            self.conn.query(query, {"batch": data_list})
            
    def create_relationship(self, from_id, to_id, rel_type: str, properties: dict = None):
        if properties is None:
            properties = {}
        prop_string = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        prop_clause = f" {{{prop_string}}}" if properties else ""
        
        query = f"""
        MATCH (a), (b)
        WHERE id(a) = $from_id AND id(b) = $to_id
        CREATE (a)-[r:{rel_type}{prop_clause}]->(b)
        RETURN r
        """
        params = {"from_id": from_id, "to_id": to_id, **properties}
        return self.conn.query(query, params)

    def create_relationship_by_qualname(self, from_qualname: str, to_qualname: str, rel_type: str, properties: dict = None):
        if properties is None:
            properties = {}
        prop_string = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        prop_clause = f" {{{prop_string}}}" if properties else ""
        
        query = f"""
        MATCH (a), (b)
        WHERE a.qualname = $from_qualname AND b.qualname = $to_qualname
        MERGE (a)-[r:{rel_type}{prop_clause}]->(b)
        RETURN r
        """
        params = {"from_qualname": from_qualname, "to_qualname": to_qualname, **properties}
        return self.conn.query(query, params)

    def get_all_entities_by_label(self, label: str):
        query = f"MATCH (n:{label}) RETURN n"
        return self.conn.query(query)
