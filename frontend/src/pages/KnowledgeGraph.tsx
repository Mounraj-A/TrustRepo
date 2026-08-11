import { useEffect, useState, useMemo, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { 
  GitGraph, Maximize2, Minimize2, Filter, 
  Search, Scan, Undo2, Map, Layout, Zap 
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
  Panel,
  Node,
  Edge,
  MiniMap,
  useReactFlow,
  ReactFlowProvider,
  Position
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';

import SemanticNode from '@/components/graph/SemanticNode';
import SemanticEdge from '@/components/graph/SemanticEdge';

const nodeTypes = { semantic: SemanticNode };
const edgeTypes = { semantic: SemanticEdge };

const VIEWS = ['Overview', 'Code', 'Technology', 'Architecture', 'Custom'] as const;
type View = typeof VIEWS[number];

// Dagre Layout Helper
const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  // Add some spacing to make it breathable
  dagreGraph.setGraph({ rankdir: direction, ranksep: 100, nodesep: 60 });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 160, height: 70 });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      targetPosition: (direction === 'TB' ? Position.Top : Position.Left) as Position,
      sourcePosition: (direction === 'TB' ? Position.Bottom : Position.Right) as Position,
      position: {
        x: nodeWithPosition.x - 160 / 2,
        y: nodeWithPosition.y - 70 / 2,
      },
    };
  });

  return { layoutedNodes, layoutedEdges: edges };
};

