import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../utils/api'
import { Shield, Users, Image, Star, MessageCircle, Plus, X } from 'lucide-react'
import toast from 'react-hot-toast'

export default function AdminDashboard() {
  const qc = useQueryClient()
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [creatorForm, setCreatorForm] = useState({ username: '', email: '', password: '', display_name: '' })

  const { data: stats } = useQuery({
    queryKey: ['adminStats'],
    queryFn: () => adminApi.stats().then((r) => r.data),
  })

  const { data: users = [] } = useQuery({
    queryKey: ['adminUsers'],
    queryFn: () => adminApi.listUsers().then((r) => r.data),
  })

  const createCreatorMutation = useMutation({
    mutationFn: (data) => adminApi.createCreator(data),
    onSuccess: () => {
      qc.invalidateQueries(['adminUsers'])
      setShowCreateForm(false)
      setCreatorForm({ username: '', email: '', password: '', display_name: '' })
      toast.success('Creator account created!')
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to create creator'),
  })

  const roleBadge = (role) => {
    const styles = {
      admin: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
      creator: 'bg-gold-500/20 text-gold-300 border-gold-500/30',
      consumer: 'bg-white/5 text-white/40 border-white/10',
    }
    return <span className={`px-2 py-0.5 rounded-full text-xs border ${styles[role] || styles.consumer}`}>{role}</span>
  }

  return (
    <main className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
      <div className="flex items-center gap-3 mb-10">
        <div className="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center">
          <Shield size={18} className="text-rose-300" />
        </div>
        <div>
          <h1 className="font-display text-3xl font-bold text-cream">Admin Panel</h1>
          <p className="text-white/40 text-sm">Platform management</p>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
          {[
            { label: 'Photos', value: stats.total_photos, icon: <Image size={16} />, color: 'text-gold-400' },
            { label: 'Users', value: stats.total_users, icon: <Users size={16} />, color: 'text-blue-400' },
            { label: 'Comments', value: stats.total_comments, icon: <MessageCircle size={16} />, color: 'text-emerald-400' },
            { label: 'Ratings', value: stats.total_ratings, icon: <Star size={16} />, color: 'text-violet-400' },
          ].map(({ label, value, icon, color }) => (
            <div key={label} className="bg-ink-800 rounded-2xl p-5 border border-white/5">
              <div className={`flex items-center gap-1.5 ${color} text-sm mb-3`}>{icon} {label}</div>
              <div className="font-display text-3xl font-bold text-cream">{value}</div>
            </div>
          ))}
        </div>
      )}

      {/* Create Creator */}
      <div className="bg-ink-800 rounded-2xl border border-white/5 overflow-hidden mb-8">
        <div className="flex items-center justify-between p-5 border-b border-white/5">
          <h2 className="font-semibold text-cream">Creator Accounts</h2>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="flex items-center gap-1.5 bg-gold-500 hover:bg-gold-400 text-ink-950 font-semibold px-3 py-1.5 rounded-lg text-sm transition-colors"
          >
            {showCreateForm ? <X size={14} /> : <Plus size={14} />}
            {showCreateForm ? 'Cancel' : 'New Creator'}
          </button>
        </div>

        {showCreateForm && (
          <form
            className="p-5 border-b border-white/5 grid grid-cols-2 gap-4"
            onSubmit={(e) => { e.preventDefault(); createCreatorMutation.mutate(creatorForm) }}
          >
            {[
              { field: 'username', label: 'Username *', placeholder: 'creator123', required: true },
              { field: 'display_name', label: 'Display name', placeholder: 'Jane Doe' },
              { field: 'email', label: 'Email *', placeholder: 'jane@example.com', required: true },
              { field: 'password', label: 'Password *', placeholder: 'min 8 chars', required: true, type: 'password' },
            ].map(({ field, label, placeholder, required, type = 'text' }) => (
              <div key={field}>
                <label className="block text-xs text-white/50 mb-1">{label}</label>
                <input
                  type={type}
                  required={required}
                  placeholder={placeholder}
                  value={creatorForm[field]}
                  onChange={(e) => setCreatorForm({ ...creatorForm, [field]: e.target.value })}
                  className="w-full bg-ink-700 border border-white/10 rounded-xl px-3 py-2 text-sm text-cream placeholder-white/20 focus:border-gold-500/50 transition-colors"
                />
              </div>
            ))}
            <div className="col-span-2">
              <button
                type="submit"
                disabled={createCreatorMutation.isPending}
                className="bg-gold-500 hover:bg-gold-400 disabled:opacity-50 text-ink-950 font-semibold px-4 py-2 rounded-lg text-sm transition-colors"
              >
                {createCreatorMutation.isPending ? 'Creating…' : 'Create Creator Account'}
              </button>
            </div>
          </form>
        )}

        {/* User list */}
        <div className="divide-y divide-white/5">
          {users.map((u) => (
            <div key={u.id} className="flex items-center justify-between px-5 py-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-ink-700 border border-white/10 flex items-center justify-center text-xs text-white/40 font-mono">
                  {u.username[0].toUpperCase()}
                </div>
                <div>
                  <p className="text-sm text-cream">{u.display_name || u.username}</p>
                  <p className="text-xs text-white/30">{u.email}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {roleBadge(u.role)}
                <span className="text-xs text-white/25 hidden sm:block">
                  {new Date(u.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
