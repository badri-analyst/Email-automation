import { Router } from 'express';
import { upload } from '../middleware/upload.js';
import * as controller from '../controllers/pipelineController.js';

const router = Router();

router.get('/health', controller.health);
router.get('/supabase-health', controller.supabaseHealth);
router.get('/campaigns', controller.listCampaigns);
router.get('/campaigns/:id', controller.getCampaign);
router.post('/campaigns/:id/run', controller.runCampaign);
router.post('/upload', upload.single('file'), controller.uploadSpreadsheet);
router.post('/validation', controller.validation);
router.post('/cleaning', controller.cleaning);
router.post('/role-country', controller.roleCountry);
router.post('/linkedin-research', controller.linkedinResearch);
router.post('/company-research', controller.companyResearch);
router.post('/candidate-assets', controller.candidateAssets);
router.get('/candidate-profile', controller.candidateProfile);
router.post('/gmail-auth', controller.gmailAuth);
router.get('/gmail-oauth-url', controller.gmailOAuthUrl);
router.get('/gmail/accounts', controller.listGmailAccountsHandler);
router.delete('/gmail/accounts/:gmailAddress', controller.revokeGmailAccountHandler);
router.post('/decision-engine', controller.decisionEngine);
router.post('/email-personalization', controller.emailPersonalization);
router.post('/pipeline/run', controller.runPipeline);

export default router;
