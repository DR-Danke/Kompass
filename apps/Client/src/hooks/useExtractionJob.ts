import { useState, useCallback, useRef, useEffect } from 'react';
import { extractionService } from '@/services/kompassService';
import type { ExtractedProduct, ExtractionJobStatus, ExtractionJobDTO } from '@/types/kompass';

interface UseExtractionJobReturn {
  jobId: string | null;
  status: ExtractionJobStatus | null;
  progress: number;
  products: ExtractedProduct[];
  errors: string[];
  isProcessing: boolean;
  totalFiles: number;
  processedFiles: number;
  startJob: (files: FileList) => Promise<void>;
  resetJob: () => void;
  uploadError: string | null;
}

const POLL_INTERVAL_MS = 2000;

export function useExtractionJob(): UseExtractionJobReturn {
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<ExtractionJobStatus | null>(null);
  const [progress, setProgress] = useState(0);
  const [products, setProducts] = useState<ExtractedProduct[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [totalFiles, setTotalFiles] = useState(0);
  const [processedFiles, setProcessedFiles] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const isProcessing = status === 'pending' || status === 'processing';

  const stopPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  }, []);

  const updateJobState = useCallback((job: ExtractionJobDTO) => {
    setStatus(job.status);
    setProgress(job.progress);
    setTotalFiles(job.total_files);
    setProcessedFiles(job.processed_files);
    setErrors(job.errors);

    if (job.status === 'completed' || job.status === 'failed') {
      setProducts(job.extracted_products);
      stopPolling();
    }
  }, [stopPolling]);

  const pollJobStatus = useCallback(async (id: string) => {
    try {
      const job = await extractionService.getJobStatus(id);
      updateJobState(job);
    } catch (error) {
      console.error('INFO [useExtractionJob]: Error polling job status', error);
      setErrors((prev) => [...prev, 'Failed to fetch job status']);
      stopPolling();
    }
  }, [updateJobState, stopPolling]);

  const startPolling = useCallback((id: string) => {
    stopPolling();
    pollIntervalRef.current = setInterval(() => {
      pollJobStatus(id);
    }, POLL_INTERVAL_MS);
    pollJobStatus(id);
  }, [pollJobStatus, stopPolling]);

  const startJob = useCallback(async (files: FileList) => {
    setUploadError(null);
    setStatus('pending');
    setProgress(0);
    setProducts([]);
    setErrors([]);
    setTotalFiles(files.length);
    setProcessedFiles(0);

    try {
      console.log(`INFO [useExtractionJob]: Starting extraction job with ${files.length} files`);
      const response = await extractionService.uploadFiles(files);
      setJobId(response.job_id);
      startPolling(response.job_id);
    } catch (error) {
      console.error('INFO [useExtractionJob]: Error starting extraction job', error);
      setStatus('failed');
      const message = error instanceof Error ? error.message : 'Failed to upload files';
      setUploadError(message);
      setErrors([message]);
    }
  }, [startPolling]);

  const resetJob = useCallback(() => {
    stopPolling();
    setJobId(null);
    setStatus(null);
    setProgress(0);
    setProducts([]);
    setErrors([]);
    setTotalFiles(0);
    setProcessedFiles(0);
    setUploadError(null);
  }, [stopPolling]);

  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return {
    jobId,
    status,
    progress,
    products,
    errors,
    isProcessing,
    totalFiles,
    processedFiles,
    startJob,
    resetJob,
    uploadError,
  };
}
