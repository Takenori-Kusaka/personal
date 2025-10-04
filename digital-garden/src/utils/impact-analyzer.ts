import type { CollectionEntry } from 'astro:content';
import yaml from 'yaml';

// Impact analysis types
export interface ImpactScore {
  businessValue?: {
    marketOpportunity: number;
    competitiveAdvantage: number;
    revenuePotential: number;
  };
  implementationFeasibility?: {
    technicalComplexity: number;
    resourceRequirements: number;
    timelineEstimate: number;
  };
  socialImpact?: {
    userBenefit: number;
    societalContribution: number;
    sustainability: number;
  };
  strategicAlignment?: {
    visionFit: number;
    skillDevelopment: number;
    networkExpansion: number;
  };
  overallScore?: number;
  confidence?: number;
  notes?: string;
}

export interface ImpactCriteria {
  dimension: string;
  criteria: Array<{
    name: string;
    description: string;
    weight: number;
    scoringGuide: {
      1: string;
      2: string;
      3: string;
      4: string;
      5: string;
    };
  }>;
}

export interface ImpactAnalysisResult {
  scores: ImpactScore;
  recommendations: string[];
  riskFactors: string[];
  actionPriority: 'low' | 'medium' | 'high' | 'urgent';
  confidenceLevel: 'very_low' | 'low' | 'medium' | 'high';
  comparativeRanking?: number;
  metadata: {
    analyzedAt: string;
    dataPoints: number;
    algorithm: string;
    version: string;
  };
}

export class ImpactAnalyzer {
  private criteriaConfig: ImpactCriteria[];
  private weights: Record<string, number>;

  constructor(criteriaConfigPath?: string) {
    // Default weights from impact-criteria.yaml
    this.weights = {
      business_value: 0.3,
      implementation_feasibility: 0.25,
      social_impact: 0.25,
      strategic_alignment: 0.2
    };
  }

  /**
   * Initialize analyzer with criteria configuration
   */
  async initialize(criteriaConfig: any) {
    try {
      if (typeof criteriaConfig === 'string') {
        // Parse YAML content if string
        const config = yaml.parse(criteriaConfig);
        this.loadCriteriaFromConfig(config);
      } else {
        // Use provided config object
        this.loadCriteriaFromConfig(criteriaConfig);
      }
    } catch (error) {
      console.error('Failed to initialize impact analyzer:', error);
      throw new Error(`Impact analyzer initialization failed: ${error.message}`);
    }
  }

  /**
   * Analyze impact of an insight
   */
  async analyzeInsight(insight: CollectionEntry<'insights'>): Promise<ImpactAnalysisResult> {
    const startTime = Date.now();

    try {
      // Extract data for analysis
      const {
        title,
        category,
        exhibition,
        keyInsights,
        content,
        impact: existingImpact
      } = insight.data;

      // Calculate impact scores
      const scores = existingImpact || await this.calculateImpactScores({
        title,
        category,
        exhibition,
        keyInsights,
        content: insight.body || ''
      });

      // Calculate overall score
      const overallScore = this.calculateOverallScore(scores);
      scores.overallScore = overallScore;

      // Determine confidence level
      const confidenceLevel = this.determineConfidenceLevel(scores.confidence || 0.5);

      // Generate recommendations
      const recommendations = this.generateRecommendations(scores, category);

      // Identify risk factors
      const riskFactors = this.identifyRiskFactors(scores);

      // Determine action priority
      const actionPriority = this.determineActionPriority(overallScore, scores.confidence || 0.5);

      const processingTime = Date.now() - startTime;

      return {
        scores,
        recommendations,
        riskFactors,
        actionPriority,
        confidenceLevel,
        metadata: {
          analyzedAt: new Date().toISOString(),
          dataPoints: this.countDataPoints(scores),
          algorithm: 'weighted_multi_criteria_v1.0',
          version: '1.0.0'
        }
      };

    } catch (error) {
      console.error('Impact analysis failed:', error);
      throw new Error(`Impact analysis failed: ${error.message}`);
    }
  }

