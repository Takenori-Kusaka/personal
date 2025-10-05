import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { ImpactAnalyzer, type ImpactAnalysisResult } from '../../utils/impact-analyzer';

export interface ImpactAnalysisRequest {
  slug?: string; // Single insight analysis
  slugs?: string[]; // Batch analysis
  forceReanalysis?: boolean;
  includeComparison?: boolean;
}

export interface ImpactAnalysisResponse {
  success: boolean;
  analysis?: ImpactAnalysisResult;
  batchAnalysis?: Array<{
    slug: string;
    analysis: ImpactAnalysisResult;
    rank?: number;
  }>;
  comparison?: {
    averageScore: number;
    topInsights: Array<{
      slug: string;
      score: number;
      priority: string;
    }>;
    priorityDistribution: Record<string, number>;
  };
  error?: string;
  metadata?: {
    processedAt: string;
    processingTime: number;
    insightsProcessed: number;
  };
}

export const POST: APIRoute = async ({ request }) => {
  const startTime = Date.now();

  try {
    // Parse request
    const requestData: ImpactAnalysisRequest = await request.json();
    const { slug, slugs, forceReanalysis = false, includeComparison = false } = requestData;

    // Validate request
    if (!slug && !slugs) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Either slug or slugs parameter is required'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Initialize analyzer
    const analyzer = new ImpactAnalyzer();

    // Load impact criteria configuration
    try {
      // In a real implementation, load from content/config/impact-criteria.yaml
      const criteriaConfig = {
        business_value: {
          dimension: 'Business Value',
          criteria: [
            {
              name: 'market_opportunity',
              description: '市場機会の大きさと成長性',
              weight: 0.4,
              scoringGuide: {
                1: 'ニッチ市場または縮小市場（<10億円）',
                2: '小規模市場、限定的な成長性（10-50億円）',
                3: '中規模市場、安定した成長性（50-200億円）',
                4: '大規模市場、高い成長性（200-1000億円）',
                5: '巨大市場、急成長中（>1000億円）'
              }
            }
          ]
        },
        overall_calculation: {
          method: 'weighted_average',
          weights: {
            business_value: 0.3,
            implementation_feasibility: 0.25,
            social_impact: 0.25,
            strategic_alignment: 0.2
          }
        }
      };

      await analyzer.initialize(criteriaConfig);
    } catch (initError) {
      console.warn('Using default configuration:', initError);
    }

    // Get insights collection
    const insights = await getCollection('insights');

    let response: ImpactAnalysisResponse;

    if (slug) {
      // Single insight analysis
      const insight = insights.find(i => i.slug === slug);
      if (!insight) {
        return new Response(JSON.stringify({
          success: false,
          error: `Insight with slug '${slug}' not found`
        }), {
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      // Check if analysis already exists and force reanalysis is not requested
      if (insight.data.impact && !forceReanalysis) {
        response = {
          success: true,
          analysis: {
            scores: insight.data.impact,
            recommendations: ['使用既存の影響分析結果'],
            riskFactors: [],
            actionPriority: 'medium',
            confidenceLevel: 'medium',
            metadata: {
              analyzedAt: new Date().toISOString(),
              dataPoints: Object.keys(insight.data.impact).length,
              algorithm: 'existing_data_v1.0',
              version: '1.0.0'
            }
          }
        };
      } else {
        // Perform new analysis
        const analysis = await analyzer.analyzeInsight(insight);
        response = {
          success: true,
          analysis
        };
      }

    } else if (slugs) {
      // Batch analysis
      const targetInsights = insights.filter(i => slugs.includes(i.slug));

      if (targetInsights.length === 0) {
        return new Response(JSON.stringify({
          success: false,
          error: 'No matching insights found for provided slugs'
        }), {
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      const batchResults = await analyzer.batchAnalyze(targetInsights);

      // Add rankings if comparison is requested
      let rankedResults = batchResults;
      if (includeComparison) {
        rankedResults = ImpactAnalyzer.compareInsights(
          batchResults.map(r => ({ analysis: r.analysis }))
        ).map((item, index) => ({
          slug: batchResults[index].slug,
          analysis: item.analysis,
          rank: item.rank
        }));
      }

      response = {
        success: true,
        batchAnalysis: rankedResults
      };

      // Add comparison data
      if (includeComparison) {
        const scores = batchResults
          .map(r => r.analysis.scores.overallScore || 0)
          .filter(s => s > 0);

        const averageScore = scores.length > 0
          ? scores.reduce((sum, score) => sum + score, 0) / scores.length
          : 0;

        const topInsights = rankedResults
          .filter(r => r.analysis.scores.overallScore)
          .slice(0, 5)
          .map(r => ({
            slug: r.slug,
            score: r.analysis.scores.overallScore!,
            priority: r.analysis.actionPriority
          }));

        const priorityDistribution = batchResults.reduce((acc, r) => {
          const priority = r.analysis.actionPriority;
          acc[priority] = (acc[priority] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);

        response.comparison = {
          averageScore,
          topInsights,
          priorityDistribution
        };
      }
    }

    // Add metadata
    const processingTime = Date.now() - startTime;
    response.metadata = {
      processedAt: new Date().toISOString(),
      processingTime,
      insightsProcessed: slugs ? slugs.length : 1
    };

    return new Response(JSON.stringify(response), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Impact analysis error:', error);

    const processingTime = Date.now() - startTime;
    const errorResponse: ImpactAnalysisResponse = {
      success: false,
      error: error.message,
      metadata: {
        processedAt: new Date().toISOString(),
        processingTime,
        insightsProcessed: 0
      }
    };

    return new Response(JSON.stringify(errorResponse), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

export const GET: APIRoute = async ({ url }) => {
  // Health check and utilities

  if (url.searchParams.get('health') === 'true') {
    return new Response(JSON.stringify({
      status: 'ok',
      service: 'impact-analysis',
      version: '1.0.0',
      timestamp: new Date().toISOString()
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // Get analysis status for a specific insight
  const slug = url.searchParams.get('slug');
  if (slug) {
    try {
      const insights = await getCollection('insights');
      const insight = insights.find(i => i.slug === slug);

      if (!insight) {
        return new Response(JSON.stringify({
          error: `Insight '${slug}' not found`
        }), {
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      const hasAnalysis = !!insight.data.impact;
      const analysisDate = hasAnalysis
        ? insight.data.lastModified || insight.data.date
        : null;

      return new Response(JSON.stringify({
        slug,
        hasAnalysis,
        analysisDate: analysisDate?.toISOString(),
        overallScore: insight.data.impact?.overallScore,
        confidence: insight.data.impact?.confidence
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      return new Response(JSON.stringify({
        error: error.message
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  // Get overall statistics
  if (url.searchParams.get('stats') === 'true') {
    try {
      const insights = await getCollection('insights');
      const analyzedInsights = insights.filter(i => i.data.impact);

      const stats = {
        totalInsights: insights.length,
        analyzedInsights: analyzedInsights.length,
        analysisRate: insights.length > 0 ? (analyzedInsights.length / insights.length) * 100 : 0,
        averageScore: analyzedInsights.length > 0
          ? analyzedInsights.reduce((sum, i) => sum + (i.data.impact?.overallScore || 0), 0) / analyzedInsights.length
          : 0,
        priorityDistribution: analyzedInsights.reduce((acc, insight) => {
          // Simple priority calculation based on score
          const score = insight.data.impact?.overallScore || 0;
          const priority = score >= 4.0 ? 'urgent' :
                          score >= 3.5 ? 'high' :
                          score >= 2.5 ? 'medium' : 'low';
          acc[priority] = (acc[priority] || 0) + 1;
          return acc;
        }, {} as Record<string, number>)
      };

      return new Response(JSON.stringify(stats), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      return new Response(JSON.stringify({
        error: error.message
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  return new Response(JSON.stringify({
    error: 'Invalid request. Use POST for analysis or GET with ?health=true, ?slug=<slug>, or ?stats=true'
  }), {
    status: 400,
    headers: { 'Content-Type': 'application/json' }
  });
};