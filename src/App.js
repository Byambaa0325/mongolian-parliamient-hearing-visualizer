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
      setError(null);
      
      // First, try health check to verify backend is accessible
      try {
        const healthResponse = await fetch(`${API_BASE}/health`);
        if (!healthResponse.ok) {
          console.warn('Health check failed, but continuing...');
        }
      } catch (e) {
        console.warn('Health check failed:', e);
      }
      
      const response = await fetch(`${API_BASE}/transcripts`);
      
      if (!response.ok) {
        // Try to get error message from response
        let errorMessage = `Failed to fetch transcripts: ${response.status} ${response.statusText}`;
        let errorDetails = '';
        try {
          const errorData = await response.json();
          if (errorData.error) {
            errorMessage = errorData.error;
          }
          if (errorData.traceback) {
            errorDetails = errorData.traceback;
            console.error('Backend traceback:', errorDetails);
          }
        } catch (e) {
          // Response is not JSON, try to get text
          try {
            const text = await response.text();
            errorDetails = text.substring(0, 500);
            console.error('Backend error response:', errorDetails);
          } catch (e2) {
            // Can't read response
          }
        }
        throw new Error(errorMessage);
      }
      
      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        throw new Error(`Backend returned non-JSON response. Make sure Flask server is running on port 8080. Response: ${text.substring(0, 100)}`);
      }
      
      const data = await response.json();
      setTranscripts(data);
    } catch (err) {
      console.error('Error fetching transcripts:', err);
      setError(err.message || 'Failed to connect to backend server. Make sure the Flask server is running on port 8080.');
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