  /**
   * Calculate impact scores using content analysis
   */
  private async calculateImpactScores(data: {
    title: string;
    category: string[];
    exhibition: string;
    keyInsights?: string[];
    content: string;
  }): Promise<ImpactScore> {
    // This is a simplified scoring algorithm
    // In a real implementation, you might use ML models or more sophisticated NLP

    const scores: ImpactScore = {};

    // Business Value Analysis
    scores.businessValue = {
      marketOpportunity: this.analyzeMarketOpportunity(data),
      competitiveAdvantage: this.analyzeCompetitiveAdvantage(data),
      revenuePotential: this.analyzeRevenuePotential(data)
    };

    // Implementation Feasibility Analysis
    scores.implementationFeasibility = {
      technicalComplexity: this.analyzeTechnicalComplexity(data),
      resourceRequirements: this.analyzeResourceRequirements(data),
      timelineEstimate: this.analyzeTimelineEstimate(data)
    };

    // Social Impact Analysis
    scores.socialImpact = {
      userBenefit: this.analyzeUserBenefit(data),
      societalContribution: this.analyzeSocietalContribution(data),
      sustainability: this.analyzeSustainability(data)
    };

    // Strategic Alignment Analysis
    scores.strategicAlignment = {
      visionFit: this.analyzeVisionFit(data),
      skillDevelopment: this.analyzeSkillDevelopment(data),
      networkExpansion: this.analyzeNetworkExpansion(data)
    };

    // Calculate confidence based on data completeness and quality
    scores.confidence = this.calculateConfidence(data);

    return scores;
  }

  /**
   * Calculate weighted overall score
   */
  private calculateOverallScore(scores: ImpactScore): number {
    let totalScore = 0;
    let totalWeight = 0;

    // Business Value
    if (scores.businessValue) {
      const bvScore = (
        scores.businessValue.marketOpportunity * 0.4 +
        scores.businessValue.competitiveAdvantage * 0.3 +
        scores.businessValue.revenuePotential * 0.3
      );
      totalScore += bvScore * this.weights.business_value;
      totalWeight += this.weights.business_value;
    }

    // Implementation Feasibility (inverse scoring for complexity/requirements)
    if (scores.implementationFeasibility) {
      const ifScore = (
        (6 - scores.implementationFeasibility.technicalComplexity) * 0.4 +
        (6 - scores.implementationFeasibility.resourceRequirements) * 0.3 +
        (6 - scores.implementationFeasibility.timelineEstimate) * 0.3
      );
      totalScore += ifScore * this.weights.implementation_feasibility;
      totalWeight += this.weights.implementation_feasibility;
    }

    // Social Impact
    if (scores.socialImpact) {
      const siScore = (
        scores.socialImpact.userBenefit * 0.4 +
        scores.socialImpact.societalContribution * 0.3 +
        scores.socialImpact.sustainability * 0.3
      );
      totalScore += siScore * this.weights.social_impact;
      totalWeight += this.weights.social_impact;
    }

    // Strategic Alignment
    if (scores.strategicAlignment) {
      const saScore = (
        scores.strategicAlignment.visionFit * 0.3 +
        scores.strategicAlignment.skillDevelopment * 0.35 +
        scores.strategicAlignment.networkExpansion * 0.35
      );
      totalScore += saScore * this.weights.strategic_alignment;
      totalWeight += this.weights.strategic_alignment;
    }

    return totalWeight > 0 ? totalScore / totalWeight : 0;
  }

