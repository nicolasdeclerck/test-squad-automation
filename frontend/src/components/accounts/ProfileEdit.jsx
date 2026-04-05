import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import Avatar from "../ui/Avatar";

export default function ProfileEdit() {
  const { user, updateProfile, deleteAvatar } = useAuth();
  const [firstName, setFirstName] = useState(user?.first_name || "");
  const [lastName, setLastName] = useState(user?.last_name || "");
  const [avatar, setAvatar] = useState(null);
  const [errors, setErrors] = useState({});
  const [successMsg, setSuccessMsg] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setSuccessMsg("");

    const formData = new FormData();
    formData.append("first_name", firstName);
    formData.append("last_name", lastName);
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
    if (
      !window.confirm(
        "\u00cates-vous s\u00fbr de vouloir supprimer votre avatar ?"
      )
    ) {
      return;
    }
    const res = await deleteAvatar();
    if (res.ok) {
      setSuccessMsg("Votre avatar a \u00e9t\u00e9 supprim\u00e9.");
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
          <button
            onClick={handleDeleteAvatar}
            className="text-sm text-red-600 hover:text-red-800 underline"
          >
            Supprimer l&apos;avatar
          </button>
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
