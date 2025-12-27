import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import TranscriptSelector from './components/TranscriptSelector';
import TranscriptViewer from './components/TranscriptViewer';
import TaggedView from './components/TaggedView';
import ExportPanel from './components/ExportPanel';

const API_BASE = process.env.REACT_APP_API_URL || '/api';

function App() {
  const [transcripts, setTranscripts] = useState([]);
  const [selectedTranscript, setSelectedTranscript] = useState(null);
  const [currentView, setCurrentView] = useState('select'); // 'select', 'tagging', 'tagged'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch transcripts list
  useEffect(() => {
    fetchTranscripts();
  }, []);

  const fetchTranscripts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/transcripts`);
      if (!response.ok) throw new Error('Failed to fetch transcripts');
      const data = await response.json();
      setTranscripts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTranscriptSelect = useCallback((transcriptId) => {
    setSelectedTranscript(transcriptId);
    setCurrentView('tagging');
  }, []);

  const handleViewChange = useCallback((view) => {
    setCurrentView(view);
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Transcript Speaker Tagger</h1>
        <nav className="nav-tabs">
          <button
            className={currentView === 'select' ? 'active' : ''}
            onClick={() => handleViewChange('select')}
          >
            Select Transcript
          </button>
          {selectedTranscript && (
            <>
              <button
                className={currentView === 'tagging' ? 'active' : ''}
                onClick={() => handleViewChange('tagging')}
              >
                Tagging
              </button>
              <button
                className={currentView === 'tagged' ? 'active' : ''}
                onClick={() => handleViewChange('tagged')}
              >
                Tagged View
              </button>
            </>
          )}
        </nav>
      </header>

      <main className="App-main">
        {error && (
          <div className="error-message">
            Error: {error}
          </div>
        )}

        {currentView === 'select' && (
          <TranscriptSelector
            transcripts={transcripts}
            loading={loading}
            onSelect={handleTranscriptSelect}
            onRefresh={fetchTranscripts}
          />
        )}

        {currentView === 'tagging' && selectedTranscript && (
          <TranscriptViewer
            transcriptId={selectedTranscript}
            apiBase={API_BASE}
          />
        )}

        {currentView === 'tagged' && selectedTranscript && (
          <>
            <TaggedView
              transcriptId={selectedTranscript}
              apiBase={API_BASE}
            />
            <ExportPanel
              transcriptId={selectedTranscript}
              apiBase={API_BASE}
            />
          </>
        )}
      </main>
    </div>
  );
}

export default App;
