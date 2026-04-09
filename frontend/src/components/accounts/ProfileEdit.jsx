import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import Avatar from "../ui/Avatar";

export default function ProfileEdit() {
  const { user, updateProfile, deleteAvatar } = useAuth();
  const [firstName, setFirstName] = useState(user?.first_name || "");
  const [lastName, setLastName] = useState(user?.last_name || "");
  const [email, setEmail] = useState(user?.email || "");
  const [avatar, setAvatar] = useState(null);
  const [errors, setErrors] = useState({});
  const [successMsg, setSuccessMsg] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setSuccessMsg("");

    const formData = new FormData();
    formData.append("first_name", firstName);
    formData.append("last_name", lastName);
    formData.append("email", email);
    if (avatar) {
      formData.append("avatar", avatar);
    }

    const res = await updateProfile(formData);
    if (res.ok) {
      setSuccessMsg("Votre profil a \u00e9t\u00e9 mis \u00e0 jour.");
      setAvatar(null);
    } else if (res.errors) {
      setErrors(res.errors);
    }
  };

  const handleDeleteAvatar = async () => {
    setSuccessMsg("");
    setErrors({});
    setIsDeleting(true);
    try {
      const res = await deleteAvatar();
      if (res.ok) {
        setSuccessMsg("Votre avatar a été supprimé.");
      } else {
        setErrors({ non_field_errors: ["Erreur lors de la suppression de l'avatar."] });
      }
    } catch {
      setErrors({ non_field_errors: ["Erreur lors de la suppression de l'avatar."] });
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  if (!user) return null;

  return (
    <div className="max-w-sm mx-auto px-4 py-16">
      {user.avatar && (
        <div className="mb-6 flex justify-center">
          <Avatar user={user} size="lg" />
        </div>
      )}

      <Helmet>
        <title>Modifier mon profil</title>
        <meta name="description" content="Modifiez votre profil : pr\u00e9nom, nom et avatar." />
      </Helmet>
      <h1 className="text-2xl font-bold text-gray-900 text-center mb-8">
        Modifier mon profil
      </h1>

      {successMsg && (
        <div className="mb-6 p-3 border border-green-200 bg-green-50 rounded">
          <p className="text-sm text-green-800">{successMsg}</p>
        </div>
      )}

      {errors.non_field_errors && (
        <div className="mb-6 p-3 border border-red-200 bg-red-50 rounded">
          {errors.non_field_errors.map((err, i) => (
            <p key={i} className="text-sm text-red-800">
              {err}
            </p>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className="mb-4">
          <label htmlFor="first_name" className="form-label">
            Pr&eacute;nom
          </label>
          <input
            type="text"
            id="first_name"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            className={`form-input${
              errors.first_name ? " border-red-500" : ""
            }`}
          />
          {errors.first_name &&
            errors.first_name.map((err, i) => (
              <p key={i} className="form-error">
                {err}
              </p>
            ))}
        </div>

        <div className="mb-4">
          <label htmlFor="last_name" className="form-label">
            Nom
          </label>
          <input
            type="text"
            id="last_name"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            className={`form-input${
              errors.last_name ? " border-red-500" : ""
            }`}
          />
          {errors.last_name &&
            errors.last_name.map((err, i) => (
              <p key={i} className="form-error">
                {err}
              </p>
            ))}
        </div>

        <div className="mb-4">
          <label htmlFor="email" className="form-label">
            Adresse email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={`form-input${
              errors.email ? " border-red-500" : ""
            }`}
          />
          {errors.email &&
            errors.email.map((err, i) => (
              <p key={i} className="form-error">
                {err}
              </p>
            ))}
        </div>

        <div className="mb-6">
          <label htmlFor="avatar" className="form-label">
            Avatar
          </label>
          <input
            type="file"
            id="avatar"
            accept="image/jpeg,image/png,image/webp"
            onChange={(e) => setAvatar(e.target.files[0] || null)}
            className={`form-input${errors.avatar ? " border-red-500" : ""}`}
          />
          {errors.avatar &&
            errors.avatar.map((err, i) => (
              <p key={i} className="form-error">
                {err}
              </p>
            ))}
          <p className="text-xs text-gray-400 mt-1">
            JPEG, PNG ou WebP &mdash; 5 Mo maximum
          </p>
        </div>

        <button type="submit" className="btn-primary w-full py-3">
          Enregistrer
        </button>
      </form>

      {user.avatar && (
        <div className="mt-4 text-center">
          {!showDeleteConfirm ? (
            <button
              type="button"
              onClick={() => setShowDeleteConfirm(true)}
              className="text-sm text-red-600 hover:text-red-800 underline"
            >
              Supprimer l&apos;avatar
            </button>
          ) : (
            <div className="flex items-center justify-center gap-3">
              <button
                type="button"
                onClick={handleDeleteAvatar}
                disabled={isDeleting}
                className="text-sm text-white bg-red-600 hover:bg-red-700 px-3 py-1 rounded disabled:opacity-50"
              >
                {isDeleting ? "Suppression..." : "Confirmer la suppression"}
              </button>
              <button
                type="button"
                onClick={() => setShowDeleteConfirm(false)}
                className="text-sm text-gray-500 hover:text-gray-700 underline"
              >
                Annuler
              </button>
            </div>
          )}
        </div>
      )}

      <div className="mt-6 text-center">
        <Link
          to="/"
          className="text-sm text-gray-500 hover:text-black"
        >
          Retour
        </Link>
      </div>
    </div>
  );
}
