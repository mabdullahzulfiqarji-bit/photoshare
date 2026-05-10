import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { photosApi } from '../utils/api'
import PhotoCard from '../components/PhotoCard'
import { Camera, TrendingUp, Clock, Star } from 'lucide-react'

const SORT_OPTIONS = [
  { value: 'newest', label: 'Latest', icon: <Clock size={14} /> },
  { value: 'top_rated', label: 'Top Rated', icon: <Star size={14} /> },
  { value: 'most_viewed', label: 'Trending', icon: <TrendingUp size={14} /> },
]

export default function Home() {
  const [sort, setSort] = useState('newest')
  const [page, setPage] = useState(1)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['photos', sort, page],
    queryFn: () => photosApi.list({ sort, page, page_size: 12 }).then((r) => r.data),
    keepPreviousData: true,
  })

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
      {/* Hero */}
      <section className="mb-12 text-center space-y-4">
        <div className="inline-flex items-center gap-2 bg-gold-500/10 border border-gold-500/20 rounded-full px-4 py-1.5 text-sm text-gold-400 mb-4">
          <Camera size={13} />
          Cloud-Native Photo Platform
        </div>
        <h1 className="font-display text-5xl sm:text-6xl font-bold text-cream leading-tight">
          Discover stunning<br />
          <span className="gold-shimmer">photography</span>
        </h1>
        <p className="text-white/50 text-lg max-w-xl mx-auto">
          Explore curated photos from creators around the world. Rate, comment, and engage with visual stories.
        </p>
      </section>

      {/* Sort tabs */}
      <div className="flex items-center gap-2 mb-8">
        {SORT_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => { setSort(opt.value); setPage(1) }}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              sort === opt.value
                ? 'bg-gold-500 text-ink-950'
                : 'bg-ink-800 text-white/60 hover:text-cream hover:bg-ink-700'
            }`}
          >
            {opt.icon}
            {opt.label}
          </button>
        ))}
      </div>

      {/* Grid */}
      {isLoading ? (
        <SkeletonGrid />
      ) : isError ? (
        <div className="text-center py-20 text-white/40">Failed to load photos. Is the API running?</div>
      ) : data?.photos?.length === 0 ? (
        <Empty />
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {data.photos.map((photo, i) => (
              <div key={photo.id} className="fade-in-up" style={{ animationDelay: `${i * 40}ms` }}>
                <PhotoCard photo={photo} />
              </div>
            ))}
          </div>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="flex items-center justify-center gap-3 mt-12">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 rounded-lg bg-ink-800 text-sm text-white/60 hover:text-cream disabled:opacity-30 transition-colors"
              >
                Previous
              </button>
              <span className="text-sm text-white/40">
                Page {page} of {data.total_pages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                disabled={page === data.total_pages}
                className="px-4 py-2 rounded-lg bg-ink-800 text-sm text-white/60 hover:text-cream disabled:opacity-30 transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </main>
  )
}

function SkeletonGrid() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
      {Array.from({ length: 12 }).map((_, i) => (
        <div key={i} className="rounded-2xl overflow-hidden bg-ink-800">
          <div className="skeleton aspect-square" />
          <div className="p-3 space-y-2">
            <div className="skeleton h-4 w-3/4" />
            <div className="skeleton h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  )
}

function Empty() {
  return (
    <div className="text-center py-24 space-y-3">
      <Camera size={48} className="text-white/10 mx-auto" />
      <p className="text-white/40 text-lg">No photos yet.</p>
      <p className="text-white/25 text-sm">Creators will post here soon.</p>
    </div>
  )
}
