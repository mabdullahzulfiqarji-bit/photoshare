import { useState } from 'react'
import { Star } from 'lucide-react'

export default function StarRating({ current = 0, onRate, readonly = false }) {
  const [hover, setHover] = useState(0)

  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => {
        const filled = star <= (hover || current)
        return (
          <button
            key={star}
            type="button"
            disabled={readonly}
            className={`star-btn ${readonly ? 'cursor-default' : 'cursor-pointer'}`}
            onMouseEnter={() => !readonly && setHover(star)}
            onMouseLeave={() => !readonly && setHover(0)}
            onClick={() => !readonly && onRate?.(star)}
          >
            <Star
              size={20}
              className={`transition-colors ${
                filled ? 'text-gold-400' : 'text-white/20'
              }`}
              fill={filled ? 'currentColor' : 'none'}
            />
          </button>
        )
      })}
    </div>
  )
}
