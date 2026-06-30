import { useEffect, useState } from "react";
import { getBatchOptions, runValidation } from "./services/api";
import "./App.css";

function App() {
  const [batchOptions, setBatchOptions] = useState([]);

  const [formData, setFormData] = useState({
    batch_name: "",
    host_generator_key: "",
  });

  const [status, setStatus] = useState("");
  const [reportPath, setReportPath] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadBatchOptions = async () => {
      try {
        const options = await getBatchOptions();
        setBatchOptions(options);
      } catch (error) {
        setStatus("Unable to load batch options.");
      }
    };

    loadBatchOptions();
  }, []);

  const handleBatchChange = (event) => {
    const selectedBatch = event.target.value;

    const selectedOption = batchOptions.find(
      (item) => item.batch_name === selectedBatch
    );

    setFormData({
      batch_name: selectedBatch,
      host_generator_key: selectedOption
        ? selectedOption.host_generator_key
        : "",
    });

    setStatus("");
    setReportPath("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setLoading(true);
    setStatus("Validation is running...");
    setReportPath("");

    const payload = {
      batch_name: formData.batch_name,
      host_generator_key: formData.host_generator_key,
    };

    try {
      const result = await runValidation(payload);
      setStatus("Validation completed successfully.");
      setReportPath(result.output_path || "");
    } catch (error) {
      setStatus(error.response?.data?.detail || "Validation failed.");
      setReportPath("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="card">
        <h1>Rule Injection Validation</h1>
        <p className="subtitle">
          SDTM Original vs Dirty Data Validation Dashboard
        </p>

        <form onSubmit={handleSubmit}>
          <label>Batch Name</label>
          <select
            name="batch_name"
            value={formData.batch_name}
            onChange={handleBatchChange}
            required
          >
            <option value="">Select Batch</option>

            {batchOptions.map((item) => (
              <option key={item.batch_name} value={item.batch_name}>
                {item.batch_name}
              </option>
            ))}
          </select>

          <label>Host Generator Key</label>
          <input
            type="text"
            name="host_generator_key"
            value={formData.host_generator_key}
            readOnly
          />

          <button type="submit" disabled={loading}>
            {loading ? "Running..." : "Run Validation"}
          </button>
        </form>

        {status && (
          <div className="status">
            <strong>{status}</strong>

            {reportPath && (
              <div className="report-path">
                {reportPath}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;