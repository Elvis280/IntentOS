import { useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { eventBus } from '../../services/eventBus'
import { useOverlayStore } from '../../store/overlayStore'
import { OverlayManager } from './OverlayManager'
import { FloatingOrb } from './components/FloatingOrb'

export function OverlayPage() {
  const { isInteractive, showOverlay, hideOverlay } = useOverlayStore()

  // Toggle click-through at the OS level using the Rust command
  useEffect(() => {
    // If not interactive, ignore cursor events (click-through)
    invoke('set_click_through', { ignore: !isInteractive }).catch(console.error)
  }, [isInteractive])

  // Listen for Events
  useEffect(() => {
    const unlistenShow = eventBus.listen<any>('overlay:show', (event) => {
      const { type, payload, position, interactive } = event.payload
      showOverlay(type, payload, position, interactive)
    })

    const unlistenHide = eventBus.listen('overlay:hide', () => {
      hideOverlay()
    })

    return () => {
      unlistenShow.then(fn => fn())
      unlistenHide.then(fn => fn())
    }
  }, [showOverlay, hideOverlay])

  return (
    <div className="w-screen h-screen overflow-hidden bg-transparent">
      <OverlayManager />
      <FloatingOrb />
    </div>
  )
}
