/**
 * Bát Tự (Four Pillars / Ba Zi) calculation API route
 */

import { NextRequest, NextResponse } from 'next/server';

interface BatTuRequest {
  year: number;
  month: number;
  day: number;
  hour: number;
  gender: string;
  label?: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: BatTuRequest = await request.json();
    const { year, month, day, hour, gender, label } = body;
    
    // Validate required fields
    if (!year || !month || !day || hour === undefined || !gender) {
      return NextResponse.json(
        {
          error: 'Missing required fields',
          detail: 'year, month, day, hour, and gender are required'
        },
        { status: 400 }
      );
    }
    
    // Validate ranges
    if (year < 1900 || year > 2100) {
      return NextResponse.json(
        { error: 'Invalid year', detail: 'Year must be between 1900 and 2100' },
        { status: 400 }
      );
    }
    
    if (month < 1 || month > 12) {
      return NextResponse.json(
        { error: 'Invalid month' },
        { status: 400 }
      );
    }
    
    if (day < 1 || day > 31) {
      return NextResponse.json(
        { error: 'Invalid day' },
        { status: 400 }
      );
    }
    
    if (hour < 0 || hour > 23) {
      return NextResponse.json(
        { error: 'Invalid hour' },
        { status: 400 }
      );
    }
    
    // Normalize gender
    const normalizedGender = normalizeGender(gender);
    if (!normalizedGender) {
      return NextResponse.json(
        { error: 'Invalid gender', detail: 'Gender must be "male" or "female"' },
        { status: 400 }
      );
    }
    
    console.log(`Calculating Bát Tự for ${year}-${month}-${day} ${hour}:00`);
    
    // Dynamic import to avoid SSR issues
    const { BaziCalculator } = await import('bazi-calculator-by-alvamind');
    
    // Calculate chart
    const calculator = new (BaziCalculator as any)(year, month, day, hour, normalizedGender === 'male' ? 0 : 1);
    const rawAnalysis = calculator.getCompleteAnalysis();
    
    // Normalize output
    const normalized = normalizeOutput(rawAnalysis, year, month, day, hour, gender, label);
    
    console.log('Bát Tự calculated successfully');
    return NextResponse.json(normalized, { status: 200 });
    
  } catch (error: any) {
    console.error('Bát Tự calculation error:', error);
    return NextResponse.json(
      {
        error: 'Calculation failed',
        detail: error.message || 'Unexpected error occurred'
      },
      { status: 500 }
    );
  }
}

function normalizeGender(gender: string): string | null {
  const g = gender.toLowerCase().trim();
  if (['male', 'nam', '0'].includes(g)) return 'male';
  if (['female', 'nữ', 'nu', '1'].includes(g)) return 'female';
  return null;
}

function normalizeOutput(
  rawAnalysis: any,
  year: number,
  month: number,
  day: number,
  hour: number,
  gender: string,
  label?: string
) {
  const birthDate = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  const birthTime = `${String(hour).padStart(2, '0')}:00`;
  
  return {
    chart_type: 'BATU',
    version: '1.0',
    metadata: {
      label: label || 'Lá số Bát Tự',
      birth_date: birthDate,
      birth_time: birthTime,
      gender: gender,
      calculated_at: new Date().toISOString()
    },
    pillars: {
      year: extractPillar(rawAnalysis, 'year'),
      month: extractPillar(rawAnalysis, 'month'),
      day: extractPillar(rawAnalysis, 'day'),
      hour: extractPillar(rawAnalysis, 'hour')
    },
    elements: extractElements(rawAnalysis),
    raw_data: rawAnalysis
  };
}

function extractPillar(rawAnalysis: any, pillarType: string) {
  const pillar = rawAnalysis?.pillars?.[pillarType] || rawAnalysis?.[pillarType];
  return {
    thien_can: pillar?.heavenlyStem || pillar?.stem || '',
    dia_chi: pillar?.earthlyBranch || pillar?.branch || '',
    nap_am: pillar?.napAm || pillar?.nayin || '',
    hidden_stems: pillar?.hiddenStems || []
  };
}

function extractElements(rawAnalysis: any) {
  return {
    day_master: rawAnalysis?.dayMaster || '',
    elements_count: rawAnalysis?.elementsCount || {},
    strength: rawAnalysis?.strength || '',
    favorable_elements: rawAnalysis?.favorableElements || [],
    unfavorable_elements: rawAnalysis?.unfavorableElements || []
  };
}