// src/components/Layout.jsx
import { useState, useEffect } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth, useTheme } from '../App'
import { pantryAPI } from '../api/client'
import NotifBell from './NotifBell'
import {
  Home, Package, PlusCircle, Bot,
  BarChart2, Settings, LogOut,
  Moon, Sun, Salad, Shield
} from 'lucide-react'

export default function Layout() {
  const { user, logout } = useAuth()
  const { dark, setDark } = useTheme()
  const navigate  = useNavigate()
  const [expiring, setExpiring] = useState([])

  useEffect(() => {
    pantryAPI.getExpiring(7)
      .then(r => setExpiring(r.data.items || []))
      .catch(() => {})
  }, [])

  const fname = user?.full_name || user?.username || 'User'
  const init  = fname[0]?.toUpperCase() || 'U'
  const isAdmin = user?.role === 'admin'

  const NAV = [
    { to:"/",          icon:Home,       label:"Home"        },
    { to:"/pantry",    icon:Package,    label:"My Pantry"   },
    { to:"/add",       icon:PlusCircle, label:"Add Item"    },
    { to:"/recipes",   icon:Bot,        label:"AI Recipes"  },
    { to:"/dashboard", icon:BarChart2,  label:"Dashboard"   },
    { to:"/settings",  icon:Settings,   label:"Settings"    },
    // Admin-only nav item
    ...(isAdmin ? [{ to:"/admin", icon:Shield, label:"Admin Panel" }] : []),
  ]

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-dark">

      {/* ── Sidebar ── */}
      <aside className="w-64 flex-shrink-0 flex flex-col h-full
                        bg-white dark:bg-dark-card
                        border-r border-light-border dark:border-dark-border
                        shadow-sm">

        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-5
                        border-b border-gray-100 dark:border-dark-border">
          <div className="text-3xl">🥗</div>
          <div>
            <h1 className="font-bold text-lg text-primary leading-tight">
              FreshMind
            </h1>
            <p className="text-xs text-gray-400">Smart Pantry</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
          <p className="text-xs font-bold uppercase tracking-widest
                        text-gray-400 px-3 mb-2">Navigation</p>

          {NAV.map(({ to, icon:Icon, label }) => (
            <NavLink
              key={to} to={to} end={to === "/"}
              className={({ isActive }) =>
                `sidebar-btn ${isActive ? 'active' : ''}`
              }
            >
              <Icon size={17}/>
              <span>{label}</span>
              {/* Admin badge */}
              {to === '/admin' && (
                <span className="ml-auto bg-purple-100 text-purple-700
                                 dark:bg-purple-900/40 dark:text-purple-300
                                 text-xs px-1.5 py-0.5 rounded-full font-semibold">
                  Admin
                </span>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Bottom — dark mode + user card + logout */}
        <div className="px-3 pb-4 space-y-2
                        border-t border-gray-100 dark:border-dark-border pt-3">

          {/* User card */}
          <div className="flex items-center gap-3 px-3 py-2
                          bg-gray-50 dark:bg-dark-card2
                          rounded-xl border border-gray-100
                          dark:border-dark-border">
            <div className="w-8 h-8 rounded-full flex-shrink-0
                            bg-gradient-to-br from-indigo-500 to-purple-500
                            flex items-center justify-center
                            text-white text-sm font-bold">
              {init}
            </div>
            <div className="overflow-hidden flex-1">
              <p className="text-sm font-semibold truncate
                            text-gray-800 dark:text-white">
                {fname}
              </p>
              <p className="text-xs text-gray-400 truncate">
                @{user?.username}
                {isAdmin && (
                  <span className="ml-1 text-purple-500">· Admin</span>
                )}
              </p>
            </div>
          </div>

          {/* Logout */}
          <button
            onClick={() => { logout(); navigate('/login') }}
            className="sidebar-btn w-full text-red-500
                       hover:bg-red-50 dark:hover:bg-red-900/20"
          >
            <LogOut size={17}/>
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <main className="flex-1 flex flex-col overflow-hidden">

        {/* Topbar */}
        <header className="flex items-center justify-between
                           px-6 py-3 bg-white dark:bg-dark-card
                           border-b border-gray-100 dark:border-dark-border
                           shadow-sm flex-shrink-0">
          <div className="flex items-center gap-2">
            <Salad size={20} className="text-primary"/>
            <span className="font-semibold text-gray-700 dark:text-white">
              FreshMind
            </span>
          </div>
          <div className="flex items-center gap-1">
            <NotifBell expiring={expiring}/>
            <button
              onClick={() => setDark(!dark)}
              className="p-2 rounded-xl hover:bg-gray-100
                         dark:hover:bg-dark-card2 transition"
            >
              {dark
                ? <Sun  size={18} className="text-yellow-400"/>
                : <Moon size={18} className="text-gray-500"/>
              }
            </button>
          </div>
        </header>

        {/* Page content */}
        <div className="flex-1 overflow-y-auto p-6">
          <Outlet/>
        </div>
      </main>
    </div>
  )
}