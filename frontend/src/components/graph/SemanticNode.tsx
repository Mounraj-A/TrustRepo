import { Handle, Position, NodeProps } from '@xyflow/react';
import { Package, GitBranch, Layers, Code2, Zap, FileCode2, Link2, Box } from 'lucide-react';

const TYPE_CONFIG: Record<string, { color: string, bg: string, icon: any }> = {
  Technology: { color: 'text-emerald-600', bg: 'bg-emerald-50 border-emerald-300', icon: Box },
  Feature: { color: 'text-violet-600', bg: 'bg-violet-50 border-violet-300', icon: Zap },
  Capability: { color: 'text-pink-600', bg: 'bg-pink-50 border-pink-300', icon: Package },
  Architecture: { color: 'text-amber-600', bg: 'bg-amber-50 border-amber-300', icon: Layers },
  Repository: { color: 'text-slate-800', bg: 'bg-slate-100 border-slate-400', icon: GitBranch },
  Folder: { color: 'text-slate-500', bg: 'bg-slate-50 border-slate-200', icon: FileCode2 },
  File: { color: 'text-slate-600', bg: 'bg-slate-50 border-slate-200', icon: FileCode2 },
  Symbol: { color: 'text-blue-600', bg: 'bg-blue-50 border-blue-300', icon: Code2 },
  Evidence: { color: 'text-teal-600', bg: 'bg-teal-50 border-teal-300', icon: Link2 },
  Default: { color: 'text-slate-600', bg: 'bg-white border-slate-200', icon: Box }
};

export default function SemanticNode({ data, selected }: NodeProps) {
  const typeStr = (data.type as string) || 'Default';
  const config = TYPE_CONFIG[typeStr] || TYPE_CONFIG.Default;
  const Icon = config.icon;

  return (
    <div 
      className={`min-w-[140px] px-4 py-3 rounded-xl border-2 transition-all shadow-sm flex flex-col gap-1 items-center justify-center
        ${config.bg} 
        ${selected ? 'ring-4 ring-primary/20 shadow-md border-primary' : ''}
      `}
    >
      {/* We use a large, invisible handle covering the node to make connections easier visually, 
          though layout will primarily drive the edges */}
      <Handle type="target" position={Position.Top} className="opacity-0" />
      
      <div className={`flex items-center gap-2 ${config.color}`}>
        <Icon size={14} />
        <span className="text-[10px] font-bold uppercase tracking-wider opacity-80">{typeStr}</span>
      </div>
      
      <div className="font-semibold text-xs text-slate-800 text-center break-all max-w-[180px]">
        {data.label as string}
      </div>

      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
}
