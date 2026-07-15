import GoalInput from '../components/GoalInput'
import StatusCard from '../components/StatusCard'
import ThoughtCard from '../components/ThoughtCard'
import ActionCard from '../components/ActionCard'
import ProgressCard from '../components/ProgressCard'
import Timeline from '../components/Timeline'
import ScreenshotPanel from '../components/ScreenshotPanel'
import WorldPanel from '../components/WorldPanel'
import SystemInfo from '../components/SystemInfo'

export default function Overview() {
  return (
    <div className="flex flex-1 overflow-hidden">
      {/* Center Panel (Workspace) */}
      <div className="flex-1 p-6 flex flex-col gap-6 overflow-y-auto custom-scrollbar border-r border-border min-w-[500px]">
        <GoalInput />
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <StatusCard />
          <ProgressCard />
        </div>

        <ThoughtCard />
        <ActionCard />
        <Timeline />
      </div>

      {/* Right Panel (Context) */}
      <div className="w-[400px] flex-shrink-0 p-6 flex flex-col gap-6 overflow-y-auto custom-scrollbar bg-surface/30">
        <div className="h-[280px]">
          <ScreenshotPanel />
        </div>
        <div className="flex-1 min-h-[300px]">
          <WorldPanel />
        </div>
        <div>
          <SystemInfo />
        </div>
      </div>
    </div>
  )
}
