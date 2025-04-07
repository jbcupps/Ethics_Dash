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
      const models = await ethicalReviewApi.getModels();
      setAvailableModels(models);
    };
    fetchModels();
  }, []);

  const handleEnterTool = () => setView('tool');
  const handleViewMemes = () => setView('memes');
  const handleViewDocs = () => setView('docs');
  const handleViewLanding = () => setView('landing');
  const handleViewTool = () => setView('tool');

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
        ethicalAnalysisText: response.ethical_analysis_text,
        ethicalScores: response.ethical_scores
      });
    } catch (err) {
      setError(err.message || 'An error occurred during analysis');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderHeader = () => (
    <header className="app-header">
      <nav>
        <button 
          onClick={handleViewTool} 
          className={`nav-button ${view === 'tool' ? 'active' : ''}`}
          data-tooltip-id="nav-tooltip"
          data-tooltip-content="Go to the main analysis tool"
        >
          Ethical Review Tool
        </button>
        <button 
          onClick={handleViewMemes} 
          className={`nav-button ${view === 'memes' ? 'active' : ''}`}
          data-tooltip-id="nav-tooltip"
          data-tooltip-content="Explore the Ethical Memes Library"
        >
          Memes Library
        </button>
        <button 
          onClick={handleViewDocs} 
          className={`nav-button ${view === 'docs' ? 'active' : ''}`}
          data-tooltip-id="nav-tooltip"
          data-tooltip-content="View project documentation and explanation"
        >
          Documentation
        </button>
      </nav>
    </header>
  );

  const renderContent = () => {
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
            />
          </>
        );
      case 'memes':
        return <MemesDashboard />;
      case 'docs':
        return <DocumentationPage />;
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