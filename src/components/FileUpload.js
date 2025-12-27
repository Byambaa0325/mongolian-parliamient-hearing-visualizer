import React, { useRef, useState } from 'react';
import './FileUpload.css';

function FileUpload({ onFileLoad }) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState('');

  const processFile = (file) => {
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target.result;
      // Split by newlines and filter empty lines
      const lines = content
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
      
      setFileName(file.name);
      onFileLoad(lines);
    };
    reader.readAsText(file, 'UTF-8');
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      processFile(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'text/plain') {
      processFile(file);
    } else {
      alert('Please upload a text file (.txt)');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  return (
    <div className="file-upload-container">
      <div
        className={`upload-area ${isDragging ? 'dragging' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="upload-icon">📄</div>
        <h2>Upload Transcript File</h2>
        <p>Drag and drop a .txt file here, or click to browse</p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        {fileName && (
          <div className="file-name">
            Loaded: {fileName}
          </div>
        )}
      </div>
      
      <div className="upload-info">
        <h3>Instructions:</h3>
        <ul>
          <li>Upload a raw text transcript file (.txt)</li>
          <li>The file will be split into lines for tagging</li>
          <li>After upload, go to the "Tagging" tab to assign speakers</li>
        </ul>
      </div>
    </div>
  );
}

export default FileUpload;

