import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import Avatar from "../ui/Avatar";

export default function Header() {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    function handleClick(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, []);

  const handleLogout = async () => {
    await logout();
    setDropdownOpen(false);
    setMobileOpen(false);
  };

  return (
    <header className="border-b border-gray-200">
      <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link
          to="/"
          className="text-base font-semibold text-gray-900 hover:text-black"
        >
          NICKORP
        </Link>

        {/* Navigation desktop */}
        <nav className="hidden md:flex items-center gap-6">
          <Link to="/" className="nav-link">
            Accueil
          </Link>
          <Link to="/articles" className="nav-link">
            Articles
          </Link>
          <Link to="/a-propos" className="nav-link">
            &Agrave; propos
          </Link>
          <Link to="/contact" className="nav-link">
            Contact
          </Link>
        </nav>

        {/* Boutons auth desktop */}
        <div className="hidden md:flex items-center gap-3">
          {user ? (
            <>
              {user.is_superuser && (
                <Link to="/articles/creer" className="btn-primary">
                  Ajouter un article
                </Link>
              )}
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setDropdownOpen(!dropdownOpen);
                  }}
                  className="flex items-center rounded-full focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
                >
                  <Avatar user={user} size="md" />
                </button>
                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded shadow-lg py-1 z-50">
                    <Link
                      to="/comptes/profil/modifier"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setDropdownOpen(false)}
                    >
                      Mon profil
                    </Link>
                    <Link
                      to="/articles/mes-brouillons"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setDropdownOpen(false)}
                    >
                      Mes brouillons
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      Se d&eacute;connecter
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <Link to="/comptes/connexion" className="btn-secondary">
                Se connecter
              </Link>
              <Link to="/comptes/inscription" className="btn-primary">
                Cr&eacute;er un compte
              </Link>
            </>
          )}
        </div>

        {/* Hamburger mobile */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
          aria-expanded={mobileOpen}
          aria-label="Menu de navigation"
        >
          {mobileOpen ? (
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          ) : (
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          )}
        </button>
      </div>

      {/* Menu mobile */}
      {mobileOpen && (
        <div className="md:hidden border-t border-gray-200 px-4 py-4">
          <nav className="flex flex-col gap-3">
            <Link
              to="/"
              className="nav-link"
              onClick={() => setMobileOpen(false)}
            >
              Accueil
            </Link>
            <Link
              to="/articles"
              className="nav-link"
              onClick={() => setMobileOpen(false)}
            >
              Articles
            </Link>
            <Link
              to="/a-propos"
              className="nav-link"
              onClick={() => setMobileOpen(false)}
            >
              &Agrave; propos
            </Link>
            <Link
              to="/contact"
              className="nav-link"
              onClick={() => setMobileOpen(false)}
            >
              Contact
            </Link>
          </nav>
          <div className="mt-4 pt-4 border-t border-gray-200 flex flex-col gap-3">
            {user ? (
              <>
                <Link
                  to="/comptes/profil/modifier"
                  className="btn-secondary text-center"
                  onClick={() => setMobileOpen(false)}
                >
                  Mon profil
                </Link>
                <Link
                  to="/articles/mes-brouillons"
                  className="btn-secondary text-center"
                  onClick={() => setMobileOpen(false)}
                >
                  Mes brouillons
                </Link>
                {user.is_superuser && (
                  <Link
                    to="/articles/creer"
                    className="btn-primary text-center"
                    onClick={() => setMobileOpen(false)}
                  >
                    Ajouter un article
                  </Link>
                )}
                <button onClick={handleLogout} className="btn-secondary w-full">
                  Se d&eacute;connecter
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/comptes/connexion"
                  className="btn-secondary text-center"
                  onClick={() => setMobileOpen(false)}
                >
                  Se connecter
                </Link>
                <Link
                  to="/comptes/inscription"
                  className="btn-primary text-center"
                  onClick={() => setMobileOpen(false)}
                >
                  Cr&eacute;er un compte
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
