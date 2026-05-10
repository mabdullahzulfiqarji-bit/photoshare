import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { searchApi } from '../utils/api'
import PhotoCard from '../components/PhotoCard'
import { Search } from 'lucide-react'

export default function SearchResults() {
  const [params] = useSearchParams()
  const q = params.get('q') || ''

  const { data, isLoading } = useQuery({
    queryKey: ['search', q],
    queryFn: () => searchApi.search({ q, page_size: 24 }).then((r) => r.data),
    enabled: !!q,
  })

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
      <div className="mb-8">
        <div className="flex items-center gap-2 text-white/40 text-sm mb-2">
          <Search size={14} />
          Search results
        </div>
        <h1 className="font-display text-2xl font-bold text-cream">
          "{q}"
        </h1>
        {!isLoading && data && (
          <p className="text-white/40 text-sm mt-1">{data.total} photo{data.total !== 1 ? 's' : ''} found</p>
        )}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="skeleton aspect-square rounded-2xl" />
          ))}
        </div>
      ) : data?.photos?.length === 0 ? (
        <div className="text-center py-24 space-y-3">
          <Search size={48} className="text-white/10 mx-auto" />
          <p className="text-white/40">No photos found for "{q}"</p>
          <p className="text-white/25 text-sm">Try different keywords</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {data?.photos?.map((photo, i) => (
            <div key={photo.id} className="fade-in-up" style={{ animationDelay: `${i * 40}ms` }}>
              <PhotoCard photo={photo} />
            </div>
          ))}
        </div>
      )}
    </main>
  )
}
