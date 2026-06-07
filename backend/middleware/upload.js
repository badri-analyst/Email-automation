import multer from 'multer';

const storage = multer.memoryStorage();

export const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 },
  fileFilter: (_request, file, callback) => {
    const safe = /\.(csv|xlsx|pdf|docx)$/i.test(file.originalname);
    callback(safe ? null : new Error('Unsupported file type.'), safe);
  },
});
