import React, { useState, useEffect } from 'react';
import ethicalReviewApi from '../services/api';
import '../App.css'; // Assuming shared styles

const MemesDashboard = ({ searchTerm }) => {
  const [memes, setMemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMemes = async () => {
      setLoading(true);
      setError(null);
      try {
        const fetchedMemes = await ethicalReviewApi.getMemes();
        setMemes(fetchedMemes);
      } catch (err) {
        setError('Failed to fetch memes. Please try again later.');
        console.error("Error in fetchMemes:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchMemes();
  }, []);

  // Helper to render dimension badges
  const renderDimensionBadges = (dimensions) => {
    if (!dimensions || dimensions.length === 0) return null;
    return dimensions.map(dim => (
      <span key={dim} className={`badge badge-${dim.toLowerCase()}`}>{dim}</span>
    ));
  };

  // Filter memes based on search term
  const filteredMemes = searchTerm 
    ? memes.filter(meme => 
        meme.name.toLowerCase().includes(searchTerm) || 
        meme.description.toLowerCase().includes(searchTerm) || 
        (meme.keywords && meme.keywords.some(kw => kw.toLowerCase().includes(searchTerm))) ||
        (meme.source_concept && meme.source_concept.toLowerCase().includes(searchTerm))
      )
    : memes;

  return (
    <div className="memes-dashboard">
      <h2 className="mb-lg">Ethical Memes Library</h2>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading memes...</p>
        </div>
      )}
      
      {error && <div className="alert alert-error" role="alert">{error}</div>}

      {!loading && !error && (
        <div className="memes-list">
          {filteredMemes.length > 0 ? (
            filteredMemes.map(meme => (
              <div key={meme._id} className="card meme-card mb-lg">
                <h3>{meme.name}</h3>
                <div className="meme-dimensions mb-sm">
                  {renderDimensionBadges(meme.ethical_dimension)}
                </div>
                <p className="text-secondary mb-sm">Source Concept: {meme.source_concept}</p>
                <p>{meme.description}</p>
                {meme.keywords && meme.keywords.length > 0 && (
                   <p><small>Keywords: {meme.keywords.join(', ')}</small></p>
                )}
                {/* Add more details or link to a full view later */}
              </div>
            ))
          ) : (
            <p>No memes found matching your search criteria.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default MemesDashboard; 