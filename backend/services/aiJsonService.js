import { createChatCompletion, isAiConfigured } from './aiClient.js';

const forbiddenPatterns = [
  /score/i,
  /rating/i,
  /ranking/i,
  /percentage/i,
  /fit_value/i,
  /personality diagnosis/i,
  /mental health/i,
  /religion/i,
  /politics/i,
  /ethnicity/i,
  /sexuality/i,
  /family status/i,
];

function safeParseJson(text) {
  const trimmed = String(text || '').trim();
  const start = trimmed.indexOf('{');
  const end = trimmed.lastIndexOf('}');
  if (start === -1 || end === -1 || end <= start) {
    throw new Error('AI response did not contain JSON.');
  }
  return JSON.parse(trimmed.slice(start, end + 1));
}

function containsForbiddenContent(value) {
  const text = JSON.stringify(value);
  return forbiddenPatterns.some((pattern) => pattern.test(text));
}

export async function generateSafeJson({
  task,
  input,
  schemaHint,
  fallback,
  moduleName,
  temperature = 0.2,
  topP,
  maxTokens = 1200,
  failOpen = true,
}) {
  if (!isAiConfigured(moduleName)) {
    return fallback;
  }

  const system = [
    'You are a backend JSON generation service for a recruiter outreach platform.',
    'Return JSON only.',
    'Use only the provided input JSON.',
    'Do not invent facts, metrics, funding, company news, achievements, recruiter details, or private traits.',
    'Do not include scores, rankings, ratings, percentages, fit values, or sensitive inferences.',
    'If evidence is weak, use "Insufficient data.".',
  ].join(' ');

  try {
    const content = await createChatCompletion({
      moduleName,
      temperature,
      topP,
      maxTokens,
      messages: [
        { role: 'system', content: system },
        {
          role: 'user',
          content: JSON.stringify({ task, schemaHint, input }),
        },
      ],
    });
    const parsed = safeParseJson(content);
    if (containsForbiddenContent(parsed)) {
      throw new Error('AI response contained forbidden content.');
    }
    return parsed;
  } catch (error) {
    if (failOpen) return fallback;
    throw error;
  }
}
