import React, { useState, useRef, useEffect, useCallback } from 'react';
import './TranscriptViewer.css';

// Generate consistent colors for speakers
const SPEAKER_COLORS = [
  { bg: '#E3F2FD', border: '#1976D2', text: '#0D47A1' },  // Blue
  { bg: '#FCE4EC', border: '#C2185B', text: '#880E4F' },  // Pink
  { bg: '#E8F5E9', border: '#388E3C', text: '#1B5E20' },  // Green
  { bg: '#FFF3E0', border: '#F57C00', text: '#E65100' },  // Orange
  { bg: '#F3E5F5', border: '#7B1FA2', text: '#4A148C' },  // Purple
  { bg: '#E0F7FA', border: '#0097A7', text: '#006064' },  // Cyan
  { bg: '#FFFDE7', border: '#FBC02D', text: '#F57F17' },  // Yellow
  { bg: '#FFEBEE', border: '#D32F2F', text: '#B71C1C' },  // Red
  { bg: '#E8EAF6', border: '#303F9F', text: '#1A237E' },  // Indigo
  { bg: '#F1F8E9', border: '#689F38', text: '#33691E' },  // Light Green
  { bg: '#FBE9E7', border: '#E64A19', text: '#BF360C' },  // Deep Orange
  { bg: '#E1F5FE', border: '#0288D1', text: '#01579B' },  // Light Blue
];

function getSpeakerColor(speaker, speakerList) {
  if (!speaker) return null;
  const index = speakerList.indexOf(speaker);
  if (index === -1) {
    // Hash the speaker name to get a consistent color
    let hash = 0;
    for (let i = 0; i < speaker.length; i++) {
      hash = speaker.charCodeAt(i) + ((hash << 5) - hash);
    }
    return SPEAKER_COLORS[Math.abs(hash) % SPEAKER_COLORS.length];
  }
  return SPEAKER_COLORS[index % SPEAKER_COLORS.length];
}

