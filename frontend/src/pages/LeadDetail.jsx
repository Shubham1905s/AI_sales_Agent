import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Zap, Globe, Mail, Linkedin, Copy, Check } from 'lucide-react'
import { leadsApi } from '../lib/api'

const ScoreBar = ({ label, value, max = 25 }) => (
  <div style={{ marginBottom: 10 }}>
    <div style={{ display:'flex', justifyContent:'space-between', marginBottom:4 }}>
      <span style={{ fontSize:12, color:'var(--muted)' }}>{label}</span>
      <span style={{ fontSize:12, fontFamily:'var(--mono)', color:'var(--text)' }}>{Math.round(value || 0)}/{max}</span>
    </div>
    <div style={{ height:5, background:'var(--bg3)', borderRadius:99 }}>
      <div style={{ height:'100%', borderRadius:99, width:`${((value||0)/max)*100}%`,
        background: (value/max) >= 0.7 ? 'var(--green)' : (value/max) >= 0.4 ? 'var(--amber)' : 'var(--muted)',
        transition:'width 0.5s ease' }}/>
    </div>
  </div>
)

const CopyBtn = ({ text }) => {
  const [copied, setCopied] = useState(false)
  const copy = () => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }
  return (
    <button className="btn btn-ghost" style={{ padding:'4px 8px', fontSize:12 }} onClick={copy}>
      {copied ? <Check size={12}/> : <Copy size={12}/>}
      {copied ? 'Copied' : 'Copy'}
    </button>
  )
}

