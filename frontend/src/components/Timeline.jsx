import useAgentStore from '../store/agentStore'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, X, Loader2, ListTree } from 'lucide-react'
import { cn } from '../lib/utils'

export default function Timeline() {
  // `history` is the key used by the updated agentStore (previously called `timeline`)
  // The `?? []` guard ensures we never call .map() on undefined.
  const history = useAgentStore((s) => s.history ?? [])

  return (
    <div className="bg-card rounded-xl border border-border flex flex-col h-[300px] shadow-sm">
      <div className="p-4 border-b border-border flex items-center gap-2 text-foreground">
        <ListTree size={18} className="text-primary" />
        <h3 className="font-medium">Execution Timeline</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence initial={false}>
          {history.length === 0 && (
            <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
              No actions yet. Run a goal to see the timeline.
            </div>
          )}
          {history.map((item, index) => {
            const isLast = index === history.length - 1
            
            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative flex gap-4"
              >
                {/* Connecting Line */}
                {!isLast && (
                  <div className="absolute left-3 top-8 bottom-[-16px] w-px bg-border z-0" />
                )}
                
                {/* Icon */}
                <div className="relative z-10 flex-shrink-0 mt-1">
                  <div className={cn(
                    "w-6 h-6 rounded-full flex items-center justify-center border transition-all duration-500",
                    item.verified === true && "bg-success/10 border-success/30 text-success",
                    item.verified === false && "bg-danger/10 border-danger/30 text-danger",
                    item.verified === 'pending' && "bg-primary/20 border-primary text-primary shadow-[0_0_10px_rgba(59,130,246,0.5)]"
                  )}>
                    {item.verified === true && <Check size={12} strokeWidth={3} />}
                    {item.verified === false && <X size={12} strokeWidth={3} />}
                    {item.verified === 'pending' && (
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                      </span>
                    )}
                  </div>
                </div>

                {/* Content */}
                <div className="flex flex-col pb-1">
                  <span className="text-xs text-muted-foreground font-mono mb-1">{item.time}</span>
                  <span className={cn(
                    "text-sm font-medium",
                    item.verified === false ? "text-danger" : "text-foreground"
                  )}>
                    {item.text}
                  </span>
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </div>
  )
}
