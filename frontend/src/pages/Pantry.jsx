// src/pages/Pantry.jsx
import { useState, useEffect } from 'react'
import { pantryAPI } from '../api/client'
import { Pencil, Trash2, CheckCircle, Search, Filter } from 'lucide-react'

const FOOD_EMOJIS = {
  Dairy:"🥛", Vegetables:"🥦", Fruits:"🍎",
  "Meat & Seafood":"🍗", "Grains & Cereals":"🌾",
  Snacks:"🍿", Beverages:"🥤", Condiments:"🧂", Other:"🛒"
}
const CATS = ["All","Dairy","Vegetables","Fruits","Meat & Seafood",
              "Grains & Cereals","Snacks","Beverages","Condiments","Other"]

function getExpInfo(expiry_str) {
  const today  = new Date(); today.setHours(0,0,0,0)
  const expiry = new Date(expiry_str)
  const days   = Math.round((expiry - today) / 86400000)
  if (days < 0)   return { label:`EXPIRED!`,    cls:"badge-red",    days, bar:"bg-red-500"    }
  if (days === 0) return { label:`Today!`,       cls:"badge-red",    days, bar:"bg-red-500"    }
  if (days <= 3)  return { label:`${days}d left`,cls:"badge-red",    days, bar:"bg-red-400"    }
  if (days <= 7)  return { label:`${days}d left`,cls:"badge-orange", days, bar:"bg-orange-400" }
  return              { label:`${days}d left`,   cls:"badge-green",  days, bar:"bg-green-400"  }
}

