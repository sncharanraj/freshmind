// src/components/NotifBell.jsx
import { useState, useRef, useEffect } from 'react'
import { Bell, X } from 'lucide-react'

const FOOD_EMOJIS = {
  Dairy:"🥛", Vegetables:"🥦", Fruits:"🍎",
  "Meat & Seafood":"🍗", "Grains & Cereals":"🌾",
  Snacks:"🍿", Beverages:"🥤", Condiments:"🧂", Other:"🛒"
}

function getExpiryInfo(expiry_str) {
  const today  = new Date(); today.setHours(0,0,0,0)
  const expiry = new Date(expiry_str)
  const days   = Math.round((expiry - today) / 86400000)
  if (days < 0)  return { label:`EXPIRED ${Math.abs(days)}d ago!`, color:"#f44336", bg:"#fff5f5" }
  if (days === 0) return { label:"Expires TODAY! 🚨",               color:"#f44336", bg:"#fff5f5" }
  if (days <= 3)  return { label:`In ${days} day(s) ⚠️`,           color:"#ff9800", bg:"#fff8f0" }
  return              { label:expiry_str,                            color:"#ff9800", bg:"#fff8f0" }
}

export default function NotifBell({ expiring = [] }) {
  const [open, setOpen] = useState(false)
  const ref = useRef()

  // Close on outside click
  useEffect(() => {
    const handler = e => {
      if (ref.current && !ref.current.contains(e.target))
        setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  // Close on ESC
  useEffect(() => {
    const handler = e => { if (e.key === 'Escape') setOpen(false) }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [])

  return (
    <div className="relative" ref={ref}>

      {/* Bell button */}
      <button
        onClick={() => setOpen(!open)}
        className="relative p-2 rounded-xl
                   hover:bg-gray-100 dark:hover:bg-dark-card2
                   transition"
      >
        <Bell size={18} className={
          expiring.length > 0
            ? "text-red-500 animate-pulse-slow"
            : "text-gray-600 dark:text-gray-300"
        }/>
        {expiring.length > 0 && (
          <span className="absolute -top-1 -right-1
                           bg-red-500 text-white text-[9px]
                           font-bold min-w-[16px] h-4
                           rounded-full flex items-center
                           justify-center px-1 border-2
                           border-white dark:border-dark-card">
            {expiring.length}
          </span>
        )}
      </button>

      {/* Dropdown popup */}
      {open && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
            onClick={() => setOpen(false)}
          />

          {/* Panel */}
          <div className="fixed top-1/2 left-1/2 z-50
                          w-[min(420px,90vw)] max-h-[72vh]
                          bg-white dark:bg-dark-card
                          rounded-2xl shadow-2xl
                          border border-light-border dark:border-dark-border
                          flex flex-col modal-box"
               style={{ transform:'translate(-50%,-50%)' }}>

            {/* Header */}
            <div className="flex items-center justify-between
                            px-5 py-4
                            border-b border-light-border dark:border-dark-border">
              <div className="flex items-center gap-2">
                <Bell size={18} className="text-red-500" />
                <h2 className="font-bold text-gray-800 dark:text-white">
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
                className="p-1.5 rounded-full
                           hover:bg-red-100 dark:hover:bg-red-900/30
                           hover:text-red-500 transition"
              >
                <X size={16} />
              </button>
            </div>

            {/* Body */}
            <div className="overflow-y-auto flex-1 p-4 space-y-3">
              {expiring.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-4xl mb-3">✅</div>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">
                    No expiry alerts! Everything is fresh.
                  </p>
                </div>
              ) : expiring.map(item => {
                const { label, color } = getExpiryInfo(item.expiry_date)
                const emoji = FOOD_EMOJIS[item.category] || '🛒'
                return (
                  <div key={item.id}
                       className="flex items-center justify-between
                                  p-3 rounded-xl
                                  bg-gray-50 dark:bg-dark-card2"
                       style={{ borderLeft:`3px solid ${color}` }}>
                    <div>
                      <p className="font-semibold text-sm
                                    text-gray-800 dark:text-white">
                        {emoji} {item.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                        📁 {item.category} &nbsp;|&nbsp; 📏 {item.quantity}
                      </p>
                    </div>
                    <span className="text-xs font-bold px-2.5 py-1
                                     rounded-full whitespace-nowrap ml-3"
                          style={{ color, background:`${color}22` }}>
                      {label}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
