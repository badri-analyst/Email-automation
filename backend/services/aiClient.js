const DEFAULT_BASE_URL = 'https://api.aimlapi.com/v1';
const NVIDIA_BASE_URL = 'https://integrate.api.nvidia.com/v1';
const DEFAULT_MODEL = 'gpt-4o';

const MODULE_CONFIG = {
  role_country: {
    apiKeyEnv: 'ROLE_COUNTRY_API_KEY',
    baseUrlEnv: 'ROLE_COUNTRY_API_BASE_URL',
    modelEnv: 'ROLE_COUNTRY_AI_MODEL',
    defaultBaseUrl: NVIDIA_BASE_URL,
    defaultModel: 'nvidia/nemotron-mini-4b-instruct',
  },
  linkedin_research: {
    apiKeyEnv: 'LINKEDIN_RESEARCH_API_KEY',
    baseUrlEnv: 'LINKEDIN_RESEARCH_API_BASE_URL',
    modelEnv: 'LINKEDIN_RESEARCH_AI_MODEL',
    defaultBaseUrl: NVIDIA_BASE_URL,
    defaultModel: 'mistralai/mistral-large-3-675b-instruct-2512',
  },
  company_research: {
    apiKeyEnv: 'COMPANY_RESEARCH_API_KEY',
    baseUrlEnv: 'COMPANY_RESEARCH_API_BASE_URL',
    modelEnv: 'COMPANY_RESEARCH_AI_MODEL',
    defaultBaseUrl: NVIDIA_BASE_URL,
    defaultModel: 'meta/llama-4-maverick-17b-128e-instruct',
  },
  communication_signal: {
    apiKeyEnv: 'COMMUNICATION_SIGNAL_API_KEY',
    baseUrlEnv: 'COMMUNICATION_SIGNAL_API_BASE_URL',
    modelEnv: 'COMMUNICATION_SIGNAL_AI_MODEL',
    defaultBaseUrl: NVIDIA_BASE_URL,
    defaultModel: 'stepfun-ai/step-3.5-flash',
  },
  email_writing: {
    apiKeyEnv: 'EMAIL_WRITING_API_KEY',
    baseUrlEnv: 'EMAIL_WRITING_API_BASE_URL',
    modelEnv: 'EMAIL_WRITING_AI_MODEL',
    defaultBaseUrl: NVIDIA_BASE_URL,
    defaultModel: 'mistralai/mistral-large-3-675b-instruct-2512',
  },
};

function getModuleConfig(moduleName) {
  return MODULE_CONFIG[moduleName] || {};
}

function getApiKey(moduleName) {
  const config = getModuleConfig(moduleName);
  return process.env[config.apiKeyEnv]
    || process.env.AI_API_KEY
    || process.env.AIMLAPI_API_KEY
    || process.env.OPENAI_API_KEY;
}

function getBaseUrl(moduleName) {
  const config = getModuleConfig(moduleName);
  return (
    process.env[config.baseUrlEnv]
    || process.env.NVIDIA_API_BASE_URL
    || process.env.AI_API_BASE_URL
    || config.defaultBaseUrl
    || DEFAULT_BASE_URL
  ).replace(/\/$/, '');
}

function getModel(moduleName, requestedModel) {
  const config = getModuleConfig(moduleName);
  // Per-module model takes priority over global AI_MODEL override
  return requestedModel
    || process.env[config.modelEnv]
    || config.defaultModel
    || process.env.AI_MODEL
    || DEFAULT_MODEL;
}

export function isAiConfigured(moduleName) {
  return Boolean(getApiKey(moduleName));
}

export async function createChatCompletion({
  messages,
  responseFormat = null,
  temperature = 0.2,
  topP,
  maxTokens = 1200,
  model,
  moduleName,
}) {
  const apiKey = getApiKey(moduleName);
  if (!apiKey) {
    throw new Error('AI API key is not configured.');
  }

  const baseUrl = getBaseUrl(moduleName);
  const selectedModel = getModel(moduleName, model);
  const useResponseFormat = responseFormat && process.env.AI_USE_RESPONSE_FORMAT === 'true';
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30_000);
  let response;
  try {
    response = await fetch(`${baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: selectedModel,
        messages,
        temperature,
        top_p: topP,
        max_tokens: maxTokens,
        response_format: useResponseFormat ? { type: responseFormat } : undefined,
      }),
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeoutId);
  }

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`AI API request failed: ${response.status} ${detail}`);
  }

  const data = await response.json();
  return data.choices?.[0]?.message?.content || '';
}
