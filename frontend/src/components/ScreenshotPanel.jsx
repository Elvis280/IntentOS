import { MonitorPlay } from 'lucide-react'
import useAgentStore from '../store/agentStore'
import { motion } from 'framer-motion'

export default function ScreenshotPanel() {
  const { screenshotUrl, status } = useAgentStore()
  const isScanning = status === 'Observing' || status === 'Verifying'

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden shadow-sm flex flex-col h-full">
      <div className="p-3 border-b border-border bg-surface/50 flex items-center justify-between">
        <div className="flex items-center gap-2 text-foreground">
          <MonitorPlay size={16} className="text-primary" />
          <h3 className="text-sm font-medium">Live Desktop</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-danger opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-danger"></span>
          </span>
          <span className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Live</span>
        </div>
      </div>
      
      <div className="flex-1 bg-black relative p-2 overflow-hidden">
        <motion.img 
          key={screenshotUrl}
          initial={{ opacity: 0.8 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          src={screenshotUrl} 
          alt="Desktop screen" 
          className="w-full h-full object-cover rounded-md border border-border/50"
        />
        
        {/* Scanning Laser Animation */}
        {isScanning && (
          <motion.div
            className="absolute top-0 left-0 w-full h-1 bg-primary/50 shadow-[0_0_15px_rgba(59,130,246,0.8)] z-10"
            initial={{ top: '0%' }}
            animate={{ top: '100%' }}
            transition={{
              duration: 2,
              ease: "linear",
              repeat: Infinity,
            }}
          />
        )}
      </div>
    </div>
  )
}
