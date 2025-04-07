import React from 'react';

// Helper function to capitalize the first letter
const capitalize = (s) => {
  if (typeof s !== 'string') return ''
  return s.charAt(0).toUpperCase() + s.slice(1).replace('_', ' ') // Replace underscore for display
}

const Results = ({ 
  prompt, 
  originModelUsed, 
  analysisModelUsed, 
  initialResponse, 
  ethicalAnalysisText, 
  ethicalScores 
}) => {
  // Don't render anything if no prompt is available (initial state or error before R1)
  if (!prompt) {
    return null;
  }

  const scoreDimensions = ethicalScores ? Object.keys(ethicalScores) : [];

  return (
    <div className="results-container">
      <h2>Results</h2>
      
      {/* Display Used Models */}
      <div className="model-info-box">
        {originModelUsed && <p><strong>Origin Model Used (R1):</strong> {originModelUsed}</p>}
        {analysisModelUsed && <p><strong>Analysis Model Used (R2):</strong> {analysisModelUsed}</p>}
      </div>
      
      {/* Initial Prompt */}
      <div>
        <h3>Initial Prompt (P1)</h3>
        <div className="result-box"><pre>{prompt}</pre></div>
      </div>
      
      {/* Generated Response (R1) */}
      {initialResponse && (
        <div>
          <h3>Generated Response (R1)</h3>
          <div className="result-box"><pre>{initialResponse}</pre></div>
        </div>
      )}
      
      {/* Textual Ethical Analysis (R2) */}
      {ethicalAnalysisText && (
        <div>
          <h3>Ethical Review Summary (R2)</h3>
          <div className="result-box"><pre>{ethicalAnalysisText}</pre></div>
        </div>
      )}

      {/* Ethical Scores Section (R2) (Conditional) */}
      {ethicalAnalysisText && ( // Only show scoring section if analysis text exists
        <div className="scores-section"> 
          <h3>Ethical Scoring (R2)</h3>
          {ethicalScores && scoreDimensions.length > 0 ? (
            // Render scores if available
            scoreDimensions.map((dimKey) => {
              const dimensionData = ethicalScores?.[dimKey]; 
              return (
                <div key={dimKey} className="dimension-score-box">
                  <h4>{capitalize(dimKey)}</h4>
                  <p><strong>Adherence Score:</strong> {dimensionData?.adherence_score ?? 'N/A'} / 10</p>
                  <p><strong>Confidence Score:</strong> {dimensionData?.confidence_score ?? 'N/A'} / 10</p>
                  <p><strong>Justification:</strong></p>
                  <pre>{dimensionData?.justification || 'N/A'}</pre>
                </div>
              );
            })
          ) : (
            // Render message if scores are missing but analysis text exists
            <p><em>Ethical scoring data could not be generated or parsed.</em></p>
          )}
        </div>
      )}
      
      {/* Handle case where R1 succeeded but R2 failed */}
      {initialResponse && !ethicalAnalysisText && (
         <div>
           <h3>Ethical Review Summary (R2)</h3>
           <p><em>Ethical analysis could not be generated.</em></p>
         </div>
      )}
    </div>
  );
};

export default Results; 