import { useTheme } from "../../contexts/ThemeContext";

const LABELS = {
  light: "Thème clair — cliquer pour passer au thème sombre",
  dark: "Thème sombre — cliquer pour suivre le thème système",
  auto: "Thème système — cliquer pour passer au thème clair",
};

const NEXT = { light: "dark", dark: "auto", auto: "light" };

function SunIcon() {
  return (
    <svg
      className="h-5 w-5"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.7}
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 3v1.5m0 15V21m9-9h-1.5M4.5 12H3m15.364-6.364-1.06 1.06M6.697 17.303l-1.061 1.06m12.728 0-1.06-1.06M6.697 6.697l-1.061-1.06M16.5 12a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0Z"
      />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg
      className="h-5 w-5"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.7}
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z"
      />
    </svg>
  );
}

function AutoIcon() {
  return (
    <svg
      className="h-5 w-5"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.7}
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="8" />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 4a8 8 0 0 0 0 16z"
        fill="currentColor"
      />
    </svg>
  );
}

export default function ThemeToggle({ className = "" }) {
  const { theme, setTheme } = useTheme();
  const icon =
    theme === "light" ? <SunIcon /> : theme === "dark" ? <MoonIcon /> : <AutoIcon />;

  return (
    <button
      type="button"
      onClick={() => setTheme(NEXT[theme])}
      className={`inline-flex items-center justify-center p-2 rounded-[3px] text-editorial-dim hover:text-editorial-ink hover:bg-editorial-rule2 focus:outline-none focus:ring-2 focus:ring-editorial-ink focus:ring-offset-2 focus:ring-offset-editorial-paper transition-colors ${className}`}
      aria-label={LABELS[theme]}
      title={LABELS[theme]}
    >
      {icon}
    </button>
  );
}
