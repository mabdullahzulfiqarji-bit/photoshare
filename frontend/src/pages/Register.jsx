import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Camera } from 'lucide-react'
import { authApi } from '../utils/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '', display_name: '' })
  const [loading, setLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password.length < 8) return toast.error('Password must be at least 8 characters')
    setLoading(true)
    try {
      const { data } = await authApi.register(form)
      setAuth(data.user, data.access_token)
      toast.success('Account created! Welcome to PhotoShare.')
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const f = (field) => ({ value: form[field], onChange: (e) => setForm({ ...form, [field]: e.target.value }) })

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm space-y-8">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center mx-auto">
            <Camera size={22} className="text-ink-950" />
          </div>
          <h1 className="font-display text-3xl font-bold text-cream">Create account</h1>
          <p className="text-white/40 text-sm">Join as a consumer. Creators are invited by admins.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {[
            { label: 'Username', field: 'username', type: 'text', placeholder: 'johndoe', required: true },
            { label: 'Display name', field: 'display_name', type: 'text', placeholder: 'John Doe' },
            { label: 'Email', field: 'email', type: 'email', placeholder: 'john@example.com', required: true },
            { label: 'Password', field: 'password', type: 'password', placeholder: '••••••••', required: true },
          ].map(({ label, field, type, placeholder, required }) => (
            <div key={field}>
              <label className="block text-sm text-white/60 mb-1.5">{label}</label>
              <input
                type={type}
                required={required}
                placeholder={placeholder}
                {...f(field)}
                className="w-full bg-ink-800 border border-white/10 rounded-xl px-4 py-3 text-cream text-sm placeholder-white/25 focus:border-gold-500/50 transition-colors"
              />
            </div>
          ))}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gold-500 hover:bg-gold-400 disabled:opacity-50 text-ink-950 font-semibold py-3 rounded-xl transition-all text-sm mt-2"
          >
            {loading ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p className="text-center text-sm text-white/40">
          Already have an account?{' '}
          <Link to="/login" className="text-gold-400 hover:text-gold-300 transition-colors">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
