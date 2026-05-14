import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Plus, Zap, Users, TrendingUp, Target, Trash2, Search, Loader } from 'lucide-react'
import { leadsApi } from '../lib/api'

const statusColor = (s) => ({ new:'badge-new', scored:'badge-scored', outreach_ready:'badge-outreach_ready', contacted:'badge-contacted' }[s] || 'badge-new')
const priorityColor = (p) => ({ hot:'badge-hot', warm:'badge-warm', cold:'badge-cold' }[p] || 'badge-cold')

const ScoreRing = ({ score }) => {
  const color = score >= 70 ? '#10d98a' : score >= 45 ? '#f59e0b' : '#6b6b7e'
  return (
    <div className="score-ring" style={{ border: `2.5px solid ${color}`, color }}>
      {score != null ? Math.round(score) : '—'}
    </div>
  )
}

const emptyForm = { first_name:'', last_name:'', email:'', title:'', company:'', company_size:'', industry:'', location:'', linkedin_url:'', website:'', source:'manual' }

export default function Dashboard() {
  const nav = useNavigate()
  const qc = useQueryClient()
  const [tab, setTab] = useState('leads')           // 'leads' | 'add' | 'discover'
  const [form, setForm] = useState(emptyForm)
  const [discoverTarget, setDiscoverTarget] = useState('')
  const [discoverMax, setDiscoverMax] = useState(10)
  const [discoverAutoEnrich, setDiscoverAutoEnrich] = useState(true)
  const [discoverAutoScore, setDiscoverAutoScore] = useState(true)
  const [discoverResult, setDiscoverResult] = useState(null)
  const [loadingId, setLoadingId] = useState(null)

  const { data: leads = [], isLoading } = useQuery({ queryKey: ['leads'], queryFn: leadsApi.list })

  const createLead = useMutation({
    mutationFn: leadsApi.create,
    onSuccess: () => { qc.invalidateQueries(['leads']); setTab('leads'); setForm(emptyForm) }
  })

  const deleteLead = useMutation({
    mutationFn: leadsApi.delete,
    onSuccess: () => qc.invalidateQueries(['leads'])
  })

  const discoverMut = useMutation({
    mutationFn: ({ target, max, autoEnrich, autoScore }) => leadsApi.discover(target, max, autoEnrich, autoScore),
    onSuccess: (data) => { setDiscoverResult(data); qc.invalidateQueries(['leads']) }
  })

  const scoreAll = async () => {
    const unscored = leads.filter(l => !l.score)
    for (const l of unscored) {
      setLoadingId(l.id)
      await leadsApi.score(l.id)
    }
    setLoadingId(null)
    qc.invalidateQueries(['leads'])
  }

  const hot    = leads.filter(l => l.score?.priority === 'hot').length
  const scored = leads.filter(l => l.score).length
  const avg    = scored ? Math.round(leads.filter(l => l.score).reduce((a, l) => a + l.score.total_score, 0) / scored) : 0

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '2rem 1.5rem' }}>

      {/* Header */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:'2rem' }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 600, letterSpacing: '-0.5px' }}>LeadGen AI</h1>
          <p style={{ color:'var(--muted)', fontSize:13, marginTop:2 }}>100% powered by Claude · no mock data</p>
        </div>
        <div style={{ display:'flex', gap:8 }}>
          <button className="btn btn-ghost" onClick={scoreAll} disabled={!leads.length}><Zap size={14}/> Score All</button>
          <button className="btn btn-ghost" onClick={() => setTab(tab === 'discover' ? 'leads' : 'discover')}><Search size={14}/> Discover</button>
          <button className="btn btn-primary" onClick={() => setTab(tab === 'add' ? 'leads' : 'add')}><Plus size={14}/> Add Lead</button>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12, marginBottom:'1.5rem' }}>
        {[
          { label:'Total Leads', value: leads.length,    icon: Users,      color:'var(--accent2)' },
          { label:'Scored',      value: scored,          icon: Target,     color:'var(--green)'   },
          { label:'Hot Leads',   value: hot,             icon: Zap,        color:'var(--red)'     },
          { label:'Avg Score',   value: avg || '—',      icon: TrendingUp, color:'var(--amber)'   },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="card" style={{ display:'flex', alignItems:'center', gap:12 }}>
            <div style={{ width:36, height:36, borderRadius:8, background:`${color}18`, display:'flex', alignItems:'center', justifyContent:'center' }}>
              <Icon size={16} color={color}/>
            </div>
            <div>
              <div style={{ fontSize:20, fontWeight:600, fontFamily:'var(--mono)' }}>{value}</div>
              <div style={{ fontSize:11, color:'var(--muted)' }}>{label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Discover Panel */}
      {tab === 'discover' && (
        <div className="card" style={{ marginBottom:'1.5rem' }}>
          <div style={{ fontSize:14, fontWeight:500, marginBottom:6 }}>
            Discover Leads with Claude
          </div>
          <p style={{ fontSize:12, color:'var(--muted)', marginBottom:'1rem', lineHeight:1.6 }}>
            Describe your target market in plain English. Claude will search the web to find real companies and decision makers, then you can enrich and score the best matches on demand.
          </p>
          <textarea
            rows={3}
            placeholder="e.g. Automotive ADAS companies in Germany and France with VP or Director level decision makers in R&D or data engineering, 500–20,000 employees"
            value={discoverTarget}
            onChange={e => setDiscoverTarget(e.target.value)}
            style={{ width:'100%', resize:'vertical', marginBottom:10 }}
          />
          <div style={{ display:'flex', gap:12, alignItems:'center', marginBottom:12 }}>
            <label style={{ fontSize:13, color:'var(--muted)' }}>Find up to</label>
            <select
              value={discoverMax}
              onChange={e => setDiscoverMax(Number(e.target.value))}
              style={{ width:80 }}
            >
              {[5,10,15,20,25].map(n => <option key={n} value={n}>{n}</option>)}
            </select>
            <label style={{ fontSize:13, color:'var(--muted)' }}>leads</label>
            <div style={{ flex:1 }}></div>
            <label style={{ display:'flex', alignItems:'center', gap:6, fontSize:13, cursor:'pointer' }}>
              <input type="checkbox" checked={discoverAutoEnrich} onChange={e => setDiscoverAutoEnrich(e.target.checked)} style={{ width:16, height:16 }}/>
              <span>Auto-enrich</span>
            </label>
            <label style={{ display:'flex', alignItems:'center', gap:6, fontSize:13, cursor:'pointer' }}>
              <input type="checkbox" checked={discoverAutoScore} onChange={e => setDiscoverAutoScore(e.target.checked)} style={{ width:16, height:16 }}/>
              <span>Auto-score</span>
            </label>
          </div>
          <div style={{ display:'flex', gap:8 }}>
            <button
              className="btn btn-ai"
              disabled={discoverMut.isPending || !discoverTarget.trim()}
              onClick={() => { setDiscoverResult(null); discoverMut.mutate({ target: discoverTarget, max: discoverMax, autoEnrich: discoverAutoEnrich, autoScore: discoverAutoScore }) }}
            >
              {discoverMut.isPending
                ? <><Loader size={13} style={{ animation:'spin 1s linear infinite' }}/> Claude is searching…</>
                : <><Search size={13}/> Discover with Claude</>
              }
            </button>
            <button className="btn btn-ghost" onClick={() => { setTab('leads'); setDiscoverResult(null) }}>Cancel</button>
          </div>

          {discoverMut.isPending && (
            <div style={{ marginTop:'1rem', padding:'1rem', background:'var(--bg3)', borderRadius:8, fontSize:13, color:'var(--muted)' }}>
              Claude is searching the web for real companies and decision makers…{discoverAutoEnrich && ' enriching company intelligence…'}{discoverAutoScore && ' scoring leads…'} this may take 30–120 seconds.
            </div>
          )}

          {discoverResult && (
            <div style={{ marginTop:'1rem', padding:'1rem', background:'var(--bg3)', borderRadius:8 }}>
              <div style={{ fontSize:13, fontWeight:500, marginBottom:6, color:'var(--green)' }}>
                ✓ Found {discoverResult.saved} new leads (skipped {discoverResult.skipped} duplicates)
              </div>
              {discoverResult.search_summary && (
                <p style={{ fontSize:12, color:'var(--muted)', marginBottom:8 }}>{discoverResult.search_summary}</p>
              )}
              <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
                {(discoverResult.leads || []).map((l, i) => (
                  <div key={i} style={{ display:'flex', justifyContent:'space-between', fontSize:12 }}>
                    <span>{l.name} · <span style={{ color:'var(--muted)' }}>{l.company}</span></span>
                    {l.score != null && <span style={{ fontFamily:'var(--mono)', color: l.score >= 70 ? 'var(--green)' : l.score >= 45 ? 'var(--amber)' : 'var(--muted)' }}>{Math.round(l.score)}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {discoverMut.isError && (
            <div style={{ marginTop:'1rem', padding:'1rem', background:'rgba(248,113,113,0.08)', borderRadius:8, fontSize:13, color:'var(--red)' }}>
              Error: {discoverMut.error?.response?.data?.detail || discoverMut.error?.message || 'Something went wrong'}
            </div>
          )}
        </div>
      )}

      {/* Add Lead Form */}
      {tab === 'add' && (
        <div className="card" style={{ marginBottom:'1.5rem' }}>
          <div style={{ fontSize:14, fontWeight:500, marginBottom:'1rem' }}>Add Lead Manually</div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:10 }}>
            {['first_name','last_name','email','title','company','company_size','industry','location','linkedin_url','website'].map(f => (
              <input key={f} placeholder={f.replace(/_/g,' ')} value={form[f]}
                onChange={e => setForm(p => ({...p, [f]: e.target.value}))}
                style={{ width:'100%' }}/>
            ))}
          </div>
          <p style={{ fontSize:11, color:'var(--muted)', marginTop:8 }}>
            Claude will automatically enrich and score this lead after saving.
          </p>
          <div style={{ display:'flex', gap:8, marginTop:12 }}>
            <button className="btn btn-primary"
              disabled={createLead.isPending || !form.first_name || !form.last_name}
              onClick={() => createLead.mutate(form)}>
              {createLead.isPending
                ? <><Loader size={13} style={{ animation:'spin 1s linear infinite' }}/> Claude is analysing…</>
                : 'Save & Analyse with Claude'
              }
            </button>
            <button className="btn btn-ghost" onClick={() => setTab('leads')}>Cancel</button>
          </div>
        </div>
      )}

      {/* Leads Table */}
      <div className="card" style={{ padding:0 }}>
        <table style={{ width:'100%', borderCollapse:'collapse' }}>
          <thead>
            <tr style={{ borderBottom:'1px solid var(--border)' }}>
              {['Score','Name','Title','Company','Industry','Status',''].map(h => (
                <th key={h} style={{ padding:'10px 14px', textAlign:'left', fontSize:11, fontWeight:500, color:'var(--muted)', textTransform:'uppercase', letterSpacing:'0.05em' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={7} style={{ padding:'2rem', textAlign:'center', color:'var(--muted)' }}>Loading…</td></tr>}
            {!isLoading && leads.length === 0 && (
              <tr><td colSpan={7} style={{ padding:'3rem', textAlign:'center', color:'var(--muted)' }}>
                No leads yet. Click <strong>Discover</strong> to let Claude find leads, or <strong>Add Lead</strong> to add manually.
              </td></tr>
            )}
            {leads.map(lead => (
              <tr key={lead.id}
                style={{ borderBottom:'1px solid var(--border)', cursor:'pointer', transition:'background 0.1s' }}
                onMouseEnter={e => e.currentTarget.style.background='var(--bg3)'}
                onMouseLeave={e => e.currentTarget.style.background='transparent'}
                onClick={() => nav(`/leads/${lead.id}`)}>
                <td style={{ padding:'10px 14px' }}>
                  {loadingId === lead.id
                    ? <div style={{ width:52, height:52, borderRadius:'50%', border:'2.5px solid var(--border)', display:'flex', alignItems:'center', justifyContent:'center', color:'var(--muted)', fontSize:10 }}>…</div>
                    : <ScoreRing score={lead.score?.total_score}/>
                  }
                </td>
                <td style={{ padding:'10px 14px', fontWeight:500 }}>{lead.first_name} {lead.last_name}</td>
                <td style={{ padding:'10px 14px', color:'var(--muted)', fontSize:13 }}>{lead.title || '—'}</td>
                <td style={{ padding:'10px 14px', fontSize:13 }}>{lead.company || '—'}</td>
                <td style={{ padding:'10px 14px', fontSize:13, color:'var(--muted)' }}>{lead.industry || '—'}</td>
                <td style={{ padding:'10px 14px' }}>
                  <span className={`badge ${statusColor(lead.status)}`}>{lead.status}</span>
                  {lead.score?.priority && <span className={`badge ${priorityColor(lead.score.priority)}`} style={{ marginLeft:4 }}>{lead.score.priority}</span>}
                  {lead.source === 'claude_discover' && <span className="badge" style={{ marginLeft:4, background:'rgba(108,99,255,0.12)', color:'var(--accent2)' }}>claude</span>}
                </td>
                <td style={{ padding:'10px 14px' }} onClick={e => { e.stopPropagation(); deleteLead.mutate(lead.id) }}>
                  <Trash2 size={14} color="var(--muted)"/>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
