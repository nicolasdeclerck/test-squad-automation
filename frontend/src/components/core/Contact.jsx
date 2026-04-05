export default function Contact() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Contact</h1>

      <section className="mb-8">
        <p className="text-gray-600 leading-relaxed mb-6">
          Retrouvez-nous sur les plateformes suivantes :
        </p>
        <ul className="space-y-4">
          <li>
            <a
              href="https://github.com/nicolasdeclerck/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              GitHub &mdash; nicolasdeclerck
            </a>
          </li>
          <li>
            <a
              href="https://www.linkedin.com/in/nicolas-declerck/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              LinkedIn &mdash; Nicolas Declerck
            </a>
          </li>
        </ul>
      </section>
    </div>
  );
}
