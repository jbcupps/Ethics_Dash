import React from 'react';
import { Link } from 'react-router-dom'; // Import Link
import '../App.css'; // Assuming shared styles

const LandingPage = ({ onEnter }) => {
  return (
    <div className="landing-page">
      {/* Hero Section */}
      <header className="hero text-center mb-xl">
        {/* Placeholder for an icon or logo if desired */}
        {/* <div className="hero-icon mb-lg">&#x1F916;</div> */}
        <h1>AI Ethical Review Dashboard</h1>
        <p className="lead text-secondary mb-lg" style={{ maxWidth: '700px', margin: '0 auto var(--spacing-lg) auto' }}>
          Analyze Large Language Model responses through the integrated lens of Deontology, Teleology, Areteology, and Memetics.
        </p>
        <button onClick={onEnter} className="button button-large" >
          Start Analysis Tool
        </button>
      </header>

      {/* Features Section */}
      <section className="features-overview text-center">
        <h2 className="mb-lg">Key Features</h2>
        <div className="features-grid">
          <div className="feature-item card">
            {/* Icon placeholder */}
            {/* <div className="feature-icon">&#x1F50D;</div> */} 
            <h3>Multi-Framework Analysis</h3>
            <p className="text-secondary">
              Evaluate LLM outputs using Deontology, Teleology, Areteology, and Memetics based on a defined ontology.
            </p>
          </div>
          <div className="feature-item card">
             {/* Icon placeholder */}
            {/* <div className="feature-icon">&#x1F9E0;</div> */} 
            <h3>Flexible LLM Selection</h3>
            <p className="text-secondary">
              Choose from OpenAI, Gemini, or Anthropic models for both initial response generation (R1) and ethical review (R2).
            </p>
          </div>
          <div className="feature-item card">
            {/* Icon placeholder */}
            {/* <div className="feature-icon">&#x1F4C2;</div> */} 
            <h3>Ethical Memes Library</h3>
            <p className="text-secondary">
              Explore and manage a database of ethical concepts treated as memes, analyzed across all framework dimensions.
            </p>
          </div>
        </div>
      </section>

      <section className="how-it-works text-center">
        <h2>How It Works</h2>
        <ol>
          <li>Enter a prompt for an AI model (R1).</li>
          <li>Select the AI model (R1) to generate the initial response.</li>
          <li>Select a second AI model (R2) to perform the ethical review.</li>
          <li>R1 generates a response based on your prompt.</li>
          <li>R2 analyzes both the prompt (P1) and the response (R1) using the defined <Link to="/documentation">Ethical Architecture</Link>.</li>
          <li>Results are displayed, including the ethical analysis summary and scores.</li>
          <li>(Optional) Populate or query the Ethical Memes Database via the API endpoints described in the documentation.</li>
        </ol>
      </section>

      <section className="ethical-framework text-center">
        <h2>Ethical Framework</h2>
        <p>
          Evaluate LLM outputs using Deontology, Teleology, Areteology, and Memetics based on a defined ontology.
        </p>
      </section>
    </div>
  );
};

export default LandingPage; 