// Selection-based Split Editor - Select text to extract as separate line
function SplitEditor({ text, onSplit, onCancel }) {
  const [segments, setSegments] = useState([{ text, isNew: false }]);
  const [selectedSegmentIndex, setSelectedSegmentIndex] = useState(null);
  const textRef = useRef(null);

  // Handle text selection within a segment
  const handleMouseUp = (segmentIndex) => {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) return;
    
    const selectedText = selection.toString().trim();
    if (!selectedText) return;
    
    // Get selection range relative to the segment
    const range = selection.getRangeAt(0);
    const segmentElement = document.getElementById(`segment-${segmentIndex}`);
    if (!segmentElement) return;
    
    // Calculate positions
    const preCaretRange = range.cloneRange();
    preCaretRange.selectNodeContents(segmentElement);
    preCaretRange.setEnd(range.startContainer, range.startOffset);
    const start = preCaretRange.toString().length;
    const end = start + selectedText.length;
    
    const segment = segments[segmentIndex];
    const before = segment.text.substring(0, start).trim();
    const selected = segment.text.substring(start, end).trim();
    const after = segment.text.substring(end).trim();
    
    if (!selected) return;
    
    // Create new segments array
    const newSegments = [...segments];
    newSegments.splice(segmentIndex, 1);
    
    const insertIndex = segmentIndex;
    const toInsert = [];
    
    if (before) toInsert.push({ text: before, isNew: true });
    toInsert.push({ text: selected, isNew: true, isSelected: true });
    if (after) toInsert.push({ text: after, isNew: true });
    
    newSegments.splice(insertIndex, 0, ...toInsert);
    setSegments(newSegments);
    
    // Clear selection
    selection.removeAllRanges();
  };

  // Auto-detect speaker patterns and split
  const autoDetectSplitPoints = () => {
    const patterns = [
      /За\.\s*[А-ЯЁ]/g,
      /\d+\s+номерын\s+микрофон/g,
      /За\s+\d+\s+номер/g,
      /(?<=[.?!])\s+За\s+/g,
    ];
    
    let fullText = segments.map(s => s.text).join(' ');
    const splitPoints = [0];
    
    patterns.forEach(pattern => {
      let match;
      const regex = new RegExp(pattern);
      while ((match = regex.exec(fullText)) !== null) {
        if (match.index > 30) {
          splitPoints.push(match.index);
        }
      }
    });
    
    splitPoints.push(fullText.length);
    const uniquePoints = [...new Set(splitPoints)].sort((a, b) => a - b);
    
    const newSegments = [];
    for (let i = 0; i < uniquePoints.length - 1; i++) {
      const segText = fullText.substring(uniquePoints[i], uniquePoints[i + 1]).trim();
      if (segText) {
        newSegments.push({ text: segText, isNew: true });
      }
    }
    
    if (newSegments.length > 0) {
      setSegments(newSegments);
    }
  };

  // Merge segment with previous
  const mergeWithPrevious = (index) => {
    if (index <= 0) return;
    const newSegments = [...segments];
    newSegments[index - 1].text = newSegments[index - 1].text + ' ' + newSegments[index].text;
    newSegments[index - 1].isNew = true;
    newSegments.splice(index, 1);
    setSegments(newSegments);
  };

  // Merge segment with next
  const mergeWithNext = (index) => {
    if (index >= segments.length - 1) return;
    const newSegments = [...segments];
    newSegments[index].text = newSegments[index].text + ' ' + newSegments[index + 1].text;
    newSegments[index].isNew = true;
    newSegments.splice(index + 1, 1);
    setSegments(newSegments);
  };

  // Delete a segment
  const deleteSegment = (index) => {
    if (segments.length <= 1) return;
    const newSegments = segments.filter((_, i) => i !== index);
    setSegments(newSegments);
  };

  // Reset to original
  const resetSegments = () => {
    setSegments([{ text, isNew: false }]);
  };

  // Build split positions from segments
  const getSplitPositions = () => {
    const positions = [];
    let currentPos = 0;
    
    for (let i = 0; i < segments.length - 1; i++) {
      currentPos += segments[i].text.length;
      positions.push(currentPos);
    }
    
    return positions;
  };

  // Get final segments for preview
  const getPreviewSegments = () => {
    return segments.map(s => s.text).filter(t => t.trim());
  };

  const finalSegments = getPreviewSegments();

  return (
    <div className="split-editor">
      <div className="split-toolbar">
        <button onClick={autoDetectSplitPoints} className="auto-detect-btn">
          🔍 Auto-Detect Speakers
        </button>
        <button onClick={resetSegments} className="clear-splits-btn">
          ↺ Reset
        </button>
        <span className="split-hint">
          💡 Select text with mouse to extract as separate line
        </span>
      </div>
      
      <div className="segments-editor" ref={textRef}>
        {segments.map((segment, idx) => (
          <div 
            key={idx} 
            className={`editable-segment ${segment.isNew ? 'new-segment' : ''} ${segment.isSelected ? 'selected-segment' : ''}`}
          >
            <div className="segment-header">
              <span className="segment-badge">Line {idx + 1}</span>
              <div className="segment-actions">
                {idx > 0 && (
                  <button 
                    onClick={() => mergeWithPrevious(idx)} 
                    className="segment-action-btn"
                    title="Merge with previous"
                  >
                    ⬆️ Merge Up
                  </button>
                )}
                {idx < segments.length - 1 && (
                  <button 
                    onClick={() => mergeWithNext(idx)} 
                    className="segment-action-btn"
                    title="Merge with next"
                  >
                    ⬇️ Merge Down
                  </button>
                )}
                {segments.length > 1 && (
                  <button 
                    onClick={() => deleteSegment(idx)} 
                    className="segment-action-btn delete-btn"
                    title="Delete segment"
                  >
                    🗑️
                  </button>
                )}
              </div>
            </div>
            <div 
              id={`segment-${idx}`}
              className="segment-text-editable"
              onMouseUp={() => handleMouseUp(idx)}
            >
              {segment.text}
            </div>
          </div>
        ))}
      </div>
      
      <div className="split-summary">
        <div className="summary-info">
          <span className="summary-count">{finalSegments.length}</span> lines will be created
        </div>
      </div>
      
      <div className="split-actions">
        <button 
          onClick={() => onSplit(getSplitPositions())}
          disabled={segments.length <= 1}
          className="confirm-split-btn"
        >
          ✓ Split into {finalSegments.length} Lines
        </button>
        <button onClick={onCancel} className="cancel-split-btn">
          Cancel
        </button>
      </div>
    </div>
  );
}

