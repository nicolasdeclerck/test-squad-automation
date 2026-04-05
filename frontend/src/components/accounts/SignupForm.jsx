import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

export default function SignupForm() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");
  const [errors, setErrors] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    const res = await signup(email, password1, password2);
    if (res.ok) {
      navigate("/");
    } else if (res.errors) {
      setErrors(res.errors);
    }
  };

  const nonFieldErrors = errors.non_field_errors
    ? [errors.non_field_errors].flat()
    : null;

  return (
    <div className="max-w-sm mx-auto px-4 py-16">
      <h1 className="text-2xl font-bold text-gray-900 text-center mb-8">
        Cr&eacute;er un compte
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
            [errors.email].flat().map((err, i) => (
              <p key={i} className="form-error">
                {err}
              </p>
            ))}
        </div>

        <div className="mb-4">
          <label htmlFor="password1" className="form-label">
            Mot de passe
          </label>
          <input
            type="password"
            id="password1"
            value={password1}
            onChange={(e) => setPassword1(e.target.value)}
            required
            className={`form-input${errors.password1 ? " border-red-500" : ""}`}
          />
          <p className="text-gray-400 text-xs mt-1">
            Au moins 8 caract&egrave;res, pas trop courant ni enti&egrave;rement
            num&eacute;rique.
          </p>
          {errors.password1 &&
            [errors.password1].flat().map((err, i) => (
              <p key={i} className="form-error">
                {err}
              </p>
            ))}
        </div>

        <div className="mb-6">
          <label htmlFor="password2" className="form-label">
            Confirmer le mot de passe
          </label>
          <input
            type="password"
            id="password2"
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
            required
            className={`form-input${errors.password2 ? " border-red-500" : ""}`}
          />
          {errors.password2 &&
            [errors.password2].flat().map((err, i) => (
              <p key={i} className="form-error">
                {err}
              </p>
            ))}
        </div>

        <button type="submit" className="btn-primary w-full py-3">
          Cr&eacute;er mon compte
        </button>
      </form>

      <div className="mt-6 text-center space-y-2">
        <p className="text-sm text-gray-500">
          D&eacute;j&agrave; un compte ?{" "}
          <Link
            to="/comptes/connexion"
            className="text-gray-900 hover:text-black font-medium"
          >
            Se connecter
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
