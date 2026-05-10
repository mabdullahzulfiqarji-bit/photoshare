import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import CreatorDashboard from './pages/CreatorDashboard'
import Upload from './pages/Upload'
import PhotoDetail from './pages/PhotoDetail'
import AdminDashboard from './pages/AdminDashboard'
import SearchResults from './pages/SearchResults'

function ProtectedRoute({ children, requireCreator = false, requireAdmin = false }) {
  const { isAuthenticated, isCreator, isAdmin } = useAuthStore()
  if (!isAuthenticated()) return <Navigate to="/login" replace />
  if (requireAdmin && !isAdmin()) return <Navigate to="/" replace />
  if (requireCreator && !isCreator()) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-ink-950">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/search" element={<SearchResults />} />
          <Route path="/photo/:id" element={<PhotoDetail />} />
          <Route
            path="/creator"
            element={
              <ProtectedRoute requireCreator>
                <CreatorDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/upload"
            element={
              <ProtectedRoute requireCreator>
                <Upload />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute requireAdmin>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
