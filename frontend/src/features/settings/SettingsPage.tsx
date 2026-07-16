import { useEffect, useState } from 'react'
import { Settings, Loader2, Save, CheckCircle2 } from 'lucide-react'
import { agentApi } from '../../services/agentApi'
import type { AppSettings } from '../../types/agent'

function SectionTitle({ title }: { title: string }) {
  return <h2 className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600 mb-3 mt-5">{title}</h2>
}

function Toggle({ label, description, checked, onChange, id }: {
  label: string; description: string; checked: boolean; onChange: (v: boolean) => void; id: string
}) {
  return (
    <div className="flex items-start justify-between gap-4 py-3 border-b border-white/[0.04]">
      <div>
        <p className="text-xs text-zinc-200 font-medium">{label}</p>
        <p className="text-[11px] text-zinc-600 mt-0.5">{description}</p>
      </div>
      <button
        id={id}
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative flex-shrink-0 w-9 h-5 rounded-full border transition-all ${checked ? 'bg-sky-600 border-sky-500' : 'bg-zinc-800 border-zinc-700'}`}
      >
        <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all ${checked ? 'left-[18px]' : 'left-0.5'}`} />
      </button>
    </div>
  )
}

function InputRow({ label, description, value, onChange, id, type = 'text', placeholder }: {
  label: string; description?: string; value: string | number; onChange: (v: string) => void;
  id: string; type?: string; placeholder?: string
}) {
  return (
    <div className="flex items-start justify-between gap-4 py-3 border-b border-white/[0.04]">
      <div>
        <p className="text-xs text-zinc-200 font-medium">{label}</p>
        {description && <p className="text-[11px] text-zinc-600 mt-0.5">{description}</p>}
      </div>
      <input
        id={id}
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-48 bg-[#0d0e10] border border-white/[0.08] rounded-lg px-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-sky-500/50 transition-colors"
      />
    </div>
  )
}

export function SettingsPage() {
  const [settings, setSettings] = useState<AppSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    agentApi.getSettings().then(s => {
      setSettings(s)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const patch = (key: keyof AppSettings, value: unknown) => {
    if (!settings) return
    setSettings({ ...settings, [key]: value })
    setSaved(false)
  }

  const save = async () => {
    if (!settings) return
    setSaving(true)
    try {
      await agentApi.updateSettings(settings)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  if (loading || !settings) {
    return (
      <div className="flex items-center justify-center h-full text-zinc-600">
        <Loader2 size={18} className="animate-spin mr-2" /> Loading settings…
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-5 py-4 border-b border-white/[0.06]">
        <Settings size={14} className="text-zinc-500" />
        <h1 className="text-sm font-semibold text-zinc-200">Settings</h1>
        <button
          id="settings-save-btn"
          onClick={() => void save()}
          disabled={saving}
          className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 disabled:opacity-60 text-white text-xs font-medium transition-colors"
        >
          {saved ? <CheckCircle2 size={13} /> : saving ? <Loader2 size={13} className="animate-spin" /> : <Save size={13} />}
          {saved ? 'Saved' : 'Save'}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-6 pb-8 max-w-2xl">
        <SectionTitle title="Voice" />
        <Toggle
          id="setting-enable-voice"
          label="Enable Voice Runtime"
          description="Allow IntentOS to listen for voice commands."
          checked={settings.enable_voice}
          onChange={v => patch('enable_voice', v)}
        />

        <SectionTitle title="Runtime" />
        <InputRow
          id="setting-max-history"
          label="Max History Jobs"
          description="Maximum number of sessions to retain on disk."
          value={settings.max_history_jobs}
          type="number"
          onChange={v => patch('max_history_jobs', parseInt(v, 10) || 50)}
        />

        <SectionTitle title="Appearance" />
        <div className="py-3 border-b border-white/[0.04] flex items-center justify-between gap-4">
          <div>
            <p className="text-xs text-zinc-200 font-medium">Theme</p>
            <p className="text-[11px] text-zinc-600 mt-0.5">Controls the Mission Control color scheme.</p>
          </div>
          <select
            id="setting-theme"
            value={settings.theme}
            onChange={e => patch('theme', e.target.value)}
            className="bg-[#0d0e10] border border-white/[0.08] rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-sky-500/50"
          >
            <option value="system">System</option>
            <option value="dark">Dark</option>
            <option value="light">Light</option>
          </select>
        </div>

        <SectionTitle title="Logging & Developer" />
        <Toggle
          id="setting-debug-mode"
          label="Debug Mode"
          description="Enable verbose structured logging to stdout."
          checked={settings.debug_mode}
          onChange={v => patch('debug_mode', v)}
        />
      </div>
    </div>
  )
}
