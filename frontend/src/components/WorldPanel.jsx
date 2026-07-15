import { Globe, AppWindow, MousePointerClick, Type } from 'lucide-react'
import useAgentStore from '../store/agentStore'
import { motion } from 'framer-motion'

export default function WorldPanel() {
  // The store key is `world`, not `worldModel`.
  // The fallback `{}` with optional chaining below means no crash if the
  // polling response arrives slightly late on first render.
  const world = useAgentStore((s) => s.world ?? {})

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.05 }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 10, scale: 0.95 },
    show: { opacity: 1, y: 0, scale: 1 }
  }

  const CardSection = ({ title, icon: Icon, items, activeItem }) => (
    <div className="mb-4 last:mb-0">
      <div className="flex items-center gap-2 mb-2 text-muted-foreground">
        <Icon size={14} />
        <h4 className="text-xs font-semibold uppercase tracking-wider">{title}</h4>
      </div>
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="flex flex-wrap gap-2"
      >
        {activeItem && (
          <motion.span variants={itemVariants} className="px-2 py-1 bg-primary/20 text-primary border border-primary/30 rounded text-xs font-medium">
            {activeItem}
          </motion.span>
        )}
        {items?.map((item, i) => (
          item !== activeItem && (
            <motion.span variants={itemVariants} key={i} className="px-2 py-1 bg-surface border border-border rounded text-xs text-foreground">
              {item}
            </motion.span>
          )
        ))}
      </motion.div>
    </div>
  )

  return (
    <div className="bg-card rounded-xl border border-border shadow-sm p-4 flex flex-col h-full overflow-y-auto custom-scrollbar">
      <div className="flex items-center gap-2 text-foreground mb-4 border-b border-border pb-3">
        <Globe size={18} className="text-primary" />
        <h3 className="font-medium">World Model</h3>
      </div>
      
      <CardSection 
        title="Applications" 
        icon={AppWindow} 
        activeItem={world?.activeWindow}
        items={world?.applications} 
      />
      
      <CardSection 
        title="Detected Buttons" 
        icon={MousePointerClick} 
        items={world?.buttonsDetected} 
      />
      
      <CardSection 
        title="Visible Text" 
        icon={Type} 
        items={world?.visibleText} 
      />
    </div>
  )
}
