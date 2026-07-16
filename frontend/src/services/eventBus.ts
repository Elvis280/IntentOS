import { emit, listen, type EventCallback, type UnlistenFn } from '@tauri-apps/api/event'

export const eventBus = {
  /**
   * Emit an event globally across all Tauri windows.
   */
  emit: async <T>(eventName: string, payload?: T): Promise<void> => {
    try {
      await emit(eventName, payload)
    } catch (err) {
      console.error(`Failed to emit event ${eventName}:`, err)
    }
  },

  /**
   * Listen for an event globally across all Tauri windows.
   */
  listen: async <T>(eventName: string, handler: EventCallback<T>): Promise<UnlistenFn> => {
    try {
      return await listen<T>(eventName, handler)
    } catch (err) {
      console.error(`Failed to listen to event ${eventName}:`, err)
      return () => {}
    }
  }
}
