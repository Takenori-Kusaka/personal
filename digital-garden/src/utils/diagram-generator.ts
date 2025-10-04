import type { CollectionEntry } from 'astro:content';

export interface DiagramConfig {
  type: 'flowchart' | 'mindmap' | 'timeline' | 'impact-flow' | 'sequence' | 'gantt' | 'pie';
  title: string;
  theme: 'default' | 'dark' | 'neutral' | 'forest' | 'base';
  responsive: boolean;
  exportable: boolean;
}

export interface GeneratedDiagram {
  config: DiagramConfig;
  diagram: string;
  metadata: {
    generatedAt: string;
    sourceData: string;
    complexity: 'simple' | 'medium' | 'complex';
    estimatedRenderTime: number;
  };
}

export class DiagramGenerator {
  /**
   * Generate impact flow diagram from insight impact analysis
   */
  static generateImpactFlow(insight: CollectionEntry<'insights'>): GeneratedDiagram {
    const { title, exhibition, impact } = insight.data;

    if (!impact) {
      throw new Error('No impact data available for diagram generation');
    }

    const diagram = `graph TD
      A["${exhibition}"] --> B["${this.truncateText(title, 40)}"]
      B --> C[Business Value]
      B --> D[Implementation Feasibility]
      B --> E[Social Impact]
      B --> F[Strategic Alignment]

      C --> C1["Market Opportunity<br/>${this.getScoreBar(impact.businessValue?.marketOpportunity)}"]
      C --> C2["Revenue Potential<br/>${this.getScoreBar(impact.businessValue?.revenuePotential)}"]

      D --> D1["Technical Complexity<br/>${this.getScoreBar(impact.implementationFeasibility?.technicalComplexity, true)}"]
      D --> D2["Resource Requirements<br/>${this.getScoreBar(impact.implementationFeasibility?.resourceRequirements, true)}"]

      E --> E1["User Benefit<br/>${this.getScoreBar(impact.socialImpact?.userBenefit)}"]
      E --> E2["Societal Contribution<br/>${this.getScoreBar(impact.socialImpact?.societalContribution)}"]

      F --> F1["Vision Fit<br/>${this.getScoreBar(impact.strategicAlignment?.visionFit)}"]
      F --> F2["Skill Development<br/>${this.getScoreBar(impact.strategicAlignment?.skillDevelopment)}"]

      %% Styling
      classDef exhibition fill:#e0f2fe,stroke:#0277bd,stroke-width:2px
      classDef insight fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
      classDef dimension fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
      classDef criteria fill:#e8f5e8,stroke:#388e3c,stroke-width:1px

      class A exhibition
      class B insight
      class C,D,E,F dimension
      class C1,C2,D1,D2,E1,E2,F1,F2 criteria`;

    return {
      config: {
        type: 'impact-flow',
        title: `Impact Analysis: ${this.truncateText(title, 50)}`,
        theme: 'default',
        responsive: true,
        exportable: true
      },
      diagram,
      metadata: {
        generatedAt: new Date().toISOString(),
        sourceData: 'impact_analysis',
        complexity: 'complex',
        estimatedRenderTime: 800
      }
    };
  }

  /**
   * Generate timeline diagram from insight chronology
   */
  static generateTimeline(insights: CollectionEntry<'insights'>[]): GeneratedDiagram {
    // Sort insights by date
    const sortedInsights = insights
      .sort((a, b) => new Date(a.data.date).getTime() - new Date(b.data.date).getTime())
      .slice(0, 10); // Limit to 10 items for readability

    const diagram = `timeline
      title Innovation Timeline

      ${sortedInsights.map(insight => {
        const date = new Date(insight.data.date);
        const monthYear = date.toLocaleDateString('ja-JP', {
          year: 'numeric',
          month: 'short'
        });

        return `${monthYear} : ${this.truncateText(insight.data.title, 30)}
                         : ${insight.data.exhibition}`;
      }).join('\n      ')}`;

    return {
      config: {
        type: 'timeline',
        title: 'Innovation Discovery Timeline',
        theme: 'default',
        responsive: true,
        exportable: true
      },
      diagram,
      metadata: {
        generatedAt: new Date().toISOString(),
        sourceData: 'multiple_insights',
        complexity: 'medium',
        estimatedRenderTime: 600
      }
    };
  }