function TranscriptViewer({ transcriptId, apiBase }) {
  const [lines, setLines] = useState([]);
  const [selectedLines, setSelectedLines] = useState(new Set());
  const [activeLine, setActiveLine] = useState(null); // Single active line for keyboard actions
  const [expandedLines, setExpandedLines] = useState(new Set()); // Lines with expanded text
  const [newSpeakerName, setNewSpeakerName] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [speakers, setSpeakers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState(null);
  const [stats, setStats] = useState(null);
  const [mlDetecting, setMlDetecting] = useState(false);
  const [mlResults, setMlResults] = useState([]);
  const [showMlPanel, setShowMlPanel] = useState(false);
  const [splitMode, setSplitMode] = useState(false);
  const [splitLineId, setSplitLineId] = useState(null);
  const [splitText, setSplitText] = useState('');
  const [editingSpeaker, setEditingSpeaker] = useState(null); // { lineId, value }
  const containerRef = useRef(null);
  const lineRefs = useRef({});
  const speakerInputRef = useRef(null);

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

  // Set first line as active when lines load
  useEffect(() => {
    if (lines.length > 0 && !activeLine) {
      setActiveLine(lines[0].id);
    }
  }, [lines, activeLine]);

  // Keyboard navigation and shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Skip if user is typing in an input
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || splitMode) {
        return;
      }

      const lineIds = lines.map(l => l.id);
      const currentIndex = activeLine ? lineIds.indexOf(activeLine) : -1;

      switch (e.key) {
        case 'ArrowUp':
        case 'k': // vim-style
          e.preventDefault();
          if (currentIndex > 0) {
            const newActiveId = lineIds[currentIndex - 1];
            setActiveLine(newActiveId);
            lineRefs.current[newActiveId]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
          break;
        case 'ArrowDown':
        case 'j': // vim-style
          e.preventDefault();
          if (currentIndex < lineIds.length - 1) {
            const newActiveId = lineIds[currentIndex + 1];
            setActiveLine(newActiveId);
            lineRefs.current[newActiveId]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
          break;
        case 's':
        case 'S':
          e.preventDefault();
          if (activeLine) {
            const line = lines.find(l => l.id === activeLine);
            if (line) handleEnterSplitMode(activeLine, line.text);
          }
          break;
        case 'm':
        case 'M':
          e.preventDefault();
          if (activeLine) handleMergeLine(activeLine);
          break;
        case 'c':
        case 'C':
          e.preventDefault();
          if (activeLine) handleClearSpeaker(activeLine);
          break;
        case 'e':
        case 'E':
          e.preventDefault();
          if (activeLine) toggleExpand(activeLine);
          break;
        case ' ': // Space to select/deselect
          e.preventDefault();
          if (activeLine) {
            const newSelection = new Set(selectedLines);
            if (newSelection.has(activeLine)) {
              newSelection.delete(activeLine);
            } else {
              newSelection.add(activeLine);
            }
            setSelectedLines(newSelection);
          }
          break;
        case 'Escape':
          setSelectedLines(new Set());
          break;
        default:
          // Number keys 1-9 to assign speaker
          if (e.key >= '1' && e.key <= '9') {
            const speakerIndex = parseInt(e.key) - 1;
            if (speakers[speakerIndex] && activeLine) {
              handleSpeakerSelect(speakers[speakerIndex]);
            }
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [lines, activeLine, selectedLines, speakers, splitMode]);

  // Toggle line expand/collapse
  const toggleExpand = (lineId) => {
    const newExpanded = new Set(expandedLines);
    if (newExpanded.has(lineId)) {
      newExpanded.delete(lineId);
    } else {
      newExpanded.add(lineId);
    }
    setExpandedLines(newExpanded);
  };

  // Clear speaker from a line
  const handleClearSpeaker = async (lineId) => {
    try {
      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/lines/${lineId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ speaker: null })
      });
      
      if (!response.ok) throw new Error('Failed to clear speaker');
      
      await fetchLines(page, searchTerm);
      await fetchStats();
    } catch (err) {
      console.error('Error clearing speaker:', err);
      alert('Failed to clear speaker');
    }
  };

  // Start editing speaker name inline
  const startEditingSpeaker = (lineId, currentSpeaker, e) => {
    e.stopPropagation();
    setEditingSpeaker({ lineId, value: currentSpeaker || '' });
    // Focus the input after render
    setTimeout(() => speakerInputRef.current?.focus(), 0);
  };

  // Save edited speaker name
  const saveEditedSpeaker = async () => {
    if (!editingSpeaker) return;
    
    const { lineId, value } = editingSpeaker;
    const trimmedValue = value.trim();
    
    try {
      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/lines/${lineId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ speaker: trimmedValue || null })
      });
      
      if (!response.ok) throw new Error('Failed to update speaker');
      
      // Add to speakers list if new
      if (trimmedValue && !speakers.includes(trimmedValue)) {
        setSpeakers([...speakers, trimmedValue]);
      }
      
      await fetchLines(page, searchTerm);
      await fetchStats();
    } catch (err) {
      console.error('Error updating speaker:', err);
      alert('Failed to update speaker');
    } finally {
      setEditingSpeaker(null);
    }
  };

  // Cancel editing
  const cancelEditingSpeaker = () => {
    setEditingSpeaker(null);
  };

  // Handle speaker input key events
  const handleSpeakerInputKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      saveEditedSpeaker();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      cancelEditingSpeaker();
    }
  };

  const handleLineClick = (lineId, e) => {
    // Always set as active line
    setActiveLine(lineId);
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

  // ML Speaker Detection
  const handleMLDetection = async (autoTag = false) => {
    try {
      setMlDetecting(true);
      const lineIds = selectedLines.size > 0 ? Array.from(selectedLines) : null;
      
      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/detect-speakers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          line_ids: lineIds,
          auto_tag: autoTag
        })
      });
      
      if (!response.ok) throw new Error('ML detection failed');
      const data = await response.json();
      
      setMlResults(data.results);
      setShowMlPanel(true);
      
      if (autoTag && data.updates_made > 0) {
        await fetchLines(page, searchTerm);
        await fetchStats();
        setSelectedLines(new Set());
      }
      
    } catch (err) {
      console.error('Error in ML detection:', err);
      alert('ML detection failed: ' + err.message);
    } finally {
      setMlDetecting(false);
    }
  };

  const applyMLDetection = async (lineId, speaker) => {
    try {
      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/lines/${lineId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ speaker })
      });
      
      if (!response.ok) throw new Error('Failed to apply detection');
      
      await fetchLines(page, searchTerm);
      await fetchStats();
      
      // Remove from results
      setMlResults(mlResults.filter(r => r.line_id !== lineId));
      
    } catch (err) {
      console.error('Error applying ML detection:', err);
      alert('Failed to apply detection');
    }
  };

  // Line Splitting
  const handleEnterSplitMode = (lineId, text) => {
    setSplitMode(true);
    setSplitLineId(lineId);
    setSplitText(text);
  };

  const handleSplitLine = async (positions) => {
    try {
      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/lines/${splitLineId}/split`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ split_positions: positions })
      });
      
      if (!response.ok) throw new Error('Split failed');
      
      await fetchLines(page, searchTerm);
      await fetchStats();
      setSplitMode(false);
      setSplitLineId(null);
      
    } catch (err) {
      console.error('Error splitting line:', err);
      alert('Failed to split line: ' + err.message);
    }
  };

  const handleMergeLine = async (lineId) => {
    if (!window.confirm('Merge this line with the next line?')) return;
    
    try {
      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/lines/${lineId}/merge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) throw new Error('Merge failed');
      
      await fetchLines(page, searchTerm);
      await fetchStats();
      
    } catch (err) {
      console.error('Error merging line:', err);
      alert('Failed to merge line: ' + err.message);
    }
  };

  // Get active line object
  const activeLineObj = lines.find(l => l.id === activeLine);

  return (
    <div className="transcript-viewer">
      {/* Top Controls Bar */}
      <div className="top-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search transcript..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && pagination && (
            <span className="search-results">{pagination.total} results</span>
          )}
        </div>
        
        {stats && (
          <div className="stats-inline">
            <span>📄 {stats.total_lines}</span>
            <span>✅ {stats.tagged_lines}</span>
            <span>📊 {stats.progress}%</span>
          </div>
        )}

        {selectedLines.size > 0 && (
          <div className="selection-info">
            {selectedLines.size} selected
            <button onClick={() => setSelectedLines(new Set())} className="clear-selection-btn">
              Clear
            </button>
          </div>
        )}
      </div>

      {/* Main Layout with Floating Panels */}
      <div className="main-layout">
        
        {/* Floating Speaker Panel - Left */}
        <div className="floating-panel floating-speakers">
          <h3>👥 Speakers</h3>
          <div className="speaker-list">
            {speakers.slice(0, 15).map((speaker, index) => {
              const color = SPEAKER_COLORS[index % SPEAKER_COLORS.length];
              return (
                <button
                  key={speaker}
                  className="speaker-btn-float"
                  onClick={() => handleSpeakerSelect(speaker)}
                  disabled={selectedLines.size === 0 && !activeLine}
                  style={{
                    backgroundColor: color.bg,
                    borderLeftColor: color.border,
                    color: color.text,
                  }}
                  title={`Press ${index + 1} to assign`}
                >
                  <span className="speaker-key">{index + 1}</span>
                  <span className="speaker-name-text">{speaker}</span>
                </button>
              );
            })}
          </div>
          {speakers.length > 15 && (
            <div className="more-speakers">+{speakers.length - 15} more</div>
          )}
          <div className="add-speaker-compact">
            <input
              type="text"
              placeholder="New speaker..."
              value={newSpeakerName}
              onChange={(e) => setNewSpeakerName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddSpeaker()}
            />
            <button onClick={handleAddSpeaker}>+</button>
          </div>
        </div>

        {/* Floating Action Panel - Right */}
        <div className="floating-panel floating-actions">
          <h3>⚡ Actions</h3>
          
          <div className="action-group">
            <div className="action-label">Line Controls</div>
            <button
              className="action-btn"
              onClick={() => activeLine && activeLineObj && handleEnterSplitMode(activeLine, activeLineObj.text)}
              disabled={!activeLine}
              title="Split this line into multiple lines"
            >
              ✂️ Split <kbd>S</kbd>
            </button>
            <button
              className="action-btn"
              onClick={() => activeLine && handleMergeLine(activeLine)}
              disabled={!activeLine}
              title="Merge with next line"
            >
              🔗 Merge <kbd>M</kbd>
            </button>
            <button
              className="action-btn"
              onClick={() => activeLine && toggleExpand(activeLine)}
              disabled={!activeLine}
              title="Expand or collapse line text"
            >
              {activeLine && expandedLines.has(activeLine) ? '📕 Shrink' : '📖 Expand'} <kbd>E</kbd>
            </button>
            <button
              className="action-btn clear-btn"
              onClick={() => activeLine && handleClearSpeaker(activeLine)}
              disabled={!activeLine || !activeLineObj?.speaker}
              title="Clear the speaker tag from this line"
            >
              🚫 Clear Tag <kbd>C</kbd>
            </button>
          </div>

          <div className="action-group">
            <div className="action-label">Navigation</div>
            <div className="nav-keys">
              <span><kbd>↑</kbd> / <kbd>K</kbd> Up</span>
              <span><kbd>↓</kbd> / <kbd>J</kbd> Down</span>
              <span><kbd>Space</kbd> Select</span>
              <span><kbd>Esc</kbd> Deselect</span>
            </div>
          </div>

          <div className="action-group">
            <div className="action-label">ML Detection</div>
            <button
              className="action-btn ml-action"
              onClick={() => handleMLDetection(false)}
              disabled={mlDetecting}
            >
              🔍 Detect
            </button>
            <button
              className="action-btn ml-action"
              onClick={() => handleMLDetection(true)}
              disabled={mlDetecting}
            >
              🤖 Auto-Tag
            </button>
          </div>

          {activeLine && (
            <div className="active-line-info">
              <div className="info-label">Active Line</div>
              <div className="info-value">#{lines.find(l => l.id === activeLine)?.line_number || '?'}</div>
              {activeLineObj?.speaker && (
                <div className="info-speaker">{activeLineObj.speaker}</div>
              )}
            </div>
          )}
        </div>

        {/* Center Content Area */}
        <div className="content-area">
          {loading && <div className="loading">Loading lines...</div>}

          <div className="transcript-lines" ref={containerRef}>
            {lines.map((line, index) => {
              const isSelected = selectedLines.has(line.id);
              const isActive = activeLine === line.id;
              const hasSpeaker = !!line.speaker;
              const isLongLine = line.text && line.text.length > 200;
              const isExpanded = expandedLines.has(line.id);
              const speakerColor = getSpeakerColor(line.speaker, speakers);
              
              const prevLine = index > 0 ? lines[index - 1] : null;
              const isNewSpeaker = !prevLine || prevLine.speaker !== line.speaker;

              return (
                <div
                  key={line.id}
                  ref={el => lineRefs.current[line.id] = el}
                  className={`transcript-line ${isSelected ? 'selected' : ''} ${isActive ? 'active' : ''} ${hasSpeaker ? 'tagged' : ''} ${isNewSpeaker ? 'new-speaker' : ''}`}
                  onClick={(e) => handleLineClick(line.id, e)}
                  style={speakerColor ? {
                    backgroundColor: speakerColor.bg,
                    borderLeftColor: speakerColor.border,
                  } : {}}
                >
                  <div className="line-number">{line.line_number}</div>
                  <div className={`line-content ${isExpanded ? 'expanded' : ''} ${isLongLine && !isExpanded ? 'truncated' : ''}`}>
                    {hasSpeaker ? (
                      <div className="speaker-line">
                        {editingSpeaker?.lineId === line.id ? (
                          <input
                            ref={speakerInputRef}
                            type="text"
                            className="speaker-edit-input"
                            value={editingSpeaker.value}
                            onChange={(e) => setEditingSpeaker({ ...editingSpeaker, value: e.target.value })}
                            onKeyDown={handleSpeakerInputKeyDown}
                            onBlur={saveEditedSpeaker}
                            onClick={(e) => e.stopPropagation()}
                            style={speakerColor ? { 
                              borderColor: speakerColor.border,
                              color: speakerColor.text 
                            } : {}}
                          />
                        ) : (
                          <span 
                            className="speaker-name editable" 
                            style={speakerColor ? { color: speakerColor.text } : {}}
                            onClick={(e) => startEditingSpeaker(line.id, line.speaker, e)}
                            title="Click to edit speaker name"
                          >
                            {line.speaker}:
                          </span>
                        )}
                        <span className="line-text">{line.text}</span>
                      </div>
                    ) : (
                      <div className="untagged-line">
                        {editingSpeaker?.lineId === line.id ? (
                          <input
                            ref={speakerInputRef}
                            type="text"
                            className="speaker-edit-input untagged"
                            value={editingSpeaker.value}
                            onChange={(e) => setEditingSpeaker({ ...editingSpeaker, value: e.target.value })}
                            onKeyDown={handleSpeakerInputKeyDown}
                            onBlur={saveEditedSpeaker}
                            onClick={(e) => e.stopPropagation()}
                            placeholder="Enter speaker name..."
                          />
                        ) : (
                          <span 
                            className="untagged-marker editable"
                            onClick={(e) => startEditingSpeaker(line.id, '', e)}
                            title="Click to add speaker name"
                          >
                            [?]
                          </span>
                        )}
                        <span className="line-text">{line.text}</span>
                      </div>
                    )}
                  </div>
                  {isLongLine && (
                    <button
                      className="expand-btn"
                      onClick={(e) => { e.stopPropagation(); toggleExpand(line.id); }}
                      title={isExpanded ? 'Collapse' : 'Expand'}
                    >
                      {isExpanded ? '📕' : '📖'}
                    </button>
                  )}
                </div>
              );
            })}
          </div>

          {pagination && pagination.pages > 1 && (
            <div className="pagination">
              <button onClick={() => handlePageChange(page - 1)} disabled={page === 1} className="page-btn">
                ← Prev
              </button>
              <span className="page-info">Page {page} / {pagination.pages}</span>
              <button onClick={() => handlePageChange(page + 1)} disabled={page === pagination.pages} className="page-btn">
                Next →
              </button>
            </div>
          )}
        </div>
      </div>

      {/* ML Results Panel (floating overlay) */}
      {showMlPanel && mlResults.length > 0 && (
        <div className="ml-results-overlay">
          <div className="ml-results-panel">
            <div className="ml-panel-header">
              <h3>🎯 ML Results ({mlResults.length})</h3>
              <button onClick={() => setShowMlPanel(false)} className="close-panel-btn">×</button>
            </div>
            <div className="ml-results-list">
              {mlResults.slice(0, 10).map((result) => (
                <div key={result.line_id} className="ml-result-item">
                  <div className="result-info">
                    <span className="result-line">Line {result.line_number}</span>
                    <span className={`result-confidence ${result.confidence >= 0.8 ? 'high' : 'medium'}`}>
                      {Math.round(result.confidence * 100)}%
                    </span>
                  </div>
                  <div className="result-speaker">{result.detected_speaker}</div>
                  <div className="result-actions">
                    <button onClick={() => applyMLDetection(result.line_id, result.detected_speaker)} className="apply-btn">✓</button>
                    <button onClick={() => setMlResults(mlResults.filter(r => r.line_id !== result.line_id))} className="skip-btn">✗</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Split Line Modal */}
      {splitMode && (
        <div className="split-modal-overlay">
          <div className="split-modal">
            <h3>✂️ Split Line</h3>
            <p>Click where you want to split the line. Each click adds a split point.</p>
            <SplitEditor 
              text={splitText} 
              onSplit={handleSplitLine}
              onCancel={() => { setSplitMode(false); setSplitLineId(null); }}
            />
          </div>
        </div>
      )}

      {/* Footer with keyboard hints */}
      <div className="viewer-footer">
        <div className="keyboard-hints">
          <span><kbd>↑↓</kbd> Navigate</span>
          <span><kbd>S</kbd> Split</span>
          <span><kbd>M</kbd> Merge</span>
          <span><kbd>E</kbd> Expand</span>
          <span><kbd>C</kbd> Clear</span>
          <span><kbd>1-9</kbd> Assign Speaker</span>
          <span><kbd>Space</kbd> Select</span>
        </div>
      </div>
    </div>
  );
}

export default TranscriptViewer;
