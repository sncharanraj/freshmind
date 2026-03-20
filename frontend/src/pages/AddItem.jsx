// src/pages/AddItem.jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { pantryAPI, imageAPI } from '../api/client'
import { Upload, Camera, Globe, CheckCircle } from 'lucide-react'

const CATS = ["Dairy","Vegetables","Fruits","Meat & Seafood",
              "Grains & Cereals","Snacks","Beverages","Condiments","Other"]
const FOOD_EMOJIS = {
  Dairy:"🥛", Vegetables:"🥦", Fruits:"🍎",
  "Meat & Seafood":"🍗", "Grains & Cereals":"🌾",
  Snacks:"🍿", Beverages:"🥤", Condiments:"🧂", Other:"🛒"
}

const today = () => new Date().toISOString().split('T')[0]

export default function AddItem() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name:'', quantity:'', category:'Other',
    purchase_date: today(), expiry_date: today(), image_url:''
  })
  const [imgTab,    setImgTab]    = useState('wiki')
  const [preview,   setPreview]   = useState('')
  const [emoji,     setEmoji]     = useState('🛒')
  const [wikiLoad,  setWikiLoad]  = useState(false)
  const [success,   setSuccess]   = useState('')
  const [error,     setError]     = useState('')
  const [submitting,setSubmitting]= useState(false)

  // Auto-fetch Wikipedia image when name changes
  useEffect(() => {
    if (!form.name || form.name.length < 3 || imgTab !== 'wiki') return
    const t = setTimeout(async () => {
      setWikiLoad(true)
      try {
        const res = await imageAPI.fetch(form.name)
        setPreview(res.data.url || '')
        setEmoji(res.data.emoji || FOOD_EMOJIS[form.category] || '🛒')
        if (res.data.url)
          setForm(f => ({ ...f, image_url: res.data.url }))
      } catch {} finally { setWikiLoad(false) }
    }, 600)
    return () => clearTimeout(t)
  }, [form.name, imgTab])

  const handleLocal = e => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = ev => {
      setPreview(ev.target.result)
      setForm(f => ({ ...f, image_url: ev.target.result }))
    }
    reader.readAsDataURL(file)
  }

  const handleCamera = e => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = ev => {
      setPreview(ev.target.result)
      setForm(f => ({ ...f, image_url: ev.target.result }))
    }
    reader.readAsDataURL(file)
  }

  const submit = async e => {
    e.preventDefault(); setError(''); setSuccess('')
    if (!form.name || !form.quantity)
      return setError('Name and quantity are required!')
    if (form.expiry_date < form.purchase_date)
      return setError('Expiry date cannot be before purchase date!')
    if (form.expiry_date < today())
      return setError('Item is already expired!')
    setSubmitting(true)
    try {
      await pantryAPI.add(form)
      setSuccess(`✅ ${form.name} added to pantry!`)
      setForm({
        name:'', quantity:'', category:'Other',
        purchase_date: today(), expiry_date: today(), image_url:''
      })
      setPreview(''); setEmoji('🛒')
      setTimeout(() => navigate('/pantry'), 1500)
    } catch(e) {
      setError(e.response?.data?.error || 'Failed to add item!')
    } finally { setSubmitting(false) }
  }

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  return (
    <div className="animate-fade-in max-w-2xl mx-auto space-y-5">

      {/* Hero */}
      <div className="bg-gradient-to-r from-green-800 to-emerald-600
                      rounded-2xl p-5 text-white">
        <h1 className="text-2xl font-bold">➕ Add New Item</h1>
        <p className="text-green-100 text-sm mt-1">Add items to your pantry</p>
      </div>

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-xl
                        p-4 text-green-700 flex items-center gap-2">
          <CheckCircle size={18}/> {success}
        </div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl
                        p-4 text-red-600 text-sm">
          ❌ {error}
        </div>
      )}

      <form onSubmit={submit} className="space-y-5">

        {/* Item name */}
        <div className="card">
          <label className="text-sm font-semibold text-gray-700
                            dark:text-gray-300 block mb-2">
            Item Name *
          </label>
          <input className="input" placeholder="e.g. Milk, Eggs, Spinach"
                 value={form.name}
                 onChange={e => set('name', e.target.value)}/>
        </div>

        {/* Image section */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 dark:text-white mb-3">
            🖼️ Item Image
          </h2>

          {/* Image tabs */}
          <div className="flex bg-gray-100 dark:bg-dark-card2
                          rounded-xl p-1 mb-4 gap-1">
            {[
              { key:'wiki',  icon:Globe,  label:'Auto (Wikipedia)' },
              { key:'local', icon:Upload, label:'Local File'       },
              { key:'cam',   icon:Camera, label:'Camera'           },
            ].map(({ key, icon:Icon, label }) => (
              <button key={key} type="button"
                      onClick={() => setImgTab(key)}
                      className={`flex-1 flex items-center justify-center
                                  gap-1.5 py-2 text-xs font-medium
                                  rounded-lg transition-all
                                  ${imgTab === key
                                    ? 'bg-white dark:bg-dark-card shadow text-primary'
                                    : 'text-gray-500 hover:text-gray-700'
                                  }`}>
                <Icon size={14}/>{label}
              </button>
            ))}
          </div>

          {/* Preview */}
          <div className="flex items-start gap-4">
            <div className="w-28 h-28 rounded-xl overflow-hidden
                            border-2 border-dashed border-light-border
                            dark:border-dark-border flex-shrink-0
                            flex items-center justify-center
                            bg-gray-50 dark:bg-dark-card2">
              {preview
                ? <img src={preview} alt="preview"
                       className="w-full h-full object-cover"/>
                : wikiLoad
                  ? <div className="text-2xl animate-spin">🔄</div>
                  : <div className="text-4xl">{emoji}</div>
              }
            </div>

            <div className="flex-1">
              {imgTab === 'wiki' && (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {wikiLoad
                    ? '🔍 Fetching image...'
                    : preview
                      ? '✅ Image found from Wikipedia!'
                      : 'Type item name above to auto-fetch image'
                  }
                </p>
              )}
              {imgTab === 'local' && (
                <div>
                  <input type="file" accept="image/*"
                         onChange={handleLocal}
                         className="hidden" id="local-upload"/>
                  <label htmlFor="local-upload"
                         className="btn-ghost cursor-pointer inline-flex
                                    items-center gap-2 text-sm">
                    <Upload size={16}/> Choose File
                  </label>
                  {preview && (
                    <p className="text-xs text-green-600 mt-2">
                      ✅ Image uploaded!
                    </p>
                  )}
                </div>
              )}
              {imgTab === 'cam' && (
                <div>
                  <input type="file" accept="image/*"
                         capture="environment"
                         onChange={handleCamera}
                         className="hidden" id="cam-upload"/>
                  <label htmlFor="cam-upload"
                         className="btn-ghost cursor-pointer inline-flex
                                    items-center gap-2 text-sm">
                    <Camera size={16}/> Take Photo
                  </label>
                  {preview && (
                    <p className="text-xs text-green-600 mt-2">
                      ✅ Photo captured!
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Item details */}
        <div className="card space-y-4">
          <h2 className="font-semibold text-gray-800 dark:text-white">
            📋 Item Details
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-500 mb-1 block">
                Quantity *
              </label>
              <input className="input" placeholder="e.g. 1 litre, 500g"
                     value={form.quantity}
                     onChange={e => set('quantity', e.target.value)}/>
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">
                Category *
              </label>
              <select className="input" value={form.category}
                      onChange={e => set('category', e.target.value)}>
                {CATS.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">
                Purchase Date *
              </label>
              <input className="input" type="date"
                     value={form.purchase_date}
                     onChange={e => set('purchase_date', e.target.value)}/>
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">
                Expiry Date *
              </label>
              <input className="input" type="date"
                     value={form.expiry_date}
                     onChange={e => set('expiry_date', e.target.value)}/>
            </div>
          </div>
        </div>

        <button type="submit" disabled={submitting}
                className="btn-primary w-full py-3 text-base
                           disabled:opacity-60">
          {submitting ? '⏳ Adding...' : '➕ Add to Pantry'}
        </button>
      </form>
    </div>
  )
}
