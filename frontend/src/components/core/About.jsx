import { Helmet } from "react-helmet-async";

export default function About() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <Helmet>
        <title>&Agrave; propos &mdash; NICKORP</title>
        <meta name="description" content="D\u00e9couvrez NICKORP, notre histoire et notre mission." />
      </Helmet>
      <h1 className="text-4xl font-bold text-gray-900 mb-8">
        &Agrave; propos de NICKORP
      </h1>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          Notre histoire
        </h2>
        <p className="text-gray-600 leading-relaxed">
          NICKORP est une entreprise passionn&eacute;e par la technologie et
          l&apos;innovation. Depuis notre cr&eacute;ation, nous nous engageons
          &agrave; fournir des solutions num&eacute;riques de qualit&eacute; qui
          r&eacute;pondent aux besoins de nos clients et de notre
          communaut&eacute;.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          Notre mission
        </h2>
        <p className="text-gray-600 leading-relaxed">
          Notre mission est de rendre la technologie accessible &agrave; tous en
          proposant des outils et des contenus qui simplifient le quotidien. Nous
          croyons en un num&eacute;rique ouvert, collaboratif et responsable.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          Nos valeurs
        </h2>
        <ul className="list-disc list-inside text-gray-600 leading-relaxed space-y-2">
          <li>
            <strong>Innovation</strong> &mdash; Explorer de nouvelles id&eacute;es
            pour cr&eacute;er de la valeur.
          </li>
          <li>
            <strong>Transparence</strong> &mdash; Communiquer ouvertement avec nos
            utilisateurs et partenaires.
          </li>
          <li>
            <strong>Qualit&eacute;</strong> &mdash; Viser l&apos;excellence dans
            chaque projet que nous entreprenons.
          </li>
          <li>
            <strong>Collaboration</strong> &mdash; Travailler ensemble pour aller
            plus loin.
          </li>
        </ul>
      </section>
    </div>
  );
}
