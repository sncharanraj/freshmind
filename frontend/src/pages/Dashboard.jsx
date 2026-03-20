// src/pages/Dashboard.jsx
import { useState, useEffect } from 'react'
import { pantryAPI } from '../api/client'
import {
  PieChart, Pie, Cell, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts'

const COLORS = ['#667eea','#43e97b','#fa709a','#f44336',
                '#ff9800','#4facfe','#f093fb','#30cfd0','#a8edea']

function getExpDays(expiry_str) {
  const today  = new Date(); today.setHours(0,0,0,0)
  const expiry = new Date(expiry_str)
  return Math.round((expiry - today) / 86400000)
}

export default function Dashboard() {
  const [items,   setItems]   = useState([])
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([pantryAPI.getAll(), pantryAPI.getHistory()])
      .then(([a, h]) => {
        setItems(a.data.items || [])
        setHistory(h.data.history || [])
        setLoading(false)
      }).catch(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-4xl animate-bounce">📊</div>
    </div>
  )

  // ── Category distribution ──
  const catCount = {}
  items.forEach(i => {
    catCount[i.category] = (catCount[i.category] || 0) + 1
  })
  const catData = Object.entries(catCount).map(([name, value]) => ({
    name, value
  }))

  // ── Expiry breakdown ──
  const expBreak = { Expired:0, Critical:0, Soon:0, Fresh:0 }
  items.forEach(i => {
    const d = getExpDays(i.expiry_date)
    if (d < 0)      expBreak.Expired++
    else if (d <= 3) expBreak.Critical++
    else if (d <= 7) expBreak.Soon++
    else             expBreak.Fresh++
  })
  const expData = Object.entries(expBreak)
    .filter(([,v]) => v > 0)
    .map(([name, value]) => ({ name, value }))
  const EXP_COLORS = { Expired:'#f44336', Critical:'#ff9800', Soon:'#ffd600', Fresh:'#43e97b' }

  // ── Saved vs Wasted ──
  const saved  = history.filter(h => !h.was_wasted).length
  const wasted = history.filter(h =>  h.was_wasted).length
  const swData = [
    { name:'Saved',  value: saved,  fill:'#43e97b' },
    { name:'Wasted', value: wasted, fill:'#f44336' },
  ]

  // ── Recent activity bar chart (last 7 items) ──
  const recentMap = {}
  history.slice(0, 20).forEach(h => {
    const d = h.used_date
    if (!recentMap[d]) recentMap[d] = { date:d, saved:0, wasted:0 }
    if (h.was_wasted) recentMap[d].wasted++
    else              recentMap[d].saved++
  })
  const recentData = Object.values(recentMap).slice(0, 7)

  const STAT = [
    { label:"Total Items",   value:items.length,   color:"text-primary",  emoji:"📦" },
    { label:"Expiring Soon", value:items.filter(i=>getExpDays(i.expiry_date)<=7).length,
      color:"text-orange-500", emoji:"⚠️" },
    { label:"Items Saved",   value:saved,           color:"text-success",  emoji:"✅" },
    { label:"Items Wasted",  value:wasted,          color:"text-danger",   emoji:"🗑️" },
  ]

  return (
    <div className="animate-fade-in space-y-6">

      {/* Hero */}
      <div className="bg-gradient-to-r from-green-800 to-emerald-600
                      rounded-2xl p-5 text-white">
        <h1 className="text-2xl font-bold">📊 Dashboard</h1>
        <p className="text-green-100 text-sm mt-1">Your pantry analytics</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {STAT.map(s => (
          <div key={s.label} className="card text-center py-5">
            <div className="text-3xl mb-2">{s.emoji}</div>
            <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
            <p className="text-xs text-gray-500 mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Category distribution */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 dark:text-white mb-4">
            🏷️ Items by Category
          </h2>
          {catData.length === 0 ? (
            <p className="text-center text-gray-400 py-8">No items yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={catData} cx="50%" cy="50%"
                     innerRadius={55} outerRadius={90}
                     paddingAngle={3} dataKey="value">
                  {catData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]}/>
                  ))}
                </Pie>
                <Tooltip formatter={(v, n) => [v, n]}/>
                <Legend iconType="circle" iconSize={10}
                        formatter={v => (
                          <span className="text-xs text-gray-600 dark:text-gray-300">
                            {v}
                          </span>
                        )}/>
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Expiry breakdown */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 dark:text-white mb-4">
            📅 Expiry Status
          </h2>
          {expData.length === 0 ? (
            <p className="text-center text-gray-400 py-8">No items yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={expData} cx="50%" cy="50%"
                     innerRadius={55} outerRadius={90}
                     paddingAngle={3} dataKey="value">
                  {expData.map((entry) => (
                    <Cell key={entry.name}
                          fill={EXP_COLORS[entry.name] || '#888'}/>
                  ))}
                </Pie>
                <Tooltip/>
                <Legend iconType="circle" iconSize={10}
                        formatter={v => (
                          <span className="text-xs text-gray-600 dark:text-gray-300">
                            {v}
                          </span>
                        )}/>
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Saved vs Wasted */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 dark:text-white mb-4">
            ♻️ Saved vs Wasted
          </h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={swData} barSize={48}>
              <XAxis dataKey="name" tick={{ fontSize:12 }}/>
              <YAxis tick={{ fontSize:11 }} allowDecimals={false}/>
              <Tooltip/>
              <Bar dataKey="value" radius={[8,8,0,0]}>
                {swData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill}/>
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent activity */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 dark:text-white mb-4">
            📈 Recent Activity
          </h2>
          {recentData.length === 0 ? (
            <p className="text-center text-gray-400 py-8">No activity yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={recentData} barSize={16}>
                <XAxis dataKey="date" tick={{ fontSize:10 }}/>
                <YAxis tick={{ fontSize:11 }} allowDecimals={false}/>
                <Tooltip/>
                <Legend iconSize={10}
                        formatter={v=>(
                          <span className="text-xs">{v}</span>
                        )}/>
                <Bar dataKey="saved"  name="Saved"
                     fill="#43e97b" radius={[4,4,0,0]} stackId="a"/>
                <Bar dataKey="wasted" name="Wasted"
                     fill="#f44336" radius={[4,4,0,0]} stackId="a"/>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Waste reduction tips */}
      <div className="card bg-gradient-to-r from-green-50 to-emerald-50
                      dark:from-green-900/20 dark:to-emerald-900/20
                      border-green-200 dark:border-green-800">
        <h2 className="font-semibold text-green-800 dark:text-green-300 mb-3">
          💡 Waste Reduction Score
        </h2>
        {saved + wasted === 0 ? (
          <p className="text-sm text-gray-500">No history yet — start using your pantry!</p>
        ) : (
          <>
            <div className="flex items-center gap-3 mb-2">
              <div className="flex-1 bg-gray-200 dark:bg-dark-border
                              rounded-full h-3 overflow-hidden">
                <div className="h-full bg-gradient-to-r from-primary to-success
                                rounded-full transition-all duration-1000"
                     style={{
                       width:`${Math.round(saved/(saved+wasted)*100)}%`
                     }}/>
              </div>
              <span className="font-bold text-primary">
                {Math.round(saved/(saved+wasted)*100)}%
              </span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              You saved <b className="text-success">{saved}</b> items
              and wasted <b className="text-danger">{wasted}</b> items.
              {saved/(saved+wasted) >= 0.8 ? ' 🎉 Excellent job!' :
               saved/(saved+wasted) >= 0.6 ? ' 👍 Good effort!' :
               ' 💪 Try to use items before they expire!'}
            </p>
          </>
        )}
      </div>
    </div>
  )
}
