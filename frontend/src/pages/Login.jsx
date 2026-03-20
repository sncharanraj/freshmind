// src/pages/Login.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../App'
import { authAPI } from '../api/client'

const FOOD = ["🥦","🍎","🥛","🧅","🍗","🥚","🍞","🥕","🧄","🍋","🥬","🍅"]

export default function Login() {
  const { login } = useAuth()
  const navigate  = useNavigate()
  const [tab, setTab]     = useState('login')
  const [err, setErr]     = useState('')
  const [loading, setLoading] = useState(false)

  // Login form
  const [lUser, setLUser] = useState('')
  const [lPass, setLPass] = useState('')

  // Register form
  const [rName,  setRName]  = useState('')
  const [rUser,  setRUser]  = useState('')
  const [rEmail, setREmail] = useState('')
  const [rPass,  setRPass]  = useState('')
  const [rPass2, setRPass2] = useState('')

  const doLogin = async e => {
    e.preventDefault(); setErr('')
    if (!lUser || !lPass) return setErr('Fill in all fields!')
    setLoading(true)
    try {
      const res = await authAPI.login({ username: lUser, password: lPass })
      login(res.data.user, res.data.token)
      navigate('/')
    } catch(e) {
      setErr(e.response?.data?.error || 'Login failed!')
    } finally { setLoading(false) }
  }

  const doRegister = async e => {
    e.preventDefault(); setErr('')
    if (!rName || !rUser || !rPass) return setErr('Fill all required fields!')
    if (rPass.length < 6) return setErr('Password min 6 characters!')
    if (rPass !== rPass2) return setErr('Passwords don\'t match!')
    setLoading(true)
    try {
      const res = await authAPI.register({
        username: rUser, password: rPass,
        email: rEmail, full_name: rName
      })
      login(res.data.user, res.data.token)
      navigate('/')
    } catch(e) {
      setErr(e.response?.data?.error || 'Register failed!')
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center
                    bg-gradient-to-br from-green-900 via-green-700
                    to-emerald-600 relative overflow-hidden">

      {/* Food rain animation */}
      {FOOD.map((f, i) => (
        <div key={i} className="food-drop text-2xl opacity-30"
             style={{
               left:`${5 + i * 8}%`,
               animationDuration:`${4 + i * 0.4}s`,
               animationDelay:`${i * 0.3}s`,
               fontSize:'1.6rem'
             }}>
          {f}
        </div>
      ))}

      {/* Card */}
      <div className="relative z-10 w-full max-w-md mx-4
                      bg-white dark:bg-dark-card rounded-3xl
                      shadow-2xl p-8 animate-slide-up">

        {/* Logo */}
        <div className="text-center mb-6">
          <div className="text-5xl mb-2">🥗</div>
          <h1 className="text-2xl font-bold bg-gradient-to-r
                         from-primary to-success bg-clip-text
                         text-transparent">
            FreshMind
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Your AI-Powered Smart Pantry Assistant
          </p>
        </div>

        {/* Tabs */}
        <div className="flex bg-gray-100 dark:bg-dark-card2
                        rounded-xl p-1 mb-6">
          {['login','register'].map(t => (
            <button key={t} onClick={() => { setTab(t); setErr('') }}
                    className={`flex-1 py-2 text-sm font-medium
                                rounded-lg transition-all duration-150
                                ${tab === t
                                  ? 'bg-white dark:bg-dark-card shadow text-primary'
                                  : 'text-gray-500 hover:text-gray-700'
                                }`}>
              {t === 'login' ? '🔐 Login' : '📝 Register'}
            </button>
          ))}
        </div>

        {/* Error */}
        {err && (
          <div className="bg-red-50 border border-red-200 text-red-600
                          rounded-xl px-4 py-2.5 text-sm mb-4">
            ❌ {err}
          </div>
        )}

        {/* LOGIN FORM */}
        {tab === 'login' && (
          <form onSubmit={doLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-600
                                dark:text-gray-300 mb-1">
                👤 Username
              </label>
              <input className="input" placeholder="Enter username"
                     value={lUser} onChange={e=>setLUser(e.target.value)}/>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600
                                dark:text-gray-300 mb-1">
                🔒 Password
              </label>
              <input className="input" type="password"
                     placeholder="Enter password"
                     value={lPass} onChange={e=>setLPass(e.target.value)}/>
            </div>
            <button type="submit" disabled={loading}
                    className="btn-primary w-full py-3 text-base
                               disabled:opacity-60">
              {loading ? '⏳ Logging in...' : '🔐 Login'}
            </button>
            <p className="text-center text-xs text-gray-400 mt-2">
              Demo: <b className="text-gray-600 dark:text-gray-300">admin</b>
              {' / '}
              <b className="text-gray-600 dark:text-gray-300">admin123</b>
            </p>
          </form>
        )}

        {/* REGISTER FORM */}
        {tab === 'register' && (
          <form onSubmit={doRegister} className="space-y-3">
            {[
              { label:"👤 Full Name *", val:rName,  set:setRName,  ph:"Your full name" },
              { label:"🆔 Username *",  val:rUser,  set:setRUser,  ph:"Choose a username" },
              { label:"📧 Email",       val:rEmail, set:setREmail, ph:"your@email.com" },
            ].map(f => (
              <div key={f.label}>
                <label className="block text-sm font-medium text-gray-600
                                  dark:text-gray-300 mb-1">{f.label}</label>
                <input className="input" placeholder={f.ph}
                       value={f.val} onChange={e=>f.set(e.target.value)}/>
              </div>
            ))}
            <div>
              <label className="block text-sm font-medium text-gray-600
                                dark:text-gray-300 mb-1">🔒 Password *</label>
              <input className="input" type="password" placeholder="Min 6 characters"
                     value={rPass} onChange={e=>setRPass(e.target.value)}/>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600
                                dark:text-gray-300 mb-1">🔒 Confirm *</label>
              <input className="input" type="password" placeholder="Repeat password"
                     value={rPass2} onChange={e=>setRPass2(e.target.value)}/>
            </div>
            <button type="submit" disabled={loading}
                    className="btn-primary w-full py-3 text-base
                               disabled:opacity-60 mt-2">
              {loading ? '⏳ Creating...' : '📝 Create Account'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
