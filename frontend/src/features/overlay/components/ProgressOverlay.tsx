import { Loader2 } from 'lucide-react'

interface ProgressOverlayProps {
  payload: {
    message: string
  }
}

export function ProgressOverlay({ payload }: ProgressOverlayProps) {
  return (
    <div className="bg-[#1c1d1f]/90 backdrop-blur-md border border-white/10 rounded-full px-4 py-2 flex items-center gap-3 shadow-lg">
      <Loader2 size={14} className="text-sky-400 animate-spin" />
      <span className="text-xs text-zinc-200 font-medium">{payload.message}</span>
    </div>
  )
}
