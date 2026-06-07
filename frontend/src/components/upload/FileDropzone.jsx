import { useDropzone } from 'react-dropzone';
import { UploadCloud } from 'lucide-react';

export default function FileDropzone({ accept, onFile, label = 'Drop file here or click to browse' }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept,
    multiple: false,
    onDrop: (files) => files[0] && onFile(files[0]),
  });
  return (
    <div
      {...getRootProps()}
      className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition ${isDragActive ? 'border-brand-500 bg-brand-50' : 'border-slate-200 bg-slate-50 hover:bg-white'}`}
    >
      <input {...getInputProps()} />
      <UploadCloud className="mx-auto mb-3 text-brand-600" />
      <p className="font-medium text-slate-800">{label}</p>
      <p className="mt-1 text-sm text-slate-500">Files are sent to the backend for safe processing.</p>
    </div>
  );
}
