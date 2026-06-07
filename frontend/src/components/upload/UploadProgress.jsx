export default function UploadProgress({ progress = 0 }) {
  return (
    <div className="mt-4">
      <div className="mb-1 flex justify-between text-xs text-slate-500">
        <span>Upload progress</span>
        <span>{progress}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-200">
        <div className="h-full rounded-full bg-brand-600 transition-all" style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
}
