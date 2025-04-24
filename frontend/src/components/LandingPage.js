import React from 'react';
import { Link, useNavigate } from 'react-router-dom'; // Import useNavigate
import '../App.css'; // Assuming shared styles

const LandingPage = ({ onEnter }) => {
  const navigate = useNavigate(); // Get navigate function
  
  // Handle button click with both the provided onEnter function and direct navigation
  const handleEnterClick = () => {
    if (onEnter) {
      onEnter(); // Call the provided onEnter function
    }
    // Also directly navigate to ensure routing works
    navigate('/tool');
  };
  
  return (
    <div className="landing-page">
      {/* Hero Section */}
      <header className="hero text-center mb-xl">
        {/* Add the AI Ethics image */}
        <div className="hero-image mb-lg">
          <img src="/images/herodash.webp" alt="AI Ethics Dashboard" className="hero-img" />
        </div>
        <h1>Transforming AI Ethics Analysis</h1>
        <p className="lead text-secondary mb-lg" style={{ maxWidth: '700px', margin: '0 auto var(--spacing-lg) auto' }}>
          Unlock deeper insights into AI responses with our advanced ethical review tool, integrating Deontology, Teleology, Areteology, and Memetics.
        </p>
        <button onClick={handleEnterClick} className="button button-large" >
          Explore Ethical Analysis Now
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

      {/* Featured Paper Section */}
      <section className="featured-paper text-center mb-xl">
        <h2>Featured Paper</h2>
        <p>
          <a href="/documents/Toward%20Decentralized%20Ethical%20AI%20Governance%20and%20Verification_%20A%20Strategic%20Roadmap.pdf" target="_blank" rel="noopener noreferrer">
            Toward Decentralized Ethical AI Governance and Verification: A Strategic Roadmap
          </a>
        </p>
        <p className="text-secondary" style={{ maxWidth: '800px', margin: '0 auto' }}>
          This strategic roadmap outlines a decentralized, federated framework for ethical AI governance that leverages consensus mechanisms and memetic principles to create transparent, verifiable, and inclusive AI policies across distributed stakeholders.
        </p>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works text-center">
        <h2>How It Works</h2>
        <ul style={{ listStyleType: 'none', padding: 0, maxWidth: '700px', margin: '0 auto' }}>
          <li>Enter a prompt for an AI model (R1).</li>
          <li>Select the AI model (R1) to generate the initial response.</li>
          <li>Select a second AI model (R2) to perform the ethical review.</li>
          <li>R1 generates a response based on your prompt.</li>
          <li>R2 analyzes both the prompt (P1) and the response (R1) using the defined <Link to="/documentation">Ethical Architecture</Link>.</li>
          <li>Results are displayed, including the ethical analysis summary and scores.</li>
          <li>(Optional) Populate or query the Ethical Memes Database via the API endpoints described in the documentation.</li>
        </ul>
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