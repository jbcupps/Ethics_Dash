import React, { useState, useEffect } from 'react';
import './App.css';
import PromptForm from './components/PromptForm';
import Results from './components/Results';
import ethicalReviewApi from './services/api';

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableModels, setAvailableModels] = useState([]);
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

  return (
    <div className="app">
      <div className="container">
        <h1>Ethical Review Tool</h1>
        
        {error && <div className="flash-error">{error}</div>}
        
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
      </div>
    </div>
  );
}

export default App; 