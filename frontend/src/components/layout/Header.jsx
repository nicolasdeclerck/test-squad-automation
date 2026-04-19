import { useEffect, useRef, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import Avatar from "../ui/Avatar";

const navLinkClass = ({ isActive }) =>
  isActive ? "nav-link-active" : "nav-link";

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
    <header className="border-b border-editorial-rule bg-white sticky top-0 z-10">
      <div className="max-w-[1200px] mx-auto px-5 sm:px-10 py-4 flex items-center justify-between">
        <Link
          to="/"
          className="text-sm font-semibold text-editorial-ink hover:text-editorial-ink2 tracking-[2px]"
        >
          NICKORP
        </Link>

        {/* Navigation desktop */}
        <nav className="hidden md:flex items-center gap-7">
          <NavLink to="/" end className={navLinkClass}>
            Accueil
          </NavLink>
          <NavLink to="/articles" className={navLinkClass}>
            Articles
          </NavLink>
          <NavLink to="/contact" className={navLinkClass}>
            Contact
          </NavLink>
        </nav>

        {/* Boutons auth desktop */}
        <div className="hidden md:flex items-center gap-3">
          {user ? (
            <>
              {user.is_superuser && (
                <Link
                  to="/articles/creer"
                  className="inline-flex items-center text-[13px] font-medium bg-editorial-ink text-white hover:bg-editorial-ink2 transition-colors"
                  style={{ padding: "8px 14px", borderRadius: 3 }}
                >
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
                  <div className="absolute right-0 mt-2 w-48 bg-white border border-editorial-rule rounded-[3px] shadow-lg py-1 z-50">
                    <Link
                      to="/comptes/profil/modifier"
                      className="block px-4 py-2 text-sm text-editorial-text hover:bg-editorial-rule2"
                      onClick={() => setDropdownOpen(false)}
                    >
                      Mon profil
                    </Link>
                    {user.is_superuser && (
                      <Link
                        to="/articles/mes-brouillons"
                        className="block px-4 py-2 text-sm text-editorial-text hover:bg-editorial-rule2"
                        onClick={() => setDropdownOpen(false)}
                      >
                        Mes brouillons
                      </Link>
                    )}
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-editorial-text hover:bg-editorial-rule2"
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
          className="md:hidden inline-flex items-center justify-center p-2 rounded-[3px] text-editorial-ink2 hover:text-editorial-ink hover:bg-editorial-rule2"
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
        <div className="md:hidden border-t border-editorial-rule px-5 py-4">
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
              to="/contact"
              className="nav-link"
              onClick={() => setMobileOpen(false)}
            >
              Contact
            </Link>
          </nav>
          <div className="mt-4 pt-4 border-t border-editorial-rule flex flex-col gap-3">
            {user ? (
              <>
                <Link
                  to="/comptes/profil/modifier"
                  className="btn-secondary text-center"
                  onClick={() => setMobileOpen(false)}
                >
                  Mon profil
                </Link>
                {user.is_superuser && (
                  <Link
                    to="/articles/mes-brouillons"
                    className="btn-secondary text-center"
                    onClick={() => setMobileOpen(false)}
                  >
                    Mes brouillons
                  </Link>
                )}
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
