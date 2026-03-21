// src/pages/Settings.jsx
import { useState } from 'react'
import { useAuth } from '../App'
import { usersAPI } from '../api/client'
import { Lock, CheckCircle, User, AlertCircle, X } from 'lucide-react'

export default function Settings() {
  const { user } = useAuth()
  const [oldPass,  setOldPass]  = useState('')
  const [newPass,  setNewPass]  = useState('')
  const [newPass2, setNewPass2] = useState('')
  const [msg,      setMsg]      = useState({ text:'', ok:true })
  const [loading,  setLoading]  = useState(false)

  const changePass = async e => {
    e.preventDefault(); setMsg({ text:'', ok:true })
    if (!oldPass || !newPass) return setMsg({ text:'Fill all fields!', ok:false })
    if (newPass.length < 6)   return setMsg({ text:'Min 6 characters!', ok:false })
    if (newPass !== newPass2) return setMsg({ text:"Passwords don't match!", ok:false })
    setLoading(true)
    try {
      const res = await usersAPI.changePassword({
        old_password: oldPass, new_password: newPass
      })
      setMsg({ text: res.data.message || 'Password updated!', ok:true })
      setOldPass(''); setNewPass(''); setNewPass2('')
    } catch(e) {
      setMsg({ text: e.response?.data?.error || 'Update failed!', ok:false })
    } finally { setLoading(false) }
  }

  const fname = user?.full_name || user?.username || 'User'
  const init  = fname[0]?.toUpperCase() || 'U'

  return (
    <div className="animate-fade-in max-w-2xl mx-auto space-y-5">

      {/* Hero */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-violet-600
                      rounded-2xl p-5 text-white shadow-lg">
        <h1 className="text-2xl font-bold">⚙️ Settings</h1>
        <p className="text-indigo-100 text-sm mt-1">Manage your account</p>
      </div>

      {/* Profile card */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 dark:text-white
                       flex items-center gap-2 mb-5">
          <User size={18} className="text-indigo-500"/> My Profile
        </h2>

        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-2xl
                          bg-gradient-to-br from-indigo-500 to-purple-500
                          flex items-center justify-center
                          text-white text-2xl font-bold shadow-lg flex-shrink-0">
            {init}
          </div>
          <div>
            <p className="font-bold text-gray-800 dark:text-white text-xl">{fname}</p>
            <p className="text-sm text-gray-400 mt-0.5">@{user?.username}</p>
            <span className={`badge mt-1.5
                             ${user?.role === 'admin'
                               ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300'
                               : 'badge-green'}`}>
              {user?.role === 'admin' ? '👑 Admin' : '👤 Member'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {[
            { label:'Username',    value:`@${user?.username}`            },
            { label:'Full Name',   value: user?.full_name   || '—'      },
            { label:'Email',       value: user?.email       || '—'      },
            { label:'Member Since',value:(user?.created_at  || '').slice(0,10) || '—' },
            { label:'Role',        value: user?.role        || 'member' },
          ].map(f => (
            <div key={f.label}
                 className="bg-gray-50 dark:bg-dark-card2 rounded-xl px-4 py-3">
              <p className="text-xs text-gray-400 mb-0.5">{f.label}</p>
              <p className="font-medium text-gray-700 dark:text-gray-200 text-sm">
                {f.value}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Change password */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 dark:text-white
                       flex items-center gap-2 mb-5">
          <Lock size={18} className="text-indigo-500"/> Change Password
        </h2>

        {/* Persistent message */}
        {msg.text && (
          <div className={`rounded-xl px-4 py-3 mb-4 flex items-start gap-2
                           ${msg.ok
                             ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-300'
                             : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400'}`}>
            {msg.ok
              ? <CheckCircle size={16} className="flex-shrink-0 mt-0.5"/>
              : <AlertCircle size={16} className="flex-shrink-0 mt-0.5"/>
            }
            <p className="text-sm flex-1">{msg.text}</p>
            <button onClick={() => setMsg({ text:'', ok:true })}
                    className="text-current opacity-60 hover:opacity-100 flex-shrink-0">
              <X size={14}/>
            </button>
          </div>
        )}

        <form onSubmit={changePass} className="space-y-4">
          {[
            { label:'Current Password', val:oldPass, set:setOldPass,  ph:'Enter current password' },
            { label:'New Password',     val:newPass,  set:setNewPass,  ph:'Min 6 characters'       },
            { label:'Confirm Password', val:newPass2, set:setNewPass2, ph:'Repeat new password'    },
          ].map(f => (
            <div key={f.label}>
              <label className="text-sm font-medium text-gray-600 dark:text-gray-300 block mb-1.5">
                {f.label}
              </label>
              <input className="input" type="password" placeholder={f.ph}
                     value={f.val} onChange={e => f.set(e.target.value)}/>
            </div>
          ))}
          <button type="submit" disabled={loading}
                  className="btn-primary w-full py-2.5 disabled:opacity-60">
            {loading
              ? <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin"/>
                  Updating...
                </span>
              : '🔒 Update Password'
            }
          </button>
        </form>
      </div>

      {/* App info */}
      <div className="card text-center py-6">
        <div className="text-4xl mb-2">🥗</div>
        <p className="font-bold text-gray-700 dark:text-gray-200">FreshMind v1.0</p>
        <p className="text-xs text-gray-400 mt-1">
          AI-Powered Smart Pantry Assistant
        </p>
        <p className="text-xs text-gray-400 mt-0.5">
          Built with Flask + React + Tailwind
        </p>
      </div>
    </div>
  )
}