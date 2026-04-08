import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

export default function Footer() {
  const { user } = useAuth();

  return (
    <footer className="border-t border-gray-200">
      <div className="max-w-3xl mx-auto px-4 py-6">
        {user && (
          <p className="text-sm text-gray-400 text-center mb-2">
            <Link to="/suivi-des-devs" className="hover:text-gray-600">
              Suivi des devs
            </Link>
          </p>
        )}
        <p className="text-sm text-gray-400 text-center">
          &copy; {new Date().getFullYear()} NICKORP
        </p>
      </div>
    </footer>
  );
}