export default function Pantry() {
  const [items,     setItems]     = useState([])
  const [loading,   setLoading]   = useState(true)
  const [search,    setSearch]    = useState('')
  const [catFilter, setCatFilter] = useState('All')
  const [expFilter, setExpFilter] = useState('All')
  const [editItem,  setEditItem]  = useState(null)
  const [editForm,  setEditForm]  = useState({})

  const load = () => {
    setLoading(true)
    pantryAPI.getAll()
      .then(r => { setItems(r.data.items || []); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const markUsed = async id => {
    await pantryAPI.markUsed(id); load()
  }
  const deleteIt = async id => {
    if (!confirm('Delete this item?')) return
    await pantryAPI.delete(id, true); load()
  }
  const startEdit = item => {
    setEditItem(item.id)
    setEditForm({
      name: item.name, quantity: item.quantity,
      expiry_date: item.expiry_date, category: item.category
    })
  }
  const saveEdit = async id => {
    await pantryAPI.update(id, editForm)
    setEditItem(null); load()
  }

  const filtered = items.filter(item => {
    const { days } = getExpInfo(item.expiry_date)
    const ms = !search || item.name.toLowerCase().includes(search.toLowerCase())
    const mc = catFilter === 'All' || item.category === catFilter
    const me = expFilter === 'All'
            || (expFilter === 'Critical (≤3d)' && days <= 3)
            || (expFilter === 'Expiring (≤7d)' && days <= 7)
            || (expFilter === 'Fresh (>7d)'    && days > 7)
    return ms && mc && me
  })

  return (
    <div className="animate-fade-in space-y-5">

      {/* Hero */}
      <div className="bg-gradient-to-r from-green-800 to-emerald-600
                      rounded-2xl p-5 text-white">
        <h1 className="text-2xl font-bold">📦 My Pantry</h1>
        <p className="text-green-100 text-sm mt-1">Manage your food items</p>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2
                                       -translate-y-1/2 text-gray-400"/>
          <input className="input pl-9" placeholder="Search items..."
                 value={search} onChange={e=>setSearch(e.target.value)}/>
        </div>
        <select className="input" value={catFilter}
                onChange={e=>setCatFilter(e.target.value)}>
          {CATS.map(c => <option key={c}>{c}</option>)}
        </select>
        <select className="input" value={expFilter}
                onChange={e=>setExpFilter(e.target.value)}>
          {["All","Critical (≤3d)","Expiring (≤7d)","Fresh (>7d)"].map(f =>
            <option key={f}>{f}</option>
          )}
        </select>
      </div>

      <p className="text-sm text-gray-500 dark:text-gray-400">
        Showing <b>{filtered.length}</b> of <b>{items.length}</b> items
      </p>

      {loading ? (
        <div className="text-center py-12 text-4xl animate-bounce">🥗</div>
      ) : filtered.length === 0 ? (
        <div className="card text-center py-12 text-gray-400">
          🛒 No items found!
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(item => {
            const { label, cls, days, bar } = getExpInfo(item.expiry_date)
            const emoji = FOOD_EMOJIS[item.category] || '🛒'

            if (editItem === item.id) return (
              <div key={item.id} className="card border-2 border-primary/30 space-y-3">
                <h3 className="font-semibold text-gray-800 dark:text-white">
                  ✏️ Editing: <b>{item.name}</b>
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Name</label>
                    <input className="input" value={editForm.name}
                           onChange={e=>setEditForm({...editForm,name:e.target.value})}/>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Quantity</label>
                    <input className="input" value={editForm.quantity}
                           onChange={e=>setEditForm({...editForm,quantity:e.target.value})}/>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Category</label>
                    <select className="input" value={editForm.category}
                            onChange={e=>setEditForm({...editForm,category:e.target.value})}>
                      {CATS.filter(c=>c!=='All').map(c=><option key={c}>{c}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Expiry Date</label>
                    <input className="input" type="date" value={editForm.expiry_date}
                           onChange={e=>setEditForm({...editForm,expiry_date:e.target.value})}/>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button onClick={()=>saveEdit(item.id)}
                          className="btn-primary flex-1">💾 Save</button>
                  <button onClick={()=>setEditItem(null)}
                          className="btn-ghost flex-1">❌ Cancel</button>
                </div>
              </div>
            )

            return (
              <div key={item.id}
                   className="card flex items-center gap-4
                              hover:shadow-lg hover:border-primary/30
                              transition-all duration-200"
                   style={{ borderLeft:`4px solid ${days<=3?'#f44336':days<=7?'#ff9800':'#43e97b'}` }}>

                {/* Image / Emoji */}
                {item.image_url ? (
                  <img src={item.image_url} alt={item.name}
                       className="w-14 h-14 rounded-xl object-cover flex-shrink-0
                                  shadow-sm"/>
                ) : (
                  <div className="w-14 h-14 rounded-xl flex-shrink-0
                                  bg-gradient-to-br from-primary/20 to-success/20
                                  flex items-center justify-center text-2xl">
                    {emoji}
                  </div>
                )}

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center flex-wrap gap-2">
                    <h3 className="font-semibold text-gray-800 dark:text-white">
                      {item.name}
                    </h3>
                    <span className={`badge ${cls}`}>{label}</span>
                    <span className="badge badge-gray">{item.category}</span>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    📏 {item.quantity} &nbsp;|&nbsp; 📅 {item.expiry_date}
                  </p>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1 flex-shrink-0">
                  <button onClick={()=>markUsed(item.id)}
                          className="p-2 rounded-xl hover:bg-green-100
                                     dark:hover:bg-green-900/30
                                     text-green-600 transition"
                          title="Mark used">
                    <CheckCircle size={18}/>
                  </button>
                  <button onClick={()=>startEdit(item)}
                          className="p-2 rounded-xl hover:bg-blue-100
                                     dark:hover:bg-blue-900/30
                                     text-blue-600 transition"
                          title="Edit">
                    <Pencil size={18}/>
                  </button>
                  <button onClick={()=>deleteIt(item.id)}
                          className="p-2 rounded-xl hover:bg-red-100
                                     dark:hover:bg-red-900/30
                                     text-red-500 transition"
                          title="Delete">
                    <Trash2 size={18}/>
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