function KnowledgeGraphInner() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  const { fitView, setCenter } = useReactFlow();
  
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [activeView, setActiveView] = useState<View>('Overview');
  const [search, setSearch] = useState('');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [focusMode, setFocusMode] = useState(false);
  
  // Custom View Filters
  const [customNodeTypes, setCustomNodeTypes] = useState<Set<string>>(new Set(['Technology', 'Feature', 'Capability']));
  
  const graph = analysisResult?.graph_metrics;
  const rawNodes = graph?.raw_nodes || [];
  const rawEdges = graph?.raw_edges || [];

  // 1. Filter Nodes/Edges based on View
  const filteredData = useMemo(() => {
    let allowedTypes = new Set<string>();
    
    if (activeView === 'Overview') {
      allowedTypes = new Set(['Repository', 'Technology', 'Feature', 'Capability', 'Architecture']);
    } else if (activeView === 'Code') {
      allowedTypes = new Set(['Folder', 'File', 'Symbol', 'Class', 'Method', 'Function', 'Dependency']);
    } else if (activeView === 'Technology') {
      allowedTypes = new Set(['Technology', 'Feature', 'Capability']);
    } else if (activeView === 'Architecture') {
      allowedTypes = new Set(['Architecture', 'Capability', 'Feature']);
    } else {
      allowedTypes = customNodeTypes;
    }

    const filteredNodes = rawNodes.filter(n => allowedTypes.has(n.type));
    const validNodeIds = new Set(filteredNodes.map(n => n.id));
    
    // Only keep edges where both source and target are in the filtered nodes
    const filteredEdges = rawEdges.filter(e => validNodeIds.has(e.source) && validNodeIds.has(e.target));
    
    return { nodes: filteredNodes, edges: filteredEdges };
  }, [rawNodes, rawEdges, activeView, customNodeTypes]);

  // 2. Apply Focus Mode (if active)
  const displayData = useMemo(() => {
    if (!focusMode || !selectedNodeId) return filteredData;
    
    const focusNode = rawNodes.find(n => n.id === selectedNodeId);
    if (!focusNode) return filteredData;

    // Direct neighbors
    const connectedEdgeIds = new Set<string>();
    const connectedNodeIds = new Set<string>([selectedNodeId]);

    rawEdges.forEach(e => {
      if (e.source === selectedNodeId) {
        connectedNodeIds.add(e.target);
        connectedEdgeIds.add(`${e.source}-${e.target}`);
      }
      if (e.target === selectedNodeId) {
        connectedNodeIds.add(e.source);
        connectedEdgeIds.add(`${e.source}-${e.target}`);
      }
    });

    const displayNodes = rawNodes.filter(n => connectedNodeIds.has(n.id));
    const displayEdges = rawEdges.filter(e => connectedEdgeIds.has(`${e.source}-${e.target}`));

    return { nodes: displayNodes, edges: displayEdges };
  }, [filteredData, rawNodes, rawEdges, focusMode, selectedNodeId]);

  // 3. Layout with Dagre
  useEffect(() => {
    if (!displayData.nodes.length) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const flowNodes: Node[] = displayData.nodes.map(n => ({
      id: n.id,
      position: { x: 0, y: 0 },
      data: { ...n, label: n.name || n.id },
      type: 'semantic',
    }));

    const flowEdges: Edge[] = displayData.edges.map(e => ({
      id: `${e.source}-${e.target}`,
      source: e.source,
      target: e.target,
      label: e.type,
      type: 'semantic',
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#cbd5e1',
      },
    }));

    const { layoutedNodes, layoutedEdges } = getLayoutedElements(flowNodes, flowEdges, 'TB');
    
    setNodes(layoutedNodes);
    setEdges(layoutedEdges);

    // Give it a tick to render then fit
    setTimeout(() => {
      fitView({ padding: 0.2, duration: 800 });
    }, 50);

  }, [displayData, setNodes, setEdges, fitView]);

  // 4. Node Selection & Interaction
  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNodeId(node.id);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null);
    setFocusMode(false);
  }, []);

  // Sync selected state to edges/nodes
  useEffect(() => {
    setNodes(nds => nds.map(n => ({
      ...n,
      selected: n.id === selectedNodeId
    })));
    setEdges(eds => eds.map(e => ({
      ...e,
      selected: e.source === selectedNodeId || e.target === selectedNodeId,
      style: {
        ...e.style,
        zIndex: (e.source === selectedNodeId || e.target === selectedNodeId) ? 1000 : 0
      }
    })));
  }, [selectedNodeId, setNodes, setEdges]);

  // Handle Search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!search) return;
    const q = search.toLowerCase();
    const match = nodes.find(n => 
      ((n.data.label as string) || '').toLowerCase().includes(q) || 
      ((n.data.type as string) || '').toLowerCase().includes(q)
    );

    if (match) {
      setSelectedNodeId(match.id);
      setCenter(match.position.x + 80, match.position.y + 35, { zoom: 1.5, duration: 800 });
    }
  };

  const selectedNodeData = rawNodes.find(n => n.id === selectedNodeId);
  const selectedNodeEdges = rawEdges.filter(e => e.source === selectedNodeId || e.target === selectedNodeId);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const content = (
    <div className={`flex flex-col animate-in ${isFullscreen ? 'fixed inset-0 z-[9999] bg-white p-6' : 'h-[calc(100vh-80px)] p-6'}`}>
      
      {/* ── Header & Controls ────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-4 shrink-0 gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <GitGraph size={24} className="text-primary" />
            Knowledge Graph Explorer
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Displaying {nodes.length} nodes and {edges.length} relationships
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Search */}
          <form onSubmit={handleSearch} className="relative w-48 lg:w-64">
            <Search className="absolute left-2.5 top-2 text-slate-400" size={14} />
            <input 
              type="text" 
              placeholder="Search nodes..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-lg pl-8 pr-3 py-1.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all shadow-sm"
            />
          </form>

          {/* Graph Controls */}
          <div className="flex bg-white rounded-lg border border-slate-200 p-1 shadow-sm">
            <button 
              onClick={() => fitView({ duration: 800 })}
              className="p-1.5 hover:bg-slate-100 rounded text-slate-600 transition-colors"
              title="Fit Graph"
            >
              <Scan size={16} />
            </button>
            <button 
              onClick={() => {
                // Force layout recalculation
                const { layoutedNodes, layoutedEdges } = getLayoutedElements(nodes, edges, 'TB');
                setNodes(layoutedNodes);
                setEdges(layoutedEdges);
                setTimeout(() => fitView({ duration: 800 }), 50);
              }}
              className="p-1.5 hover:bg-slate-100 rounded text-slate-600 transition-colors"
              title="Reset Layout"
            >
              <Layout size={16} />
            </button>
          </div>

          <button className="btn-secondary px-3" onClick={() => setIsFullscreen(!isFullscreen)}>
            {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
            <span className="ml-2 hidden sm:inline">{isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}</span>
          </button>
        </div>
      </div>

      {/* ── View Tabs ────────────────────────────────────────────────── */}
      <div className="flex items-center gap-6 border-b border-border mb-4 shrink-0">
        {VIEWS.map(view => (
          <button 
            key={view}
            className={`pb-3 text-sm font-medium transition-colors border-b-2 ${activeView === view ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
            onClick={() => {
              setActiveView(view);
              setFocusMode(false);
              setSelectedNodeId(null);
            }}
          >
            {view}
          </button>
        ))}
      </div>

      {/* ── Graph Canvas ─────────────────────────────────────────────── */}
      <div className="flex-1 flex gap-4 min-h-0 relative">
        <div className="flex-1 glass rounded-2xl overflow-hidden relative border border-border shadow-sm bg-slate-50/50">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            minZoom={0.1}
            maxZoom={4}
            fitView
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#cbd5e1" gap={20} size={2} />
            <Controls className="bg-white border-slate-200 shadow-sm" showInteractive={false} />
          </ReactFlow>
        </div>

        {/* ── Right Panel (Details / Filters) ────────────────────────── */}
        <AnimatePresence mode="wait">
          {selectedNodeData ? (
            <motion.div 
              key="node-details"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="w-80 glass rounded-2xl flex flex-col h-full overflow-hidden shadow-sm border border-border bg-white"
            >
              <div className="p-4 border-b border-slate-100 bg-slate-50/50">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-slate-800 break-all">{selectedNodeData.name || selectedNodeData.id.split('.').pop()}</h3>
                    <div className="mt-1 flex items-center gap-2">
                      <span className="status-badge bg-primary/10 text-primary border border-primary/20">{selectedNodeData.type}</span>
                    </div>
                  </div>
                  <button onClick={() => setSelectedNodeId(null)} className="text-slate-400 hover:text-slate-600">✕</button>
                </div>
                
                <div className="mt-4 flex gap-2">
                  <button 
                    onClick={() => setFocusMode(!focusMode)}
                    className={`flex-1 py-1.5 text-xs font-semibold rounded-md border flex justify-center items-center gap-1 transition-colors ${focusMode ? 'bg-primary text-primary-foreground border-primary' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}`}
                  >
                    <Scan size={12} /> {focusMode ? 'Exit Focus' : 'Focus Mode'}
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-6">
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Properties</h4>
                  <div className="space-y-2 text-sm">
                    {Object.entries(selectedNodeData.properties || {}).filter(([k]) => k !== 'name' && k !== 'type').map(([key, value]) => (
                      <div key={key} className="flex flex-col bg-slate-50 p-2 rounded-lg border border-slate-100">
                        <span className="text-[10px] text-slate-500 uppercase">{key}</span>
                        <span className="font-mono text-slate-700 truncate">{String(value)}</span>
                      </div>
                    ))}
                    {Object.keys(selectedNodeData.properties || {}).length === 0 && (
                      <p className="text-xs text-muted-foreground italic">No additional properties.</p>
                    )}
                  </div>
                </div>

                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Relationships ({selectedNodeEdges.length})</h4>
                  <div className="space-y-2">
                    {selectedNodeEdges.map((e, i) => {
                      const isOut = e.source === selectedNodeId;
                      const connectedId = isOut ? e.target : e.source;
                      return (
                        <div key={i} className="flex flex-col bg-slate-50 p-2 rounded-lg border border-slate-100 text-xs">
                          <span className="text-[10px] font-bold text-slate-500 tracking-wider">
                            {isOut ? `${e.type} ➔` : `➔ ${e.type}`}
                          </span>
                          <span 
                            className="font-mono text-primary truncate cursor-pointer hover:underline"
                            onClick={() => {
                              setSelectedNodeId(connectedId);
                              const node = nodes.find(n => n.id === connectedId);
                              if (node) setCenter(node.position.x + 80, node.position.y + 35, { zoom: 1.5, duration: 800 });
                            }}
                          >
                            {connectedId.split('.').pop()}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            </motion.div>
          ) : activeView === 'Custom' ? (
            <motion.div 
              key="custom-filters"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="w-64 glass rounded-2xl flex flex-col h-full overflow-hidden shadow-sm border border-border bg-white"
            >
              <div className="p-4 border-b border-slate-100 bg-slate-50/50">
                <h3 className="font-semibold text-sm flex items-center gap-2"><Filter size={16} className="text-primary"/> Custom Filters</h3>
              </div>
              <div className="p-4 overflow-y-auto">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Node Types</p>
                <div className="space-y-2">
                  {Array.from(new Set(rawNodes.map(n => n.type))).map(type => (
                    <label key={type} className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={customNodeTypes.has(type)}
                        onChange={(e) => {
                          const newTypes = new Set(customNodeTypes);
                          if (e.target.checked) newTypes.add(type);
                          else newTypes.delete(type);
                          setCustomNodeTypes(newTypes);
                        }}
                        className="rounded border-slate-300 text-primary focus:ring-primary"
                      />
                      {type}
                    </label>
                  ))}
                </div>
              </div>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>
    </div>
  );

  if (isFullscreen) {
    return createPortal(content, document.body);
  }

  return content;
}

export default function KnowledgeGraph() {
  return (
    <ReactFlowProvider>
      <KnowledgeGraphInner />
    </ReactFlowProvider>
  );
}
