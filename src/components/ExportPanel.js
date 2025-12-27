import React, { useState } from 'react';
import './ExportPanel.css';

function ExportPanel({ transcriptId, apiBase }) {
  const [exportFormat, setExportFormat] = useState('txt');
  const [exporting, setExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState('');

  const handleExport = async () => {
    try {
      setExporting(true);
      setExportStatus('');

      const response = await fetch(`${apiBase}/transcripts/${transcriptId}/export?format=${exportFormat}`);
      
      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const extensions = {
        txt: 'txt',
        json: 'json',
        srt: 'srt',
        csv: 'csv'
      };
      
      link.download = `transcript_tagged.${extensions[exportFormat]}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setExportStatus(`Exported as ${exportFormat.toUpperCase()}`);
    } catch (err) {
      console.error('Export error:', err);
      setExportStatus('Export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="export-panel">
      <h3>Export Tagged Transcript</h3>
      <div className="export-controls">
        <div className="format-selector">
          <label>
            Format:
            <select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value)}
              className="format-select"
            >
              <option value="txt">Plain Text (.txt)</option>
              <option value="json">JSON (.json)</option>
              <option value="srt">SRT Subtitles (.srt)</option>
              <option value="csv">CSV (.csv)</option>
            </select>
          </label>
        </div>

        <button 
          onClick={handleExport} 
          className="export-btn"
          disabled={exporting}
        >
          {exporting ? 'Exporting...' : 'Export'}
        </button>

        {exportStatus && (
          <span className={`export-status ${exportStatus.includes('failed') ? 'error' : 'success'}`}>
            {exportStatus}
          </span>
        )}
      </div>

      <div className="export-preview">
        <h4>Export Format: {exportFormat.toUpperCase()}</h4>
        <p className="preview-description">
          {exportFormat === 'txt' && 'Plain text format with speaker tags: [Speaker]: Text'}
          {exportFormat === 'json' && 'JSON format with full transcript data and metadata'}
          {exportFormat === 'srt' && 'SRT subtitle format for video editing'}
          {exportFormat === 'csv' && 'CSV format for spreadsheet applications'}
        </p>
      </div>
    </div>
  );
}

export default ExportPanel;
