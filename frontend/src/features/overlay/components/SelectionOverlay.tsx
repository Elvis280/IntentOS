interface SelectionOverlayProps {
  payload: {
    options: Array<{ id: string, label: string, x: number, y: number }>
  }
}

export function SelectionOverlay({ payload }: SelectionOverlayProps) {
  return (
    <>
      {payload.options.map((opt, i) => (
        <div 
          key={opt.id}
          className="absolute flex items-center justify-center w-6 h-6 rounded-full bg-sky-500 text-white text-[10px] font-bold shadow-md cursor-pointer hover:scale-110 hover:bg-sky-400 transition-all border border-sky-300"
          style={{ left: opt.x, top: opt.y, transform: 'translate(-50%, -50%)' }}
        >
          {i + 1}
        </div>
      ))}
    </>
  )
}
