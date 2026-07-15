import { Eye } from 'lucide-react'
import ScreenshotPanel from '../components/ScreenshotPanel'
import WorldPanel from '../components/WorldPanel'
import useAgentStore from '../store/agentStore'

export default function Vision() {
  const { worldModel } = useAgentStore()
  
  return (
    <div className="p-8 flex-1 overflow-y-auto custom-scrollbar">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-primary/10 p-3 rounded-xl border border-primary/20">
          <Eye className="text-primary" size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Vision Analysis</h1>
          <p className="text-muted-foreground">Current screen context and AI bounding boxes.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="h-[500px]">
          <ScreenshotPanel />
        </div>
        <div className="h-[500px]">
          <WorldPanel />
        </div>
      </div>

      <div className="mt-8 bg-card rounded-xl border border-border p-6 shadow-sm">
        <h3 className="font-medium text-foreground mb-4">Raw World Model JSON</h3>
        <pre className="bg-surface p-4 rounded-lg overflow-x-auto text-muted-foreground font-mono text-sm border border-border">
          {JSON.stringify(worldModel, null, 2)}
        </pre>
      </div>
    </div>
  )
}
