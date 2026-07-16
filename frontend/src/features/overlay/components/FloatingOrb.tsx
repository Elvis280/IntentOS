import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

type OrbState = 'idle' | 'listening' | 'thinking' | 'executing' | 'paused' | 'clarification' | 'completed'

interface OrbPayload {
  orbState: OrbState
  stage: string
  status: string
}

const ORB_STYLES: Record<OrbState, { color: string; glow: string; label: string }> = {
  idle:          { color: '#18181b', glow: 'rgba(255,255,255,0.05)',   label: '' },
  listening:     { color: '#0284c7', glow: 'rgba(2,132,199,0.45)',    label: 'Listening' },
  thinking:      { color: '#6d28d9', glow: 'rgba(109,40,217,0.45)',   label: 'Thinking' },
  executing:     { color: '#0891b2', glow: 'rgba(8,145,178,0.45)',    label: 'Executing' },
  paused:        { color: '#d97706', glow: 'rgba(217,119,6,0.40)',    label: 'Paused' },
  clarification: { color: '#b45309', glow: 'rgba(180,83,9,0.50)',     label: 'Awaiting Input' },
  completed:     { color: '#059669', glow: 'rgba(5,150,105,0.45)',    label: 'Done' },
}

const PULSE_VARIANTS = {
  idle:          { scale: [1, 1],       opacity: [0.6, 0.6] },
  listening:     { scale: [1, 1.18, 1], opacity: [0.9, 1, 0.9] },
  thinking:      { scale: [1, 1.1, 1],  opacity: [0.8, 1, 0.8] },
  executing:     { scale: [1, 1.14, 1], opacity: [1, 0.85, 1] },
  paused:        { scale: [1, 1],       opacity: [0.7, 0.7] },
  clarification: { scale: [1, 1.08, 1], opacity: [0.9, 1, 0.9] },
  completed:     { scale: [1, 1.2, 1],  opacity: [1, 0.8, 1] },
}

const PULSE_DURATION: Record<OrbState, number> = {
  idle: 0, listening: 0.9, thinking: 1.4, executing: 0.6,
  paused: 0, clarification: 1.1, completed: 0.8,
}

function tryTauriListen(handler: (payload: OrbPayload) => void): (() => void) | undefined {
  try {
    // @ts-ignore
    if (typeof window !== 'undefined' && window.__TAURI__) {
      let unlisten: (() => void) | undefined
      // @ts-ignore
      window.__TAURI__.event.listen('intentos:orb-state', (event: { payload: OrbPayload }) => {
        handler(event.payload)
      }).then((fn: () => void) => { unlisten = fn })
      return () => { unlisten?.() }
    }
  } catch { /* browser dev mode */ }
}

export function FloatingOrb() {
  const [orbState, setOrbState] = useState<OrbState>('idle')
  const [visible, setVisible] = useState(false)
  const [hideTimer, setHideTimer] = useState<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    const cleanup = tryTauriListen((payload) => {
      setOrbState(payload.orbState)
      if (payload.orbState === 'idle') {
        // Auto-hide 3s after going idle
        const t = setTimeout(() => setVisible(false), 3000)
        setHideTimer(t)
      } else {
        if (hideTimer) { clearTimeout(hideTimer); setHideTimer(null) }
        setVisible(true)
      }
    })
    return () => { cleanup?.(); if (hideTimer) clearTimeout(hideTimer) }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const { color, glow, label } = ORB_STYLES[orbState]
  const pulse = PULSE_VARIANTS[orbState]
  const duration = PULSE_DURATION[orbState]

  return (
    <div className="fixed bottom-8 right-8 flex flex-col items-center gap-2 select-none pointer-events-none z-50">
      <AnimatePresence>
        {visible && label && (
          <motion.span
            key="label"
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            className="text-[10px] font-medium text-white/70 tracking-wider"
          >
            {label}
          </motion.span>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {visible && (
          <motion.div
            key="orb"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.5, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 260, damping: 22 }}
          >
            {/* Glow ring */}
            <motion.div
              animate={{ boxShadow: `0 0 28px 8px ${glow}`, scale: pulse.scale, opacity: pulse.opacity }}
              transition={duration ? { duration, repeat: Infinity, ease: 'easeInOut' } : {}}
              style={{ borderRadius: '50%' }}
            >
              <motion.div
                animate={{ backgroundColor: color }}
                transition={{ duration: 0.4 }}
                className="w-12 h-12 rounded-full flex items-center justify-center"
                style={{ boxShadow: `0 0 0 2px rgba(255,255,255,0.08)` }}
              >
                {orbState === 'thinking' && (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1.8, repeat: Infinity, ease: 'linear' }}
                    className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white/80"
                  />
                )}
                {orbState === 'executing' && (
                  <motion.div
                    animate={{ scale: [1, 1.3, 1], opacity: [1, 0.6, 1] }}
                    transition={{ duration: 0.5, repeat: Infinity }}
                    className="w-3 h-3 rounded-full bg-white/70"
                  />
                )}
              </motion.div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
