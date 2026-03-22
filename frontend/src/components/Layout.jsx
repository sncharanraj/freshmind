// src/components/Layout.jsx
import { useState, useEffect } from 'react'
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useAuth, useTheme } from '../App'
import { pantryAPI } from '../api/client'
import NotifBell from './NotifBell'
import {
  Home, Package, PlusCircle, Bot,
  BarChart2, Settings, LogOut,
  Moon, Sun, Salad, Shield, Menu, X
} from 'lucide-react'

export default function Layout() {
  const { user, logout }        = useAuth()
  const { dark, setDark }       = useTheme()
  const navigate                = useNavigate()
  const location                = useLocation()
  const [expiring, setExpiring] = useState([])
  const [sideOpen, setSideOpen] = useState(false)

  // Close sidebar on route change
  useEffect(() => { setSideOpen(false) }, [location.pathname])

  // Close on resize to desktop
  useEffect(() => {
    const h = () => { if (window.innerWidth >= 1024) setSideOpen(false) }
    window.addEventListener('resize', h)
    return () => window.removeEventListener('resize', h)
  }, [])

  useEffect(() => {
    pantryAPI.getExpiring(7)
      .then(r => setExpiring(r.data.items || []))
      .catch(() => {})
  }, [])

  const fname   = user?.full_name || user?.username || 'User'
  const init    = fname[0]?.toUpperCase() || 'U'
  const isAdmin = user?.role === 'admin'

  // Full nav for sidebar
  const SIDENAV = [
    { to:"/",          icon:Home,       label:"Home"       },
    { to:"/pantry",    icon:Package,    label:"My Pantry"  },
    { to:"/add",       icon:PlusCircle, label:"Add Item"   },
    { to:"/recipes",   icon:Bot,        label:"AI Recipes" },
    { to:"/dashboard", icon:BarChart2,  label:"Dashboard"  },
    { to:"/settings",  icon:Settings,   label:"Settings"   },
    ...(isAdmin ? [{ to:"/admin", icon:Shield, label:"Admin", admin:true }] : []),
  ]

  // Bottom nav — 5 main items only (fits mobile screen)
  const BOTTOMNAV = [
    { to:"/",          icon:Home,       label:"Home"      },
    { to:"/pantry",    icon:Package,    label:"Pantry"    },
    { to:"/add",       icon:PlusCircle, label:"Add"       },
    { to:"/recipes",   icon:Bot,        label:"Recipes"   },
    { to:"/dashboard", icon:BarChart2,  label:"Dashboard" },
  ]

  const SidebarContent = () => (
    <div className="flex flex-col h-full">

      {/* Logo + close */}
      <div className="flex items-center justify-between px-5 py-5
                      border-b border-gray-100 dark:border-dark-border
                      flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="text-3xl">🥗</div>
          <div>
            <h1 className="font-bold text-lg text-primary leading-tight">
              FreshMind
            </h1>
            <p className="text-xs text-gray-400">Smart Pantry</p>
          </div>
        </div>
        <button onClick={() => setSideOpen(false)}
                className="lg:hidden p-2 rounded-xl hover:bg-gray-100
                           dark:hover:bg-dark-card2 text-gray-500 transition">
          <X size={20}/>
        </button>
      </div>

      {/* Nav links */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
        <p className="text-xs font-bold uppercase tracking-widest
                      text-gray-400 px-3 mb-2">Navigation</p>
        {SIDENAV.map(({ to, icon:Icon, label, admin }) => (
          <NavLink key={to} to={to} end={to === "/"}
                   className={({ isActive }) =>
                     `sidebar-btn ${isActive ? 'active' : ''}`
                   }>
            <Icon size={17}/>
            <span>{label}</span>
            {admin && (
              <span className="ml-auto bg-purple-100 text-purple-700
                               dark:bg-purple-900/40 dark:text-purple-300
                               text-xs px-1.5 py-0.5 rounded-full font-semibold">
                Admin
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom of sidebar */}
      <div className="px-3 pb-4 space-y-2 flex-shrink-0
                      border-t border-gray-100 dark:border-dark-border pt-3">


        {/* User card */}
        <div className="flex items-center gap-3 px-3 py-2
                        bg-gray-50 dark:bg-dark-card2 rounded-xl
                        border border-gray-100 dark:border-dark-border">
          <div className="w-8 h-8 rounded-full flex-shrink-0
                          bg-gradient-to-br from-indigo-500 to-purple-500
                          flex items-center justify-center
                          text-white text-sm font-bold">
            {init}
          </div>
          <div className="overflow-hidden flex-1">
            <p className="text-sm font-semibold truncate
                          text-gray-800 dark:text-white">{fname}</p>
            <p className="text-xs text-gray-400 truncate">
              @{user?.username}
              {isAdmin && <span className="ml-1 text-purple-500">· Admin</span>}
            </p>
          </div>
        </div>

        <button onClick={() => { logout(); navigate('/login') }}
                className="sidebar-btn w-full text-red-500
                           hover:bg-red-50 dark:hover:bg-red-900/20">
          <LogOut size={17}/><span>Logout</span>
        </button>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-dark">

      {/* ── Desktop Sidebar ── */}
      <aside className="hidden lg:flex w-64 flex-shrink-0 flex-col h-full
                        bg-white dark:bg-dark-card
                        border-r border-light-border dark:border-dark-border
                        shadow-sm">
        <SidebarContent/>
      </aside>

      {/* ── Mobile Sidebar Drawer ── */}
      {sideOpen && (
        <>
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
               onClick={() => setSideOpen(false)}/>
          <aside className="fixed top-0 left-0 h-full w-72 z-50
                            bg-white dark:bg-dark-card shadow-2xl
                            lg:hidden flex flex-col"
                 style={{ animation:'slideInLeft 0.2s ease' }}>
            <SidebarContent/>
          </aside>
        </>
      )}

      {/* ── Main ── */}
      <main className="flex-1 flex flex-col overflow-hidden min-w-0">

        {/* Topbar */}
        <header className="flex items-center justify-between px-4 py-3
                           bg-white dark:bg-dark-card
                           border-b border-gray-100 dark:border-dark-border
                           shadow-sm flex-shrink-0">
          <div className="flex items-center gap-3">
            {/* Hamburger — mobile only */}
            <button onClick={() => setSideOpen(true)}
                    className="lg:hidden p-2 rounded-xl hover:bg-gray-100
                               dark:hover:bg-dark-card2
                               text-gray-600 dark:text-gray-300 transition">
              <Menu size={20}/>
            </button>
            <div className="flex items-center gap-2">
              <Salad size={20} className="text-primary hidden sm:block"/>
              <span className="font-semibold text-gray-700 dark:text-white
                               text-sm sm:text-base">
                FreshMind
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <NotifBell expiring={expiring}/>
            <button onClick={() => setDark(!dark)}
                    className="p-2 rounded-xl hover:bg-gray-100
                               dark:hover:bg-dark-card2 transition">
              {dark
                ? <Sun  size={18} className="text-yellow-400"/>
                : <Moon size={18} className="text-gray-500"/>
              }
            </button>
          </div>
        </header>

        {/* Page content — extra bottom padding on mobile for bottom nav */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 pb-24 lg:pb-6">
          <Outlet/>
        </div>

        {/* ── Bottom Nav Bar — mobile only ── */}
        <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-30
                        bg-white dark:bg-dark-card
                        border-t border-gray-200 dark:border-dark-border
                        shadow-[0_-4px_20px_rgba(0,0,0,0.08)]">
          <div className="flex items-center justify-around px-2 py-2
                          max-w-lg mx-auto">
            {BOTTOMNAV.map(({ to, icon:Icon, label }) => {
              const isActive = location.pathname === to ||
                (to !== "/" && location.pathname.startsWith(to))
              return (
                <NavLink key={to} to={to} end={to === "/"}
                         className="flex flex-col items-center gap-0.5
                                    px-3 py-1.5 rounded-xl
                                    transition-all duration-150 min-w-0
                                    flex-1">
                  <div className={`p-1.5 rounded-xl transition-all duration-150
                                   ${isActive
                                     ? 'bg-indigo-100 dark:bg-indigo-900/40'
                                     : 'hover:bg-gray-100 dark:hover:bg-dark-card2'
                                   }`}>
                    <Icon size={20} className={
                      isActive
                        ? 'text-indigo-600 dark:text-indigo-400'
                        : 'text-gray-500 dark:text-gray-400'
                    }/>
                  </div>
                  <span className={`text-[10px] font-medium truncate
                                    transition-colors duration-150
                                    ${isActive
                                      ? 'text-indigo-600 dark:text-indigo-400'
                                      : 'text-gray-500 dark:text-gray-400'
                                    }`}>
                    {label}
                  </span>
                </NavLink>
              )
            })}
          </div>
        </nav>
      </main>

      <style>{`
        @keyframes slideInLeft {
          from { transform: translateX(-100%); opacity: 0; }
          to   { transform: translateX(0);     opacity: 1; }
        }
      `}</style>
    </div>
  )
}
