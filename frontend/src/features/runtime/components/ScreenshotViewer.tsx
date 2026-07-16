import { Monitor } from 'lucide-react'

interface ScreenshotViewerProps {
  /** Base64-encoded PNG screenshot from the backend. */
  screenshot?: string
}

export function ScreenshotViewer({ screenshot }: ScreenshotViewerProps) {
  return (
    <div className="flex flex-col h-full bg-[#0d0e10] rounded-lg border border-white/[0.06] overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/[0.06]">
        <Monitor size={13} className="text-zinc-500" />
        <span className="text-xs font-medium text-zinc-500 tracking-wider uppercase">Live View</span>
      </div>

      {/* Image area */}
      <div className="flex-1 flex items-center justify-center p-3 min-h-0">
        {screenshot ? (
          <img
            src={`data:image/png;base64,${screenshot}`}
            alt="Live desktop screenshot"
            className="w-full h-full object-contain rounded"
          />
        ) : (
          <div className="flex flex-col items-center gap-3 text-center">
            <div className="w-10 h-10 rounded-full bg-white/[0.04] flex items-center justify-center border border-white/[0.06]">
              <Monitor size={18} className="text-zinc-600" />
            </div>
            <p className="text-xs text-zinc-600">No screenshot yet</p>
          </div>
        )}
      </div>
    </div>
  )
}
