import { Terminal } from 'lucide-react'
import useAgentStore from '../store/agentStore'
import { motion } from 'framer-motion'

export default function ActionCard() {
  const { action } = useAgentStore()

  if (!action) return null

  return (
    <div className="bg-card rounded-xl border border-primary/30 p-5 shadow-[0_0_20px_rgba(59,130,246,0.1)] flex flex-col gap-3 relative overflow-hidden transition-all duration-700 hover:shadow-[0_0_25px_rgba(59,130,246,0.15)]">
      {/* Background accent */}
      <div className="absolute top-0 right-0 p-16 bg-primary/5 rounded-bl-full -z-0"></div>

      <div className="flex items-center gap-2 text-primary relative z-10">
        <Terminal size={18} />
        <h3 className="text-sm font-medium uppercase tracking-wider">Next Action</h3>
      </div>
      
      <motion.div 
        key={action.type + JSON.stringify(action.payload)}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <span className="px-3 py-1 bg-primary/10 text-primary rounded-md font-mono text-sm font-bold">
            {action.type}
          </span>
        </div>
        {action.payload && (
          <div className="bg-surface border border-border rounded-lg p-3 overflow-x-auto">
            <code className="text-muted-foreground text-sm font-mono whitespace-pre">
              {typeof action.payload === 'object' ? JSON.stringify(action.payload, null, 2) : action.payload}
            </code>
          </div>
        )}
      </motion.div>
    </div>
  )
}
