import { useEffect, useState, useMemo } from 'react';
import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { GitGraph, Maximize2, Minimize2, ZoomIn, ZoomOut, Filter } from 'lucide-react';
import { motion } from 'framer-motion';

import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
  Panel,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// Cytoscape layout could be added here for headless layouting, 
// but for now we'll use a simple generic layout to place nodes.
import cytoscape from 'cytoscape';

export default function KnowledgeGraph() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const graph = analysisResult?.graph_metrics;
  
  // Transform raw nodes into React Flow nodes using Cytoscape for layout
  useEffect(() => {
    if (!graph?.raw_nodes || !graph?.raw_edges) return;
    
    // 1. Initialize Cytoscape headless for layout computation
    const cy = cytoscape({
      elements: {
        nodes: graph.raw_nodes.map(n => ({ data: { id: n.id, ...n } })),
        edges: graph.raw_edges.map(e => ({ data: { id: `${e.source}-${e.target}`, source: e.source, target: e.target, label: e.type } }))
      },
      headless: true,
      styleEnabled: true
    });
    
    // 2. Run a layout (e.g., cose or grid)
    const layout = cy.layout({
      name: 'cose',
      idealEdgeLength: 100,
      nodeOverlap: 20,
      refresh: 20,
      fit: true,
      padding: 30,
      randomize: true,
      componentSpacing: 100,
      nodeRepulsion: 400000,
      edgeElasticity: 100,
      nestingFactor: 5,
      gravity: 80,
      numIter: 1000,
      initialTemp: 200,
      coolingFactor: 0.95,
      minTemp: 1.0
    });
    
    layout.run();
    
    // 3. Map back to React Flow
    const flowNodes = cy.nodes().map(node => {
      const pos = node.position();
      const data = node.data();
      let color = '#3b82f6';
      if (data.type === 'Technology') color = '#10b981';
      if (data.type === 'Feature') color = '#8b5cf6';
      if (data.type === 'Architecture') color = '#f59e0b';
      if (data.type === 'Capability') color = '#ec4899';
      
      return {
        id: data.id,
        position: { x: pos.x, y: pos.y },
        data: { label: data.name || data.id },
        style: { 
          background: '#1a1d24', 
          color: '#fff',
          border: `2px solid ${color}`,
          borderRadius: '8px',
          padding: '10px',
          fontSize: '12px',
          minWidth: '120px',
          textAlign: 'center'
        },
      };
    });
    
    const flowEdges = cy.edges().map(edge => {
      const data = edge.data();
      return {
        id: data.id,
        source: data.source,
        target: data.target,
        label: data.label,
        animated: data.label === 'CALLS' || data.label === 'DEPENDS_ON',
        style: { stroke: '#4b5563' },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#4b5563',
        },
      };
    });
    
    setNodes(flowNodes);
    setEdges(flowEdges);
    
  }, [graph?.raw_nodes, graph?.raw_edges, setNodes, setEdges]);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  return (
    <div className={`p-6 animate-in flex flex-col ${isFullscreen ? 'fixed inset-0 z-50 bg-background' : 'h-[calc(100vh-80px)]'}`}>
      <div className="flex items-center justify-between mb-4 shrink-0">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <GitGraph size={20} className="text-primary" />
          Enterprise Knowledge Graph Explorer
        </h1>
        <div className="flex items-center gap-2">
          <button className="btn-secondary px-3" onClick={() => setIsFullscreen(!isFullscreen)}>
            {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
            <span className="ml-2">{isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}</span>
          </button>
        </div>
      </div>

      <div className="flex-1 glass rounded-2xl overflow-hidden relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          className="bg-black/20"
        >
          <Background color="#333" gap={16} />
          <Controls />
          <Panel position="top-right" className="bg-background/90 p-4 rounded-xl border border-border/50 backdrop-blur-md shadow-xl m-4 w-64">
            <h3 className="font-semibold flex items-center gap-2 mb-3">
              <Filter size={14} /> Legend
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#10b981]" /> Technology</div>
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#8b5cf6]" /> Feature</div>
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#ec4899]" /> Capability</div>
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#f59e0b]" /> Architecture</div>
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#3b82f6]" /> Source Code</div>
            </div>
            <div className="mt-4 pt-4 border-t border-border/50 space-y-1">
              <p className="text-xs text-muted-foreground flex justify-between">
                <span>Nodes</span>
                <span className="font-mono text-foreground">{graph?.nodes || 0}</span>
              </p>
              <p className="text-xs text-muted-foreground flex justify-between">
                <span>Edges</span>
                <span className="font-mono text-foreground">{graph?.edges || 0}</span>
              </p>
            </div>
          </Panel>
        </ReactFlow>
      </div>
    </div>
  );
}