  /**
   * Generate mindmap diagram from categories and themes
   */
  static generateMindmap(
    categories: Array<{ name: string; count: number; keywords?: string[] }>,
    themes: string[]
  ): GeneratedDiagram {
    const topCategories = categories.slice(0, 6);
    const mainThemes = themes.slice(0, 4);

    const diagram = `mindmap
  root((Digital Garden<br/>Insights))
    Categories
      ${topCategories.map(cat => {
        const keywords = cat.keywords?.slice(0, 3) || [];
        return `${cat.name} (${cat.count})
        ${keywords.map(keyword => `  ${keyword}`).join('\n        ')}`;
      }).join('\n      ')}
    Themes
      ${mainThemes.map(theme => `"${this.truncateText(theme, 20)}"`).join('\n      ')}`;

    return {
      config: {
        type: 'mindmap',
        title: 'Knowledge Map Overview',
        theme: 'forest',
        responsive: true,
        exportable: true
      },
      diagram,
      metadata: {
        generatedAt: new Date().toISOString(),
        sourceData: 'categories_themes',
        complexity: 'medium',
        estimatedRenderTime: 500
      }
    };
  }

  /**
   * Generate pie chart from category distribution
   */
  static generateCategoryPie(
    categories: Array<{ name: string; count: number }>
  ): GeneratedDiagram {
    const diagram = `pie title Category Distribution
      ${categories.map(cat => `"${cat.name}" : ${cat.count}`).join('\n    ')}`;

    return {
      config: {
        type: 'pie',
        title: 'Insight Categories Distribution',
        theme: 'default',
        responsive: true,
        exportable: true
      },
      diagram,
      metadata: {
        generatedAt: new Date().toISOString(),
        sourceData: 'category_counts',
        complexity: 'simple',
        estimatedRenderTime: 300
      }
    };
  }

  /**
   * Generate Gantt chart from action items
   */
  static generateActionGantt(
    actionItems: Array<{
      title: string;
      priority: string;
      estimatedHours?: number;
      deadline?: Date;
      status: string;
      category: string;
    }>
  ): GeneratedDiagram {
    const now = new Date();
    const endDate = new Date(now.getTime() + 60 * 24 * 60 * 60 * 1000); // 60 days from now

    const diagram = `gantt
    title Action Items Timeline
    dateFormat YYYY-MM-DD
    axisFormat %m/%d

    ${actionItems.map((item, index) => {
      const startDate = now.toISOString().split('T')[0];
      const itemEndDate = item.deadline
        ? item.deadline.toISOString().split('T')[0]
        : endDate.toISOString().split('T')[0];

      const statusMap = {
        pending: '',
        'in-progress': 'active, ',
        completed: 'done, ',
        cancelled: 'crit, '
      };

      const prioritySection = this.getPrioritySection(item.priority);
      const taskId = `task${index + 1}`;

      return `section ${prioritySection}
    ${this.truncateText(item.title, 30)} :${statusMap[item.status]}${taskId}, ${startDate}, ${itemEndDate}`;
    }).join('\n    ')}`;

    return {
      config: {
        type: 'gantt',
        title: 'Action Items Schedule',
        theme: 'default',
        responsive: true,
        exportable: true
      },
      diagram,
      metadata: {
        generatedAt: new Date().toISOString(),
        sourceData: 'action_items',
        complexity: 'complex',
        estimatedRenderTime: 700
      }
    };
  }

  /**
   * Generate sequence diagram for process flow
   */
  static generateProcessSequence(
    processName: string,
    steps: Array<{ actor: string; action: string; target?: string }>
  ): GeneratedDiagram {
    const actors = [...new Set(steps.map(step => step.actor))];

    const diagram = `sequenceDiagram
    title ${processName}

    ${actors.map(actor => `participant ${actor.replace(/\s+/g, '')}`).join('\n    ')}

    ${steps.map(step => {
      const actor = step.actor.replace(/\s+/g, '');
      const target = step.target ? step.target.replace(/\s+/g, '') : actor;
      return `${actor}->>+${target}: ${this.truncateText(step.action, 40)}`;
    }).join('\n    ')}`;

    return {
      config: {
        type: 'sequence',
        title: `Process Flow: ${processName}`,
        theme: 'default',
        responsive: true,
        exportable: true
      },
      diagram,
      metadata: {
        generatedAt: new Date().toISOString(),
        sourceData: 'process_steps',
        complexity: 'medium',
        estimatedRenderTime: 600
      }
    };
  }

