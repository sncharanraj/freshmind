// src/pages/Settings.jsx
import { useState, useEffect } from 'react'
import { useAuth } from '../App'
import { usersAPI } from '../api/client'
import { Shield, User, Lock, CheckCircle } from 'lucide-react'

export default function Settings() {
  const { user } = useAuth()
  const [allUsers, setAllUsers] = useState([])
  const [oldPass,  setOldPass]  = useState('')
  const [newPass,  setNewPass]  = useState('')
  const [newPass2, setNewPass2] = useState('')
  const [msg,      setMsg]      = useState({ text:'', ok:true })
  const [loading,  setLoading]  = useState(false)

  useEffect(() => {
    if (user?.role === 'admin') {
      usersAPI.list()
        .then(r => setAllUsers(r.data.users || []))
        .catch(() => {})
    }
  }, [user])

  const changePass = async e => {
    e.preventDefault(); setMsg({ text:'', ok:true })
    if (!oldPass || !newPass) return setMsg({ text:'Fill all fields!', ok:false })
    if (newPass.length < 6)   return setMsg({ text:'Min 6 characters!', ok:false })
    if (newPass !== newPass2) return setMsg({ text:"Passwords don't match!", ok:false })
    setLoading(true)
    try {
      const res = await usersAPI.changePassword({
        old_password: oldPass,
        new_password: newPass
      })
      setMsg({ text: res.data.message || 'Password updated!', ok:true })
      setOldPass(''); setNewPass(''); setNewPass2('')
    } catch(e) {
      setMsg({ text: e.response?.data?.error || 'Failed!', ok:false })
    } finally { setLoading(false) }
  }

  const fname = user?.full_name || user?.username || 'User'
  const init  = fname[0]?.toUpperCase() || 'U'

  return (
    <div className="animate-fade-in max-w-2xl mx-auto space-y-5">

      {/* Hero */}
      <div className="bg-gradient-to-r from-green-800 to-emerald-600
                      rounded-2xl p-5 text-white">
        <h1 className="text-2xl font-bold">⚙️ Settings</h1>
        <p className="text-green-100 text-sm mt-1">Manage your account</p>
      </div>

      {/* Profile card */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 dark:text-white
                       flex items-center gap-2 mb-4">
          <User size={18} className="text-primary"/> Profile Info
        </h2>
        <div className="flex items-center gap-4 mb-5">
          <div className="w-16 h-16 rounded-2xl
                          bg-gradient-to-br from-primary to-success
                          flex items-center justify-center
                          text-white text-2xl font-bold shadow-lg">
            {init}
          </div>
          <div>
            <p className="font-bold text-gray-800 dark:text-white text-lg">
              {fname}
            </p>
            <p className="text-sm text-gray-500">
              @{user?.username}
            </p>
            <span className={`badge mt-1
                             ${user?.role === 'admin'
                               ? 'bg-purple-100 text-purple-700'
                               : 'badge-green'}`}>
              {user?.role === 'admin' ? '👑 Admin' : '👤 Member'}
            </span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          {[
            { label:'Username', value:`@${user?.username}`     },
            { label:'Full Name', value: user?.full_name || '—' },
            { label:'Email',     value: user?.email || '—'     },
            { label:'Member Since',
              value:(user?.created_at || '').slice(0,10) || '—' },
          ].map(f => (
            <div key={f.label}
                 className="bg-gray-50 dark:bg-dark-card2
                            rounded-xl px-3 py-2.5">
              <p className="text-xs text-gray-400 mb-0.5">{f.label}</p>
              <p className="font-medium text-gray-700 dark:text-gray-200">
                {f.value}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Change password */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 dark:text-white
                       flex items-center gap-2 mb-4">
          <Lock size={18} className="text-primary"/> Change Password
        </h2>

        {msg.text && (
          <div className={`rounded-xl px-4 py-2.5 text-sm mb-4
                           flex items-center gap-2
                           ${msg.ok
                             ? 'bg-green-50 border border-green-200 text-green-700'
                             : 'bg-red-50 border border-red-200 text-red-600'
                           }`}>
            {msg.ok ? <CheckCircle size={16}/> : '❌'}
            {msg.text}
          </div>
        )}

        <form onSubmit={changePass} className="space-y-3">
          {[
            { label:'Current Password', val:oldPass, set:setOldPass  },
            { label:'New Password',     val:newPass,  set:setNewPass  },
            { label:'Confirm Password', val:newPass2, set:setNewPass2 },
          ].map(f => (
            <div key={f.label}>
              <label className="text-xs text-gray-500 mb-1 block">
                {f.label}
              </label>
              <input className="input" type="password"
                     placeholder={f.label}
                     value={f.val}
                     onChange={e=>f.set(e.target.value)}/>
            </div>
          ))}
          <button type="submit" disabled={loading}
                  className="btn-primary w-full py-2.5
                             disabled:opacity-60 mt-2">
            {loading ? '⏳ Updating...' : '🔒 Update Password'}
          </button>
        </form>
      </div>

      {/* Admin: All users */}
      {user?.role === 'admin' && allUsers.length > 0 && (
        <div className="card">
          <h2 className="font-semibold text-gray-800 dark:text-white
                         flex items-center gap-2 mb-4">
            <Shield size={18} className="text-purple-500"/> All Users
          </h2>
          <div className="space-y-2">
            {allUsers.map(u => (
              <div key={u.id}
                   className="flex items-center gap-3 p-3
                              bg-gray-50 dark:bg-dark-card2
                              rounded-xl">
                <div className="w-9 h-9 rounded-full
                                bg-gradient-to-br from-primary to-success
                                flex items-center justify-center
                                text-white text-sm font-bold flex-shrink-0">
                  {(u.full_name || u.username)[0]?.toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm text-gray-800
                                dark:text-white truncate">
                    {u.full_name || u.username}
                  </p>
                  <p className="text-xs text-gray-400">@{u.username}</p>
                </div>
                <span className={`badge text-xs
                                 ${u.role === 'admin'
                                   ? 'bg-purple-100 text-purple-700'
                                   : 'badge-gray'}`}>
                  {u.role}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