export default function LeadDetail() {
  const { id } = useParams()
  const nav = useNavigate()
  const qc = useQueryClient()
  const [activeTab, setActiveTab] = useState('overview')

  const { data, isLoading } = useQuery({ queryKey: ['lead', id], queryFn: () => leadsApi.get(id) })

  const scoreMut = useMutation({ mutationFn: () => leadsApi.score(id), onSuccess: () => qc.invalidateQueries(['lead', id]) })
  const enrichMut = useMutation({ mutationFn: () => leadsApi.enrich(id), onSuccess: () => qc.invalidateQueries(['lead', id]) })
  const outreachMut = useMutation({ mutationFn: () => leadsApi.generateOutreach(id), onSuccess: () => { qc.invalidateQueries(['lead', id]); setActiveTab('outreach') } })

  if (isLoading) return <div style={{ padding:'4rem', textAlign:'center', color:'var(--muted)' }}>Loading...</div>
  if (!data) return <div style={{ padding:'4rem', textAlign:'center', color:'var(--muted)' }}>Lead not found</div>

  const { lead, score, outreach = [] } = data
  const linkedin = outreach.find(o => o.type === 'linkedin')
  const emails = outreach.filter(o => o.type === 'email').sort((a,b) => a.sequence_step - b.sequence_step)

  const totalScore = score?.total_score || 0
  const scoreColor = totalScore >= 70 ? 'var(--green)' : totalScore >= 45 ? 'var(--amber)' : 'var(--muted)'

  const tabs = ['overview', 'score', 'outreach', 'enrichment']

  return (
    <div style={{ maxWidth: 900, margin:'0 auto', padding:'2rem 1.5rem' }}>
      <button className="btn btn-ghost" style={{ marginBottom:'1.5rem' }} onClick={() => nav('/')}>
        <ArrowLeft size={14}/> Back
      </button>

      <div className="card" style={{ marginBottom:'1.5rem' }}>
        <div style={{ display:'flex', alignItems:'flex-start', justifyContent:'space-between' }}>
          <div style={{ display:'flex', alignItems:'center', gap:14 }}>
            <div style={{ width:52, height:52, borderRadius:12, background:'var(--accent)22', display:'flex', alignItems:'center', justifyContent:'center', fontSize:18, fontWeight:600, color:'var(--accent2)' }}>
              {lead.first_name[0]}{lead.last_name[0]}
            </div>
            <div>
              <h2 style={{ fontSize:18, fontWeight:600 }}>{lead.first_name} {lead.last_name}</h2>
              <p style={{ color:'var(--muted)', fontSize:13 }}>{lead.title} {lead.company && `at ${lead.company}`}</p>
              <div style={{ display:'flex', gap:10, marginTop:6 }}>
                {lead.email && <span style={{ fontSize:12, color:'var(--muted)', display:'flex', alignItems:'center', gap:4 }}><Mail size={11}/>{lead.email}</span>}
                {lead.linkedin_url && <a href={lead.linkedin_url} target="_blank" style={{ fontSize:12, color:'var(--blue)', display:'flex', alignItems:'center', gap:4 }}><Linkedin size={11}/>LinkedIn</a>}
              </div>
            </div>
          </div>
          {score && (
            <div style={{ textAlign:'center' }}>
              <div style={{ fontSize:36, fontWeight:700, fontFamily:'var(--mono)', color:scoreColor }}>{Math.round(totalScore)}</div>
              <div style={{ fontSize:11, color:'var(--muted)' }}>/ 100</div>
              <span className={`badge badge-${score.priority}`} style={{ marginTop:4 }}>{score.priority}</span>
            </div>
          )}
        </div>
        <div style={{ display:'flex', gap:8, marginTop:'1.25rem', flexWrap:'wrap' }}>
          <button className="btn btn-ai" onClick={() => scoreMut.mutate()} disabled={scoreMut.isPending}>
            <Zap size={13}/> {scoreMut.isPending ? 'Scoring...' : score ? 'Re-score' : 'Score with AI'}
          </button>
          <button className="btn btn-ghost" onClick={() => enrichMut.mutate()} disabled={enrichMut.isPending}>
            <Globe size={13}/> {enrichMut.isPending ? 'Enriching...' : 'Enrich with Web'}
          </button>
          <button className="btn btn-primary" onClick={() => outreachMut.mutate()} disabled={outreachMut.isPending}>
            <Mail size={13}/> {outreachMut.isPending ? 'Generating...' : outreach.length ? 'Regenerate Outreach' : 'Generate Outreach'}
          </button>
        </div>
      </div>

      <div style={{ display:'flex', gap:4, marginBottom:'1rem', borderBottom:'1px solid var(--border)', paddingBottom:0 }}>
        {tabs.map(t => (
          <button key={t} onClick={() => setActiveTab(t)}
            style={{ padding:'8px 14px', background:'transparent', color: activeTab===t ? 'var(--text)' : 'var(--muted)',
              borderBottom: activeTab===t ? '2px solid var(--accent)' : '2px solid transparent',
              fontSize:13, fontWeight: activeTab===t ? 500 : 400, transition:'all 0.15s', fontFamily:'var(--font)' }}>
            {t.charAt(0).toUpperCase()+t.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="card">
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1rem' }}>
            {[['Company', lead.company], ['Industry', lead.industry], ['Company size', lead.company_size],
              ['Location', lead.location], ['Source', lead.source], ['Status', lead.status]].map(([k,v]) => (
              <div key={k}>
                <div style={{ fontSize:11, color:'var(--muted)', marginBottom:2, textTransform:'uppercase', letterSpacing:'0.05em' }}>{k}</div>
                <div style={{ fontSize:14 }}>{v || '—'}</div>
              </div>
            ))}
          </div>
          {lead.extra_data && Object.keys(lead.extra_data).length > 0 && (
            <div style={{ marginTop:'1.25rem', paddingTop:'1.25rem', borderTop:'1px solid var(--border)' }}>
              <div style={{ fontSize:12, color:'var(--muted)', marginBottom:8 }}>Enriched data</div>
              <pre style={{ fontSize:12, fontFamily:'var(--mono)', color:'var(--muted)', whiteSpace:'pre-wrap' }}>
                {JSON.stringify(lead.extra_data, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {activeTab === 'score' && (
        <div className="card">
          {!score ? (
            <p style={{ color:'var(--muted)', textAlign:'center', padding:'2rem' }}>No score yet. Click "Score with AI" above.</p>
          ) : (
            <>
              <ScoreBar label="Firmographic fit" value={score.firmographic_score} />
              <ScoreBar label="Title / seniority" value={score.title_score} />
              <ScoreBar label="Intent signals" value={score.intent_score} />
              <ScoreBar label="Engagement" value={score.engagement_score} />
              <div style={{ marginTop:'1.25rem', padding:'1rem', background:'var(--bg3)', borderRadius:8 }}>
                <div style={{ fontSize:11, color:'var(--muted)', marginBottom:6 }}>AI Reasoning</div>
                <p style={{ fontSize:13, lineHeight:1.7 }}>{score.reasoning}</p>
              </div>
              <div style={{ display:'flex', gap:12, marginTop:'1rem' }}>
                <div><span style={{ fontSize:11, color:'var(--muted)' }}>ICP Match: </span><span style={{ fontSize:13 }}>{score.icp_match}</span></div>
                <div><span style={{ fontSize:11, color:'var(--muted)' }}>Priority: </span><span className={`badge badge-${score.priority}`}>{score.priority}</span></div>
              </div>
            </>
          )}
        </div>
      )}

      {activeTab === 'outreach' && (
        <div>
          {outreach.length === 0 ? (
            <div className="card"><p style={{ color:'var(--muted)', textAlign:'center', padding:'2rem' }}>No outreach yet. Click "Generate Outreach" above.</p></div>
          ) : (
            <>
              {linkedin && (
                <div className="card" style={{ marginBottom:'1rem' }}>
                  <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:10 }}>
                    <div style={{ display:'flex', alignItems:'center', gap:6 }}>
                      <Linkedin size={14} color="var(--blue)"/>
                      <span style={{ fontSize:13, fontWeight:500 }}>LinkedIn Message</span>
                    </div>
                    <CopyBtn text={linkedin.body}/>
                  </div>
                  <p style={{ fontSize:13, lineHeight:1.7, color:'var(--text)' }}>{linkedin.body}</p>
                </div>
              )}
              {emails.map((email, i) => (
                <div key={email.id} className="card" style={{ marginBottom:'1rem' }}>
                  <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:10 }}>
                    <div style={{ display:'flex', alignItems:'center', gap:6 }}>
                      <Mail size={14} color="var(--accent2)"/>
                      <span style={{ fontSize:13, fontWeight:500 }}>Email Step {i+1}</span>
                    </div>
                    <CopyBtn text={`Subject: ${email.subject}\n\n${email.body}`}/>
                  </div>
                  <div style={{ fontSize:12, color:'var(--muted)', marginBottom:6 }}>Subject: {email.subject}</div>
                  <p style={{ fontSize:13, lineHeight:1.7, whiteSpace:'pre-wrap' }}>{email.body}</p>
                </div>
              ))}
            </>
          )}
        </div>
      )}

      {activeTab === 'enrichment' && (
        <div className="card">
          <p style={{ fontSize:13, color:'var(--muted)', marginBottom:'1rem' }}>Click "Enrich with Web" to let Claude research this company and person using live web search.</p>
          {lead.extra_data && Object.keys(lead.extra_data).length > 0 ? (
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1rem' }}>
              {Object.entries(lead.extra_data).map(([k,v]) => (
                <div key={k}>
                  <div style={{ fontSize:11, color:'var(--muted)', marginBottom:2, textTransform:'uppercase', letterSpacing:'0.04em' }}>{k.replace(/_/g,' ')}</div>
                  <div style={{ fontSize:13 }}>{Array.isArray(v) ? v.join(', ') : String(v)}</div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color:'var(--muted)', textAlign:'center', padding:'2rem' }}>No enrichment data yet.</p>
          )}
        </div>
      )}
    </div>
  )
}
