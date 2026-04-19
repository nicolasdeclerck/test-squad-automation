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

  const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ");

  return (
    <div className="max-w-[1200px] mx-auto px-5 sm:px-10 py-12 lg:py-16">
      <Helmet>
        <title>Modifier mon profil</title>
        <meta name="description" content="Modifiez votre profil : pr\u00e9nom, nom, email et avatar." />
      </Helmet>

      <div className="max-w-[760px]">
        <p
          className="font-sans text-editorial-accent font-semibold mb-3"
          style={{
            fontSize: 11,
            letterSpacing: 2,
            textTransform: "uppercase",
          }}
        >
          Compte
        </p>
        <div className="flex items-end justify-between gap-6 mb-10">
          <h1
            className="font-serif text-editorial-ink"
            style={{
              fontSize: "clamp(32px, 4.6vw, 54px)",
              lineHeight: 1.05,
              fontWeight: 600,
              letterSpacing: "-0.02em",
              margin: 0,
            }}
          >
            Mon profil
          </h1>
          <Link
            to="/"
            className="text-sm text-editorial-dim hover:text-editorial-ink transition-colors shrink-0 pb-2"
          >
            ← Retour
          </Link>
        </div>

        <div className="flex items-start gap-4 pb-8 mb-8 border-b border-editorial-rule">
          <div className="flex flex-col items-center gap-2 shrink-0">
            <Avatar user={user} size="lg" />
            {user.avatar && !showDeleteConfirm && (
              <button
                type="button"
                onClick={() => setShowDeleteConfirm(true)}
                className="font-sans text-xs text-editorial-dim hover:text-editorial-ink transition-colors"
              >
                Supprimer l&apos;avatar
              </button>
            )}
          </div>
          <div className="min-w-0 pt-1">
            {fullName && (
              <p className="font-serif text-editorial-ink text-xl leading-tight tracking-tight mb-1">
                {fullName}
              </p>
            )}
            <p className="font-sans text-sm text-editorial-dim break-all">
              {user.email}
            </p>
          </div>
        </div>

        {user.avatar && showDeleteConfirm && (
          <div
            className="mb-6 px-4 py-3 border border-editorial-rule bg-editorial-rule2 flex items-center gap-3"
            style={{ borderRadius: 3 }}
          >
            <p className="font-sans text-sm text-editorial-text flex-1">
              Confirmer la suppression de l&apos;avatar ?
            </p>
            <button
              type="button"
              onClick={() => setShowDeleteConfirm(false)}
              className="btn-secondary py-2"
            >
              Annuler
            </button>
            <button
              type="button"
              onClick={handleDeleteAvatar}
              disabled={isDeleting}
              className="btn-danger py-2 disabled:opacity-50"
            >
              {isDeleting ? "Suppression…" : "Supprimer"}
            </button>
          </div>
        )}

        {successMsg && (
          <div
            className="mb-6 px-4 py-3 border border-editorial-rule bg-editorial-rule2 font-sans text-sm text-editorial-ink"
            style={{ borderRadius: 3 }}
          >
            {successMsg}
          </div>
        )}

        {errors.non_field_errors && (
          <div
            className="mb-6 px-4 py-3 border border-red-200 dark:border-red-700 bg-red-50 dark:bg-red-900/30"
            style={{ borderRadius: 3 }}
          >
            {errors.non_field_errors.map((err, i) => (
              <p key={i} className="font-sans text-sm text-red-700 dark:text-red-300">
                {err}
              </p>
            ))}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div className="mb-5">
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

          <div className="mb-5">
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

          <div className="mb-5">
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

          <div className="mb-8">
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
            <p className="font-sans text-editorial-dim2 mt-2" style={{ fontSize: 11 }}>
              JPEG, PNG ou WebP &middot; 5 Mo maximum
            </p>
          </div>

          <div className="flex gap-3">
            <button type="submit" className="btn-primary flex-1 py-3">
              Enregistrer
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