  /**
   * Auto-generate appropriate diagram based on content type
   */
  static autoGenerate(
    content: any,
    contentType: 'insight' | 'weekly-review' | 'category-analysis'
  ): GeneratedDiagram[] {
    const diagrams: GeneratedDiagram[] = [];

    switch (contentType) {
      case 'insight':
        if (content.data?.impact) {
          diagrams.push(this.generateImpactFlow(content));
        }
        break;

      case 'weekly-review':
        if (content.data?.topCategories) {
          diagrams.push(this.generateCategoryPie(content.data.topCategories));
        }
        if (content.data?.actionItemsGenerated > 0 && content.actionItems) {
          diagrams.push(this.generateActionGantt(content.actionItems));
        }
        break;

      case 'category-analysis':
        if (content.categories && content.themes) {
          diagrams.push(this.generateMindmap(content.categories, content.themes));
        }
        break;
    }

    return diagrams;
  }

  /**
   * Generate diagram from natural language description
   */
  static generateFromDescription(
    description: string,
    context?: any
  ): GeneratedDiagram {
    // Simple NLP-based diagram type detection
    const keywords = description.toLowerCase();

    let type: DiagramConfig['type'] = 'flowchart';
    let diagram = '';

    if (keywords.includes('timeline') || keywords.includes('chronolog') || keywords.includes('sequence')) {
      type = 'timeline';
      diagram = this.generateTimelineFromText(description);
    } else if (keywords.includes('impact') || keywords.includes('effect') || keywords.includes('influence')) {
      type = 'impact-flow';
      diagram = this.generateImpactFromText(description);
    } else if (keywords.includes('process') || keywords.includes('workflow') || keywords.includes('step')) {
      type = 'flowchart';
      diagram = this.generateFlowchartFromText(description);
    } else if (keywords.includes('mindmap') || keywords.includes('concept') || keywords.includes('idea')) {
      type = 'mindmap';
      diagram = this.generateMindmapFromText(description);
    } else {
      // Default flowchart
      diagram = this.generateFlowchartFromText(description);
    }

    return {
      config: {
        type,
        title: this.extractTitleFromDescription(description),
        theme: 'default',
        responsive: true,
        exportable: true
      },
      diagram,
      metadata: {
        generatedAt: new Date().toISOString(),
        sourceData: 'natural_language',
        complexity: 'simple',
        estimatedRenderTime: 400
      }
    };
  }

  // Helper methods
  private static truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
  }

  private static getScoreBar(score?: number, inverse = false): string {
    if (typeof score !== 'number') return '■□□□□';

    const normalizedScore = inverse ? 6 - score : score;
    const filled = Math.min(Math.max(normalizedScore, 0), 5);
    const empty = 5 - filled;

    return '■'.repeat(filled) + '□'.repeat(empty);
  }

  private static getPrioritySection(priority: string): string {
    const priorityMap = {
      urgent: 'Urgent',
      high: 'High Priority',
      medium: 'Medium Priority',
      low: 'Low Priority'
    };
    return priorityMap[priority] || 'Other';
  }

  private static extractTitleFromDescription(description: string): string {
    // Extract first sentence or first 50 characters as title
    const firstSentence = description.split('.')[0];
    return this.truncateText(firstSentence, 50);
  }

  private static generateFlowchartFromText(description: string): string {
    // Simple pattern matching for basic flowchart generation
    const sentences = description.split(/[.!?]+/).filter(s => s.trim());

    let diagram = 'graph TD\n';
    sentences.forEach((sentence, index) => {
      const nodeId = String.fromCharCode(65 + index); // A, B, C...
      const text = this.truncateText(sentence.trim(), 30);
      diagram += `    ${nodeId}["${text}"]\n`;

      if (index > 0) {
        const prevNodeId = String.fromCharCode(65 + index - 1);
        diagram += `    ${prevNodeId} --> ${nodeId}\n`;
      }
    });

    return diagram;
  }

  private static generateTimelineFromText(description: string): string {
    // Extract dates and events from text
    const datePattern = /(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})/g;
    const dates = description.match(datePattern) || [];

    let diagram = 'timeline\n    title Process Timeline\n';

    dates.forEach((date, index) => {
      diagram += `    ${date} : Event ${index + 1}\n`;
    });

    return diagram;
  }

  private static generateImpactFromText(description: string): string {
    const impacts = description.split(/[,;]/);

    let diagram = 'graph TD\n    A["Source"] --> B["Impact Analysis"]\n';

    impacts.forEach((impact, index) => {
      const nodeId = String.fromCharCode(67 + index); // C, D, E...
      const text = this.truncateText(impact.trim(), 25);
      diagram += `    B --> ${nodeId}["${text}"]\n`;
    });

    return diagram;
  }

  private static generateMindmapFromText(description: string): string {
    const concepts = description.split(/[,;]/).slice(0, 8);

    let diagram = 'mindmap\n  root((Central Concept))\n';

    concepts.forEach(concept => {
      const text = this.truncateText(concept.trim(), 20);
      diagram += `    ${text}\n`;
    });

    return diagram;
  }
}

