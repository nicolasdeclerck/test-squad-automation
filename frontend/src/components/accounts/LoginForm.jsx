import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

export default function LoginForm() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    const res = await login(email, password);
    if (res.ok) {
      navigate("/");
    } else if (res.errors) {
      setErrors(res.errors);
    }
  };

  const nonFieldErrors = errors.non_field_errors || errors.detail
    ? [errors.detail || errors.non_field_errors].flat()
    : null;

  return (
    <div className="max-w-sm mx-auto px-4 py-16">
      <Helmet>
        <title>Se connecter</title>
        <meta name="description" content="Connectez-vous \u00e0 votre compte pour acc\u00e9der au blog." />
      </Helmet>
      <h1 className="text-2xl font-bold text-gray-900 text-center mb-8">
        Se connecter
      </h1>

      {nonFieldErrors && (
        <div className="mb-6 p-3 border border-red-200 rounded">
          {nonFieldErrors.map((err, i) => (
            <p key={i} className="form-error">
              {err}
            </p>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className="mb-4">
          <label htmlFor="email" className="form-label">
            Adresse email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className={`form-input${errors.email ? " border-red-500" : ""}`}
          />
          {errors.email &&
            errors.email.map((err, i) => (
              <p key={i} className="form-error">
                {err}
              </p>
            ))}
        </div>

        <div className="mb-6">
          <label htmlFor="password" className="form-label">
            Mot de passe
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className={`form-input${errors.password ? " border-red-500" : ""}`}
          />
          {errors.password &&
            errors.password.map((err, i) => (
              <p key={i} className="form-error">
                {err}
              </p>
            ))}
        </div>

        <button type="submit" className="btn-primary w-full py-3">
          Se connecter
        </button>
      </form>

      <div className="mt-6 text-center space-y-2">
        <p className="text-sm text-gray-500">
          Pas encore de compte ?{" "}
          <Link
            to="/comptes/inscription"
            className="text-gray-900 hover:text-black font-medium"
          >
            Cr&eacute;er un compte
          </Link>
        </p>
        <Link
          to="/"
          className="text-sm text-gray-500 hover:text-black block"
        >
          Retour
        </Link>
      </div>
    </div>
  );
}
