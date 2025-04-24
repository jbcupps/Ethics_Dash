import React, { useState, useEffect, useMemo } from 'react';
import ethicalReviewApi from '../services/api';
import ForceGraph2D from 'react-force-graph-2d';
import ReactMarkdown from 'react-markdown';
import '../App.css'; // Assuming shared styles

const MemesDashboard = ({ searchTerm }) => {
  const [memes, setMemes] = useState([]);
  const [ontologyText, setOntologyText] = useState('');
  const [loadingMemes, setLoadingMemes] = useState(true);
  const [loadingOntology, setLoadingOntology] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('list'); // 'list' | 'graph' | 'ontology'

  useEffect(() => {
    const fetchMemes = async () => {
      setLoadingMemes(true);
      setError(null);
      try {
        const fetchedMemes = await ethicalReviewApi.getMemes();
        setMemes(fetchedMemes);
      } catch (err) {
        setError('Failed to fetch memes. Please try again later.');
        console.error("Error in fetchMemes:", err);
      } finally {
        setLoadingMemes(false);
      }
    };

    fetchMemes();
  }, []);

  // Fetch ontology lazily when ontology tab is first activated
  useEffect(() => {
    if (activeTab === 'ontology' && !ontologyText && !loadingOntology) {
      const fetchOntology = async () => {
        setLoadingOntology(true);
        try {
          const text = await ethicalReviewApi.getOntology();
          setOntologyText(text);
        } catch (err) {
          setError('Failed to fetch ontology.');
          console.error('Error fetching ontology:', err);
        } finally {
          setLoadingOntology(false);
        }
      };
      fetchOntology();
    }
  }, [activeTab, ontologyText, loadingOntology]);

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

  /* ----------------- Graph Construction ----------------- */
  const graphData = useMemo(() => {
    if (memes.length === 0) return { nodes: [], links: [] };

    const nodes = memes.map((m) => ({ id: m._id, label: m.name }));
    const links = [];

    // Build links using morphisms if available, else fallback to related_memes
    memes.forEach((m) => {
      const sourceId = m._id;
      if (Array.isArray(m.morphisms)) {
        m.morphisms.forEach((morph) => {
          const targetId = morph?.target_meme_id;
          if (targetId) links.push({ source: sourceId, target: targetId, label: morph?.type || 'relates' });
        });
      }
      if (Array.isArray(m.related_memes)) {
        m.related_memes.forEach((rel) => {
          const target = memes.find(tm => tm._id === rel || tm.name === rel);
          if (target) links.push({ source: sourceId, target: target._id, label: 'related_to' });
        });
      }
    });

    // Deduplicate
    const seen = new Set();
    const dedup = [];
    links.forEach(l => {
      const key = `${l.source}-${l.target}`;
      if (!seen.has(key)) { seen.add(key); dedup.push(l); }
    });

    return { nodes, links: dedup };
  }, [memes]);

  return (
    <div className="memes-dashboard">
      <h2 className="mb-lg">Ethical Memes Library</h2>

      {/* Tab Controls */}
      <div className="tab-controls mb-md">
        <button 
          className={`tab-button ${activeTab === 'list' ? 'active' : ''}`} 
          onClick={() => setActiveTab('list')}
        >
          List
        </button>
        <button 
          className={`tab-button ${activeTab === 'graph' ? 'active' : ''}`} 
          onClick={() => setActiveTab('graph')}
        >
          Graph
        </button>
        <button 
          className={`tab-button ${activeTab === 'ontology' ? 'active' : ''}`} 
          onClick={() => setActiveTab('ontology')}
        >
          Ontology
        </button>
      </div>

      {loadingMemes && activeTab !== 'ontology' && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading memes...</p>
        </div>
      )}
      
      {error && <div className="alert alert-error" role="alert">{error}</div>}

      {/* List View */}
      {activeTab === 'list' && !loadingMemes && !error && (
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
              </div>
            ))
          ) : (
            <p>No memes found matching your search criteria.</p>
          )}
        </div>
      )}

      {/* Graph View */}
      {activeTab === 'graph' && (
        loadingMemes ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading graph...</p>
          </div>
        ) : (
          <div className="meme-graph-wrapper" style={{ width: '100%', height: '600px' }}>
            {graphData.nodes.length > 0 ? (
              <ForceGraph2D
                graphData={graphData}
                nodeLabel="label"
                linkLabel="label"
                width={window.innerWidth}
                height={600}
                nodeColor={() => "#007bff"}
                linkColor={() => "#6c757d"}
                nodeCanvasObject={(node, ctx, globalScale) => {
                  // Draw node
                  const label = node.label;
                  const fontSize = 12/globalScale;
                  ctx.font = `${fontSize}px Sans-Serif`;
                  const textWidth = ctx.measureText(label).width;
                  const bgDiameter = Math.max(textWidth + 8, 20);
                  
                  // Node circle
                  ctx.fillStyle = "#007bff";
                  ctx.beginPath();
                  ctx.arc(node.x, node.y, bgDiameter/2, 0, 2 * Math.PI);
                  ctx.fill();
                  
                  // Node text
                  ctx.fillStyle = "#ffffff";
                  ctx.textAlign = "center";
                  ctx.textBaseline = "middle";
                  ctx.fillText(label, node.x, node.y);
                }}
                linkDirectionalArrowLength={3}
                linkDirectionalArrowRelPos={1}
              />
            ) : (
              <p>No data available to display the graph.</p>
            )}
          </div>
        )
      )}

      {/* Ontology View */}
      {activeTab === 'ontology' && (
        loadingOntology ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading ontology...</p>
          </div>
        ) : (
          <div className="ontology-markdown">
            <ReactMarkdown>{ontologyText}</ReactMarkdown>
          </div>
        )
      )}
    </div>
  );
};

export default MemesDashboard; 