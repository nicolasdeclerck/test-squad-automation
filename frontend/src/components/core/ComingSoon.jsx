import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

export default function ComingSoon() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-gray-800">Coming Soon</h1>
        <p className="text-xl text-gray-500 mt-4">
          Notre blog arrive bient&ocirc;t. Restez connect&eacute;s !
        </p>
        {user ? (
          <>
            <p className="text-lg text-gray-600 mt-4">
              Bienvenue, {user.username} !
            </p>
            <button
              onClick={logout}
              className="mt-6 inline-block border border-red-600 text-red-600 px-6 py-3 rounded-lg hover:bg-red-50 transition font-semibold"
            >
              Se d&eacute;connecter
            </button>
          </>
        ) : (
          <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/comptes/inscription"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-semibold"
            >
              Cr&eacute;er un compte
            </Link>
            <Link
              to="/comptes/connexion"
              className="inline-block border border-blue-600 text-blue-600 px-6 py-3 rounded-lg hover:bg-blue-50 transition font-semibold"
            >
              Se connecter
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
