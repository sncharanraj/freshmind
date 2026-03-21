// src/pages/Login.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../App'
import { authAPI } from '../api/client'
import { Eye, EyeOff, AlertCircle, X } from 'lucide-react'

export default function Login() {
  const { login } = useAuth()
  const navigate  = useNavigate()
  const [tab,        setTab]        = useState('login')
  const [err,        setErr]        = useState('')
  const [loading,    setLoading]    = useState(false)
  const [showForgot, setShowForgot] = useState(false)
  const [showLP,     setShowLP]     = useState(false)
  const [showRP,     setShowRP]     = useState(false)

  const [lUser, setLUser] = useState('')
  const [lPass, setLPass] = useState('')
  const [rName, setRName]   = useState('')
  const [rUser, setRUser]   = useState('')
  const [rEmail,setREmail]  = useState('')
  const [rPass, setRPass]   = useState('')
  const [rPass2,setRPass2]  = useState('')

  const doLogin = async e => {
    e.preventDefault(); setErr('')
    if (!lUser || !lPass) return setErr('Please fill in all fields!')
    setLoading(true)
    try {
      const res = await authAPI.login({ username:lUser, password:lPass })
      login(res.data.user, res.data.token)
      navigate('/')
    } catch(e) {
      setErr(e.response?.data?.error || 'Wrong username or password!')
    } finally { setLoading(false) }
  }

  const doRegister = async e => {
    e.preventDefault(); setErr('')
    if (!rName||!rUser||!rPass) return setErr('Fill all required fields!')
    if (rPass.length < 6)       return setErr('Password must be at least 6 characters!')
    if (rPass !== rPass2)       return setErr("Passwords don't match!")
    setLoading(true)
    try {
      const res = await authAPI.register({ username:rUser, password:rPass, email:rEmail, full_name:rName })
      login(res.data.user, res.data.token); navigate('/')
    } catch(e) { setErr(e.response?.data?.error || 'Registration failed!')
    } finally { setLoading(false) }
  }

  const ErrBanner = () => !err ? null : (
    <div className="flex items-start gap-2.5 bg-red-50 dark:bg-red-900/30
                    border border-red-200 dark:border-red-800
                    rounded-xl px-4 py-3 mb-5">
      <AlertCircle size={16} className="text-red-500 mt-0.5 flex-shrink-0"/>
      <p className="text-sm text-red-600 dark:text-red-400 flex-1">{err}</p>
      <button onClick={() => setErr('')} className="text-red-400 hover:text-red-600 flex-shrink-0">
        <X size={14}/>
      </button>
    </div>
  )

  return (
    <div className="min-h-screen flex">

      {/* ── LEFT — decorative panel ── */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden flex-col
                      items-center justify-center p-12 select-none">
        {/* Real food photo */}
        <img
          src="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=900&auto=format&fit=crop&q=80"
          alt="Fresh food"
          className="absolute inset-0 w-full h-full object-cover"
        />
        {/* Dark overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/75 via-slate-800/60 to-emerald-900/70"/>

        <div className="relative z-10 text-center text-white max-w-sm">
          <div className="text-6xl mb-5">🥗</div>
          <h1 className="text-4xl font-bold mb-3 drop-shadow-lg">FreshMind</h1>
          <p className="text-slate-200 text-base mb-8 leading-relaxed">
            Your AI-powered smart pantry assistant that reduces food waste and saves money.
          </p>
          <div className="space-y-2 text-left">
            {[
              "🔔 Expiry alerts before food goes bad",
              "🤖 AI recipes from what you have",
              "📊 Track your food saving progress",
              "📦 Smart pantry management",
            ].map(f => (
              <div key={f} className="flex items-center gap-2 text-sm text-slate-200
                                     bg-white/10 backdrop-blur-sm rounded-full px-4 py-2">
                {f}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── RIGHT — form panel ── */}
      <div className="w-full lg:w-1/2 flex items-center justify-center
                      bg-gray-50 dark:bg-dark p-6 overflow-y-auto">
        <div className="w-full max-w-md py-8">

          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="text-5xl mb-2">🥗</div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-success
                           bg-clip-text text-transparent">FreshMind</h1>
          </div>

          <div className="bg-white dark:bg-dark-card rounded-3xl shadow-xl p-8
                          border border-gray-100 dark:border-dark-border">

            <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-1">
              {tab === 'login' ? '👋 Welcome back!' : '🆕 Create account'}
            </h2>
            <p className="text-sm text-gray-400 mb-6">
              {tab === 'login' ? 'Sign in to manage your pantry' : 'Join FreshMind today — it\'s free!'}
            </p>

            {/* Tabs */}
            <div className="flex bg-gray-100 dark:bg-dark-card2 rounded-xl p-1 mb-6 gap-1">
              {[['login','🔐 Login'],['register','📝 Register']].map(([t,l]) => (
                <button key={t} onClick={() => { setTab(t); setErr('') }}
                        className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all
                                    ${tab===t
                                      ? 'bg-white dark:bg-dark-card shadow text-primary'
                                      : 'text-gray-500 hover:text-gray-700'}`}>
                  {l}
                </button>
              ))}
            </div>

            <ErrBanner/>

            {/* LOGIN */}
            {tab === 'login' && (
              <form onSubmit={doLogin} className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-300 block mb-1.5">
                    Username
                  </label>
                  <input className="input" placeholder="Enter your username"
                         autoComplete="username"
                         value={lUser} onChange={e=>setLUser(e.target.value)}/>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-300 block mb-1.5">
                    Password
                  </label>
                  <div className="relative">
                    <input className="input pr-10"
                           type={showLP ? 'text' : 'password'}
                           placeholder="Enter your password"
                           autoComplete="current-password"
                           value={lPass} onChange={e=>setLPass(e.target.value)}/>
                    <button type="button" onClick={()=>setShowLP(!showLP)}
                            className="absolute right-3 top-1/2 -translate-y-1/2
                                       text-gray-400 hover:text-gray-600">
                      {showLP ? <EyeOff size={16}/> : <Eye size={16}/>}
                    </button>
                  </div>
                </div>
                <div className="flex justify-end -mt-1">
                  <button type="button" onClick={()=>setShowForgot(true)}
                          className="text-xs text-primary hover:underline">
                    Forgot password?
                  </button>
                </div>
                <button type="submit" disabled={loading}
                        className="btn-primary w-full py-3 font-semibold disabled:opacity-60">
                  {loading
                    ? <span className="flex items-center justify-center gap-2">
                        <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin"/>
                        Signing in...
                      </span>
                    : 'Sign In →'}
                </button>
              </form>
            )}

            {/* REGISTER */}
            {tab === 'register' && (
              <form onSubmit={doRegister} className="space-y-3">
                {[
                  { label:'Full Name *', val:rName,  set:setRName,  ph:'Your full name',    type:'text'  },
                  { label:'Username *',  val:rUser,  set:setRUser,  ph:'Choose a username', type:'text'  },
                  { label:'Email',       val:rEmail, set:setREmail, ph:'your@email.com',    type:'email' },
                ].map(f=>(
                  <div key={f.label}>
                    <label className="text-sm font-medium text-gray-600 dark:text-gray-300 block mb-1.5">{f.label}</label>
                    <input className="input" placeholder={f.ph} type={f.type}
                           value={f.val} onChange={e=>f.set(e.target.value)}/>
                  </div>
                ))}
                <div>
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-300 block mb-1.5">Password *</label>
                  <div className="relative">
                    <input className="input pr-10" type={showRP?'text':'password'}
                           placeholder="Min 6 characters"
                           value={rPass} onChange={e=>setRPass(e.target.value)}/>
                    <button type="button" onClick={()=>setShowRP(!showRP)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                      {showRP?<EyeOff size={16}/>:<Eye size={16}/>}
                    </button>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-300 block mb-1.5">Confirm Password *</label>
                  <input className="input" type="password" placeholder="Repeat password"
                         value={rPass2} onChange={e=>setRPass2(e.target.value)}/>
                </div>
                <button type="submit" disabled={loading}
                        className="btn-primary w-full py-3 font-semibold disabled:opacity-60 mt-1">
                  {loading
                    ? <span className="flex items-center justify-center gap-2">
                        <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin"/>
                        Creating...
                      </span>
                    : 'Create Account →'}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>

      {/* ── FORGOT PASSWORD MODAL ── */}
      {showForgot && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50
                        flex items-center justify-center p-4">
          <div className="bg-white dark:bg-dark-card rounded-2xl shadow-2xl p-6
                          w-full max-w-sm border border-gray-100 dark:border-dark-border
                          animate-slide-up">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-gray-800 dark:text-white">🔑 Forgot Password</h3>
              <button onClick={()=>setShowForgot(false)}
                      className="p-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-dark-card2
                                 text-gray-400 hover:text-gray-600 transition">
                <X size={16}/>
              </button>
            </div>
            <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200
                            dark:border-amber-800 rounded-xl p-3.5 mb-4">
              <p className="text-sm text-amber-700 dark:text-amber-300">
                Contact your admin to reset your password, or use one of the default accounts below.
              </p>
            </div>
            <div className="space-y-2 text-sm mb-5">
              {[
                ['Admin',    'admin',    'admin123'   ],
                ['Person A', 'person_a', 'persona123' ],
                ['Person B', 'person_b', 'personb123' ],
              ].map(([name, u, p]) => (
                <div key={u} className="flex justify-between items-center p-3
                                        bg-gray-50 dark:bg-dark-card2 rounded-xl">
                  <span className="text-gray-500">{name}</span>
                  <span className="font-mono text-xs bg-gray-100 dark:bg-dark-border
                                   px-2 py-1 rounded text-gray-700 dark:text-gray-200">
                    {u} / {p}
                  </span>
                </div>
              ))}
            </div>
            <button onClick={()=>setShowForgot(false)} className="btn-primary w-full py-2.5">
              Got it!
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
