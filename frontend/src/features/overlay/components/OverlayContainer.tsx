import { motion } from 'framer-motion'
import { ReactNode } from 'react'
import type { OverlayPosition } from '../../../store/overlayStore'

interface OverlayContainerProps {
  position: OverlayPosition
  type: string
  children: ReactNode
}

export function OverlayContainer({ position, type, children }: OverlayContainerProps) {
  let style: React.CSSProperties = {}
  let layoutClasses = 'absolute flex '

  if (position === 'center') {
    layoutClasses += 'inset-0 items-center justify-center'
  } else if (position === 'bottom-right') {
    layoutClasses += 'bottom-8 right-8 justify-end'
  } else if (typeof position === 'object') {
    style = { left: position.x, top: position.y }
  }

  return (
    <div className={`${layoutClasses} pointer-events-none`} style={style}>
      <motion.div
        initial={{ opacity: 0, y: 10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.2, ease: "easeOut" }}
        className="pointer-events-auto shadow-2xl"
      >
        {children}
      </motion.div>
    </div>
  )
}
