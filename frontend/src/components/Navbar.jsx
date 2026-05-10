import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { Camera, Upload, LayoutDashboard, LogOut, User, Shield, Search, Menu, X } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function Navbar() {
  const { user, logout, isAuthenticated, isCreator, isAdmin } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [searchQ, setSearchQ] = useState('')

  const handleLogout = () => {
    logout()
    toast.success('Logged out')
    navigate('/')
  }

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQ.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQ.trim())}`)
      setSearchQ('')
    }
  }

  return (
    <nav className="sticky top-0 z-50 border-b border-white/5 bg-ink-900/90 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center h-16 gap-6">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 shrink-0">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center">
              <Camera size={16} className="text-ink-950" />
            </div>
            <span className="font-display text-lg font-bold text-cream hidden sm:block">
              Photo<span className="text-gold-400">Share</span>
            </span>
          </Link>

          {/* Search */}
          <form onSubmit={handleSearch} className="flex-1 max-w-md hidden md:flex">
            <div className="relative w-full">
              <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
              <input
                type="text"
                placeholder="Search photos, places, people…"
                value={searchQ}
                onChange={(e) => setSearchQ(e.target.value)}
                className="w-full bg-ink-800 border border-white/8 rounded-lg pl-9 pr-4 py-2 text-sm text-cream placeholder-white/30 focus:border-gold-500/50 transition-colors"
              />
            </div>
          </form>

          {/* Nav links */}
          <div className="hidden md:flex items-center gap-1 ml-auto">
            {isCreator() && (
              <>
                <NavLink to="/upload" icon={<Upload size={15} />} label="Upload" active={location.pathname === '/upload'} />
                <NavLink to="/creator" icon={<LayoutDashboard size={15} />} label="Dashboard" active={location.pathname === '/creator'} />
              </>
            )}
            {isAdmin() && (
              <NavLink to="/admin" icon={<Shield size={15} />} label="Admin" active={location.pathname === '/admin'} />
            )}

            {isAuthenticated() ? (
              <div className="flex items-center gap-3 ml-3 pl-3 border-l border-white/10">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-gold-400/30 to-gold-600/30 border border-gold-500/30 flex items-center justify-center">
                    <User size={13} className="text-gold-400" />
                  </div>
                  <span className="text-sm text-white/70">{user?.display_name || user?.username}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1.5 text-sm text-white/40 hover:text-rose-400 transition-colors px-2 py-1 rounded-lg hover:bg-rose-500/10"
                >
                  <LogOut size={14} />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2 ml-3">
                <Link to="/login" className="text-sm text-white/60 hover:text-cream transition-colors px-3 py-1.5 rounded-lg hover:bg-white/5">
                  Sign in
                </Link>
                <Link to="/register" className="text-sm bg-gold-500 hover:bg-gold-400 text-ink-950 font-semibold px-3 py-1.5 rounded-lg transition-colors">
                  Join
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu btn */}
          <button className="md:hidden ml-auto p-2 text-white/60" onClick={() => setMobileOpen(!mobileOpen)}>
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden pb-4 space-y-2 border-t border-white/5 pt-4">
            <form onSubmit={handleSearch} className="mb-3">
              <div className="relative">
                <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
                <input
                  type="text"
                  placeholder="Search…"
                  value={searchQ}
                  onChange={(e) => setSearchQ(e.target.value)}
                  className="w-full bg-ink-800 border border-white/8 rounded-lg pl-9 pr-4 py-2 text-sm text-cream placeholder-white/30"
                />
              </div>
            </form>

            {isAuthenticated() ? (
              <>
                {isCreator() && (
                  <>
                    <MobileLink to="/upload" label="Upload Photo" onClick={() => setMobileOpen(false)} />
                    <MobileLink to="/creator" label="Dashboard" onClick={() => setMobileOpen(false)} />
                  </>
                )}
                {isAdmin() && <MobileLink to="/admin" label="Admin" onClick={() => setMobileOpen(false)} />}
                <button onClick={handleLogout} className="w-full text-left px-3 py-2 text-sm text-rose-400 hover:bg-rose-500/10 rounded-lg">
                  Sign out
                </button>
              </>
            ) : (
              <>
                <MobileLink to="/login" label="Sign in" onClick={() => setMobileOpen(false)} />
                <MobileLink to="/register" label="Join PhotoShare" onClick={() => setMobileOpen(false)} />
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}

function NavLink({ to, icon, label, active }) {
  return (
    <Link
      to={to}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-all ${
        active ? 'bg-gold-500/10 text-gold-400' : 'text-white/60 hover:text-cream hover:bg-white/5'
      }`}
    >
      {icon}
      {label}
    </Link>
  )
}

function MobileLink({ to, label, onClick }) {
  return (
    <Link
      to={to}
      onClick={onClick}
      className="block px-3 py-2 text-sm text-white/70 hover:text-cream hover:bg-white/5 rounded-lg"
    >
      {label}
    </Link>
  )
}
