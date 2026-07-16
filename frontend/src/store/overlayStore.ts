import { create } from 'zustand'

export type OverlayType = 
  | 'HighlightOverlay'
  | 'ConfirmationOverlay'
  | 'SelectionOverlay'
  | 'ProgressOverlay'
  | 'PreviewOverlay'

export type OverlayPosition = 'center' | 'cursor' | 'bottom-right' | { x: number, y: number }

export interface OverlayState {
  visible: boolean
  type: OverlayType | null
  position: OverlayPosition
  payload: any
  animationState: 'entering' | 'idle' | 'exiting'
  isInteractive: boolean
}

export interface OverlayStore extends OverlayState {
  showOverlay: (type: OverlayType, payload: any, position?: OverlayPosition, isInteractive?: boolean) => void
  hideOverlay: () => void
  setAnimationState: (state: 'entering' | 'idle' | 'exiting') => void
  setInteractive: (interactive: boolean) => void
}

const initialState: OverlayState = {
  visible: false,
  type: null,
  position: 'center',
  payload: null,
  animationState: 'idle',
  isInteractive: false,
}

export const useOverlayStore = create<OverlayStore>((set) => ({
  ...initialState,
  
  showOverlay: (type, payload, position = 'center', isInteractive = false) => set({
    visible: true,
    type,
    payload,
    position,
    isInteractive,
    animationState: 'entering',
  }),

  hideOverlay: () => set({ animationState: 'exiting' }), // Components should listen to exiting and call clear after animation

  setAnimationState: (state) => set((prev) => {
    if (state === 'idle' && prev.animationState === 'exiting') {
      return { ...initialState } // Reset fully after exiting
    }
    return { animationState: state }
  }),

  setInteractive: (interactive) => set({ isInteractive: interactive })
}))
