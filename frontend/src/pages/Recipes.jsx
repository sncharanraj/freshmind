// src/pages/Recipes.jsx
import { useState, useEffect, useRef } from 'react'
import { aiAPI, pantryAPI } from '../api/client'
import { Send, Trash2, Bot, ChefHat } from 'lucide-react'

export default function Recipes() {
  const [items,    setItems]    = useState([])
  const [expiring, setExpiring] = useState([])
  const [meal,     setMeal]     = useState('Any')
  const [diet,     setDiet]     = useState('Any')
  const [time_,    setTime]     = useState('Any')
  const [messages, setMessages] = useState([])   // ← renamed from history to avoid confusion
  const [input,    setInput]    = useState('')
  const [loading,  setLoading]  = useState(false)
  const [genLoad,  setGenLoad]  = useState(false)
  const chatRef = useRef()

  useEffect(() => {
    pantryAPI.getAll().then(r => setItems(r.data.items || []))
    pantryAPI.getExpiring(7).then(r => setExpiring(r.data.items || []))
  }, [])

  useEffect(() => {
    if (chatRef.current)
      chatRef.current.scrollTop = chatRef.current.scrollHeight
  }, [messages])

  const generateRecipes = async () => {
    setGenLoad(true)
    try {
      const prefs = `Meal:${meal}, Diet:${diet}, Time:${time_}`
      const res   = await aiAPI.getRecipes(prefs)
      // Just add assistant message — don't use history from server
      setMessages(prev => [...prev, { role:'assistant', content: res.data.recipes }])
    } catch {
      setMessages(prev => [...prev, { role:'assistant', content:'❌ Error getting recipes. Check your API key.' }])
    }
    setGenLoad(false)
  }

  const sendMsg = async e => {
    e.preventDefault()
    const msg = input.trim()
    if (!msg || loading) return

    // Clear input immediately
    setInput('')

    // Add user message to UI
    const userMsg = { role:'user', content: msg }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      // Send current messages + new user msg as history context
      // but DON'T use the returned history array to set messages
      // — just extract the assistant reply to avoid duplication
      const historyToSend = [...messages, userMsg]
      const res = await aiAPI.chat(msg, historyToSend)

      // Only add the assistant's reply — not the whole returned history
      const reply = res.data.response
      setMessages(prev => [...prev, { role:'assistant', content: reply }])
    } catch {
      setMessages(prev => [...prev, { role:'assistant', content:'❌ Error! Check your API key.' }])
    }
    setLoading(false)
  }

  return (
    <div className="animate-fade-in space-y-5 max-w-3xl mx-auto">

      {/* Hero */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-violet-600
                      rounded-2xl p-5 text-white shadow-lg">
        <h1 className="text-2xl font-bold">🤖 AI Recipe Suggestions</h1>
        <p className="text-indigo-100 text-sm mt-1">Smart recipes from your pantry</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3">
        <div className="card text-center py-3 border-indigo-100 dark:border-indigo-800
                        bg-indigo-50 dark:bg-indigo-900/20">
          <p className="text-2xl font-bold text-indigo-600">{items.length}</p>
          <p className="text-xs text-gray-500">Items Available</p>
        </div>
        <div className="card text-center py-3 border-amber-100 dark:border-amber-800
                        bg-amber-50 dark:bg-amber-900/20">
          <p className="text-2xl font-bold text-amber-500">{expiring.length}</p>
          <p className="text-xs text-gray-500">Expiring Soon</p>
        </div>
      </div>

      {/* Preferences */}
      <div className="card space-y-3">
        <h2 className="font-semibold text-gray-800 dark:text-white flex items-center gap-2">
          <ChefHat size={18} className="text-indigo-500"/> Preferences
        </h2>
        <div className="grid grid-cols-3 gap-3">
          {[
            { label:"🍽️ Meal", val:meal,  set:setMeal,
              opts:["Any","Breakfast","Lunch","Dinner","Snack","Dessert"] },
            { label:"🥗 Diet", val:diet,  set:setDiet,
              opts:["Any","Vegetarian","Vegan","Non-Vegetarian","Gluten-Free"] },
            { label:"⏱️ Time", val:time_, set:setTime,
              opts:["Any","<15 mins","<30 mins","<1 hour"] },
          ].map(f => (
            <div key={f.label}>
              <label className="text-xs text-gray-500 mb-1 block">{f.label}</label>
              <select className="input" value={f.val}
                      onChange={e=>f.set(e.target.value)}>
                {f.opts.map(o => <option key={o}>{o}</option>)}
              </select>
            </div>
          ))}
        </div>
        <button onClick={generateRecipes} disabled={genLoad || !items.length}
                className="btn-primary w-full py-3 flex items-center justify-center
                           gap-2 disabled:opacity-60">
          {genLoad
            ? <><div className="w-4 h-4 border-2 border-white/40 border-t-white
                                rounded-full animate-spin"/> Generating...</>
            : <><Bot size={18}/> Generate Recipes From My Pantry</>
          }
        </button>
        {!items.length && (
          <p className="text-sm text-center text-gray-400">
            🛒 Add some items to your pantry first!
          </p>
        )}
      </div>

      {/* Chat */}
      <div className="card flex flex-col" style={{ height:'440px' }}>
        <div className="flex items-center justify-between mb-3 flex-shrink-0">
          <h2 className="font-semibold text-gray-800 dark:text-white">
            💬 Recipe Chat
          </h2>
          {messages.length > 0 && (
            <button onClick={() => setMessages([])}
                    className="flex items-center gap-1 text-xs text-red-500
                               hover:bg-red-50 dark:hover:bg-red-900/20
                               px-2 py-1 rounded-lg transition">
              <Trash2 size={12}/> Clear
            </button>
          )}
        </div>

        {/* Messages */}
        <div ref={chatRef} className="flex-1 overflow-y-auto space-y-3 pr-1 mb-3">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-center text-gray-400 text-sm">
              <div>
                <div className="text-4xl mb-2">🤖</div>
                Generate recipes or ask me anything about cooking!
              </div>
            </div>
          ) : messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role==='user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[82%] px-4 py-2.5 rounded-2xl text-sm
                               leading-relaxed whitespace-pre-wrap
                               ${msg.role === 'user'
                                 ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-br-sm'
                                 : 'bg-gray-100 dark:bg-dark-card2 text-gray-800 dark:text-gray-200 rounded-bl-sm border border-gray-200 dark:border-dark-border'
                               }`}>
                {msg.content}
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 dark:bg-dark-card2 px-4 py-3
                              rounded-2xl rounded-bl-sm flex gap-1 items-center">
                {[0,1,2].map(i => (
                  <div key={i} className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                       style={{ animationDelay:`${i*0.15}s`}}/>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <form onSubmit={sendMsg} className="flex gap-2 flex-shrink-0">
          <input className="input flex-1 text-sm"
                 placeholder="Ask — 'make it spicy', 'no onions', 'quick meal'..."
                 value={input}
                 onChange={e => setInput(e.target.value)}/>
          <button type="submit" disabled={!input.trim() || loading}
                  className="btn-primary px-4 disabled:opacity-60 flex-shrink-0">
            <Send size={16}/>
          </button>
        </form>
      </div>
    </div>
  )
}