import React from 'react';
import './TranscriptSelector.css';

function TranscriptSelector({ transcripts, loading, onSelect, onRefresh }) {
  return (
    <div className="transcript-selector">
      <div className="selector-header">
        <h2>Select Transcript to Tag</h2>
        <button onClick={onRefresh} className="refresh-btn" disabled={loading}>
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {loading && (
        <div className="loading">Loading transcripts...</div>
      )}

      {!loading && transcripts.length === 0 && (
        <div className="empty-state">
          <p>No transcripts found in database.</p>
          <p>Please load transcripts using the load script.</p>
        </div>
      )}

      {!loading && transcripts.length > 0 && (
        <div className="transcript-list">
          {transcripts.map(transcript => (
            <div
              key={transcript.id}
              className="transcript-card"
              onClick={() => onSelect(transcript.id)}
            >
              <div className="card-header">
                <h3>{transcript.filename}</h3>
                {transcript.date && (
                  <span className="date-badge">
                    {new Date(transcript.date).toLocaleDateString()}
                  </span>
                )}
              </div>
              <div className="card-stats">
                <div className="stat">
                  <span className="stat-label">Total Lines:</span>
                  <span className="stat-value">{transcript.total_lines}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Tagged:</span>
                  <span className="stat-value">{transcript.tagged_lines || 0}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Progress:</span>
                  <span className="stat-value">
                    {transcript.total_lines > 0
                      ? Math.round(((transcript.tagged_lines || 0) / transcript.total_lines) * 100)
                      : 0}%
                  </span>
                </div>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{
                    width: `${transcript.total_lines > 0
                      ? ((transcript.tagged_lines || 0) / transcript.total_lines) * 100
                      : 0}%`
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TranscriptSelector;

