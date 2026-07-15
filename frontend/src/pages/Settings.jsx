import { Settings as SettingsIcon } from 'lucide-react'
import { motion } from 'framer-motion'

export default function Settings() {
  return (
    <div className="p-8 flex-1 overflow-y-auto custom-scrollbar">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-primary/10 p-3 rounded-xl border border-primary/20">
          <SettingsIcon className="text-primary" size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground">Configure agent behavior and models.</p>
        </div>
      </div>

      <div className="max-w-3xl space-y-8">
        <section>
          <h2 className="text-lg font-medium text-foreground mb-4 border-b border-border pb-2">Connection</h2>
          <div className="grid gap-4">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">Backend URL</label>
              <input type="text" defaultValue="http://localhost:8000" className="w-full bg-surface border border-border rounded-lg px-4 py-2 text-foreground focus:outline-none focus:border-primary transition-colors" />
            </div>
          </div>
        </section>

        <section>
          <h2 className="text-lg font-medium text-foreground mb-4 border-b border-border pb-2">AI Configuration</h2>
          <div className="grid gap-4">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">Reasoner Model</label>
              <select className="w-full bg-surface border border-border rounded-lg px-4 py-2 text-foreground focus:outline-none focus:border-primary transition-colors">
                <option>Gemini Flash Lite Latest</option>
                <option>Gemini 1.5 Pro</option>
              </select>
            </div>
          </div>
        </section>

        <section>
          <h2 className="text-lg font-medium text-foreground mb-4 border-b border-border pb-2">Execution Preferences</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between bg-card p-4 rounded-xl border border-border">
              <div>
                <h4 className="font-medium text-foreground">Auto-Execute Mode</h4>
                <p className="text-sm text-muted-foreground">Run actions immediately without waiting for confirmation.</p>
              </div>
              <div className="w-12 h-6 bg-primary rounded-full relative cursor-pointer">
                <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div>
              </div>
            </div>
            
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Delay Between Steps (ms)</label>
                <input type="number" defaultValue={1500} className="w-full bg-surface border border-border rounded-lg px-4 py-2 text-foreground focus:outline-none focus:border-primary transition-colors" />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Maximum Steps per Run</label>
                <input type="number" defaultValue={20} className="w-full bg-surface border border-border rounded-lg px-4 py-2 text-foreground focus:outline-none focus:border-primary transition-colors" />
              </div>
            </div>
          </div>
        </section>
        
        <div className="flex justify-end pt-4">
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bg-primary hover:bg-primary/90 text-primary-foreground px-6 py-2 rounded-lg font-medium transition-colors shadow-sm hover:shadow-[0_4px_15px_rgba(59,130,246,0.3)]"
          >
            Save Changes
          </motion.button>
        </div>
      </div>
    </div>
  )
}
