import React, { useState, useEffect } from 'react';
import './TaggedView.css';

function TaggedView({ transcriptId, apiBase }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filterSpeaker, setFilterSpeaker] = useState('');
  const [groupBySpeaker, setGroupBySpeaker] = useState(false);
  const [groupedData, setGroupedData] = useState(null);

  useEffect(() => {
    fetchStats();
  }, [transcriptId, apiBase]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/stats`);
      if (!response.ok) throw new Error('Failed to fetch stats');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchGroupedData = async () => {
    if (!groupBySpeaker) {
      setGroupedData(null);
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/lines?per_page=10000`);
      if (!response.ok) throw new Error('Failed to fetch lines');
      const data = await response.json();
      
      // Group by speaker
      const grouped = data.lines.reduce((acc, line) => {
        const speaker = line.speaker || 'UNKNOWN';
        if (!acc[speaker]) {
          acc[speaker] = [];
        }
        acc[speaker].push(line);
        return acc;
      }, {});
      
      setGroupedData(grouped);
    } catch (err) {
      console.error('Error fetching grouped data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (groupBySpeaker) {
      fetchGroupedData();
    } else {
      setGroupedData(null);
    }
  }, [groupBySpeaker, transcriptId, apiBase]);

  if (loading && !stats) {
    return <div className="loading">Loading statistics...</div>;
  }

  if (!stats) {
    return <div className="empty-state">No data available</div>;
  }

  const uniqueSpeakers = stats.speakers.map(s => s.name);

  return (
    <div className="tagged-view">
      <div className="tagged-controls">
        <div className="filter-section">
          <label>
            Filter by speaker:
            <select
              value={filterSpeaker}
              onChange={(e) => setFilterSpeaker(e.target.value)}
              className="speaker-filter"
            >
              <option value="">All speakers</option>
              {uniqueSpeakers.map(speaker => {
                const speakerData = stats.speakers.find(s => s.name === speaker);
                return (
                  <option key={speaker} value={speaker}>
                    {speaker} ({speakerData?.count || 0} lines)
                  </option>
                );
              })}
            </select>
          </label>
        </div>

        <div className="view-options">
          <label>
            <input
              type="checkbox"
              checked={groupBySpeaker}
              onChange={(e) => setGroupBySpeaker(e.target.checked)}
            />
            Group by speaker
          </label>
        </div>
      </div>

      <div className="speaker-stats">
        <h3>Speaker Statistics</h3>
        <div className="stats-grid">
          {stats.speakers
            .sort((a, b) => b.count - a.count)
            .map((speaker) => (
              <div key={speaker.name} className="stat-item">
                <span className="stat-speaker">{speaker.name}</span>
                <span className="stat-count">{speaker.count} lines</span>
                <span className="stat-percent">
                  ({Math.round((speaker.count / stats.total_lines) * 100)}%)
                </span>
              </div>
            ))}
        </div>
      </div>

      {groupBySpeaker && groupedData && (
        <div className="tagged-content">
          {Object.entries(groupedData)
            .sort((a, b) => b[1].length - a[1].length)
            .map(([speaker, items]) => (
              <div key={speaker} className="speaker-group">
                <h3 className="group-header">
                  {speaker} ({items.length} lines)
                </h3>
                <div className="group-content">
                  {items.map((item) => (
                    <div key={item.id} className="tagged-item">
                      <span className="item-number">#{item.line_number}</span>
                      <span className="item-text">{item.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
        </div>
      )}

      {!groupBySpeaker && (
        <div className="info-message">
          Enable "Group by speaker" to view all lines grouped by speaker.
        </div>
      )}
    </div>
  );
}

export default TaggedView;