  /**
   * Generate actionable recommendations
   */
  private generateRecommendations(scores: ImpactScore, categories: string[]): string[] {
    const recommendations: string[] = [];

    // Business value recommendations
    if (scores.businessValue) {
      if (scores.businessValue.marketOpportunity >= 4) {
        recommendations.push('高い市場機会があります。迅速な市場参入戦略を検討してください。');
      }
      if (scores.businessValue.revenuePotential >= 4) {
        recommendations.push('収益化の可能性が高いです。ビジネスモデルの詳細設計を進めてください。');
      }
      if (scores.businessValue.competitiveAdvantage <= 2) {
        recommendations.push('競合優位性の強化が必要です。差別化要素の明確化を検討してください。');
      }
    }

    // Implementation recommendations
    if (scores.implementationFeasibility) {
      if (scores.implementationFeasibility.technicalComplexity >= 4) {
        recommendations.push('技術的複雑度が高いです。段階的な実装アプローチを検討してください。');
      }
      if (scores.implementationFeasibility.resourceRequirements >= 4) {
        recommendations.push('大きなリソースが必要です。投資計画と体制構築を優先してください。');
      }
      if (scores.implementationFeasibility.timelineEstimate >= 4) {
        recommendations.push('長期的なプロジェクトです。マイルストーンの設定と進捗管理が重要です。');
      }
    }

    // Strategic alignment recommendations
    if (scores.strategicAlignment) {
      if (scores.strategicAlignment.visionFit >= 4) {
        recommendations.push('戦略的適合性が高いです。優先的に取り組むことをお勧めします。');
      }
      if (scores.strategicAlignment.skillDevelopment >= 4) {
        recommendations.push('スキル開発の機会が大きいです。人材育成計画と連携してください。');
      }
    }

    // Category-specific recommendations
    if (categories.includes('ai_machine_learning')) {
      recommendations.push('AI技術は急速に進歩しています。継続的な技術動向の監視が必要です。');
    }
    if (categories.includes('sustainability')) {
      recommendations.push('持続可能性は長期的な価値創造に不可欠です。ESG観点での評価も検討してください。');
    }

    return recommendations.length > 0 ? recommendations : [
      '包括的な影響分析に基づいて慎重に判断することをお勧めします。'
    ];
  }

  /**
   * Identify risk factors
   */
  private identifyRiskFactors(scores: ImpactScore): string[] {
    const risks: string[] = [];

    if (scores.implementationFeasibility) {
      if (scores.implementationFeasibility.technicalComplexity >= 4) {
        risks.push('高い技術的リスク - 実装の不確実性');
      }
      if (scores.implementationFeasibility.resourceRequirements >= 4) {
        risks.push('大きな投資リスク - ROI達成の不確実性');
      }
    }

    if (scores.businessValue?.competitiveAdvantage <= 2) {
      risks.push('競合リスク - 差別化の困難性');
    }

    if (scores.confidence && scores.confidence < 0.6) {
      risks.push('情報不足リスク - 判断材料の不足');
    }

    return risks;
  }

  /**
   * Determine action priority
   */
  private determineActionPriority(
    overallScore: number,
    confidence: number
  ): 'low' | 'medium' | 'high' | 'urgent' {
    if (overallScore >= 4.0 && confidence >= 0.7) return 'urgent';
    if (overallScore >= 3.5 && confidence >= 0.6) return 'high';
    if (overallScore >= 2.5 && confidence >= 0.5) return 'medium';
    return 'low';
  }

