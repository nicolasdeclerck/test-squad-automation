export default function Footer() {
  return (
    <footer className="border-t border-editorial-rule mt-12">
      <div className="max-w-[1200px] mx-auto px-5 sm:px-10 py-8 text-center">
        <p className="text-xs text-editorial-dim tracking-wide">
          &copy; {new Date().getFullYear()} NICKORP
        </p>
      </div>
    </footer>
  );
}
