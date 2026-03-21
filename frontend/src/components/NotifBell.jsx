// src/components/NotifBell.jsx
import { useState, useRef, useEffect } from 'react'
import { Bell, X, Package } from 'lucide-react'

const FOOD_EMOJIS = {
  Dairy:"🥛", Vegetables:"🥦", Fruits:"🍎",
  "Meat & Seafood":"🍗", "Grains & Cereals":"🌾",
  Snacks:"🍿", Beverages:"🥤", Condiments:"🧂", Other:"🛒"
}

function getExpiryInfo(expiry_str) {
  const today  = new Date(); today.setHours(0,0,0,0)
  const expiry = new Date(expiry_str)
  const days   = Math.round((expiry - today) / 86400000)
  if (days < 0)   return { label:`EXPIRED ${Math.abs(days)}d ago!`, color:"#ef4444", bg:"bg-red-50 dark:bg-red-900/20",    border:"border-red-200 dark:border-red-800"    }
  if (days === 0) return { label:"Expires TODAY! 🚨",               color:"#ef4444", bg:"bg-red-50 dark:bg-red-900/20",    border:"border-red-200 dark:border-red-800"    }
  if (days <= 3)  return { label:`In ${days} day(s) ⚠️`,           color:"#f59e0b", bg:"bg-amber-50 dark:bg-amber-900/20",border:"border-amber-200 dark:border-amber-800"}
  return              { label:`Expires ${expiry_str}`,              color:"#f59e0b", bg:"bg-amber-50 dark:bg-amber-900/20",border:"border-amber-200 dark:border-amber-800"}
}

export default function NotifBell({ expiring = [] }) {
  const [open, setOpen] = useState(false)

  // Close on ESC
  useEffect(() => {
    const handler = e => { if (e.key === 'Escape') setOpen(false) }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [])

  return (
    <>
      {/* Bell button */}
      <button
        onClick={() => setOpen(!open)}
        className="relative p-2 rounded-xl hover:bg-gray-100
                   dark:hover:bg-dark-card2 transition"
      >
        <Bell size={18} className={
          expiring.length > 0
            ? "text-red-500"
            : "text-gray-600 dark:text-gray-300"
        }/>
        {expiring.length > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white
                           text-[9px] font-bold min-w-[16px] h-4 rounded-full
                           flex items-center justify-center px-1
                           border-2 border-white dark:border-dark-card
                           animate-bounce">
            {expiring.length}
          </span>
        )}
      </button>

      {/* ── Floating popup from top-right ── */}
      {open && (
        <>
          {/* Dim backdrop — click to close */}
          <div
            className="fixed inset-0 bg-black/20 backdrop-blur-[1px] z-40"
            onClick={() => setOpen(false)}
          />

          {/* Popup panel — drops down from topbar */}
          <div className="fixed top-14 right-4 w-80 max-h-[70vh] z-50
                          bg-white dark:bg-dark-card
                          border border-gray-200 dark:border-dark-border
                          rounded-2xl shadow-2xl flex flex-col
                          animate-slide-in-right">

            {/* Header */}
            <div className="flex items-center justify-between
                            px-4 py-3 border-b border-gray-100
                            dark:border-dark-border flex-shrink-0">
              <div className="flex items-center gap-2">
                <Bell size={16} className="text-red-500"/>
                <h2 className="font-bold text-gray-800 dark:text-white text-sm">
                  Expiry Alerts
                </h2>
                {expiring.length > 0 && (
                  <span className="bg-red-500 text-white text-xs
                                   px-2 py-0.5 rounded-full font-bold">
                    {expiring.length}
                  </span>
                )}
              </div>
              <button
                onClick={() => setOpen(false)}
                className="p-1 rounded-full hover:bg-gray-100
                           dark:hover:bg-dark-card2 text-gray-400
                           hover:text-gray-600 transition"
              >
                <X size={14}/>
              </button>
            </div>

            {/* Body */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {expiring.length === 0 ? (
                <div className="flex flex-col items-center justify-center
                                py-10 text-center text-gray-400">
                  <div className="text-4xl mb-2">✅</div>
                  <p className="text-sm font-medium text-gray-500">All good! No alerts.</p>
                  <p className="text-xs mt-0.5">Everything is fresh.</p>
                </div>
              ) : (
                <>
                  <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">
                    {expiring.length} item(s) need attention
                  </p>
                  {expiring.map(item => {
                    const { label, color, bg, border } = getExpiryInfo(item.expiry_date)
                    const emoji = FOOD_EMOJIS[item.category] || '🛒'
                    return (
                      <div key={item.id}
                           className={`p-3 rounded-xl ${bg} border ${border}`}
                           style={{ borderLeft:`3px solid ${color}` }}>
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <p className="font-semibold text-sm text-gray-800
                                          dark:text-white truncate">
                              {emoji} {item.name}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                              {item.category} · {item.quantity}
                            </p>
                          </div>
                          <span className="text-xs font-bold px-2 py-1 rounded-full
                                           whitespace-nowrap flex-shrink-0"
                                style={{ color, background:`${color}22` }}>
                            {label}
                          </span>
                        </div>
                      </div>
                    )
                  })}
                </>
              )}
            </div>

            {/* Footer */}
            <div className="px-3 py-2.5 border-t border-gray-100
                            dark:border-dark-border flex-shrink-0">
              <button onClick={() => setOpen(false)}
                      className="btn-ghost w-full text-xs py-1.5">
                Close
              </button>
            </div>
          </div>
        </>
      )}
    </>
  )
}