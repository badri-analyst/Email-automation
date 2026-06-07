export function isEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value || '');
}

export function isLinkedInProfile(value) {
  return /^https?:\/\/(www\.)?linkedin\.com\/(in|pub)\//i.test(value || '') || /^(www\.)?linkedin\.com\/(in|pub)\//i.test(value || '');
}

export function isYouTube(value) {
  return !value || /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\//i.test(value);
}

export function sanitizeText(value) {
  return String(value || '').replace(/[<>]/g, '').trim();
}
