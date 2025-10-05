import { GoogleAuth } from 'google-auth-library';

// Types for Imagen 4 API
export interface ImageGenerationRequest {
  prompt: string;
  aspectRatio?: '1:1' | '3:4' | '4:3' | '9:16' | '16:9';
  negativePrompt?: string;
  sampleCount?: number;
  seed?: number;
  guidanceScale?: number;
  safetyFilterLevel?: 'block_most' | 'block_some' | 'block_few' | 'block_none';
  personGeneration?: 'allow_adult' | 'allow_all' | 'dont_allow';
  includeSafetyAttributes?: boolean;
  outputMimeType?: 'image/png' | 'image/jpeg';
}

export interface ImageGenerationResponse {
  predictions: Array<{
    bytesBase64Encoded: string;
    mimeType: string;
    safetyAttributes?: {
      categories: string[];
      scores: number[];
      blocked: boolean;
    };
  }>;
}

export interface ThumbnailConfig {
  style: 'professional' | 'creative' | 'technical' | 'minimal';
  theme: 'light' | 'dark' | 'auto';
  includeJapaneseText?: boolean;
  brandingElements?: boolean;
}

export class ImagenClient {
  private auth: GoogleAuth;
  private projectId: string;
  private location: string;
  private modelId: string;

  constructor(
    projectId?: string,
    location: string = 'us-central1',
    modelId: string = 'imagen-3.0-generate-001'
  ) {
    if (!projectId) {
      throw new Error('Google Cloud Project ID is required');
    }

    this.projectId = projectId;
    this.location = location;
    this.modelId = modelId;

    this.auth = new GoogleAuth({
      scopes: ['https://www.googleapis.com/auth/cloud-platform'],
    });
  }

  /**
   * Generate thumbnail for exhibition insight
   */
  async generateInsightThumbnail(
    title: string,
    exhibition: string,
    category: string[],
    keyInsights: string[],
    config: ThumbnailConfig = { style: 'professional', theme: 'light' }
  ): Promise<string> {
    const prompt = this.buildInsightPrompt(title, exhibition, category, keyInsights, config);
    const negativePrompt = this.buildNegativePrompt(config);

    try {
      const response = await this.generateImage({
        prompt,
        negativePrompt,
        aspectRatio: '16:9',
        sampleCount: 1,
        guidanceScale: 20,
        safetyFilterLevel: 'block_most',
        personGeneration: 'dont_allow',
        outputMimeType: 'image/jpeg',
      });

      if (response.predictions.length === 0) {
        throw new Error('No images generated');
      }

      const prediction = response.predictions[0];
      if (prediction.safetyAttributes?.blocked) {
        throw new Error('Image blocked by safety filter');
      }

      return prediction.bytesBase64Encoded;
    } catch (error) {
      console.error('Failed to generate thumbnail:', error);
      throw new Error(`Thumbnail generation failed: ${error.message}`);
    }
  }

  /**
   * Generate weekly review visualization
   */
  async generateWeeklyReviewVisual(
    week: string,
    highlights: string[],
    categories: Array<{ name: string; count: number }>,
    themes: string[]
  ): Promise<string> {
    const prompt = this.buildWeeklyReviewPrompt(week, highlights, categories, themes);

    const response = await this.generateImage({
      prompt,
      aspectRatio: '16:9',
      sampleCount: 1,
      guidanceScale: 15,
      safetyFilterLevel: 'block_some',
      outputMimeType: 'image/jpeg',
    });

    return response.predictions[0].bytesBase64Encoded;
  }

  /**
   * Generate concept visualization for complex ideas
   */
  async generateConceptVisualization(
    concept: string,
    context: string,
    style: 'diagram' | 'metaphor' | 'abstract' = 'diagram'
  ): Promise<string> {
    const prompt = this.buildConceptPrompt(concept, context, style);

    const response = await this.generateImage({
      prompt,
      aspectRatio: '4:3',
      sampleCount: 1,
      guidanceScale: 25,
      safetyFilterLevel: 'block_some',
    });

    return response.predictions[0].bytesBase64Encoded;
  }