  /**
   * Determine confidence level
   */
  private determineConfidenceLevel(confidence: number): 'very_low' | 'low' | 'medium' | 'high' {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.6) return 'medium';
    if (confidence >= 0.4) return 'low';
    return 'very_low';
  }

  // Content analysis methods (simplified implementations)
  private analyzeMarketOpportunity(data: any): number {
    const content = data.content.toLowerCase();
    const keywords = ['市場', 'market', '成長', 'growth', '機会', 'opportunity'];
    const score = keywords.reduce((acc, keyword) =>
      acc + (content.includes(keyword) ? 0.5 : 0), 0
    );
    return Math.min(Math.max(Math.round(score * 2), 1), 5);
  }

  private analyzeCompetitiveAdvantage(data: any): number {
    const content = data.content.toLowerCase();
    const keywords = ['独自', '差別化', 'unique', 'differentiation', '優位', 'advantage'];
    const score = keywords.reduce((acc, keyword) =>
      acc + (content.includes(keyword) ? 0.5 : 0), 0
    );
    return Math.min(Math.max(Math.round(score * 2), 1), 5);
  }

  private analyzeRevenuePotential(data: any): number {
    const content = data.content.toLowerCase();
    const keywords = ['収益', 'revenue', '売上', 'profit', 'ビジネス', 'business'];
    const score = keywords.reduce((acc, keyword) =>
      acc + (content.includes(keyword) ? 0.5 : 0), 0
    );
    return Math.min(Math.max(Math.round(score * 2), 1), 5);
  }

  private analyzeTechnicalComplexity(data: any): number {
    const content = data.content.toLowerCase();
    const complexKeywords = ['complex', '複雑', 'difficult', '困難', 'challenge', '課題'];
    const score = complexKeywords.reduce((acc, keyword) =>
      acc + (content.includes(keyword) ? 0.5 : 0), 0
    );
    return Math.min(Math.max(Math.round(score * 2), 1), 5);
  }

  private analyzeResourceRequirements(data: any): number {
    const content = data.content.toLowerCase();
    const keywords = ['投資', 'investment', 'cost', 'コスト', 'resource', 'リソース'];
    const score = keywords.reduce((acc, keyword) =>
      acc + (content.includes(keyword) ? 0.3 : 0), 0
    );
    return Math.min(Math.max(Math.round(score * 3), 1), 5);
  }

  private analyzeTimelineEstimate(data: any): number {
    const content = data.content.toLowerCase();
    const timeKeywords = ['年', 'year', 'ヶ月', 'month', '長期', 'long-term'];
    const score = timeKeywords.reduce((acc, keyword) =>
      acc + (content.includes(keyword) ? 0.4 : 0), 0
    );
    return Math.min(Math.max(Math.round(score * 3), 1), 5);
  }

  private analyzeUserBenefit(data: any): number {
    const content = data.content.toLowerCase();
    const keywords = ['ユーザー', 'user', '顧客', 'customer', '便利', 'benefit'];
    const score = keywords.reduce((acc, keyword) =>
      acc + (content.includes(keyword) ? 0.4 : 0), 0
    );
    return Math.min(Math.max(Math.round(score * 3), 1), 5);
  }

  private analyzeSocietalContribution(data: any): number {
    const content = data.content.toLowerCase();
    const keywords = ['社会', 'society', '貢献', 'contribution', '改善', 'improvement'];
    const score = keywords.reduce((acc, keyword) =>
      acc + (content.includes(keyword) ? 0.4 : 0), 0
    );
    return Math.min(Math.max(Math.round(score * 3), 1), 5);
  }

  private analyzeSustainability(data: any): number {
    const content = data.content.toLowerCase();
    const keywords = ['持続', 'sustain', '環境', 'environment', 'green', 'eco'];
    const score = keywords.reduce((acc, keyword) =>
      acc + (content.includes(keyword) ? 0.5 : 0), 0
    );
    return Math.min(Math.max(Math.round(score * 2), 1), 5);
  }

  private analyzeVisionFit(data: any): number {
    // In a real implementation, this would compare against organizational vision
    const categories = data.category || [];
    const strategicCategories = ['technology', 'ai_machine_learning', 'digital_transformation'];
    const fit = categories.some(cat => strategicCategories.includes(cat)) ? 4 : 3;
    return Math.min(fit, 5);
  }

  private analyzeSkillDevelopment(data: any): number {
    const content = data.content.toLowerCase();
    const keywords = ['学習', 'learning', 'skill', 'スキル', '技術', 'technology'];
    const score = keywords.reduce((acc, keyword) =>
      acc + (content.includes(keyword) ? 0.4 : 0), 0
    );
    return Math.min(Math.max(Math.round(score * 3), 1), 5);
  }

  private analyzeNetworkExpansion(data: any): number {
    const exhibition = data.exhibition || '';
    const isInternational = ['international', 'global', 'world'].some(term =>
      exhibition.toLowerCase().includes(term)
    );
    return isInternational ? 4 : 3;
  }

  private calculateConfidence(data: any): number {
    let confidence = 0.5; // Base confidence

    // Adjust based on data completeness
    if (data.keyInsights && data.keyInsights.length > 0) confidence += 0.1;
    if (data.content && data.content.length > 1000) confidence += 0.1;
    if (data.category && data.category.length > 0) confidence += 0.1;
    if (data.exhibition) confidence += 0.1;

    // Adjust based on data quality indicators
    const content = data.content || '';
    if (content.includes('データ') || content.includes('data')) confidence += 0.1;
    if (content.includes('実証') || content.includes('proven')) confidence += 0.1;

    return Math.min(confidence, 1.0);
  }

  private countDataPoints(scores: ImpactScore): number {
    let count = 0;

    if (scores.businessValue) count += Object.keys(scores.businessValue).length;
    if (scores.implementationFeasibility) count += Object.keys(scores.implementationFeasibility).length;
    if (scores.socialImpact) count += Object.keys(scores.socialImpact).length;
    if (scores.strategicAlignment) count += Object.keys(scores.strategicAlignment).length;

    return count;
  }

  private loadCriteriaFromConfig(config: any): void {
    // Load configuration from the impact-criteria.yaml structure
    this.criteriaConfig = [];

    Object.keys(config).forEach(key => {
      if (key !== 'overall_calculation' && key !== 'confidence_levels' && config[key].dimension) {
        this.criteriaConfig.push(config[key]);
      }
    });

    // Load weights if available
    if (config.overall_calculation?.weights) {
      this.weights = config.overall_calculation.weights;
    }
  }

  /**
   * Batch analyze multiple insights
   */
  async batchAnalyze(insights: CollectionEntry<'insights'>[]): Promise<Array<{
    slug: string;
    analysis: ImpactAnalysisResult;
  }>> {
    const results = [];

    for (const insight of insights) {
      try {
        const analysis = await this.analyzeInsight(insight);
        results.push({
          slug: insight.slug,
          analysis
        });

        // Rate limiting
        await new Promise(resolve => setTimeout(resolve, 100));
      } catch (error) {
        console.error(`Failed to analyze ${insight.slug}:`, error);
        // Continue with other insights
      }
    }

    return results;
  }

  /**
   * Compare insights by impact scores
   */
  static compareInsights(
    insights: Array<{ analysis: ImpactAnalysisResult }>
  ): Array<{ analysis: ImpactAnalysisResult; rank: number }> {
    const sorted = insights
      .filter(item => item.analysis.scores.overallScore)
      .sort((a, b) => b.analysis.scores.overallScore! - a.analysis.scores.overallScore!)
      .map((item, index) => ({
        ...item,
        rank: index + 1
      }));

    return sorted;
  }

  /**
   * Generate impact analysis report
   */
  static generateReport(analyses: Array<{ slug: string; analysis: ImpactAnalysisResult }>): string {
    const totalCount = analyses.length;
    const avgScore = analyses.reduce((sum, item) =>
      sum + (item.analysis.scores.overallScore || 0), 0) / totalCount;

    const priorityDistribution = analyses.reduce((acc, item) => {
      acc[item.analysis.actionPriority] = (acc[item.analysis.actionPriority] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const topInsights = analyses
      .sort((a, b) => (b.analysis.scores.overallScore || 0) - (a.analysis.scores.overallScore || 0))
      .slice(0, 5);

    return `# Impact Analysis Report

## Summary
- Total insights analyzed: ${totalCount}
- Average impact score: ${avgScore.toFixed(2)}/5.0
- High priority insights: ${priorityDistribution.high || 0}
- Urgent insights: ${priorityDistribution.urgent || 0}

## Priority Distribution
- Urgent: ${priorityDistribution.urgent || 0}
- High: ${priorityDistribution.high || 0}
- Medium: ${priorityDistribution.medium || 0}
- Low: ${priorityDistribution.low || 0}

## Top 5 Insights by Impact Score
${topInsights.map((item, index) =>
  `${index + 1}. ${item.slug} (Score: ${item.analysis.scores.overallScore?.toFixed(2)})`
).join('\n')}

Generated at: ${new Date().toISOString()}`;
  }
}