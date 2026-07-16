import { useOverlayStore } from '../../store/overlayStore'
import { OverlayContainer } from './components/OverlayContainer'
import { HighlightOverlay } from './components/HighlightOverlay'
import { ConfirmationOverlay } from './components/ConfirmationOverlay'
import { SelectionOverlay } from './components/SelectionOverlay'
import { ProgressOverlay } from './components/ProgressOverlay'
import { PreviewOverlay } from './components/PreviewOverlay'
import { AnimatePresence } from 'framer-motion'

export function OverlayManager() {
  const { visible, type, payload, position } = useOverlayStore()

  if (!visible || !type) return null

  let OverlayComponent = null
  switch (type) {
    case 'HighlightOverlay': OverlayComponent = HighlightOverlay; break;
    case 'ConfirmationOverlay': OverlayComponent = ConfirmationOverlay; break;
    case 'SelectionOverlay': OverlayComponent = SelectionOverlay; break;
    case 'ProgressOverlay': OverlayComponent = ProgressOverlay; break;
    case 'PreviewOverlay': OverlayComponent = PreviewOverlay; break;
    default: return null;
  }

  return (
    <AnimatePresence>
      {visible && (
        <OverlayContainer position={position} type={type}>
          <OverlayComponent payload={payload} />
        </OverlayContainer>
      )}
    </AnimatePresence>
  )
}
