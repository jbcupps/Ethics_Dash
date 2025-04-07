import React, { useState } from 'react';

const PromptForm = ({ onSubmit, isLoading, availableModels = [] }) => {
  const [prompt, setPrompt] = useState('');
  const [originModel, setOriginModel] = useState('');
  const [analysisModel, setAnalysisModel] = useState('');
  const [originApiKey, setOriginApiKey] = useState('');
  const [analysisApiKey, setAnalysisApiKey] = useState('');
  const [originApiEndpoint, setOriginApiEndpoint] = useState('');
  const [analysisApiEndpoint, setAnalysisApiEndpoint] = useState('');
  const [error, setError] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError('Please enter a prompt.');
      return;
    }
    
    setError('');
    onSubmit(prompt, originModel, analysisModel, originApiKey, analysisApiKey, originApiEndpoint, analysisApiEndpoint);
  };
  
  const cleanAvailableModels = Array.isArray(availableModels) 
      ? availableModels.filter(m => typeof m === 'string' && m)
      : [];

  return (
    <div className="form-container card">
      {error && <div className="alert alert-error">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="prompt"
            data-tooltip-id="form-tooltip"
            data-tooltip-content="Enter the text you want the first LLM (R1) to respond to."
          >
Enter Prompt (P1):
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            required
            disabled={isLoading}
            placeholder="Enter your prompt here..."
          />
        </div>
        
        <details className="optional-settings">
          <summary
             data-tooltip-id="form-tooltip"
             data-tooltip-content="Optionally configure specific models, API keys, or endpoints for R1 and R2 generation, overriding defaults."
          >
Optional: Specify Models, Keys & Endpoints
          </summary>
          <div className="optional-settings-content">
            <div className="form-section">
              <h4>Origin Model (R1)</h4>
              <div className="form-row">
                <div className="form-group form-group-third">
                  <label htmlFor="originModel"
                    data-tooltip-id="form-tooltip"
                    data-tooltip-content="Select the LLM to generate the initial response (R1). Defaults defined in .env."
                  >
Model:
                  </label>
                  <select
                    id="originModel"
                    value={originModel}
                    onChange={(e) => setOriginModel(e.target.value)}
                    disabled={isLoading || cleanAvailableModels.length === 0}
                  >
                    <option value="">Default (from .env)</option>
                    {cleanAvailableModels.map(model => (
                      <option key={model} value={model}>{model}</option>
                    ))}
                  </select>
                  {cleanAvailableModels.length === 0 && !isLoading && <small>Loading models...</small>}
                </div>

                <div className="form-group form-group-third">
                  <label htmlFor="originApiKey"
                    data-tooltip-id="form-tooltip"
                    data-tooltip-content="Optionally provide an API key specifically for the R1 model call."
                  >
API Key:
                  </label>
                  <input
                    type="password"
                    id="originApiKey"
                    value={originApiKey}
                    onChange={(e) => setOriginApiKey(e.target.value)}
                    disabled={isLoading}
                    placeholder="Default (from .env)"
                    autoComplete="off"
                  />
                </div>

                <div className="form-group form-group-third">
                  <label htmlFor="originApiEndpoint"
                    data-tooltip-id="form-tooltip"
                    data-tooltip-content="Optionally provide a custom API base URL/endpoint for the R1 model call."
                  >
API Endpoint:
                  </label>
                  <input
                    type="text"
                    id="originApiEndpoint"
                    value={originApiEndpoint}
                    onChange={(e) => setOriginApiEndpoint(e.target.value)}
                    disabled={isLoading}
                    placeholder="Default (Provider Standard)"
                    autoComplete="off"
                  />
                </div>
              </div>
            </div>
            
            <div className="form-section">
              <h4>Ethical Review Model (R2)</h4>
              <div className="form-row">
                <div className="form-group form-group-third">
                  <label htmlFor="analysisModel"
                    data-tooltip-id="form-tooltip"
                    data-tooltip-content="Select the LLM to perform the ethical analysis (R2). Defaults defined in .env."
                  >
Model:
                  </label>
                  <select
                    id="analysisModel"
                    value={analysisModel}
                    onChange={(e) => setAnalysisModel(e.target.value)}
                    disabled={isLoading || cleanAvailableModels.length === 0}
                  >
                    <option value="">Default (from .env)</option>
                    {cleanAvailableModels.map(model => (
                      <option key={model} value={model}>{model}</option>
                    ))}
                  </select>
                  {cleanAvailableModels.length === 0 && !isLoading && <small>Loading models...</small>}
                </div>

                <div className="form-group form-group-third">
                  <label htmlFor="analysisApiKey"
                     data-tooltip-id="form-tooltip"
                     data-tooltip-content="Optionally provide an API key specifically for the R2 analysis call."
                  >
API Key:
                  </label>
                  <input
                    type="password"
                    id="analysisApiKey"
                    value={analysisApiKey}
                    onChange={(e) => setAnalysisApiKey(e.target.value)}
                    disabled={isLoading}
                    placeholder="Default (from .env)"
                    autoComplete="off"
                  />
                </div>

                <div className="form-group form-group-third">
                  <label htmlFor="analysisApiEndpoint"
                     data-tooltip-id="form-tooltip"
                     data-tooltip-content="Optionally provide a custom API base URL/endpoint for the R2 analysis call."
                  >
API Endpoint:
                  </label>
                  <input
                    type="text"
                    id="analysisApiEndpoint"
                    value={analysisApiEndpoint}
                    onChange={(e) => setAnalysisApiEndpoint(e.target.value)}
                    disabled={isLoading}
                    placeholder="Default (Provider Standard)"
                    autoComplete="off"
                  />
                </div>
              </div>
            </div>
          </div>
        </details>
        
        <button 
          type="submit" 
          disabled={isLoading}
          data-tooltip-id="form-tooltip"
          data-tooltip-content="Submit the prompt for response generation (R1) and ethical analysis (R2)."
        >
          {isLoading ? 'Processing...' : 'Generate & Analyze'}
        </button>
      </form>
    </div>
  );
};

export default PromptForm; 