import React, { useState, useEffect } from 'react';
import './App.css';
import PromptForm from './components/PromptForm';
import Results from './components/Results';
import LandingPage from './components/LandingPage';
import MemesDashboard from './components/MemesDashboard';
import DocumentationPage from './components/DocumentationPage';
import ethicalReviewApi from './services/api';
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css';

function App() {
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
    ethicalScores: null
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

  const handleEnterTool = () => setView('tool');
  const handleViewMemes = () => setView('memes');
  const handleViewDocs = () => setView('docs');
  const handleViewLanding = () => setView('landing');
  const handleViewTool = () => setView('tool');

  const handleToggleMemeDropdown = () => setShowMemeDropdown(!showMemeDropdown);

  const handleViewMemesClick = () => {
    setView('memes');
    setShowMemeDropdown(false);
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
      ethicalScores: null
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
        ethicalScores: response.ethical_scores
      });
    } catch (err) {
      setError(err.message || 'An error occurred during analysis. Please check inputs or try again.');
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
                <a href="/dash/db#meme-creation">Interact with Database</a>
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
              searchTerm={lowerSearchTerm}
            />
          </>
        );
      case 'memes':
        return <MemesDashboard searchTerm={lowerSearchTerm} />;
      case 'docs':
        return <DocumentationPage searchTerm={lowerSearchTerm} />;
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

export default App; 