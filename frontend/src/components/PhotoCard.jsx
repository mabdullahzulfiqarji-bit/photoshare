import { Link } from 'react-router-dom'
import { Star, Eye, MapPin, MessageCircle } from 'lucide-react'

export default function PhotoCard({ photo }) {
  const thumbnailSrc = photo.thumbnail_url || photo.image_url

  return (
    <Link to={`/photo/${photo.id}`} className="block group">
      <article className="photo-card bg-ink-800 rounded-2xl overflow-hidden border border-white/5 hover:border-gold-500/20">
        {/* Image */}
        <div className="aspect-square overflow-hidden bg-ink-700 relative">
          <img
            src={thumbnailSrc}
            alt={photo.title}
            loading="lazy"
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            onError={(e) => {
              e.target.src = `https://picsum.photos/seed/${photo.id}/400/400`
            }}
          />
          {/* Overlay on hover */}
          <div className="absolute inset-0 bg-gradient-to-t from-ink-950/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-3">
            <div className="flex items-center gap-3 text-xs text-white/80">
              <span className="flex items-center gap-1">
                <Eye size={12} /> {photo.view_count || 0}
              </span>
              {photo.location && (
                <span className="flex items-center gap-1">
                  <MapPin size={12} /> {photo.location}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Info */}
        <div className="p-3 space-y-1.5">
          <h3 className="font-display text-sm font-semibold text-cream truncate group-hover:text-gold-400 transition-colors">
            {photo.title}
          </h3>
          <div className="flex items-center justify-between text-xs text-white/40">
            <span>{photo.creator?.display_name || photo.creator?.username || 'Unknown'}</span>
            <div className="flex items-center gap-1 text-gold-400">
              <Star size={11} fill="currentColor" />
              <span className="text-white/40">
                {photo.avg_rating > 0 ? photo.avg_rating.toFixed(1) : '—'}
              </span>
            </div>
          </div>
        </div>
      </article>
    </Link>
  )
}
