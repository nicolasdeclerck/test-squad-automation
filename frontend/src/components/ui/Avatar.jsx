export default function Avatar({ user, size = "sm" }) {
  const sizeClasses = {
    sm: "w-6 h-6 text-xs",
    md: "w-8 h-8 text-sm",
    lg: "w-20 h-20 text-2xl",
  };

  const initial = (
    user.first_name?.[0] ||
    user.email?.[0] ||
    user.username?.[0] ||
    "?"
  ).toUpperCase();

  if (user.avatar) {
    return (
      <img
        src={user.avatar}
        alt=""
        className={`${sizeClasses[size]} rounded-full object-cover shrink-0`}
      />
    );
  }

  return (
    <div
      className={`${sizeClasses[size]} rounded-full flex items-center justify-center font-medium shrink-0`}
      style={{ background: "#d4e7d6", color: "#1f1f1f" }}
    >
      {initial}
    </div>
  );
}
