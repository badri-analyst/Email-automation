import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadFile } from '../../services/api.js';
import { useAsyncAction } from '../../hooks/useAsyncAction.js';
import { useOutreach } from '../../context/OutreachContext.jsx';
import FileDropzone from '../upload/FileDropzone.jsx';
import UploadProgress from '../upload/UploadProgress.jsx';

export default function UploadForm() {
  const { dispatch } = useOutreach();
  const navigate = useNavigate();
  const [progress, setProgress] = useState(0);
  const { loading, run } = useAsyncAction();

  async function handleFile(file) {
    setProgress(0);
    const data = await run(
      () => uploadFile('/upload', file, {}, (event) => setProgress(Math.round((event.loaded * 100) / (event.total || 1)))),
      { success: 'Spreadsheet uploaded and processed' },
    );
    dispatch({ type: 'SET_UPLOAD', payload: data });
    dispatch({ type: 'SET_VALIDATION', payload: data.validation });
    if (data.campaign) {
      dispatch({ type: 'SET_CURRENT_CAMPAIGN', payload: { id: data.campaign.id, name: data.campaign.campaignName } });
    }
    navigate('/pipeline');
  }

  return (
    <div>
      <FileDropzone
        accept={{
          'text/csv': ['.csv'],
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
        }}
        onFile={handleFile}
        label={loading ? 'Uploading...' : 'Upload CSV or XLSX spreadsheet'}
      />
      {progress > 0 && <UploadProgress progress={progress} />}
    </div>
  );
}
