import { Check, X, ArrowRight } from 'lucide-react'
import { uiEventDispatcher } from '../../../services/uiEventDispatcher'

interface PreviewOverlayProps {
  payload: {
    title: string
    beforeImage?: string
    afterImage?: string
    beforeText?: string
    afterText?: string
  }
}

export function PreviewOverlay({ payload }: PreviewOverlayProps) {
  return (
    <div className="bg-[#1c1d1f]/95 backdrop-blur-md border border-white/10 rounded-xl p-4 flex flex-col gap-4 max-w-lg shadow-2xl">
      <div className="flex justify-between items-center border-b border-white/5 pb-2">
        <span className="text-zinc-200 text-sm font-semibold">{payload.title}</span>
        <span className="text-sky-400 text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded bg-sky-900/30">Preview</span>
      </div>

      <div className="flex items-center gap-4">
        {/* Before */}
        <div className="flex-1 flex flex-col items-center gap-2">
          <span className="text-[10px] text-zinc-500 uppercase tracking-widest">Before</span>
          <div className="w-full h-32 bg-white/5 rounded border border-white/5 flex items-center justify-center text-xs text-zinc-400 overflow-hidden">
             {payload.beforeImage ? <img src={payload.beforeImage} alt="Before" className="object-contain w-full h-full" /> : payload.beforeText}
          </div>
        </div>

        <ArrowRight size={16} className="text-zinc-600 flex-shrink-0" />

        {/* After */}
        <div className="flex-1 flex flex-col items-center gap-2">
          <span className="text-[10px] text-zinc-500 uppercase tracking-widest">After</span>
          <div className="w-full h-32 bg-white/5 rounded border border-sky-500/30 flex items-center justify-center text-xs text-zinc-200 overflow-hidden relative">
             <div className="absolute inset-0 bg-sky-500/10" />
             {payload.afterImage ? <img src={payload.afterImage} alt="After" className="object-contain w-full h-full relative z-10" /> : <span className="relative z-10">{payload.afterText}</span>}
          </div>
        </div>
      </div>

      <div className="flex gap-2 w-full mt-2">
        <button 
          onClick={() => uiEventDispatcher.hideOverlay()}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded bg-white/[0.05] hover:bg-white/[0.1] text-zinc-300 text-xs font-medium transition"
        >
          <X size={14} /> Discard
        </button>
        <button 
          onClick={() => uiEventDispatcher.hideOverlay()}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded bg-sky-600 hover:bg-sky-500 text-white text-xs font-medium transition shadow-lg shadow-sky-900/20"
        >
          <Check size={14} /> Apply Changes
        </button>
      </div>
    </div>
  )
}
