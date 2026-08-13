import { useState } from "react";
import axios from "axios";
import "./App.css";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [file, setFile] = useState(null);
  const [processingId, setProcessingId] = useState("");
  const [status, setStatus] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const uploadImage = async () => {
    if (!file) return alert("Please choose an image");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setAnalysis(null);

      const uploadRes = await axios.post(`${API}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const id = uploadRes.data.processing_id;
      setProcessingId(id);
      setStatus("pending");

      let currentStatus = "pending";

      while (currentStatus === "pending" || currentStatus === "processing") {
        await new Promise((resolve) => setTimeout(resolve, 1000));

        const statusRes = await axios.get(`${API}/status/${id}`);
        currentStatus = statusRes.data.status;
        setStatus(currentStatus);
      }

      if (currentStatus === "completed") {
        const resultRes = await axios.get(`${API}/result/${id}`);
        setAnalysis(resultRes.data.analysis);
      }
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <div className="hero">
          <h1>Intelligent Media</h1>
          <p>
            Upload a vehicle image and receive AI-powered quality analysis in
            real time.
          </p>
        </div>

        <div className="glass-card upload-card">
          <div className="upload-row">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files[0])}
            />

            <button onClick={uploadImage} disabled={loading}>
              {loading ? "Processing..." : "Upload & Analyze"}
            </button>
          </div>
        </div>

        {processingId && (
          <div className="glass-card status-card">
            <div className="status-row">
              <div>
                <h3>Processing ID</h3>
                <p className="id-text">{processingId}</p>
              </div>

              <div>
                <h3>Status</h3>
                <span className={`badge ${status}`}>
                  {status.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        )}

        {analysis && (
          <div className="glass-card results-card">
            <h2>Analysis Results</h2>

            <div className="grid">
              <div className="metric">
                <span>Blur Score</span>
                <strong>{analysis.blur_score?.toFixed(2)}</strong>
              </div>

              <div className="metric">
                <span>Blurry</span>
                <strong>{analysis.is_blurry ? "Yes" : "No"}</strong>
              </div>

              <div className="metric">
                <span>Brightness</span>
                <strong>{analysis.brightness?.toFixed(2)}</strong>
              </div>

              <div className="metric">
                <span>Low Light</span>
                <strong>{analysis.low_light ? "Yes" : "No"}</strong>
              </div>

              <div className="metric">
                <span>Duplicate</span>
                <strong>{analysis.duplicate ? "Yes" : "No"}</strong>
              </div>

              <div className="metric">
                <span>Screenshot Suspected</span>
                <strong>
                  {analysis.screenshot_suspected ? "Yes" : "No"}
                </strong>
              </div>

              <div className="metric">
                <span>Number Plate Valid</span>
                <strong>
                  {analysis.number_plate_valid ? "Yes" : "No"}
                </strong>
              </div>
            </div>

            <div className="ocr-box">
              <h3>OCR Extracted Text</h3>
              <pre>{analysis.ocr_text || "No text detected"}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}