// src/pages/Home.jsx
import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../App'
import { pantryAPI, aiAPI, weatherAPI } from '../api/client'
import { Package, AlertTriangle, CheckCircle, Trash2,
         PlusCircle, Bot, BarChart2, ChevronRight } from 'lucide-react'

const FOOD_EMOJIS = {
  Dairy:"🥛", Vegetables:"🥦", Fruits:"🍎",
  "Meat & Seafood":"🍗", "Grains & Cereals":"🌾",
  Snacks:"🍿", Beverages:"🥤", Condiments:"🧂", Other:"🛒"
}

const TIPS = [
  { i:"🥦", t:"Store Vegetables Right",  x:"Wrap leafy greens in damp paper towels. Stay fresh 2x longer!" },
  { i:"🧅", t:"Onion & Potato Rule",     x:"Never store together — onions release gases that sprout potatoes!" },
  { i:"🍋", t:"Citrus Juice Hack",       x:"Microwave lemons 15s before squeezing — 2x more juice!" },
  { i:"🥛", t:"Milk Storage Tip",        x:"Store milk on middle shelf, not the door — stays cooler!" },
  { i:"🍌", t:"Banana Trick",            x:"Wrap banana stems in plastic wrap to slow ripening!" },
  { i:"🧄", t:"Garlic Freshness",        x:"Store at room temp in a mesh bag. Lasts 6 months!" },
  { i:"🍞", t:"Bread Hack",              x:"Freeze bread you won't use in 3 days. Toast from freezer!" },
  { i:"🥚", t:"Egg Test",               x:"Sink=fresh, float=bad. Never eat a floating egg!" },
  { i:"🌿", t:"Fresh Herbs",             x:"Store in a glass of water in fridge like flowers!" },
  { i:"🍎", t:"Apple Storage",           x:"Apples release ethylene gas — store separately!" },
]

const FOOD_RAIN = ["🥦","🍎","🥛","🧅","🍗","🥚","🍞","🥕","🧄","🍋","🥬","🍅"]

function CountUp({ target, duration = 1200 }) {
  const [count, setCount] = useState(0)
  useEffect(() => {
    if (!target) { setCount(0); return }
    let start = 0
    const step = target / (duration / 16)
    const timer = setInterval(() => {
      start += step
      if (start >= target) { setCount(target); clearInterval(timer) }
      else setCount(Math.floor(start))
    }, 16)
    return () => clearInterval(timer)
  }, [target])
  return <span>{count}</span>
}

function getExpInfo(expiry_str) {
  const today  = new Date(); today.setHours(0,0,0,0)
  const expiry = new Date(expiry_str)
  const days   = Math.round((expiry - today) / 86400000)
  if (days < 0)  return { label:`EXPIRED ${Math.abs(days)}d ago!`, color:"text-red-500",    days }
  if (days === 0) return { label:"Expires TODAY!",                  color:"text-red-500",    days }
  if (days <= 3)  return { label:`In ${days}d ⚠️`,                 color:"text-orange-500", days }
  return              { label:`${days}d left`,                      color:"text-green-500",  days }
}

