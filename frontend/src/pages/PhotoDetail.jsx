import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { photosApi, commentsApi, ratingsApi } from '../utils/api'
import { useAuthStore } from '../store/authStore'
import StarRating from '../components/StarRating'
import { MapPin, Users, Eye, Calendar, Tag, Sparkles, ArrowLeft, Send, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

export default function PhotoDetail() {
  const { id } = useParams()
  const { user, isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [comment, setComment] = useState('')

  const { data: photo, isLoading } = useQuery({
    queryKey: ['photo', id],
    queryFn: () => photosApi.get(id).then((r) => r.data),
  })

  const { data: comments = [] } = useQuery({
    queryKey: ['comments', id],
    queryFn: () => commentsApi.list(id).then((r) => r.data),
    enabled: !!photo,
  })

  const rateMutation = useMutation({
    mutationFn: (score) => ratingsApi.rate(id, score),
    onSuccess: () => {
      queryClient.invalidateQueries(['photo', id])
      toast.success('Rating saved!')
    },
  })

  const commentMutation = useMutation({
    mutationFn: (content) => commentsApi.add(id, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries(['comments', id])
      setComment('')
    },
    onError: () => toast.error('Failed to post comment'),
  })

  const deleteCommentMutation = useMutation({
    mutationFn: (commentId) => commentsApi.delete(commentId),
    onSuccess: () => queryClient.invalidateQueries(['comments', id]),
  })

  if (isLoading) return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="skeleton h-8 w-48 mb-6 rounded-lg" />
      <div className="grid lg:grid-cols-2 gap-8">
        <div className="skeleton aspect-square rounded-2xl" />
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => <div key={i} className="skeleton h-6 rounded-lg" style={{ width: `${60 + i * 8}%` }} />)}
        </div>
      </div>
    </div>
  )

  if (!photo) return (
    <div className="text-center py-20 text-white/40">Photo not found.</div>
  )

  const aiTags = (() => {
    try { return JSON.parse(photo.ai_tags || '[]') } catch { return [] }
  })()

  const sentimentColor = {
    positive: 'text-emerald-400',
    negative: 'text-rose-400',
    neutral: 'text-white/40',
  }

  return (
    <main className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
      {/* Back */}
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-white/40 hover:text-cream transition-colors mb-8">
        <ArrowLeft size={16} />
        Back
      </button>

      <div className="grid lg:grid-cols-[1fr_420px] gap-10">
        {/* Image */}
        <div className="space-y-4">
          <div className="rounded-2xl overflow-hidden bg-ink-800 border border-white/5">
            <img
              src={photo.image_url}
              alt={photo.title}
              className="w-full object-contain max-h-[70vh]"
              onError={(e) => { e.target.src = `https://picsum.photos/seed/${photo.id}/800/600` }}
            />
          </div>

          {/* AI Tags */}
          {aiTags.length > 0 && (
            <div className="bg-ink-800/50 rounded-xl p-4 border border-white/5 space-y-2">
              <div className="flex items-center gap-2 text-xs text-gold-400 font-medium">
                <Sparkles size={13} />
                AI-detected tags
              </div>
              <div className="flex flex-wrap gap-1.5">
                {aiTags.map((tag) => (
                  <span key={tag} className="px-2 py-0.5 bg-ink-700 rounded-full text-xs text-white/50 border border-white/5">
                    {tag}
                  </span>
                ))}
              </div>
              {photo.ai_description && (
                <p className="text-xs text-white/40 italic mt-1">{photo.ai_description}</p>
              )}
            </div>
          )}
        </div>

        {/* Details */}
        <div className="space-y-6">
          {/* Title & creator */}
          <div>
            <h1 className="font-display text-3xl font-bold text-cream mb-1">{photo.title}</h1>
            <p className="text-white/40 text-sm">
              by <span className="text-gold-400">{photo.creator?.display_name || photo.creator?.username}</span>
            </p>
          </div>

          {/* Caption */}
          {photo.caption && (
            <p className="text-white/70 leading-relaxed">{photo.caption}</p>
          )}

          {/* Meta */}
          <div className="space-y-2 text-sm">
            {photo.location && (
              <div className="flex items-center gap-2 text-white/50">
                <MapPin size={14} className="text-gold-500" />
                {photo.location}
              </div>
            )}
            {photo.people_tagged && (
              <div className="flex items-center gap-2 text-white/50">
                <Users size={14} className="text-gold-500" />
                {photo.people_tagged}
              </div>
            )}
            <div className="flex items-center gap-4 text-white/40 pt-1">
              <span className="flex items-center gap-1"><Eye size={13} /> {photo.view_count} views</span>
              <span className="flex items-center gap-1">
                <Calendar size={13} /> {new Date(photo.upload_date).toLocaleDateString()}
              </span>
            </div>
          </div>

          {/* Rating */}
          <div className="bg-ink-800 rounded-xl p-4 border border-white/5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-cream">Rating</span>
              <span className="text-xs text-white/40">{photo.rating_count} {photo.rating_count === 1 ? 'rating' : 'ratings'}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-2xl font-display font-bold text-gold-400">
                {photo.avg_rating > 0 ? photo.avg_rating.toFixed(1) : '—'}
              </span>
              <StarRating current={Math.round(photo.avg_rating)} readonly />
            </div>
            {isAuthenticated() && (
              <div className="pt-2 border-t border-white/5">
                <p className="text-xs text-white/40 mb-2">Your rating:</p>
                <StarRating
                  current={photo.user_rating || 0}
                  onRate={(score) => rateMutation.mutate(score)}
                />
              </div>
            )}
            {!isAuthenticated() && (
              <p className="text-xs text-white/30">
                <Link to="/login" className="text-gold-400 hover:underline">Sign in</Link> to rate
              </p>
            )}
          </div>

          {/* Comments */}
          <div className="space-y-4">
            <h2 className="text-sm font-semibold text-cream flex items-center gap-2">
              Comments
              <span className="bg-ink-700 rounded-full px-2 py-0.5 text-xs text-white/40">{comments.length}</span>
            </h2>

            {/* Add comment */}
            {isAuthenticated() ? (
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  if (comment.trim()) commentMutation.mutate(comment.trim())
                }}
                className="flex gap-2"
              >
                <input
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Add a comment…"
                  className="flex-1 bg-ink-800 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-cream placeholder-white/25 focus:border-gold-500/50 transition-colors"
                />
                <button
                  type="submit"
                  disabled={!comment.trim() || commentMutation.isPending}
                  className="bg-gold-500 hover:bg-gold-400 disabled:opacity-40 text-ink-950 px-4 rounded-xl transition-colors"
                >
                  <Send size={15} />
                </button>
              </form>
            ) : (
              <p className="text-sm text-white/30">
                <Link to="/login" className="text-gold-400 hover:underline">Sign in</Link> to comment
              </p>
            )}

            {/* Comment list */}
            <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
              {comments.map((c) => (
                <div key={c.id} className="bg-ink-800/50 rounded-xl p-3 border border-white/5 space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-gold-400">
                        {c.author?.display_name || c.author?.username}
                      </span>
                      {c.sentiment && (
                        <span className={`text-xs ${sentimentColor[c.sentiment] || 'text-white/30'}`}>
                          {c.sentiment}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-white/25">{new Date(c.created_at).toLocaleDateString()}</span>
                      {user?.id === c.author_id && (
                        <button
                          onClick={() => deleteCommentMutation.mutate(c.id)}
                          className="text-white/20 hover:text-rose-400 transition-colors"
                        >
                          <Trash2 size={12} />
                        </button>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-white/70">{c.content}</p>
                </div>
              ))}
              {comments.length === 0 && (
                <p className="text-sm text-white/25 text-center py-4">No comments yet. Be the first!</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
