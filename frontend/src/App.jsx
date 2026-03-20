// src/App.jsx
import { useState, useEffect, createContext, useContext } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout    from './components/Layout'
import Login     from './pages/Login'
import Home      from './pages/Home'
import Pantry    from './pages/Pantry'
import AddItem   from './pages/AddItem'
import Recipes   from './pages/Recipes'
import Dashboard from './pages/Dashboard'
import Settings  from './pages/Settings'

export const AuthCtx  = createContext(null)
export const ThemeCtx = createContext(null)
export const useAuth  = () => useContext(AuthCtx)
export const useTheme = () => useContext(ThemeCtx)

function App() {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('fm_user')) }
    catch { return null }
  })

  const [dark, setDarkState] = useState(() =>
    localStorage.getItem('fm_dark') === 'true'
  )

  // Apply dark class on first load instantly
  useEffect(() => {
    if (dark) document.documentElement.classList.add('dark')
    else      document.documentElement.classList.remove('dark')
  }, [])

  // Instant theme toggle — injects a no-transition style for one frame
  const setDark = (val) => {
    const style = document.createElement('style')
    style.innerHTML = `*, *::before, *::after {
      transition: none !important;
      animation: none !important;
    }`
    document.head.appendChild(style)
    if (val) document.documentElement.classList.add('dark')
    else     document.documentElement.classList.remove('dark')
    localStorage.setItem('fm_dark', val)
    setDarkState(val)
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        document.head.removeChild(style)
      })
    })
  }

  const login = (userData, token) => {
    localStorage.setItem('fm_token', token)
    localStorage.setItem('fm_user',  JSON.stringify(userData))
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('fm_token')
    localStorage.removeItem('fm_user')
    setUser(null)
  }

  const ProtectedRoute = ({ children }) =>
    user ? children : <Navigate to="/login" replace />

  return (
    <AuthCtx.Provider value={{ user, login, logout }}>
      <ThemeCtx.Provider value={{ dark, setDark }}>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={
              user ? <Navigate to="/" replace /> : <Login />
            }/>
            <Route path="/" element={
              <ProtectedRoute><Layout /></ProtectedRoute>
            }>
              <Route index            element={<Home />}      />
              <Route path="pantry"    element={<Pantry />}    />
              <Route path="add"       element={<AddItem />}   />
              <Route path="recipes"   element={<Recipes />}   />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="settings"  element={<Settings />}  />
            </Route>
          </Routes>
        </BrowserRouter>
      </ThemeCtx.Provider>
    </AuthCtx.Provider>
  )
}

export default App