interface HighlightOverlayProps {
  payload: {
    width: number
    height: number
  }
}

export function HighlightOverlay({ payload }: HighlightOverlayProps) {
  return (
    <div 
      className="border-2 border-sky-400 bg-sky-400/10 rounded pointer-events-none transition-all duration-300"
      style={{ width: payload.width || 200, height: payload.height || 60 }}
    />
  )
}
