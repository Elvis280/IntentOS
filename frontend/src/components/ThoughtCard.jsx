import { BrainCircuit } from 'lucide-react'
import useAgentStore from '../store/agentStore'

export default function ThoughtCard() {
  const { thought } = useAgentStore()

  return (
    <div className="bg-card rounded-xl border border-border p-5 shadow-sm flex flex-col gap-3">
      <div className="flex items-center gap-2 text-warning">
        <BrainCircuit size={18} />
        <h3 className="text-sm font-medium uppercase tracking-wider">Current Thought</h3>
      </div>
      <p className="text-foreground font-mono text-sm leading-relaxed whitespace-pre-wrap">
        {thought || "Awaiting task..."}
      </p>
    </div>
  )
}
