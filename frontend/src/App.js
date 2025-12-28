import React, { useState, useEffect } from 'react';
import './App.css';
import PromptForm from './components/PromptForm';
import Results from './components/Results';
import LandingPage from './components/LandingPage';
import MemesDashboard from './components/MemesDashboard';
import DocumentationPage from './components/DocumentationPage';
import Governance from './components/Governance';
import AgreementBuilder from './components/AgreementBuilder';
import ethicalReviewApi from './services/api';
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';

function AppContent() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableModels, setAvailableModels] = useState([]);
  const [showTool, setShowTool] = useState(false);
  const [view, setView] = useState('landing');
  const [showMemeDropdown, setShowMemeDropdown] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState({
    prompt: '',
    originModelUsed: '',
    analysisModelUsed: '',
    initialResponse: '',
    ethicalAnalysisText: '',
    ethicalScores: null,
    aiWelfare: null,
    alignment: null
  });

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const models = await ethicalReviewApi.getModels();
        setAvailableModels(models);
      } catch (err) {
        setError(err.message || 'Failed to load models. Please try again later.');
        console.error('Failed to fetch models:', err);
        setAvailableModels([]);
      }
    };
    fetchModels();
  }, []);

  // Make sure these handle functions navigate properly
  const handleEnterTool = () => {
    setView('tool');
    navigate('/tool');
  };
  
  const handleViewMemes = () => {
    setView('memes'); 
    navigate('/memes');
  };
  
  const handleViewDocs = () => {
    setView('docs');
    navigate('/docs');
  };
  
  const handleViewLanding = () => {
    setView('landing');
    navigate('/');
  };
  
  const handleViewTool = () => {
    setView('tool');
    navigate('/tool');
  };

  const handleViewAgreements = () => {
    setView('agreements');
    navigate('/agreements');
  };

  const handleToggleMemeDropdown = () => setShowMemeDropdown(!showMemeDropdown);

  const handleViewMemesClick = () => {
    setView('memes');
    setShowMemeDropdown(false);
    navigate('/memes');
  };

  const handleSubmit = async (prompt, 
                              originModel, 
                              analysisModel, 
                              originApiKey,
                              analysisApiKey,
                              originApiEndpoint,
                              analysisApiEndpoint
                            ) => {
    setLoading(true);
    setError(null);
    setResults({
      prompt: '',
      originModelUsed: '',
      analysisModelUsed: '',
      initialResponse: '',
      ethicalAnalysisText: '',
      ethicalScores: null,
      aiWelfare: null,
      alignment: null
    });
    
    try {
      const response = await ethicalReviewApi.analyzePrompt(
          prompt, 
          originModel, 
          analysisModel,
          originApiKey,
          analysisApiKey,
          originApiEndpoint,
          analysisApiEndpoint
      );
      
      setResults({
        prompt: response.prompt,
        originModelUsed: response.model,
        analysisModelUsed: response.analysis_model,
        initialResponse: response.initial_response,
        ethicalAnalysisText: response.analysis_summary,
        ethicalScores: response.ethical_scores,
        aiWelfare: response.ai_welfare,
        alignment: response.alignment
      });
    } catch (err) {
      setError(err.message || 'An error occurred during analysis. Please check inputs or try again.');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderHeader = () => (
    <header className="app-header sticky-header">
      <nav>
        <button 
          onClick={handleViewTool} 
          className={`nav-button ${view === 'tool' ? 'active' : ''}`}
          data-tooltip-id="nav-tooltip"
          data-tooltip-content="Go to the main analysis tool"
        >
          Ethical Review Tool
        </button>
        <div className="nav-dropdown-container">
          <button 
            onClick={handleToggleMemeDropdown} 
            className={`nav-button ${view === 'memes' ? 'active' : ''}`} 
            data-tooltip-id="nav-tooltip"
            data-tooltip-content="Access Memes Library options"
          >
            Memes Library ▼
          </button>
          {showMemeDropdown && (
            <ul className="nav-dropdown-menu">
              <li>
                <button onClick={handleViewMemesClick}>View Library</button>
              </li>
              <li>
                <a href="/dash/db" onClick={(e) => {e.preventDefault(); window.location.href = '/dash/db';}}>Interact with Database</a>
              </li>
            </ul>
          )}
        </div>
        <button 
          onClick={handleViewDocs} 
          className={`nav-button ${view === 'docs' ? 'active' : ''}`}
          data-tooltip-id="nav-tooltip"
          data-tooltip-content="View project documentation and explanation"
        >
          Documentation
        </button>
        <button
          onClick={handleViewAgreements}
          className={`nav-button ${view === 'agreements' ? 'active' : ''}`}
          data-tooltip-id="nav-tooltip"
          data-tooltip-content="Build and negotiate voluntary agreements"
        >
          Agreements
        </button>
        <div className="nav-search">
          <input 
            type="text" 
            placeholder="Search content..." 
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </nav>
    </header>
  );

  const renderContent = () => {
    const lowerSearchTerm = searchTerm.toLowerCase();
    switch (view) {
      case 'tool':
        return (
          <>
            <h1>Ethical Review Tool</h1>
            {error && <div className="alert alert-error">{error}</div>}
            <PromptForm 
              onSubmit={handleSubmit}
              isLoading={loading}
              availableModels={availableModels}
            />
            {loading && (
              <div className="loading">
                <div className="spinner"></div>
              </div>
            )}
            <Results 
              prompt={results.prompt}
              originModelUsed={results.originModelUsed}
              analysisModelUsed={results.analysisModelUsed}
              initialResponse={results.initialResponse}
              ethicalAnalysisText={results.ethicalAnalysisText}
              ethicalScores={results.ethicalScores}
              aiWelfare={results.aiWelfare}
              alignment={results.alignment}
              searchTerm={lowerSearchTerm}
              onCreateAgreement={handleViewAgreements}
            />
          </>
        );
      case 'memes':
        return <MemesDashboard searchTerm={lowerSearchTerm} />;
      case 'docs':
        return <DocumentationPage searchTerm={lowerSearchTerm} />;
      case 'agreements':
        return <AgreementBuilder analysisContext={results} />;
      case 'landing':
      default:
        return <LandingPage onEnter={handleEnterTool} />;
    }
  };

  return (
    <div className="app">
      {view !== 'landing' && renderHeader()}
      <div className="container">
        {renderContent()}
      </div>
      <footer className="footer">
        <p>&copy; {new Date().getFullYear()} Ethical Review Tool. All rights reserved.</p>
      </footer>
      <Tooltip id="nav-tooltip" place="bottom" />
      <Tooltip id="form-tooltip" place="top" />
      <Tooltip id="results-tooltip" place="top" />
    </div>
  );
}

// Main app component using top-level Router from index.js
function App() {
  return (
    <Routes>
      <Route path="/*" element={<AppContent />} />
      <Route path="/governance" element={<Governance />} />
    </Routes>
  );
}

export default App; 
