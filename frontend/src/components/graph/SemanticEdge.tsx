import { BaseEdge, EdgeLabelRenderer, EdgeProps, getBezierPath, getSmoothStepPath } from '@xyflow/react';

export default function SemanticEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  label,
  selected,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <>
      <BaseEdge 
        path={edgePath} 
        markerEnd={markerEnd} 
        style={{
          ...style,
          strokeWidth: selected ? 2 : 1.5,
          stroke: selected ? '#6366f1' : '#cbd5e1', // Primary or slate-300
          transition: 'all 0.3s ease',
        }} 
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
            pointerEvents: 'all',
            opacity: selected ? 1 : 0, // Only show label when selected or hovered (we handle hover at graph level if possible, or just selected)
            transition: 'opacity 0.2s',
          }}
          className="nodrag nopan"
        >
          <div className="bg-white/95 backdrop-blur px-2 py-1 rounded-md text-[10px] font-bold tracking-wider uppercase text-slate-600 shadow-sm border border-slate-200">
            {label}
          </div>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}
