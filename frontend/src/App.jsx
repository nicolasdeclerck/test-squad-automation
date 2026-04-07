import { MantineProvider } from "@mantine/core";
import { HelmetProvider } from "react-helmet-async";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import LoginForm from "./components/accounts/LoginForm";
import ProfileEdit from "./components/accounts/ProfileEdit";
import SignupForm from "./components/accounts/SignupForm";
import PostDelete from "./components/blog/PostDelete";
import PostDetail from "./components/blog/PostDetail";
import MyDrafts from "./components/blog/MyDrafts";
import PostForm from "./components/blog/PostForm";
import PostList from "./components/blog/PostList";
import About from "./components/core/About";
import Contact from "./components/core/Contact";
import DevTracking from "./components/core/DevTracking";
import Layout from "./components/layout/Layout";
import { AuthProvider, useAuth } from "./contexts/AuthContext";

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/comptes/connexion" replace />;
  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<PostList isHome />} />
        <Route path="/articles" element={<PostList />} />
        <Route
          path="/articles/mes-brouillons"
          element={
            <ProtectedRoute>
              <MyDrafts />
            </ProtectedRoute>
          }
        />
        <Route
          path="/articles/creer"
          element={
            <ProtectedRoute>
              <PostForm />
            </ProtectedRoute>
          }
        />
        <Route path="/articles/:slug" element={<PostDetail />} />
        <Route
          path="/articles/:slug/modifier"
          element={
            <ProtectedRoute>
              <PostForm />
            </ProtectedRoute>
          }
        />
        <Route
          path="/articles/:slug/supprimer"
          element={
            <ProtectedRoute>
              <PostDelete />
            </ProtectedRoute>
          }
        />
        <Route path="/comptes/connexion" element={<LoginForm />} />
        <Route path="/comptes/inscription" element={<SignupForm />} />
        <Route
          path="/comptes/profil/modifier"
          element={
            <ProtectedRoute>
              <ProfileEdit />
            </ProtectedRoute>
          }
        />
        <Route path="/a-propos" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route
          path="/suivi-des-devs"
          element={
            <ProtectedRoute>
              <DevTracking />
            </ProtectedRoute>
          }
        />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <MantineProvider>
      <HelmetProvider>
        <BrowserRouter>
          <AuthProvider>
            <AppRoutes />
          </AuthProvider>
        </BrowserRouter>
      </HelmetProvider>
    </MantineProvider>
  );
}
