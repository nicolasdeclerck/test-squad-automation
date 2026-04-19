import { MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import { useEffect } from "react";
import { HelmetProvider } from "react-helmet-async";
import {
  createBrowserRouter,
  Link,
  Navigate,
  Outlet,
  RouterProvider,
  useRouteError,
} from "react-router-dom";
import * as Sentry from "@sentry/react";
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
import Contact from "./components/core/Contact";
import DevTracking from "./components/core/DevTracking";
import Layout from "./components/layout/Layout";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { ThemeProvider, useTheme } from "./contexts/ThemeContext";

function ErrorPage() {
  const error = useRouteError();

  useEffect(() => {
    // React Router attrape l'erreur via errorElement : elle n'atteint donc
    // pas les handlers globaux du SDK Sentry. On la remonte manuellement.
    if (error) {
      Sentry.captureException(error);
    }
  }, [error]);

  return (
    <div className="max-w-xl mx-auto px-4 py-20 text-center">
      <h1 className="text-2xl font-bold text-editorial-ink mb-4">
        Une erreur est survenue
      </h1>
      <p className="text-editorial-text mb-6">
        {error?.message || "Erreur inattendue. Veuillez réessayer."}
      </p>
      <Link
        to="/"
        className="text-sm text-editorial-dim hover:text-editorial-ink transition-colors"
      >
        &larr; Retour à l'accueil
      </Link>
    </div>
  );
}

function ProtectedRoute({ children, requireSuperUser = false }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/comptes/connexion" replace />;
  if (requireSuperUser && !user.is_superuser) return <Navigate to="/" replace />;
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
    errorElement: <ErrorPage />,
    children: [
      { path: "/", element: <PostList isHome /> },
      { path: "/articles", element: <PostList /> },
      {
        path: "/articles/mes-brouillons",
        element: (
          <ProtectedRoute requireSuperUser>
            <MyDrafts />
          </ProtectedRoute>
        ),
      },
      {
        path: "/articles/creer",
        element: (
          <ProtectedRoute requireSuperUser>
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
          <ProtectedRoute requireSuperUser>
            <PostForm />
          </ProtectedRoute>
        ),
      },
      {
        path: "/articles/:slug/supprimer",
        element: (
          <ProtectedRoute requireSuperUser>
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

function ThemedMantineProvider({ children }) {
  const { resolved } = useTheme();
  return (
    <MantineProvider forceColorScheme={resolved}>
      <Notifications position="top-right" />
      {children}
    </MantineProvider>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <ThemedMantineProvider>
        <HelmetProvider>
          <RouterProvider router={router} />
        </HelmetProvider>
      </ThemedMantineProvider>
    </ThemeProvider>
  );
}
