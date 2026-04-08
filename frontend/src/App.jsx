import { MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import { HelmetProvider } from "react-helmet-async";
import {
  createBrowserRouter,
  Navigate,
  Outlet,
  RouterProvider,
} from "react-router-dom";
import LoginForm from "./components/accounts/LoginForm";
import ProfileEdit from "./components/accounts/ProfileEdit";
import SignupForm from "./components/accounts/SignupForm";
import PostDelete from "./components/blog/PostDelete";
import PostDetail from "./components/blog/PostDetail";
import MyDrafts from "./components/blog/MyDrafts";
import PostForm from "./components/blog/PostForm";
import PostList from "./components/blog/PostList";
import VersionDetail from "./components/blog/VersionDetail";
import VersionHistory from "./components/blog/VersionHistory";
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

function AuthLayout() {
  return (
    <AuthProvider>
      <Layout />
    </AuthProvider>
  );
}

const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [
      { path: "/", element: <PostList isHome /> },
      { path: "/articles", element: <PostList /> },
      {
        path: "/articles/mes-brouillons",
        element: (
          <ProtectedRoute>
            <MyDrafts />
          </ProtectedRoute>
        ),
      },
      {
        path: "/articles/creer",
        element: (
          <ProtectedRoute>
            <PostForm />
          </ProtectedRoute>
        ),
      },
      { path: "/articles/:slug", element: <PostDetail /> },
      {
        path: "/articles/:slug/versions",
        element: (
          <ProtectedRoute>
            <VersionHistory />
          </ProtectedRoute>
        ),
      },
      {
        path: "/articles/:slug/versions/:versionNumber",
        element: (
          <ProtectedRoute>
            <VersionDetail />
          </ProtectedRoute>
        ),
      },
      {
        path: "/articles/:slug/modifier",
        element: (
          <ProtectedRoute>
            <PostForm />
          </ProtectedRoute>
        ),
      },
      {
        path: "/articles/:slug/supprimer",
        element: (
          <ProtectedRoute>
            <PostDelete />
          </ProtectedRoute>
        ),
      },
      { path: "/comptes/connexion", element: <LoginForm /> },
      { path: "/comptes/inscription", element: <SignupForm /> },
      {
        path: "/comptes/profil/modifier",
        element: (
          <ProtectedRoute>
            <ProfileEdit />
          </ProtectedRoute>
        ),
      },
      { path: "/a-propos", element: <About /> },
      { path: "/contact", element: <Contact /> },
      {
        path: "/suivi-des-devs",
        element: (
          <ProtectedRoute>
            <DevTracking />
          </ProtectedRoute>
        ),
      },
    ],
  },
]);

export default function App() {
  return (
    <MantineProvider>
      <Notifications position="top-right" />
      <HelmetProvider>
        <RouterProvider router={router} />
      </HelmetProvider>
    </MantineProvider>
  );
}
