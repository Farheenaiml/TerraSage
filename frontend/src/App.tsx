import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { AppShell } from '@/components/layout/AppShell';
import { LandingPage } from '@/pages/LandingPage';
import { LoginPage } from '@/pages/LoginPage';
import { SignupPage } from '@/pages/SignupPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { AnalyzePage } from '@/pages/AnalyzePage';
import { EnvironmentPage } from '@/pages/EnvironmentPage';
import { ConversationsPage } from '@/pages/ConversationsPage';
import { ConversationDetailPage } from '@/pages/ConversationDetailPage';
import { RecommendationsPage } from '@/pages/RecommendationsPage';
import { RecommendationDetailPage } from '@/pages/RecommendationDetailPage';
import { EvidencePage } from '@/pages/EvidencePage';
import { ProfilePage } from '@/pages/ProfilePage';
import { SettingsPage } from '@/pages/SettingsPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <AppShell>
                  <DashboardPage />
                </AppShell>
              </ProtectedRoute>
            }
          />
          <Route
            path="/analysis"
            element={
              <ProtectedRoute>
                <AppShell>
                  <AnalyzePage />
                </AppShell>
              </ProtectedRoute>
            }
          />
          <Route
            path="/environment"
            element={
              <ProtectedRoute>
                <AppShell>
                  <EnvironmentPage />
                </AppShell>
              </ProtectedRoute>
            }
          />
          <Route
            path="/conversations"
            element={
              <ProtectedRoute>
                <AppShell>
                  <ConversationsPage />
                </AppShell>
              </ProtectedRoute>
            }
          />
          <Route
            path="/conversations/:id"
            element={
              <ProtectedRoute>
                <AppShell>
                  <ConversationDetailPage />
                </AppShell>
              </ProtectedRoute>
            }
          />
          <Route
            path="/recommendations"
            element={
              <ProtectedRoute>
                <AppShell>
                  <RecommendationsPage />
                </AppShell>
              </ProtectedRoute>
            }
          />
          <Route
            path="/recommendations/:id"
            element={
              <ProtectedRoute>
                <AppShell>
                  <RecommendationDetailPage />
                </AppShell>
              </ProtectedRoute>
            }
          />
          <Route
            path="/evidence"
            element={
              <ProtectedRoute>
                <AppShell>
                  <EvidencePage />
                </AppShell>
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <AppShell>
                  <ProfilePage />
                </AppShell>
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <AppShell>
                  <SettingsPage />
                </AppShell>
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
