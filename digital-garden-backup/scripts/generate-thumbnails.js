#!/usr/bin/env node

/**
 * Batch Thumbnail Generation Script
 *
 * This script generates thumbnails for all insights in the content collection
 * using Google Imagen 4 API.
 *
 * Usage:
 *   node scripts/generate-thumbnails.js [options]
 *
 * Options:
 *   --force          Regenerate existing thumbnails
 *   --filter=slug    Generate thumbnail only for specific insight
 *   --style=style    Override default style (professional, creative, technical, minimal)
 *   --batch-size=n   Process n items at a time (default: 3)
 *   --dry-run        Show what would be generated without actually generating
 *
 * Environment Variables:
 *   GOOGLE_CLOUD_PROJECT_ID  Google Cloud Project ID
 *   GOOGLE_APPLICATION_CREDENTIALS  Path to service account key file
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';
import matter from 'gray-matter';

// ES module compatibility
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const require = createRequire(import.meta.url);

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    force: false,
    filter: null,
    style: null,
    batchSize: 3,
    dryRun: false
  };

  for (const arg of args) {
    if (arg === '--force') {
      options.force = true;
    } else if (arg === '--dry-run') {
      options.dryRun = true;
    } else if (arg.startsWith('--filter=')) {
      options.filter = arg.split('=')[1];
    } else if (arg.startsWith('--style=')) {
      options.style = arg.split('=')[1];
    } else if (arg.startsWith('--batch-size=')) {
      options.batchSize = parseInt(arg.split('=')[1]) || 3;
    } else if (arg === '--help') {
      console.log(`
Batch Thumbnail Generation Script

Usage: node scripts/generate-thumbnails.js [options]

Options:
  --force          Regenerate existing thumbnails
  --filter=slug    Generate thumbnail only for specific insight
  --style=style    Override default style (professional, creative, technical, minimal)
  --batch-size=n   Process n items at a time (default: 3)
  --dry-run        Show what would be generated without actually generating
  --help           Show this help message

Environment Variables:
  GOOGLE_CLOUD_PROJECT_ID           Google Cloud Project ID (required)
  GOOGLE_APPLICATION_CREDENTIALS    Path to service account key file (required)

Examples:
  node scripts/generate-thumbnails.js --dry-run
  node scripts/generate-thumbnails.js --filter=ceatec-ai-manufacturing
  node scripts/generate-thumbnails.js --style=creative --batch-size=5
  node scripts/generate-thumbnails.js --force
      `);
      process.exit(0);
    }
  }

  return options;
}

// Validate environment
function validateEnvironment() {
  const projectId = process.env.GOOGLE_CLOUD_PROJECT_ID;
  if (!projectId) {
    console.error('❌ Error: GOOGLE_CLOUD_PROJECT_ID environment variable is required');
    console.error('   Set it to your Google Cloud Project ID');
    process.exit(1);
  }

  // Check for authentication
  if (!process.env.GOOGLE_APPLICATION_CREDENTIALS && !process.env.GCLOUD_PROJECT) {
    console.warn('⚠️  Warning: No authentication detected');
    console.warn('   Set GOOGLE_APPLICATION_CREDENTIALS or run `gcloud auth application-default login`');
  }

  return projectId;
}

// Load insight files
async function loadInsights(contentDir, filter = null) {
  const insightsDir = path.join(contentDir, 'insights');
  const files = await fs.readdir(insightsDir);
  const insights = [];

  for (const file of files) {
    if (!file.endsWith('.md')) continue;

    const slug = path.basename(file, '.md');

    // Apply filter if specified
    if (filter && slug !== filter) continue;

    const filePath = path.join(insightsDir, file);
    const content = await fs.readFile(filePath, 'utf-8');
    const { data: frontmatter } = matter(content);

    // Skip if required fields are missing
    if (!frontmatter.title || !frontmatter.exhibition || !frontmatter.category) {
      console.warn(`⚠️  Skipping ${slug}: Missing required frontmatter fields`);
      continue;
    }

    insights.push({
      slug,
      filePath,
      frontmatter,
      hasExistingThumbnail: !!frontmatter.thumbnail,
      content: content
    });
  }

  return insights;
}

// Generate thumbnail for a single insight
async function generateThumbnail(insight, imagenClient, contentEnhancer, style = null) {
  const { slug, frontmatter } = insight;

  try {
    console.log(`📸 Generating thumbnail for: ${frontmatter.title}`);

    // Determine configuration
    const suggestedConfig = contentEnhancer.suggestThumbnailConfig(
      frontmatter.category,
      insight.content,
      frontmatter.exhibition
    );

    const config = style ? { ...suggestedConfig, style } : suggestedConfig;

    // Generate thumbnail
    const base64Image = await imagenClient.generateInsightThumbnail(
      frontmatter.title,
      frontmatter.exhibition,
      frontmatter.category,
      frontmatter.keyInsights || [frontmatter.description || frontmatter.title],
      config
    );

    // Save image
    const filename = `${slug}-thumb.jpg`;
    const imagePath = await imagenClient.saveImage(base64Image, filename, 'thumbnails');

    // Update frontmatter
    await updateInsightThumbnail(insight.filePath, imagePath);

    return {
      slug,
      success: true,
      imagePath,
      config
    };

  } catch (error) {
    console.error(`❌ Failed to generate thumbnail for ${slug}:`, error.message);
    return {
      slug,
      success: false,
      error: error.message
    };
  }
}

// Update insight file with thumbnail path
async function updateInsightThumbnail(filePath, imagePath) {
  const content = await fs.readFile(filePath, 'utf-8');
  const { data: frontmatter, content: markdownContent } = matter(content);

  // Update thumbnail path
  frontmatter.thumbnail = imagePath;
  frontmatter.imageGenerated = true;

  // Recreate the file
  const updatedContent = matter.stringify(markdownContent, frontmatter);
  await fs.writeFile(filePath, updatedContent);
}

// Process insights in batches
async function processBatch(insights, imagenClient, contentEnhancer, batchSize, options) {
  const results = [];

  for (let i = 0; i < insights.length; i += batchSize) {
    const batch = insights.slice(i, i + batchSize);
    const batchPromises = batch.map(insight =>
      generateThumbnail(insight, imagenClient, contentEnhancer, options.style)
    );

    const batchResults = await Promise.allSettled(batchPromises);

    for (const result of batchResults) {
      if (result.status === 'fulfilled') {
        results.push(result.value);
      } else {
        results.push({
          success: false,
          error: result.reason.message
        });
      }
    }

    // Rate limiting delay
    if (i + batchSize < insights.length) {
      console.log('⏳ Waiting 3 seconds before next batch...');
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
  }

  return results;
}

// Main execution
async function main() {
  const options = parseArgs();
  const projectId = validateEnvironment();

  console.log('🚀 Starting batch thumbnail generation...');
  console.log(`   Project ID: ${projectId}`);
  console.log(`   Options:`, options);

  // Determine paths
  const projectRoot = path.resolve(__dirname, '..');
  const contentDir = path.join(projectRoot, 'content');

  // Load insights
  console.log('\n📚 Loading insights...');
  const insights = await loadInsights(contentDir, options.filter);
  console.log(`   Found ${insights.length} insights`);

  // Filter out existing thumbnails if not forcing regeneration
  const toProcess = options.force
    ? insights
    : insights.filter(insight => !insight.hasExistingThumbnail);

  if (toProcess.length === 0) {
    console.log('✅ All insights already have thumbnails. Use --force to regenerate.');
    return;
  }

  console.log(`   ${toProcess.length} insights need thumbnails`);

  if (options.dryRun) {
    console.log('\n🧪 DRY RUN - Would process:');
    toProcess.forEach(insight => {
      console.log(`   - ${insight.slug}: ${insight.frontmatter.title}`);
    });
    console.log(`\nWould generate ${toProcess.length} thumbnails`);
    return;
  }

  // Initialize clients
  console.log('\n🔧 Initializing Imagen client...');
  let ImagenClient, ContentEnhancer;
  try {
    const module = await import('../src/utils/imagen-client.js');
    ImagenClient = module.ImagenClient;
    ContentEnhancer = module.ContentEnhancer;
  } catch (error) {
    console.error('❌ Failed to load Imagen client:', error.message);
    console.error('   Make sure the project is built: npm run build');
    process.exit(1);
  }

  const imagenClient = new ImagenClient(projectId);
  const contentEnhancer = new ContentEnhancer(projectId);

  // Process thumbnails
  console.log('\n🎨 Generating thumbnails...');
  const startTime = Date.now();

  const results = await processBatch(
    toProcess,
    imagenClient,
    contentEnhancer,
    options.batchSize,
    options
  );

  // Report results
  console.log('\n📊 Results:');
  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  console.log(`   ✅ Successful: ${successful.length}`);
  console.log(`   ❌ Failed: ${failed.length}`);

  if (failed.length > 0) {
    console.log('\n❌ Failed items:');
    failed.forEach(result => {
      console.log(`   - ${result.slug || 'unknown'}: ${result.error}`);
    });
  }

  const duration = (Date.now() - startTime) / 1000;
  console.log(`\n⏱️  Total time: ${duration.toFixed(1)}s`);
  console.log('✨ Thumbnail generation complete!');
}

// Error handling
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('❌ Script failed:', error.message);
    process.exit(1);
  });
}