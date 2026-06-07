import { useCallback, useState } from 'react';
import { toast } from 'react-toastify';

export function useAsyncAction() {
  const [loading, setLoading] = useState(false);
  const run = useCallback(async (action, messages = {}) => {
    setLoading(true);
    try {
      const result = await action();
      if (messages.success) toast.success(messages.success);
      return result;
    } catch (error) {
      const message = error?.code === 'ECONNABORTED'
        ? 'The request is still taking longer than expected. Refresh campaigns in a moment to see the latest status.'
        : error?.response?.data?.error || error.message || 'Request failed';
      toast.error(messages.error || message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, run };
}
