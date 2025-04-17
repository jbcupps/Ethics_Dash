import React from 'react';
import '../App.css'; // Assuming shared styles

const DocumentationPage = () => {
  return (
    <div className="documentation-page">
      <h1>Project Documentation & Explanation</h1>

      <section className="card mb-lg">
        <h2>Purpose</h2>
        <p>
          The <strong>Ethical Review Tool</strong> is designed to facilitate the analysis of Large Language Model (LLM) generated text through multiple ethical frameworks. It allows users to:
        </p>
        <ul>
          <li>Submit an initial prompt (P1).</li>
          <li>Receive a generated response (R1) from a selected LLM (OpenAI, Gemini, Anthropic).</li>
          <li>Receive an ethical analysis (R2) of the R1 response, performed by a potentially different LLM, based on a defined ethical ontology.</li>
          <li>Explore a library of ethical concepts treated as "memes".</li>
        </ul>
      </section>

      <section className="card mb-lg">
        <h2>Core Analysis Workflow (R1 & R2)</h2>
        <p>
          The primary workflow involves two stages:
        </p>
        <ol>
          <li>
            <strong>Response Generation (R1):</strong> The user provides a prompt (P1). The application sends this prompt to the selected "Origin Model" (e.g., GPT-4o, Claude Sonnet, Gemini Pro). The model's output is captured as the initial response (R1).
          </li>
          <li>
            <strong>Ethical Analysis (R2):</strong> The original prompt (P1) and the generated response (R1) are sent to the selected "Ethical Review Model" along with the project's ethical ontology. This model analyzes R1 based *strictly* on the provided ontology, generating both a textual summary and structured scores across the defined ethical dimensions. 
          </li>
        </ol>
        <p>
          Users can optionally override default API keys and endpoints for both R1 and R2 models directly in the UI.
        </p>
      </section>

      <section className="card mb-lg">
        <h2>Ethical Framework & Ontology</h2>
        <p>
          The ethical analysis (R2) is grounded in a specific, integrated ethical architecture defined within the project. This framework combines four key dimensions:
        </p>
        <ul>
          <li><strong>Deontology (Eth_Deon):</strong> Focuses on duties, rules, and intentions. An action is right if it conforms to a valid moral rule (e.g., Kant's Categorical Imperative).</li>
          <li><strong>Teleology (Eth_Teleo):</strong> Focuses on consequences and outcomes. An action is right if it produces the best overall results (e.g., Utilitarianism's "greatest good for the greatest number").</li>
          <li><strong>Areteology (Eth_Arete):</strong> Focuses on the character of the agent, promoting virtues (like honesty, compassion) that lead to human flourishing (Eudaimonia).</li>
          <li><strong>Memetics (Mem):</strong> Analyzes ethical ideas as memes, focusing on their properties like replication fidelity, persistence, and adaptability.</li>
        </ul>
        <p>
          The detailed definitions, concepts, and analysis questions for each dimension are specified in the foundational ontology document located at: <code>backend/backend/app/ontology.md</code>.
          The R2 analysis prompt explicitly instructs the LLM to adhere strictly to this document.
        </p>
      </section>

      <section className="card mb-lg">
        <h2>Ethical Memes Library</h2>
        <p>
          The project includes a backend component to store and manage a library of ethical concepts, principles, and ideas, treated as "memes". This library is stored in a MongoDB collection named <code>ethical_memes</code>.
        </p>
        <p>
          The structure for each meme document includes its name, description, source concept, keywords, variations, examples, and links to related memes. Crucially, it contains dimension-specific attributes allowing for analysis of the meme itself through the lenses of Deontology, Teleology, Areteology, and Memetics (including properties like transmissibility, persistence, etc.).
        </p>
        <p>
          The "Memes Library" page in this application provides a dashboard to browse and explore the memes currently stored in the database.
        </p>
        <p>The schema design is documented in <code>Context/prompt.txt</code>.</p>
      </section>

      <section className="card mb-lg">
        <h2>Technology Stack</h2>
        <ul>
          <li><strong>Frontend:</strong> React, Axios</li>
          <li><strong>Backend:</strong> Python, Flask, Pymongo</li>
          <li><strong>LLM Interaction:</strong> OpenAI, Google Gemini, Anthropic SDKs</li>
          <li><strong>Database:</strong> MongoDB</li>
          <li><strong>Containerization:</strong> Docker, Docker Compose</li>
          <li><strong>API Design:</strong> RESTful</li>
        </ul>
      </section>

      <section className="card mb-lg">
        <h2>Ethical Analysis (R2) Details</h2>
        <p>
          The R2 analysis generates two main outputs:
        </p>
        <ul>
          <li><strong>Ethical Scoring:</strong> R1 is quantitatively scored (1-10) on adherence to and confidence in alignment with Deontology, Teleology, Areteology, and Memetics based on the ontology and relevant memes.</li>
          <li><strong>Memetics Analysis:</strong> Explicit analysis of the memetic properties (fitness) of the ethical ideas present in R1.</li>
        </ul>
        <p>
          The core idea is to assess LLM prompts and responses through the lenses of Deontology, Teleology, Areteology, and Memetics (including properties like transmissibility, persistence, etc.).
        </p>
        <p>
          This allows for a nuanced understanding of the ethical implications, moving beyond simple right/wrong judgments.
        </p>
      </section>

    </div>
  );
};

export default DocumentationPage; 