import { Check, X } from 'lucide-react'
import { uiEventDispatcher } from '../../../services/uiEventDispatcher'

interface ConfirmationOverlayProps {
  payload: {
    message: string
  }
}

export function ConfirmationOverlay({ payload }: ConfirmationOverlayProps) {
  const onConfirm = () => {
    // In a real app, emit a specific event back to the runtime
    uiEventDispatcher.hideOverlay()
  }

  const onCancel = () => {
    uiEventDispatcher.hideOverlay()
  }

  return (
    <div className="bg-[#1c1d1f]/90 backdrop-blur-md border border-white/10 rounded-xl p-4 flex flex-col items-center gap-4 max-w-sm">
      <p className="text-zinc-200 text-sm font-medium text-center">{payload.message}</p>
      <div className="flex gap-2 w-full">
        <button 
          onClick={onCancel}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-1.5 rounded bg-white/[0.05] hover:bg-white/[0.1] text-zinc-300 text-xs transition"
        >
          <X size={14} /> Cancel
        </button>
        <button 
          onClick={onConfirm}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-1.5 rounded bg-sky-600 hover:bg-sky-500 text-white text-xs transition"
        >
          <Check size={14} /> Confirm
        </button>
      </div>
    </div>
  )
}