export default function Home() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const fname    = user?.full_name || user?.username || 'User'

  const [items,    setItems]    = useState([])
  const [expiring, setExpiring] = useState([])
  const [critical, setCritical] = useState([])
  const [history,  setHistory]  = useState([])
  const [weather,  setWeather]  = useState(null)
  const [tipIdx,   setTipIdx]   = useState(0)
  const [aiTips,   setAiTips]   = useState('')
  const [aiLoad,   setAiLoad]   = useState(false)
  const [loading,  setLoading]  = useState(true)
  const tipRef = useRef()

  useEffect(() => {
    Promise.all([
      pantryAPI.getAll(),
      pantryAPI.getExpiring(7),
      pantryAPI.getExpiring(3),
      pantryAPI.getHistory(),
      weatherAPI.get(),
    ]).then(([a, e, c, h, w]) => {
      setItems(a.data.items || [])
      setExpiring(e.data.items || [])
      setCritical(c.data.items || [])
      setHistory(h.data.history || [])
      setWeather(w.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  // Auto-advance tips every 8s
  useEffect(() => {
    const t = setInterval(() =>
      setTipIdx(i => (i + 1) % TIPS.length), 8000)
    return () => clearInterval(t)
  }, [])

  const saved  = history.filter(h => !h.was_wasted)
  const wasted = history.filter(h =>  h.was_wasted)
  const today  = new Date().toLocaleDateString('en-US', {
    weekday:'long', year:'numeric', month:'long', day:'numeric'
  })

  const getAiTips = async () => {
    setAiLoad(true); setAiTips('')
    try {
      const names = items.slice(0,10).map(i => i.name).join(', ') || 'empty pantry'
      const res   = await aiAPI.chat(
        `Give 3 quick storage/cooking tips for: ${names}. Format: emoji + tip. Each under 2 sentences.`,
        []
      )
      setAiTips(res.data.response)
    } catch { setAiTips('❌ Could not get tips. Check your API key.') }
    setAiLoad(false)
  }

  const METRICS = [
    { label:"Total Items",      value:items.length,    color:"text-primary",  bg:"bg-primary/10",  icon:Package,       nav:null        },
    { label:"Expiring This Week",value:expiring.length, color:"text-pink-500", bg:"bg-pink-50",     icon:AlertTriangle, nav:"/pantry"   },
    { label:"Items Saved",      value:saved.length,    color:"text-success",  bg:"bg-green-50",    icon:CheckCircle,   nav:null        },
    { label:"Items Wasted",     value:wasted.length,   color:"text-danger",   bg:"bg-red-50",      icon:Trash2,        nav:null        },
  ]

  const ACTIONS = [
    { icon:"➕", label:"Add Item",   desc:"Add new pantry item", to:"/add"       },
    { icon:"📦", label:"My Pantry", desc:"View & manage items",  to:"/pantry"   },
    { icon:"🤖", label:"AI Recipes",desc:"Get smart recipes",    to:"/recipes"  },
    { icon:"📊", label:"Dashboard", desc:"View analytics",       to:"/dashboard"},
  ]

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-4xl animate-bounce">🥗</div>
    </div>
  )

  return (
    <div className="space-y-6 animate-fade-in">

      {/* ── Hero Banner ── */}
      <div className="relative bg-gradient-to-r from-green-800 to-emerald-600
                      rounded-2xl p-6 overflow-hidden min-h-[110px]">
        {/* Food rain */}
        {FOOD_RAIN.map((f, i) => (
          <div key={i} className="food-drop text-lg"
               style={{
                 left:`${5+i*8}%`, top:'-30px',
                 animationDuration:`${3+i*0.3}s`,
                 animationDelay:`${i*0.2}s`
               }}>{f}</div>
        ))}

        {/* Big leaf bg */}
        <div className="absolute right-8 top-1/2 -translate-y-1/2
                        text-7xl opacity-10 pointer-events-none">🥗</div>

        {/* Content */}
        <div className="relative z-10">
          <p className="text-xs font-semibold uppercase tracking-widest
                        text-green-200 mb-1">
            {today}
          </p>
          <h1 className="text-2xl font-bold text-white">
            👋 Hello, {fname}!
          </h1>
          <p className="text-green-100 text-sm mt-1">
            Here's your pantry overview
          </p>
        </div>

        {/* Weather chip */}
        {weather && (
          <div className="absolute top-4 right-4
                          bg-white/20 backdrop-blur-md
                          rounded-xl px-3 py-1.5 text-white text-sm">
            {parseInt(weather.temp) > 30 ? '☀️' : '🌤️'}
            {' '}{weather.temp}°C · {weather.desc}
          </div>
        )}
      </div>

      {/* ── Metric Cards ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {METRICS.map(({ label, value, color, bg, icon:Icon, nav }) => (
          <div key={label}
               onClick={() => nav && navigate(nav)}
               className={`card flex flex-col items-center p-5
                           ${nav ? 'cursor-pointer hover:-translate-y-2 hover:shadow-xl' : 'hover:-translate-y-1'}
                           transition-all duration-200`}>
            <div className={`${bg} p-3 rounded-full mb-3`}>
              <Icon size={22} className={color} />
            </div>
            <p className={`text-3xl font-bold ${color}`}>
              <CountUp target={value} />
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 text-center">
              {label}
            </p>
          </div>
        ))}
      </div>

      {/* ── Alert Banners ── */}
      {critical.length > 0 && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200
                        dark:border-red-800 rounded-xl p-4">
          <p className="font-semibold text-red-600 mb-2">
            🚨 Critical — Use these items immediately!
          </p>
          {critical.map(item => {
            const { label } = getExpInfo(item.expiry_date)
            return (
              <div key={item.id}
                   className="flex items-center gap-2 text-sm
                              text-red-700 dark:text-red-300 mt-1">
                <span>⚠️</span>
                <b>{item.name}</b>
                <span className="text-gray-500">({item.category})</span>
                <span>— {label}</span>
              </div>
            )
          })}
        </div>
      )}

      {!critical.length && expiring.length > 0 && (
        <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200
                        dark:border-orange-800 rounded-xl px-4 py-3 text-sm
                        text-orange-700 dark:text-orange-300">
          ⚠️ <b>{expiring.length}</b> item(s) expiring this week!
        </div>
      )}

      {!expiring.length && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200
                        dark:border-green-800 rounded-xl px-4 py-3 text-sm
                        text-green-700 dark:text-green-300">
          ✅ Everything is fresh!
        </div>
      )}

      {/* ── Quick Actions ── */}
      <div>
        <h2 className="font-bold text-gray-800 dark:text-white mb-3">
          ⚡ Quick Actions
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {ACTIONS.map(({ icon, label, desc, to }) => (
            <button key={to} onClick={() => navigate(to)}
                    className="card flex flex-col items-center py-6
                               hover:-translate-y-2 hover:border-primary
                               hover:shadow-xl transition-all duration-200
                               cursor-pointer group">
              <div className="text-4xl mb-2 group-hover:scale-110
                              transition-transform duration-200">
                {icon}
              </div>
              <p className="font-semibold text-sm text-gray-800
                            dark:text-white">{label}</p>
              <p className="text-xs text-gray-400 mt-0.5">{desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* ── Cooking Tips ── */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-bold text-gray-800 dark:text-white">
            🍳 Cooking Tips of the Day
          </h2>
          <button onClick={getAiTips} disabled={aiLoad}
                  className="btn-ghost text-sm flex items-center gap-1.5
                             disabled:opacity-60">
            {aiLoad ? '⏳ Loading...' : '✨ AI Tips'}
          </button>
        </div>

        {aiTips && (
          <div className="bg-primary/5 border border-primary/20
                          rounded-xl p-4 mb-3 text-sm
                          text-gray-700 dark:text-gray-300 whitespace-pre-line">
            💡 {aiTips}
          </div>
        )}

        {/* Tip slider */}
        <div className="card">
          <div className="text-3xl mb-2">{TIPS[tipIdx].i}</div>
          <h3 className="font-semibold text-gray-800 dark:text-white mb-1">
            {TIPS[tipIdx].t}
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {TIPS[tipIdx].x}
          </p>

          {/* Dot indicators */}
          <div className="flex gap-1.5 mt-4">
            {TIPS.map((_, i) => (
              <button key={i} onClick={() => setTipIdx(i)}
                      className={`h-1.5 rounded-full transition-all duration-300
                                  ${i === tipIdx
                                    ? 'bg-primary w-5'
                                    : 'bg-gray-200 dark:bg-dark-border w-1.5'
                                  }`}/>
            ))}
          </div>
        </div>
      </div>

      {/* ── Recent Activity ── */}
      <div>
        <h2 className="font-bold text-gray-800 dark:text-white mb-3">
          🕐 Recent Activity
        </h2>
        {history.length === 0 ? (
          <div className="card text-center text-gray-400 py-8">
            No activity yet — start using your pantry!
          </div>
        ) : (
          <div className="space-y-2">
            {history.slice(0, 5).map((h, i) => {
              const used  = !h.was_wasted
              const color = used ? "border-success" : "border-danger"
              return (
                <div key={i}
                     className={`flex items-center gap-3 p-3
                                 bg-white dark:bg-dark-card
                                 rounded-xl border-l-4 ${color}
                                 shadow-sm`}>
                  <span className="text-lg">{used ? '✅' : '🗑️'}</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    <b>{h.item_name}</b>
                    {' — '}{used ? 'Used' : 'Wasted'}
                    {' on '}{h.used_date}
                  </span>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
