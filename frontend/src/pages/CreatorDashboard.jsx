import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { photosApi } from '../utils/api'
import { useAuthStore } from '../store/authStore'
import { Upload, Trash2, Edit3, Eye, Star, Image } from 'lucide-react'
import toast from 'react-hot-toast'

export default function CreatorDashboard() {
  const { user } = useAuthStore()
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['myPhotos', page],
    queryFn: () => photosApi.myPhotos({ page, page_size: 12 }).then((r) => r.data),
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => photosApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['myPhotos'])
      toast.success('Photo deleted')
    },
    onError: () => toast.error('Failed to delete'),
  })

  const totalViews = data?.photos?.reduce((sum, p) => sum + (p.view_count || 0), 0) || 0
  const avgRating = data?.photos?.length
    ? (data.photos.reduce((s, p) => s + (p.avg_rating || 0), 0) / data.photos.length).toFixed(1)
    : '—'

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-10">
        <div>
          <h1 className="font-display text-3xl font-bold text-cream">Creator Dashboard</h1>
          <p className="text-white/40 text-sm mt-1">Welcome back, {user?.display_name || user?.username}</p>
        </div>
        <Link
          to="/upload"
          className="flex items-center gap-2 bg-gold-500 hover:bg-gold-400 text-ink-950 font-semibold px-4 py-2.5 rounded-xl transition-colors text-sm"
        >
          <Upload size={15} />
          Upload Photo
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-10">
        {[
          { label: 'Photos', value: data?.total || 0, icon: <Image size={18} /> },
          { label: 'Total Views', value: totalViews.toLocaleString(), icon: <Eye size={18} /> },
          { label: 'Avg Rating', value: avgRating, icon: <Star size={18} /> },
        ].map(({ label, value, icon }) => (
          <div key={label} className="bg-ink-800 rounded-2xl p-5 border border-white/5">
            <div className="flex items-center gap-2 text-gold-400 text-sm mb-3">{icon} {label}</div>
            <div className="font-display text-3xl font-bold text-cream">{value}</div>
          </div>
        ))}
      </div>

      {/* Photo grid */}
      {isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="skeleton aspect-square rounded-2xl" />
          ))}
        </div>
      ) : data?.photos?.length === 0 ? (
        <div className="text-center py-24 space-y-4">
          <Image size={48} className="text-white/10 mx-auto" />
          <p className="text-white/40">You haven't uploaded any photos yet.</p>
          <Link to="/upload" className="inline-flex items-center gap-2 bg-gold-500 text-ink-950 font-semibold px-4 py-2.5 rounded-xl text-sm">
            <Upload size={15} /> Upload your first photo
          </Link>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {data.photos.map((photo) => (
              <div key={photo.id} className="group relative bg-ink-800 rounded-2xl overflow-hidden border border-white/5 hover:border-white/15 transition-all">
                <div className="aspect-square">
                  <img
                    src={photo.thumbnail_url || photo.image_url}
                    alt={photo.title}
                    className="w-full h-full object-cover"
                    onError={(e) => { e.target.src = `https://picsum.photos/seed/${photo.id}/400` }}
                  />
                </div>
                <div className="p-3">
                  <p className="text-sm text-cream truncate font-medium">{photo.title}</p>
                  <div className="flex items-center gap-3 text-xs text-white/35 mt-1">
                    <span className="flex items-center gap-1"><Eye size={11} /> {photo.view_count}</span>
                    <span className="flex items-center gap-1"><Star size={11} /> {photo.avg_rating?.toFixed(1) || '—'}</span>
                  </div>
                </div>
                {/* Hover actions */}
                <div className="absolute inset-0 bg-ink-950/80 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
                  <Link
                    to={`/photo/${photo.id}`}
                    className="bg-white/10 hover:bg-white/20 text-cream rounded-xl p-2.5 transition-colors"
                    title="View"
                  >
                    <Eye size={16} />
                  </Link>
                  <button
                    onClick={() => {
                      if (confirm('Delete this photo?')) deleteMutation.mutate(photo.id)
                    }}
                    className="bg-rose-500/20 hover:bg-rose-500/40 text-rose-400 rounded-xl p-2.5 transition-colors"
                    title="Delete"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="flex items-center justify-center gap-3 mt-10">
              <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
                className="px-4 py-2 rounded-lg bg-ink-800 text-sm text-white/60 hover:text-cream disabled:opacity-30">Previous</button>
              <span className="text-sm text-white/40">Page {page} of {data.total_pages}</span>
              <button onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))} disabled={page === data.total_pages}
                className="px-4 py-2 rounded-lg bg-ink-800 text-sm text-white/60 hover:text-cream disabled:opacity-30">Next</button>
            </div>
          )}
        </>
      )}
    </main>
  )
}
