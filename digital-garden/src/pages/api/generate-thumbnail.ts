import type { APIRoute } from 'astro';
import { ImagenClient, ContentEnhancer, type ThumbnailConfig } from '../../utils/imagen-client';

export interface ThumbnailRequest {
  title: string;
  exhibition: string;
  category: string[];
  keyInsights: string[];
  content?: string;
  slug: string;
  config?: Partial<ThumbnailConfig>;
}

export interface ThumbnailResponse {
  success: boolean;
  imagePath?: string;
  error?: string;
  metadata?: {
    generatedAt: string;
    config: ThumbnailConfig;
    processingTime: number;
  };
}

export const POST: APIRoute = async ({ request }) => {
  const startTime = Date.now();

  try {
    // Validate environment variables
    const projectId = import.meta.env.GOOGLE_CLOUD_PROJECT_ID;
    if (!projectId) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Google Cloud Project ID not configured'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Parse request body
    const requestData: ThumbnailRequest = await request.json();
    const { title, exhibition, category, keyInsights, content, slug, config = {} } = requestData;

    // Validate required fields
    if (!title || !exhibition || !category || !keyInsights || !slug) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Missing required fields: title, exhibition, category, keyInsights, slug'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Initialize clients
    const imagenClient = new ImagenClient(projectId);
    const contentEnhancer = new ContentEnhancer(projectId);

    // Determine optimal configuration
    let finalConfig: ThumbnailConfig;
    if (content) {
      finalConfig = contentEnhancer.suggestThumbnailConfig(category, content, exhibition);
      // Override with user-provided config
      finalConfig = { ...finalConfig, ...config };
    } else {
      finalConfig = {
        style: 'professional',
        theme: 'light',
        includeJapaneseText: true,
        brandingElements: false,
        ...config
      };
    }

    // Generate thumbnail
    console.log(`Generating thumbnail for: ${title}`);
    const base64Image = await imagenClient.generateInsightThumbnail(
      title,
      exhibition,
      category,
      keyInsights,
      finalConfig
    );

    // Save image
    const filename = `${slug}-${Date.now()}.jpg`;
    const imagePath = await imagenClient.saveImage(base64Image, filename, 'thumbnails');

    const processingTime = Date.now() - startTime;

    const response: ThumbnailResponse = {
      success: true,
      imagePath,
      metadata: {
        generatedAt: new Date().toISOString(),
        config: finalConfig,
        processingTime
      }
    };

    return new Response(JSON.stringify(response), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Thumbnail generation error:', error);

    const processingTime = Date.now() - startTime;

    const errorResponse: ThumbnailResponse = {
      success: false,
      error: error.message,
      metadata: {
        generatedAt: new Date().toISOString(),
        config: null,
        processingTime
      }
    };

    return new Response(JSON.stringify(errorResponse), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

export const GET: APIRoute = async ({ url }) => {
  // Health check endpoint
  if (url.searchParams.get('health') === 'true') {
    const projectId = import.meta.env.GOOGLE_CLOUD_PROJECT_ID;

    return new Response(JSON.stringify({
      status: 'ok',
      configured: !!projectId,
      timestamp: new Date().toISOString()
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // Get thumbnail generation status
  const slug = url.searchParams.get('slug');
  if (slug) {
    // In a real implementation, you would check the status from a database
    return new Response(JSON.stringify({
      slug,
      status: 'completed',
      imagePath: `/images/thumbnails/${slug}-thumb.jpg`,
      generatedAt: new Date().toISOString()
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  return new Response(JSON.stringify({
    error: 'Invalid request. Use POST for generation or GET with ?health=true for health check.'
  }), {
    status: 400,
    headers: { 'Content-Type': 'application/json' }
  });
};