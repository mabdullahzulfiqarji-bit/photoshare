import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useNavigate } from 'react-router-dom'
import { Upload, ImagePlus, X, CheckCircle } from 'lucide-react'
import { photosApi } from '../utils/api'
import toast from 'react-hot-toast'

export default function UploadPage() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [form, setForm] = useState({ title: '', caption: '', location: '', people_tagged: '' })
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)

  const onDrop = useCallback((accepted) => {
    const f = accepted[0]
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
    // Auto-fill title from filename
    const name = f.name.replace(/\.[^.]+$/, '').replace(/[-_]/g, ' ')
    setForm((prev) => ({ ...prev, title: prev.title || name }))
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp'] },
    maxFiles: 1,
    maxSize: 16 * 1024 * 1024,
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return toast.error('Please select a photo first')
    if (!form.title.trim()) return toast.error('Title is required')

    setUploading(true)
    setProgress(0)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', form.title)
    if (form.caption) formData.append('caption', form.caption)
    if (form.location) formData.append('location', form.location)
    if (form.people_tagged) formData.append('people_tagged', form.people_tagged)

    try {
      // Fake progress animation
      const interval = setInterval(() => setProgress((p) => Math.min(p + 8, 85)), 200)
      const { data } = await photosApi.upload(formData)
      clearInterval(interval)
      setProgress(100)
      toast.success('Photo uploaded successfully!')
      setTimeout(() => navigate(`/photo/${data.id}`), 500)
    } catch (err) {
      setProgress(0)
      const status = err.response?.status
      const detail = err.response?.data?.detail
      if (status === 403) {
        toast.error('Only creator accounts can upload photos.')
      } else if (status === 401) {
        toast.error('Session expired. Please log in again.')
        navigate('/login')
      } else {
        toast.error(detail || 'Upload failed. Please try again.')
      }
    } finally {
      setUploading(false)
    }
  }

  return (
    <main className="max-w-2xl mx-auto px-4 sm:px-6 py-10">
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold text-cream mb-1">Upload Photo</h1>
        <p className="text-white/40 text-sm">Share your photography with the world</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`relative rounded-2xl border-2 border-dashed cursor-pointer transition-all overflow-hidden ${
            isDragActive
              ? 'border-gold-400 bg-gold-500/5'
              : preview
              ? 'border-white/10'
              : 'border-white/15 hover:border-gold-500/40 hover:bg-gold-500/3'
          }`}
        >
          <input {...getInputProps()} />
          {preview ? (
            <div className="relative">
              <img src={preview} alt="Preview" className="w-full max-h-80 object-cover" />
              <div className="absolute inset-0 bg-gradient-to-t from-ink-950/60 to-transparent flex items-end p-4">
                <div className="flex items-center gap-2 text-sm text-white/80">
                  <CheckCircle size={16} className="text-emerald-400" />
                  {file.name} ({(file.size / 1024 / 1024).toFixed(1)}MB)
                </div>
              </div>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); setFile(null); setPreview(null) }}
                className="absolute top-3 right-3 bg-ink-950/80 text-white/60 hover:text-cream rounded-full p-1.5 transition-colors"
              >
                <X size={14} />
              </button>
            </div>
          ) : (
            <div className="py-16 text-center space-y-3">
              <ImagePlus size={40} className="text-white/20 mx-auto" />
              <div>
                <p className="text-white/60 font-medium">Drop your photo here</p>
                <p className="text-white/30 text-sm">or click to browse · JPG, PNG, GIF, WebP · max 16MB</p>
              </div>
            </div>
          )}
        </div>

        {/* Form fields */}
        <div className="space-y-4">
          <FormField label="Title *" value={form.title} onChange={(v) => setForm({ ...form, title: v })} placeholder="Enter a title for your photo" />
          <FormField label="Caption" value={form.caption} onChange={(v) => setForm({ ...form, caption: v })} placeholder="Tell the story behind this photo…" multiline />
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Location" value={form.location} onChange={(v) => setForm({ ...form, location: v })} placeholder="Paris, France" />
            <FormField label="People tagged" value={form.people_tagged} onChange={(v) => setForm({ ...form, people_tagged: v })} placeholder="Alice, Bob…" />
          </div>
        </div>

        {/* Progress bar */}
        {uploading && (
          <div className="bg-ink-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-gold-600 to-gold-400 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}

        <button
          type="submit"
          disabled={uploading || !file}
          className="w-full flex items-center justify-center gap-2 bg-gold-500 hover:bg-gold-400 disabled:opacity-40 text-ink-950 font-semibold py-3 rounded-xl transition-all"
        >
          <Upload size={16} />
          {uploading ? `Uploading… ${progress}%` : 'Upload Photo'}
        </button>
      </form>
    </main>
  )
}

function FormField({ label, value, onChange, placeholder, multiline = false }) {
  const classes = "w-full bg-ink-800 border border-white/10 rounded-xl px-4 py-3 text-cream text-sm placeholder-white/25 focus:border-gold-500/50 transition-colors resize-none"
  return (
    <div>
      <label className="block text-sm text-white/60 mb-1.5">{label}</label>
      {multiline ? (
        <textarea rows={3} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className={classes} />
      ) : (
        <input type="text" value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className={classes} />
      )}
    </div>
  )
}