// Utility class for diagram validation and optimization
export class DiagramValidator {
  /**
   * Validate Mermaid diagram syntax
   */
  static validate(diagram: string): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Basic syntax validation
    if (!diagram.trim()) {
      errors.push('Diagram cannot be empty');
    }

    // Check for balanced brackets
    const openBrackets = (diagram.match(/\[/g) || []).length;
    const closeBrackets = (diagram.match(/\]/g) || []).length;
    if (openBrackets !== closeBrackets) {
      errors.push('Mismatched square brackets');
    }

    // Check for valid diagram types
    const validTypes = ['graph', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'journey', 'gantt', 'pie', 'gitGraph', 'mindmap', 'timeline'];
    const firstWord = diagram.trim().split(/\s+/)[0];

    if (!validTypes.some(type => diagram.startsWith(type))) {
      errors.push(`Unknown diagram type: ${firstWord}`);
    }

    // Check diagram complexity (node count)
    const nodeCount = (diagram.match(/\w+\[.*?\]/g) || []).length;
    if (nodeCount > 50) {
      errors.push('Diagram too complex (>50 nodes). Consider splitting into multiple diagrams.');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Optimize diagram for better rendering
   */
  static optimize(diagram: string): string {
    let optimized = diagram;

    // Remove excessive whitespace
    optimized = optimized.replace(/\n\s*\n/g, '\n');
    optimized = optimized.replace(/[ \t]+/g, ' ');

    // Ensure proper line breaks
    optimized = optimized.replace(/(\w+)\s*-->\s*(\w+)/g, '\n    $1 --> $2');

    // Add proper indentation
    const lines = optimized.split('\n');
    optimized = lines.map(line => {
      if (line.trim().startsWith('graph') ||
          line.trim().startsWith('sequenceDiagram') ||
          line.trim().startsWith('classDiagram')) {
        return line.trim();
      }
      return line.trim() ? `    ${line.trim()}` : '';
    }).join('\n');

    return optimized;
  }

  /**
   * Estimate rendering performance
   */
  static estimateComplexity(diagram: string): {
    complexity: 'simple' | 'medium' | 'complex';
    nodeCount: number;
    edgeCount: number;
    estimatedRenderTime: number;
  } {
    const nodeCount = (diagram.match(/\w+\[.*?\]/g) || []).length;
    const edgeCount = (diagram.match(/-->/g) || []).length;

    let complexity: 'simple' | 'medium' | 'complex' = 'simple';
    let estimatedRenderTime = 200;

    if (nodeCount > 20 || edgeCount > 25) {
      complexity = 'complex';
      estimatedRenderTime = 800;
    } else if (nodeCount > 10 || edgeCount > 15) {
      complexity = 'medium';
      estimatedRenderTime = 400;
    }

    return {
      complexity,
      nodeCount,
      edgeCount,
      estimatedRenderTime
    };
  }
}