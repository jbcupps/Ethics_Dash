import React, { useEffect, useMemo, useState } from 'react';
import ethicalReviewApi from '../services/api';

const buildDefaultParties = (analysisContext) => {
  const originModel = analysisContext?.originModelUsed || 'origin_model';
  const analysisModel = analysisContext?.analysisModelUsed || 'analysis_model';
  return JSON.stringify([
    { id: 'requester', role: 'human' },
    { id: originModel, role: 'model' },
    { id: analysisModel, role: 'reviewer' },
  ], null, 2);
};

const buildDefaultHumanReadable = (analysisContext) => {
  const summary = analysisContext?.ethicalAnalysisText || '';
  const prompt = analysisContext?.prompt || '';
  return `Summary:\n${summary}\n\nPrompt:\n${prompt}`.trim();
};

const buildDefaultMachineReadable = (analysisContext) => {
  if (!analysisContext) {
    return JSON.stringify({
      ethical_scores: {},
      ai_welfare: {},
      alignment: {},
    }, null, 2);
  }
  return JSON.stringify({
    ethical_scores: analysisContext.ethicalScores || {},
    ai_welfare: analysisContext.aiWelfare || {},
    alignment: analysisContext.alignment || {},
  }, null, 2);
};

const AgreementBuilder = ({ analysisContext }) => {
  const [partiesInput, setPartiesInput] = useState(buildDefaultParties(analysisContext));
  const [humanReadableTerms, setHumanReadableTerms] = useState(buildDefaultHumanReadable(analysisContext));
  const [machineReadableTerms, setMachineReadableTerms] = useState(buildDefaultMachineReadable(analysisContext));
  const [termsTemplate, setTermsTemplate] = useState('alignment_summary');
  const [freeformNotes, setFreeformNotes] = useState('');
  const [statusMessage, setStatusMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [modelProvider, setModelProvider] = useState('');
  const [modelId, setModelId] = useState('');
  const [modelVersion, setModelVersion] = useState('');
  const [continuityWarning, setContinuityWarning] = useState(null);
  const [agreementContinuityWarning, setAgreementContinuityWarning] = useState(null);

  const [agreementIdInput, setAgreementIdInput] = useState('');
  const [currentAgreement, setCurrentAgreement] = useState(null);
  const [history, setHistory] = useState([]);

  const [actionType, setActionType] = useState('comment');
  const [actionActor, setActionActor] = useState('requester');
  const [actionPayload, setActionPayload] = useState('');
  const [counterTermsInput, setCounterTermsInput] = useState('');

  const analysisAvailable = useMemo(() => !!analysisContext?.prompt, [analysisContext]);

  useEffect(() => {
    if (analysisAvailable) {
      setPartiesInput(buildDefaultParties(analysisContext));
      setHumanReadableTerms(buildDefaultHumanReadable(analysisContext));
      setMachineReadableTerms(buildDefaultMachineReadable(analysisContext));
      const defaultMetadata = analysisContext?.analysisModelMetadata || analysisContext?.originModelMetadata || {};
      setModelProvider(defaultMetadata.model_provider || '');
      setModelId(defaultMetadata.model_id || '');
      setModelVersion(defaultMetadata.model_version || '');
    }
  }, [analysisAvailable, analysisContext]);

  useEffect(() => {
    if (!analysisAvailable) {
      return;
    }
    const warnings = [];
    const metadataPairs = [
      { label: 'Origin model', metadata: analysisContext?.originModelMetadata },
      { label: 'Analysis model', metadata: analysisContext?.analysisModelMetadata },
    ];

    metadataPairs.forEach(({ label, metadata }) => {
      if (!metadata?.model_id) {
        return;
      }
      const effectiveVersion = metadata.model_version || metadata.model_id;
      const key = `model_version:${metadata.model_provider || 'unknown'}:${metadata.model_id}`;
      const previousVersion = window.localStorage.getItem(key);
      if (previousVersion && previousVersion !== effectiveVersion) {
        warnings.push(`${label} updated from ${previousVersion} to ${effectiveVersion}.`);
      }
      if (effectiveVersion) {
        window.localStorage.setItem(key, effectiveVersion);
      }
    });

    setContinuityWarning(warnings.length ? warnings.join(' ') : null);
  }, [analysisAvailable, analysisContext]);

  useEffect(() => {
    if (!currentAgreement) {
      setAgreementContinuityWarning(null);
      return;
    }
    const currentMetadata = analysisContext?.analysisModelMetadata || analysisContext?.originModelMetadata || {};
    const agreementVersion = currentAgreement.model_version || currentAgreement.model_id;
    const currentVersion = currentMetadata.model_version || currentMetadata.model_id;
    if (agreementVersion && currentVersion && agreementVersion !== currentVersion) {
      setAgreementContinuityWarning(`Agreement model version (${agreementVersion}) differs from current model (${currentVersion}).`);
    } else {
      setAgreementContinuityWarning(null);
    }
  }, [currentAgreement, analysisContext]);

  const parseJsonField = (value, label) => {
    try {
      return JSON.parse(value);
    } catch (error) {
      throw new Error(`${label} must be valid JSON.`);
    }
  };

  const resetMessages = () => {
    setStatusMessage(null);
    setErrorMessage(null);
  };

  const handleCreateAgreement = async () => {
    resetMessages();
    try {
      const parties = parseJsonField(partiesInput, 'Parties');
      const machineReadable = parseJsonField(machineReadableTerms, 'Machine-readable terms');
      const terms = {
        template: termsTemplate,
        human_readable: humanReadableTerms,
        machine_readable: machineReadable,
        notes: freeformNotes,
      };
      const payload = {
        parties,
        terms,
        status: 'proposed',
        model_provider: modelProvider || null,
        model_id: modelId || null,
        model_version: modelVersion || null,
        needs_reaffirmation: false,
      };
      const response = await ethicalReviewApi.createAgreement(payload);
      setCurrentAgreement(response.agreement);
      setAgreementIdInput(response.agreement.id);
      setHistory([response.action]);
      setStatusMessage('Agreement proposal created.');
    } catch (error) {
      setErrorMessage(error.message || 'Failed to create agreement.');
    }
  };

  const handleLoadAgreement = async () => {
    resetMessages();
    try {
      const [agreementResponse, historyResponse] = await Promise.all([
        ethicalReviewApi.getAgreement(agreementIdInput),
        ethicalReviewApi.getAgreementHistory(agreementIdInput),
      ]);
      setCurrentAgreement(agreementResponse.agreement);
      setHistory(historyResponse.history || []);
      setStatusMessage('Agreement loaded.');
    } catch (error) {
      setErrorMessage(error.message || 'Failed to load agreement.');
    }
  };

  const handleActionSubmit = async () => {
    resetMessages();
    if (!currentAgreement?.id) {
      setErrorMessage('Load or create an agreement before taking an action.');
      return;
    }

    try {
      let payload = undefined;
      if (actionType === 'comment') {
        payload = actionPayload ? { message: actionPayload } : {};
      } else if (actionType === 'counter') {
        payload = { terms: parseJsonField(counterTermsInput || '{}', 'Counter terms') };
      } else if (actionType === 'reaffirm') {
        payload = actionPayload ? { message: actionPayload } : {};
      } else if (actionPayload) {
        payload = { message: actionPayload };
      }

      const currentModelMetadata = {
        model_provider: modelProvider || null,
        model_id: modelId || null,
        model_version: modelVersion || null,
      };
      payload = payload || {};
      payload.model_metadata = currentModelMetadata;

      const response = await ethicalReviewApi.addAgreementAction(currentAgreement.id, {
        action: actionType,
        payload,
        actor_party_id: actionActor,
      });

      const nextAgreement = response.counter_agreement || response.agreement;
      setCurrentAgreement(nextAgreement);
      const updatedHistory = await ethicalReviewApi.getAgreementHistory(nextAgreement.id);
      setHistory(updatedHistory.history || []);
      setAgreementIdInput(nextAgreement.id);
      setStatusMessage(`Action '${actionType}' recorded.`);
    } catch (error) {
      setErrorMessage(error.message || 'Failed to update agreement.');
    }
  };

  const handleFlagReaffirmation = async () => {
    resetMessages();
    if (!currentAgreement?.id) {
      setErrorMessage('Load or create an agreement before flagging reaffirmation.');
      return;
    }

    try {
      const response = await ethicalReviewApi.addAgreementAction(currentAgreement.id, {
        action: 'comment',
        payload: {
          message: 'Model version changed; reaffirmation requested.',
          model_metadata: {
            model_provider: modelProvider || null,
            model_id: modelId || null,
            model_version: modelVersion || null,
          },
        },
        actor_party_id: actionActor,
      });
      setCurrentAgreement(response.agreement);
      const updatedHistory = await ethicalReviewApi.getAgreementHistory(response.agreement.id);
      setHistory(updatedHistory.history || []);
      setAgreementIdInput(response.agreement.id);
      setStatusMessage('Reaffirmation flag recorded.');
    } catch (error) {
      setErrorMessage(error.message || 'Failed to flag reaffirmation.');
    }
  };

  const handleLoadLatestAnalysis = () => {
    if (!analysisAvailable) {
      return;
    }
    setPartiesInput(buildDefaultParties(analysisContext));
    setHumanReadableTerms(buildDefaultHumanReadable(analysisContext));
    setMachineReadableTerms(buildDefaultMachineReadable(analysisContext));
    const defaultMetadata = analysisContext?.analysisModelMetadata || analysisContext?.originModelMetadata || {};
    setModelProvider(defaultMetadata.model_provider || '');
    setModelId(defaultMetadata.model_id || '');
    setModelVersion(defaultMetadata.model_version || '');
    setStatusMessage('Loaded latest analysis into the proposal builder.');
  };

  return (
    <div className="agreement-builder">
      <h1>Agreement Builder</h1>
      <p className="agreement-intro">
        Create, propose, and negotiate voluntary agreements based on analysis results.
      </p>

      {statusMessage && <div className="alert alert-success">{statusMessage}</div>}
      {errorMessage && <div className="alert alert-error">{errorMessage}</div>}
      {continuityWarning && (
        <div className="alert alert-warning">
          <strong>Continuity warning:</strong> {continuityWarning}
        </div>
      )}

      <section className="card agreement-section">
        <div className="section-header">
          <h2>Create Proposal</h2>
          <button className="button button-secondary" onClick={handleLoadLatestAnalysis} disabled={!analysisAvailable}>
            Load Latest Analysis
          </button>
        </div>

        <div className="form-group">
          <label htmlFor="parties">Parties (JSON)</label>
          <textarea
            id="parties"
            value={partiesInput}
            onChange={(event) => setPartiesInput(event.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="template">Terms Template</label>
          <select id="template" value={termsTemplate} onChange={(event) => setTermsTemplate(event.target.value)}>
            <option value="alignment_summary">Alignment Summary</option>
            <option value="safety_commitments">Safety Commitments</option>
            <option value="custom">Custom</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="human">Human-Readable Terms</label>
          <textarea
            id="human"
            value={humanReadableTerms}
            onChange={(event) => setHumanReadableTerms(event.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="machine">Machine-Readable Terms (JSON)</label>
          <textarea
            id="machine"
            value={machineReadableTerms}
            onChange={(event) => setMachineReadableTerms(event.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="notes">Freeform Notes</label>
          <textarea
            id="notes"
            value={freeformNotes}
            onChange={(event) => setFreeformNotes(event.target.value)}
          />
        </div>

        <div className="agreement-row">
          <div className="form-group">
            <label htmlFor="modelProvider">Model Provider</label>
            <input
              id="modelProvider"
              type="text"
              value={modelProvider}
              onChange={(event) => setModelProvider(event.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="modelId">Model ID (Snapshot)</label>
            <input
              id="modelId"
              type="text"
              value={modelId}
              onChange={(event) => setModelId(event.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="modelVersion">Model Version</label>
            <input
              id="modelVersion"
              type="text"
              value={modelVersion}
              onChange={(event) => setModelVersion(event.target.value)}
            />
          </div>
        </div>

        <button className="button" onClick={handleCreateAgreement}>
          Create Proposal
        </button>
      </section>

      <section className="card agreement-section">
        <h2>Agreement Status</h2>
        <div className="agreement-row">
          <input
            type="text"
            placeholder="Agreement ID"
            value={agreementIdInput}
            onChange={(event) => setAgreementIdInput(event.target.value)}
          />
          <button className="button button-secondary" onClick={handleLoadAgreement}>
            Load
          </button>
        </div>

        {currentAgreement ? (
          <div className="agreement-status">
            <p><strong>ID:</strong> {currentAgreement.id}</p>
            <p><strong>Status:</strong> {currentAgreement.status}</p>
            <p><strong>Updated:</strong> {currentAgreement.updated_at}</p>
            <p><strong>Model Provider:</strong> {currentAgreement.model_provider || 'N/A'}</p>
            <p><strong>Model ID:</strong> {currentAgreement.model_id || 'N/A'}</p>
            <p><strong>Model Version:</strong> {currentAgreement.model_version || 'N/A'}</p>
            <p><strong>Needs Reaffirmation:</strong> {currentAgreement.needs_reaffirmation ? 'Yes' : 'No'}</p>
          </div>
        ) : (
          <p><em>No agreement loaded yet.</em></p>
        )}
      </section>

      {(agreementContinuityWarning || currentAgreement?.needs_reaffirmation) && (
        <section className="card agreement-section">
          <h2>Agreement Continuity</h2>
          {agreementContinuityWarning && (
            <div className="alert alert-warning">
              {agreementContinuityWarning}
            </div>
          )}
          {currentAgreement?.needs_reaffirmation && (
            <p><strong>This agreement is marked as needing reaffirmation.</strong></p>
          )}
          <div className="agreement-row">
            <button className="button button-secondary" onClick={handleFlagReaffirmation}>
              Flag for Reaffirmation
            </button>
            <button className="button" onClick={() => setActionType('reaffirm')}>
              Reaffirm Agreement
            </button>
          </div>
        </section>
      )}

      <section className="card agreement-section">
        <h2>Actions</h2>
        <div className="agreement-row">
          <div className="form-group">
            <label htmlFor="actionType">Action</label>
            <select id="actionType" value={actionType} onChange={(event) => setActionType(event.target.value)}>
              <option value="comment">Comment</option>
              <option value="accept">Accept</option>
              <option value="decline">Decline</option>
              <option value="counter">Counter</option>
              <option value="reaffirm">Reaffirm</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="actor">Actor Party ID</label>
            <input
              id="actor"
              type="text"
              value={actionActor}
              onChange={(event) => setActionActor(event.target.value)}
            />
          </div>
        </div>

        {actionType === 'counter' ? (
          <div className="form-group">
            <label htmlFor="counterTerms">Counter Terms (JSON)</label>
            <textarea
              id="counterTerms"
              value={counterTermsInput}
              onChange={(event) => setCounterTermsInput(event.target.value)}
              placeholder='{"human_readable": "...", "machine_readable": {}}'
            />
          </div>
        ) : (
          <div className="form-group">
            <label htmlFor="payload">Action Notes</label>
            <textarea
              id="payload"
              value={actionPayload}
              onChange={(event) => setActionPayload(event.target.value)}
              placeholder="Optional notes..."
            />
          </div>
        )}

        <button className="button" onClick={handleActionSubmit}>
          Submit Action
        </button>
      </section>

      <section className="card agreement-section">
        <h2>History</h2>
        {history.length ? (
          <ul className="agreement-history">
            {history.map((entry) => (
              <li key={entry.id}>
                <div className="history-row">
                  <span className="history-action">{entry.action}</span>
                  <span className="history-meta">{entry.timestamp}</span>
                </div>
                <div className="history-meta">
                  Actor: {entry.actor_party_id}
                </div>
                {entry.payload && (
                  <pre>{JSON.stringify(entry.payload, null, 2)}</pre>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p><em>No actions yet.</em></p>
        )}
      </section>
    </div>
  );
};

export default AgreementBuilder;
