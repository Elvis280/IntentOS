import { Mic } from 'lucide-react'
import { useState } from 'react'

export function VoicePlaceholder() {
  const [clicked, setClicked] = useState(false)

  const handleClick = () => {
    setClicked(true)
    setTimeout(() => setClicked(false), 2500)
  }

  return (
    <div className="flex items-center gap-3">
      <button
        id="voice-btn"
        onClick={handleClick}
        title="Voice input — coming soon"
        className="w-8 h-8 flex items-center justify-center rounded-full border border-white/[0.08] bg-white/[0.03] text-zinc-600 hover:text-zinc-400 hover:border-white/[0.14] hover:bg-white/[0.06] transition-all"
      >
        <Mic size={14} />
      </button>

      {clicked && (
        <span className="text-[10px] text-zinc-600 italic whitespace-nowrap">
          Voice coming soon
        </span>
      )}
    </div>
  )
}
