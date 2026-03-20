// src/components/Layout.jsx
import { useState, useEffect } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth, useTheme } from '../App'
import { pantryAPI } from '../api/client'
import NotifBell from './NotifBell'
import {
  Home, Package, PlusCircle, Bot,
  BarChart2, Settings, LogOut, Moon, Sun,
  Salad, Menu, X
} from 'lucide-react'

const NAV = [
  { to:"/",          icon:Home,       label:"Home"       },
  { to:"/pantry",    icon:Package,    label:"My Pantry"  },
  { to:"/add",       icon:PlusCircle, label:"Add Item"   },
  { to:"/recipes",   icon:Bot,        label:"AI Recipes" },
  { to:"/dashboard", icon:BarChart2,  label:"Dashboard"  },
  { to:"/settings",  icon:Settings,   label:"Settings"   },
]

export default function Layout() {
  const { user, logout }   = useAuth()
  const { dark, setDark }  = useTheme()
  const navigate           = useNavigate()
  const [expiring, setExpiring]       = useState([])
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    pantryAPI.getExpiring(7)
      .then(r => setExpiring(r.data.items || []))
      .catch(() => {})
  }, [])

  // Close sidebar on route change (mobile)
  const handleNav = () => setSidebarOpen(false)

  const fname = user?.full_name || user?.username || 'User'
  const init  = fname[0]?.toUpperCase() || 'U'

  // ── Sidebar content (shared between desktop + mobile) ──
  const SidebarContent = () => (
    <div className="flex flex-col h-full">

      {/* Logo */}
      <div className="flex items-center justify-between px-5 py-5
                      border-b border-light-border dark:border-dark-border">
        <div className="flex items-center gap-3">
          <div className="text-3xl">🥗</div>
          <div>
            <h1 className="font-bold text-lg text-primary leading-tight">
              FreshMind
            </h1>
            <p className="text-xs text-gray-400">Smart Pantry</p>
          </div>
        </div>
        {/* Close button — mobile only */}
        <button
          onClick={() => setSidebarOpen(false)}
          className="md:hidden p-1.5 rounded-lg hover:bg-gray-100
                     dark:hover:bg-dark-card2 text-gray-500"
        >
          <X size={18}/>
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <p className="text-xs font-bold uppercase tracking-widest
                      text-gray-400 px-3 mb-2">Navigation</p>
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to} to={to} end={to === "/"}
            onClick={handleNav}
            className={({ isActive }) =>
              `sidebar-btn ${isActive ? 'active' : ''}`
            }
          >
            <Icon size={18}/>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom — user card + logout (NO dark toggle here) */}
      <div className="px-3 pb-4 pt-3 space-y-2
                      border-t border-light-border dark:border-dark-border">

        {/* User card */}
        <div className="flex items-center gap-3 px-3 py-2.5
                        bg-gray-50 dark:bg-dark-card2
                        rounded-xl border border-light-border
                        dark:border-dark-border">
          <div className="w-9 h-9 rounded-full flex-shrink-0
                          bg-gradient-to-br from-primary to-success
                          flex items-center justify-center
                          text-white text-sm font-bold">
            {init}
          </div>
          <div className="overflow-hidden">
            <p className="text-sm font-semibold truncate
                          text-gray-800 dark:text-white">
              {fname}
            </p>
            <p className="text-xs text-gray-400 truncate">
              @{user?.username}
            </p>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={() => { logout(); navigate('/login') }}
          className="sidebar-btn w-full !text-red-500
                     hover:!bg-red-50 dark:hover:!bg-red-900/20"
        >
          <LogOut size={18}/>
          <span>Logout</span>
        </button>

        <p className="text-center text-xs text-gray-300
                      dark:text-gray-600 pt-1">
          Built with ❤️ Python & React
        </p>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen overflow-hidden
                    bg-gray-50 dark:bg-dark">

      {/* ── DESKTOP Sidebar (always visible on md+) ── */}
      <aside className="hidden md:flex w-64 flex-shrink-0 flex-col h-full
                        bg-white dark:bg-dark-card
                        border-r border-light-border dark:border-dark-border
                        shadow-sm">
        <SidebarContent />
      </aside>

      {/* ── MOBILE Sidebar overlay ── */}
      {sidebarOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/50 z-40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
          {/* Drawer */}
          <aside className="fixed left-0 top-0 h-full w-72 z-50
                            bg-white dark:bg-dark-card
                            border-r border-light-border dark:border-dark-border
                            shadow-2xl md:hidden
                            animate-slide-in-left">
            <SidebarContent />
          </aside>
        </>
      )}

      {/* ── Main Content ── */}
      <main className="flex-1 flex flex-col overflow-hidden min-w-0">

        {/* ── Topbar ── */}
        <header className="flex items-center justify-between
                           px-4 md:px-6 py-3
                           bg-white dark:bg-dark-card
                           border-b border-light-border dark:border-dark-border
                           shadow-sm flex-shrink-0">

          <div className="flex items-center gap-3">
            {/* Hamburger — mobile only */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 rounded-xl
                         hover:bg-gray-100 dark:hover:bg-dark-card2
                         text-gray-600 dark:text-gray-300 transition"
            >
              <Menu size={20}/>
            </button>

            {/* App name */}
            <div className="flex items-center gap-2">
              <Salad size={20} className="text-primary"/>
              <span className="font-bold text-gray-800 dark:text-white
                               hidden sm:block">
                FreshMind
              </span>
            </div>
          </div>

          {/* Right side — notif + theme toggle */}
          <div className="flex items-center gap-1">
            <NotifBell expiring={expiring}/>

            {/* Theme toggle — INSTANT, in topbar only */}
            <button
              onClick={() => setDark(!dark)}
              className="p-2 rounded-xl
                         hover:bg-gray-100 dark:hover:bg-dark-card2
                         transition-colors"
              title={dark ? 'Switch to Light' : 'Switch to Dark'}
            >
              {dark
                ? <Sun  size={18} className="text-yellow-400"/>
                : <Moon size={18} className="text-gray-500"/>
              }
            </button>
          </div>
        </header>

        {/* ── Page Content ── */}
        <div className="flex-1 overflow-y-auto">
          {/* Responsive padding */}
          <div className="p-4 md:p-6 max-w-7xl mx-auto">
            <Outlet/>
          </div>
        </div>

        {/* ── MOBILE Bottom Nav ── */}
        <nav className="md:hidden flex-shrink-0
                        bg-white dark:bg-dark-card
                        border-t border-light-border dark:border-dark-border
                        shadow-lg">
          <div className="flex items-center justify-around px-2 py-2">
            {NAV.slice(0, 5).map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to} to={to} end={to === "/"}
                className={({ isActive }) =>
                  `flex flex-col items-center gap-0.5 px-2 py-1.5
                   rounded-xl transition-all min-w-0
                   ${isActive
                     ? 'text-primary'
                     : 'text-gray-400 hover:text-gray-600'
                   }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className={`p-1.5 rounded-xl transition-all
                                    ${isActive
                                      ? 'bg-primary/10'
                                      : ''
                                    }`}>
                      <Icon size={20}/>
                    </div>
                    <span className="text-[10px] font-medium truncate
                                     max-w-[48px] text-center">
                      {label}
                    </span>
                  </>
                )}
              </NavLink>
            ))}
          </div>
        </nav>
      </main>
    </div>
  )
}