// src/pages/Admin.jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../App'
import { adminAPI } from '../api/client'
import { Shield, Users, Clock, BarChart2,
         RefreshCw, LogIn, AlertCircle } from 'lucide-react'

export default function Admin() {
  const { user }  = useAuth()
  const navigate  = useNavigate()
  const [tab,     setTab]     = useState('stats')
  const [stats,   setStats]   = useState([])
  const [history, setHistory] = useState([])
  const [users,   setUsers]   = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  // Redirect non-admins
  useEffect(() => {
    if (user && user.role !== 'admin') navigate('/')
  }, [user])

  const load = async () => {
    setLoading(true); setError('')
    try {
      const [s, h, u] = await Promise.all([
        adminAPI.getLoginStats(),
        adminAPI.getLoginHistory(100),
        adminAPI.getUsers(),
      ])
      setStats(s.data.stats     || [])
      setHistory(h.data.history || [])
      setUsers(u.data.users     || [])
    } catch(e) {
      setError(e.response?.data?.error || 'Failed to load admin data')
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const totalLogins = stats.reduce((a,s) => a + s.total_logins, 0)

  if (!user || user.role !== 'admin') return null

  return (
    <div className="animate-fade-in space-y-5 max-w-5xl mx-auto">

      {/* Hero */}
      <div className="bg-gradient-to-r from-slate-700 via-slate-800 to-slate-900
                      rounded-2xl p-5 text-white shadow-lg flex items-center
                      justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Shield size={20} className="text-purple-400"/>
            <h1 className="text-2xl font-bold">Admin Panel</h1>
          </div>
          <p className="text-slate-300 text-sm">
            User management & login history
          </p>
        </div>
        <button onClick={load}
                className="flex items-center gap-2 bg-white/10
                           hover:bg-white/20 px-4 py-2 rounded-xl
                           text-sm transition">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''}/>
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200
                        dark:border-red-800 rounded-xl px-4 py-3 text-sm
                        text-red-600 dark:text-red-400 flex items-center gap-2">
          <AlertCircle size={16}/> {error}
        </div>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label:"Total Users",    value:users.length,   icon:Users,    color:"text-indigo-600",  bg:"bg-indigo-50 dark:bg-indigo-900/20"  },
          { label:"Total Logins",   value:totalLogins,    icon:LogIn,    color:"text-emerald-600", bg:"bg-emerald-50 dark:bg-emerald-900/20"},
          { label:"Active Today",   value:history.filter(h =>
              h.login_time?.startsWith(
                new Date().toISOString().slice(0,10)
              )).length,             icon:Clock,    color:"text-amber-600",  bg:"bg-amber-50 dark:bg-amber-900/20"  },
          { label:"Unique Accounts",value:stats.length,   icon:BarChart2,color:"text-purple-600", bg:"bg-purple-50 dark:bg-purple-900/20" },
        ].map(s => (
          <div key={s.label} className="card flex items-center gap-3 py-4">
            <div className={`${s.bg} p-3 rounded-xl flex-shrink-0`}>
              <s.icon size={20} className={s.color}/>
            </div>
            <div>
              <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{s.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex bg-gray-100 dark:bg-dark-card2 rounded-xl p-1 gap-1">
        {[
          { key:'stats',   label:'📊 Login Stats'   },
          { key:'history', label:'🕐 Login History' },
          { key:'users',   label:'👥 All Users'     },
        ].map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
                  className={`flex-1 py-2 text-sm font-medium rounded-lg
                              transition-all
                              ${tab === t.key
                                ? 'bg-white dark:bg-dark-card shadow text-indigo-600'
                                : 'text-gray-500 hover:text-gray-700'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="text-4xl animate-bounce">🔐</div>
        </div>
      ) : (
        <>
          {/* ── LOGIN STATS ── */}
          {tab === 'stats' && (
            <div className="card">
              <h2 className="font-semibold text-gray-800 dark:text-white mb-4">
                📊 Login Count Per User
              </h2>
              {stats.length === 0 ? (
                <p className="text-center text-gray-400 py-8">No login data yet</p>
              ) : (
                <div className="space-y-3">
                  {stats.map((s, i) => {
                    const pct = totalLogins
                      ? Math.round(s.total_logins / totalLogins * 100)
                      : 0
                    return (
                      <div key={s.username} className="flex items-center gap-4">
                        {/* Rank */}
                        <div className={`w-7 h-7 rounded-full flex items-center
                                         justify-center text-xs font-bold flex-shrink-0
                                         ${i===0 ? 'bg-yellow-100 text-yellow-700'
                                           : i===1 ? 'bg-gray-100 text-gray-600'
                                           : i===2 ? 'bg-orange-100 text-orange-700'
                                           : 'bg-gray-50 text-gray-400'}`}>
                          {i+1}
                        </div>

                        {/* Avatar */}
                        <div className="w-9 h-9 rounded-full flex-shrink-0
                                        bg-gradient-to-br from-indigo-500 to-purple-500
                                        flex items-center justify-center
                                        text-white text-sm font-bold">
                          {(s.full_name || s.username)[0]?.toUpperCase()}
                        </div>

                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <div>
                              <span className="font-medium text-sm text-gray-800
                                               dark:text-white">
                                {s.full_name || s.username}
                              </span>
                              <span className="text-xs text-gray-400 ml-2">
                                @{s.username}
                              </span>
                            </div>
                            <span className="text-sm font-bold text-indigo-600 flex-shrink-0">
                              {s.total_logins} login{s.total_logins !== 1 ? 's' : ''}
                            </span>
                          </div>
                          <div className="h-2 bg-gray-100 dark:bg-dark-border rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500
                                            rounded-full transition-all duration-700"
                                 style={{ width:`${pct}%` }}/>
                          </div>
                          <div className="flex justify-between text-xs text-gray-400 mt-0.5">
                            <span>First: {s.first_login?.slice(0,10) || '—'}</span>
                            <span>Last: {s.last_login?.slice(0,16) || '—'}</span>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )}

          {/* ── LOGIN HISTORY ── */}
          {tab === 'history' && (
            <div className="card">
              <h2 className="font-semibold text-gray-800 dark:text-white mb-4">
                🕐 Recent Login History
                <span className="text-xs text-gray-400 font-normal ml-2">
                  (last {history.length} entries)
                </span>
              </h2>
              {history.length === 0 ? (
                <p className="text-center text-gray-400 py-8">No login history yet</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-100 dark:border-dark-border">
                        {['User','Full Name','Login Time','IP Address'].map(h => (
                          <th key={h} className="text-left py-2 px-3 text-xs
                                                  font-semibold text-gray-500
                                                  uppercase tracking-wide">
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50 dark:divide-dark-border">
                      {history.map((h, i) => (
                        <tr key={i} className="hover:bg-gray-50 dark:hover:bg-dark-card2
                                                transition-colors">
                          <td className="py-2.5 px-3">
                            <div className="flex items-center gap-2">
                              <div className="w-7 h-7 rounded-full flex-shrink-0
                                              bg-gradient-to-br from-indigo-400 to-purple-400
                                              flex items-center justify-center
                                              text-white text-xs font-bold">
                                {h.username[0]?.toUpperCase()}
                              </div>
                              <span className="font-medium text-gray-800
                                               dark:text-white">
                                @{h.username}
                              </span>
                            </div>
                          </td>
                          <td className="py-2.5 px-3 text-gray-500 dark:text-gray-400">
                            {h.full_name || '—'}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className="bg-indigo-50 dark:bg-indigo-900/30
                                             text-indigo-700 dark:text-indigo-300
                                             px-2 py-0.5 rounded-lg text-xs font-medium">
                              {h.login_time || '—'}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-gray-400 text-xs font-mono">
                            {h.ip_address || '127.0.0.1'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* ── ALL USERS ── */}
          {tab === 'users' && (
            <div className="card">
              <h2 className="font-semibold text-gray-800 dark:text-white mb-4">
                👥 All Registered Users ({users.length})
              </h2>
              {users.length === 0 ? (
                <p className="text-center text-gray-400 py-8">No users found</p>
              ) : (
                <div className="space-y-3">
                  {users.map(u => {
                    const stat = stats.find(s => s.username === u.username)
                    return (
                      <div key={u.id}
                           className="flex items-center gap-4 p-3
                                      bg-gray-50 dark:bg-dark-card2
                                      rounded-xl hover:bg-gray-100
                                      dark:hover:bg-dark-border transition">
                        {/* Avatar */}
                        <div className="w-11 h-11 rounded-xl flex-shrink-0
                                        bg-gradient-to-br from-indigo-500 to-purple-500
                                        flex items-center justify-center
                                        text-white text-lg font-bold shadow-sm">
                          {(u.full_name || u.username)[0]?.toUpperCase()}
                        </div>

                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <p className="font-semibold text-gray-800 dark:text-white">
                              {u.full_name || u.username}
                            </p>
                            <span className={`badge text-xs
                                             ${u.role === 'admin'
                                               ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300'
                                               : 'badge-green'}`}>
                              {u.role === 'admin' ? '👑 Admin' : '👤 Member'}
                            </span>
                          </div>
                          <p className="text-xs text-gray-400 mt-0.5">
                            @{u.username}
                            {u.email ? ` · ${u.email}` : ''}
                          </p>
                        </div>

                        {/* Stats */}
                        <div className="text-right flex-shrink-0">
                          <p className="text-sm font-bold text-indigo-600">
                            {stat?.total_logins || 0} logins
                          </p>
                          <p className="text-xs text-gray-400">
                            {stat?.last_login?.slice(0,10) || 'Never'}
                          </p>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}