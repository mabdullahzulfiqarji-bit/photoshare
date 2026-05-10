import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Camera, Eye, EyeOff } from 'lucide-react'
import { authApi } from '../utils/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await authApi.login(form)
      setAuth(data.user, data.access_token)
      toast.success(`Welcome back, ${data.user.display_name || data.user.username}!`)
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center px-4">
      <div className="w-full max-w-sm space-y-8">
        {/* Logo */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center mx-auto">
            <Camera size={22} className="text-ink-950" />
          </div>
          <h1 className="font-display text-3xl font-bold text-cream">Welcome back</h1>
          <p className="text-white/40 text-sm">Sign in to your PhotoShare account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-white/60 mb-1.5">Username or email</label>
            <input
              type="text"
              required
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              className="w-full bg-ink-800 border border-white/10 rounded-xl px-4 py-3 text-cream text-sm placeholder-white/25 focus:border-gold-500/50 transition-colors"
              placeholder="Enter your username"
            />
          </div>

          <div>
            <label className="block text-sm text-white/60 mb-1.5">Password</label>
            <div className="relative">
              <input
                type={showPw ? 'text' : 'password'}
                required
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="w-full bg-ink-800 border border-white/10 rounded-xl px-4 py-3 pr-11 text-cream text-sm placeholder-white/25 focus:border-gold-500/50 transition-colors"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors"
              >
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gold-500 hover:bg-gold-400 disabled:opacity-50 text-ink-950 font-semibold py-3 rounded-xl transition-all text-sm mt-2"
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <div className="text-center space-y-3">
          <p className="text-sm text-white/40">
            Don't have an account?{' '}
            <Link to="/register" className="text-gold-400 hover:text-gold-300 transition-colors">
              Join PhotoShare
            </Link>
          </p>
          <div className="bg-ink-800/50 rounded-xl p-3 border border-white/5 text-xs text-white/30 space-y-1">
            <p className="font-mono">Admin: admin / Admin@1234</p>
            <p className="font-mono text-white/20">(seed at /api/admin/seed first)</p>
          </div>
        </div>
      </div>
    </div>
  )
}
