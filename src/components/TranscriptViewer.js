import React, { useState, useRef, useEffect, useCallback } from 'react';
import './TranscriptViewer.css';

function TranscriptViewer({ transcriptId, apiBase }) {
  const [lines, setLines] = useState([]);
  const [selectedLines, setSelectedLines] = useState(new Set());
  const [newSpeakerName, setNewSpeakerName] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [speakers, setSpeakers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState(null);
  const [stats, setStats] = useState(null);
  const containerRef = useRef(null);

  const perPage = 100;

  // Fetch lines
  const fetchLines = useCallback(async (pageNum = 1, search = '') => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: pageNum,
        per_page: perPage,
      });
      if (search) {
        params.append('search', search);
      }
      
      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/lines?${params}`);
      if (!response.ok) throw new Error('Failed to fetch lines');
      const data = await response.json();
      setLines(data.lines);
      setPagination(data.pagination);
    } catch (err) {
      console.error('Error fetching lines:', err);
    } finally {
      setLoading(false);
    }
  }, [transcriptId, apiBase]);

  // Fetch speakers
  const fetchSpeakers = useCallback(async () => {
    try {
      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/speakers`);
      if (!response.ok) throw new Error('Failed to fetch speakers');
      const data = await response.json();
      setSpeakers(data.speakers.map(s => s.name));
    } catch (err) {
      console.error('Error fetching speakers:', err);
    }
  }, [transcriptId, apiBase]);

  // Fetch stats
  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/stats`);
      if (!response.ok) throw new Error('Failed to fetch stats');
      const data = await response.json();
      setStats(data);
      setSpeakers(data.speakers.map(s => s.name));
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  }, [transcriptId, apiBase]);

  // Initial load
  useEffect(() => {
    fetchLines(1);
    fetchStats();
  }, [transcriptId, fetchLines, fetchStats]);

  // Search effect
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm) {
        fetchLines(1, searchTerm);
        setPage(1);
      } else {
        fetchLines(1);
        setPage(1);
      }
    }, 300); // Debounce search

    return () => clearTimeout(timer);
  }, [searchTerm, fetchLines]);

  const handleLineClick = (lineId, e) => {
    if (e.shiftKey && selectedLines.size > 0) {
      // Range selection - find line indices
      const lineIds = lines.map(l => l.id);
      const currentIndex = lineIds.indexOf(lineId);
      const selectedIndices = Array.from(selectedLines).map(id => lineIds.indexOf(id));
      const firstIndex = Math.min(...selectedIndices, currentIndex);
      const lastIndex = Math.max(...selectedIndices, currentIndex);
      
      const newSelection = new Set();
      for (let i = firstIndex; i <= lastIndex; i++) {
        if (lineIds[i]) newSelection.add(lineIds[i]);
      }
      setSelectedLines(newSelection);
    } else if (e.ctrlKey || e.metaKey) {
      // Multi-select
      const newSelection = new Set(selectedLines);
      if (newSelection.has(lineId)) {
        newSelection.delete(lineId);
      } else {
        newSelection.add(lineId);
      }
      setSelectedLines(newSelection);
    } else {
      // Single select
      setSelectedLines(new Set([lineId]));
    }
  };

  const handleSpeakerSelect = async (speaker) => {
    if (selectedLines.size === 0) return;
    
    const lineIds = Array.from(selectedLines);
    
    try {
      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/lines/bulk`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          line_ids: lineIds,
          speaker: speaker,
          tagged_by: 'web_user'
        })
      });
      
      if (!response.ok) throw new Error('Failed to update tags');
      
      // Refresh data
      await fetchLines(page, searchTerm);
      await fetchStats();
      setSelectedLines(new Set());
    } catch (err) {
      console.error('Error updating tags:', err);
      alert('Failed to update tags. Please try again.');
    }
  };

  const handleAddSpeaker = () => {
    if (newSpeakerName.trim() && !speakers.includes(newSpeakerName.trim())) {
      setSpeakers([...speakers, newSpeakerName.trim()]);
      setNewSpeakerName('');
    }
  };

  const handleRemoveSpeaker = (speaker) => {
    setSpeakers(speakers.filter(s => s !== speaker));
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
    fetchLines(newPage, searchTerm);
    containerRef.current?.scrollTo(0, 0);
  };

  return (
    <div className="transcript-viewer">
      <div className="viewer-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search transcript..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && pagination && (
            <span className="search-results">
              {pagination.total} results
            </span>
          )}
        </div>

        <div className="speaker-panel">
          <h3>Speakers ({speakers.length})</h3>
          <div className="speaker-list">
            {speakers.map(speaker => (
              <div key={speaker} className="speaker-item">
                <button
                  className="speaker-btn"
                  onClick={() => handleSpeakerSelect(speaker)}
                  disabled={selectedLines.size === 0}
                >
                  {speaker}
                </button>
                <button
                  className="remove-speaker-btn"
                  onClick={() => handleRemoveSpeaker(speaker)}
                  title="Remove speaker"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
          
          <div className="add-speaker">
            <input
              type="text"
              placeholder="Add new speaker..."
              value={newSpeakerName}
              onChange={(e) => setNewSpeakerName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddSpeaker()}
              className="new-speaker-input"
            />
            <button onClick={handleAddSpeaker} className="add-btn">
              Add
            </button>
          </div>
        </div>

        {selectedLines.size > 0 && (
          <div className="selection-info">
            {selectedLines.size} line(s) selected
            <button
              onClick={() => setSelectedLines(new Set())}
              className="clear-selection-btn"
            >
              Clear
            </button>
          </div>
        )}
      </div>

      {stats && (
        <div className="stats-bar">
          <span>Total: {stats.total_lines}</span>
          <span>Tagged: {stats.tagged_lines}</span>
          <span>Progress: {stats.progress}%</span>
        </div>
      )}

      {loading && (
        <div className="loading">Loading lines...</div>
      )}

      <div className="transcript-lines" ref={containerRef}>
        {lines.map((line) => {
          const isSelected = selectedLines.has(line.id);
          const hasSpeaker = !!line.speaker;

          return (
            <div
              key={line.id}
              className={`transcript-line ${isSelected ? 'selected' : ''} ${hasSpeaker ? 'tagged' : ''}`}
              onClick={(e) => handleLineClick(line.id, e)}
            >
              <div className="line-number">{line.line_number}</div>
              <div className="line-content">
                {line.speaker && (
                  <span className="speaker-badge">{line.speaker}</span>
                )}
                <span className="line-text">{line.text}</span>
              </div>
            </div>
          );
        })}
      </div>

      {pagination && pagination.pages > 1 && (
        <div className="pagination">
          <button
            onClick={() => handlePageChange(page - 1)}
            disabled={page === 1}
            className="page-btn"
          >
            Previous
          </button>
          <span className="page-info">
            Page {page} of {pagination.pages}
          </span>
          <button
            onClick={() => handlePageChange(page + 1)}
            disabled={page === pagination.pages}
            className="page-btn"
          >
            Next
          </button>
        </div>
      )}

      <div className="viewer-footer">
        <div className="instructions">
          <strong>Tips:</strong> Click to select • Shift+Click for range • Ctrl/Cmd+Click for multiple
        </div>
      </div>
    </div>
  );
}

export default TranscriptViewer;