  /**
   * Core image generation method
   */
  private async generateImage(request: ImageGenerationRequest): Promise<ImageGenerationResponse> {
    const client = await this.auth.getIdTokenClient(
      `https://${this.location}-aiplatform.googleapis.com/`
    );

    const endpoint = `https://${this.location}-aiplatform.googleapis.com/v1/projects/${this.projectId}/locations/${this.location}/publishers/google/models/${this.modelId}:predict`;

    const requestBody = {
      instances: [
        {
          prompt: request.prompt,
          ...(request.negativePrompt && { negative_prompt: request.negativePrompt }),
          ...(request.aspectRatio && { aspect_ratio: request.aspectRatio }),
          ...(request.seed && { seed: request.seed }),
        }
      ],
      parameters: {
        sampleCount: request.sampleCount || 1,
        ...(request.guidanceScale && { guidance_scale: request.guidanceScale }),
        ...(request.safetyFilterLevel && { safety_filter_level: request.safetyFilterLevel }),
        ...(request.personGeneration && { person_generation: request.personGeneration }),
        ...(request.includeSafetyAttributes && { include_safety_attributes: request.includeSafetyAttributes }),
        ...(request.outputMimeType && { output_mime_type: request.outputMimeType }),
      },
    };

    try {
      const response = await client.request({
        url: endpoint,
        method: 'POST',
        data: requestBody,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      return response.data as ImageGenerationResponse;
    } catch (error) {
      console.error('Imagen API error:', error);
      throw new Error(`API request failed: ${error.message}`);
    }
  }

  /**
   * Build prompt for insight thumbnails
   */
  private buildInsightPrompt(
    title: string,
    exhibition: string,
    categories: string[],
    keyInsights: string[],
    config: ThumbnailConfig
  ): string {
    const stylePrompts = {
      professional: 'clean, modern, business-oriented design with subtle gradients',
      creative: 'vibrant, artistic, innovative design with dynamic elements',
      technical: 'structured, diagram-like, engineering-focused with precise layouts',
      minimal: 'simple, elegant, minimalist design with plenty of white space'
    };

    const themePrompts = {
      light: 'bright background, light colors, high contrast text',
      dark: 'dark background, neon accents, glowing elements',
      auto: 'balanced lighting, adaptive colors'
    };

    // Extract key technical terms for visual elements
    const techKeywords = categories.join(', ');
    const primaryInsight = keyInsights[0] || title;

    let prompt = `Professional thumbnail image for "${title}" from ${exhibition}. `;
    prompt += `${stylePrompts[config.style]}, ${themePrompts[config.theme]}. `;
    prompt += `Technology theme: ${techKeywords}. `;
    prompt += `Key concept: ${primaryInsight.slice(0, 100)}. `;

    // Add visual elements based on categories
    if (categories.includes('ai_machine_learning')) {
      prompt += 'Include AI/neural network visual elements, circuit patterns, data flow. ';
    }
    if (categories.includes('manufacturing')) {
      prompt += 'Include factory, industrial equipment, precision machinery elements. ';
    }
    if (categories.includes('iot_sensors')) {
      prompt += 'Include connected devices, sensor networks, wireless signals. ';
    }

    prompt += 'High quality, 4K resolution, suitable for web display. ';
    prompt += 'No text overlays, no human faces, abstract representation preferred. ';

    if (config.includeJapaneseText) {
      prompt += 'Japanese aesthetics, clean typography space for Japanese text. ';
    }

    if (config.brandingElements) {
      prompt += 'Space for company branding, logo placement area. ';
    }

    return prompt;
  }

  /**
   * Build negative prompt for better quality
   */
  private buildNegativePrompt(config: ThumbnailConfig): string {
    let negativePrompt = 'low quality, blurry, pixelated, distorted, ';
    negativePrompt += 'text overlays, watermarks, logos, ';
    negativePrompt += 'people, faces, hands, bodies, ';
    negativePrompt += 'cluttered, busy, confusing layout, ';
    negativePrompt += 'inappropriate content, violence, ';

    if (config.style === 'minimal') {
      negativePrompt += 'complex patterns, too many elements, ';
    }

    if (config.theme === 'professional') {
      negativePrompt += 'cartoon style, childish elements, ';
    }

    return negativePrompt;
  }

  /**
   * Build prompt for weekly review visuals
   */
  private buildWeeklyReviewPrompt(
    week: string,
    highlights: string[],
    categories: Array<{ name: string; count: number }>,
    themes: string[]
  ): string {
    const topCategories = categories.slice(0, 3).map(c => c.name).join(', ');
    const mainThemes = themes.slice(0, 3).join(', ');

    let prompt = `Weekly review visualization for ${week}. `;
    prompt += 'Dashboard-style infographic layout, modern business design. ';
    prompt += `Main themes: ${mainThemes}. `;
    prompt += `Top categories: ${topCategories}. `;
    prompt += 'Clean charts, graphs, progress indicators. ';
    prompt += 'Professional color scheme, data visualization elements. ';
    prompt += 'No text, no specific numbers, abstract representation. ';
    prompt += 'High quality, suitable for presentation use.';

    return prompt;
  }

  /**
   * Build prompt for concept visualization
   */
  private buildConceptPrompt(
    concept: string,
    context: string,
    style: 'diagram' | 'metaphor' | 'abstract'
  ): string {
    const stylePrompts = {
      diagram: 'technical diagram style, flowchart-like, systematic representation',
      metaphor: 'metaphorical representation, symbolic imagery, conceptual visualization',
      abstract: 'abstract geometric forms, conceptual art, symbolic representation'
    };

    let prompt = `Visualization of concept: "${concept}" in context of ${context}. `;
    prompt += `${stylePrompts[style]}. `;
    prompt += 'Clear, understandable visual representation. ';
    prompt += 'Professional quality, suitable for educational/business use. ';
    prompt += 'No text labels, pure visual communication.';

    return prompt;
  }

  /**
   * Save generated image to storage
   */
  async saveImage(
    base64Image: string,
    filename: string,
    directory: 'thumbnails' | 'weekly-reviews' | 'concepts' = 'thumbnails'
  ): Promise<string> {
    try {
      // In a real implementation, this would save to cloud storage
      // For now, we'll simulate the save operation
      const imagePath = `/images/${directory}/${filename}`;

      // Convert base64 to buffer for saving
      const imageBuffer = Buffer.from(base64Image, 'base64');

      // Here you would typically save to Cloudinary, AWS S3, etc.
      // await cloudinaryUpload(imageBuffer, imagePath);

      console.log(`Image saved: ${imagePath} (${imageBuffer.length} bytes)`);
      return imagePath;
    } catch (error) {
      console.error('Failed to save image:', error);
      throw new Error(`Image save failed: ${error.message}`);
    }
  }

  /**
   * Generate batch thumbnails for multiple insights
   */
  async generateBatchThumbnails(
    insights: Array<{
      title: string;
      exhibition: string;
      category: string[];
      keyInsights: string[];
      slug: string;
    }>,
    config: ThumbnailConfig = { style: 'professional', theme: 'light' }
  ): Promise<Array<{ slug: string; imagePath: string }>> {
    const results = [];

    for (const insight of insights) {
      try {
        const base64Image = await this.generateInsightThumbnail(
          insight.title,
          insight.exhibition,
          insight.category,
          insight.keyInsights,
          config
        );

        const filename = `${insight.slug}-thumb.jpg`;
        const imagePath = await this.saveImage(base64Image, filename, 'thumbnails');

        results.push({
          slug: insight.slug,
          imagePath
        });

        // Add delay to respect rate limits
        await new Promise(resolve => setTimeout(resolve, 2000));
      } catch (error) {
        console.error(`Failed to generate thumbnail for ${insight.slug}:`, error);
        results.push({
          slug: insight.slug,
          imagePath: null
        });
      }
    }

    return results;
  }
}

// Utility functions for content processing
export class ContentEnhancer {
  private imagenClient: ImagenClient;

  constructor(projectId: string) {
    this.imagenClient = new ImagenClient(projectId);
  }

  /**
   * Extract visual concepts from markdown content
   */
  extractVisualConcepts(content: string): string[] {
    // Extract key technical terms, product names, concepts
    const patterns = [
      /\*\*([^*]+)\*\*/g, // Bold text
      /`([^`]+)`/g, // Code/technical terms
      /#{1,6}\s+([^\n]+)/g, // Headers
    ];

    const concepts = new Set<string>();

    patterns.forEach(pattern => {
      const matches = content.matchAll(pattern);
      for (const match of matches) {
        const term = match[1].trim();
        if (term.length > 3 && term.length < 50) {
          concepts.add(term);
        }
      }
    });

    return Array.from(concepts).slice(0, 10);
  }

  /**
   * Analyze content sentiment for visual style selection
   */
  analyzeSentiment(content: string): 'positive' | 'negative' | 'neutral' {
    const positiveWords = ['革新', '成功', '向上', '改善', '効率', '最適', '高品質', '画期的'];
    const negativeWords = ['課題', '問題', '困難', '制約', '不足', '低下', '失敗'];

    const positiveCount = positiveWords.reduce((count, word) =>
      count + (content.match(new RegExp(word, 'g')) || []).length, 0
    );

    const negativeCount = negativeWords.reduce((count, word) =>
      count + (content.match(new RegExp(word, 'g')) || []).length, 0
    );

    if (positiveCount > negativeCount * 1.5) return 'positive';
    if (negativeCount > positiveCount * 1.5) return 'negative';
    return 'neutral';
  }

  /**
   * Suggest optimal thumbnail configuration
   */
  suggestThumbnailConfig(
    category: string[],
    content: string,
    exhibition: string
  ): ThumbnailConfig {
    const sentiment = this.analyzeSentiment(content);

    let style: ThumbnailConfig['style'] = 'professional';
    let theme: ThumbnailConfig['theme'] = 'light';

    // Style based on categories
    if (category.includes('ai_machine_learning') || category.includes('technology')) {
      style = 'technical';
    } else if (category.includes('entertainment') || category.includes('creative')) {
      style = 'creative';
    } else if (category.includes('business_model') || category.includes('finance')) {
      style = 'minimal';
    }

    // Theme based on content sentiment and category
    if (category.includes('security') || sentiment === 'negative') {
      theme = 'dark';
    } else if (sentiment === 'positive') {
      theme = 'light';
    } else {
      theme = 'auto';
    }

    return {
      style,
      theme,
      includeJapaneseText: true,
      brandingElements: exhibition.toLowerCase().includes('omron') ||
                       exhibition.toLowerCase().includes('オムロン')
    };
  }
}