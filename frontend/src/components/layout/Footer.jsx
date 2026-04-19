import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

export default function Footer() {
  const { user } = useAuth();

  return (
    <footer className="border-t border-editorial-rule mt-12">
      <div className="max-w-[1200px] mx-auto px-5 sm:px-10 py-8 text-center">
        {user && (
          <p className="text-xs text-editorial-dim mb-2">
            <Link
              to="/suivi-des-devs"
              className="hover:text-editorial-ink transition-colors"
            >
              Suivi des devs
            </Link>
          </p>
        )}
        <p className="text-xs text-editorial-dim tracking-wide">
          &copy; {new Date().getFullYear()} NICKORP
        </p>
      </div>
    </footer>
  );
}
