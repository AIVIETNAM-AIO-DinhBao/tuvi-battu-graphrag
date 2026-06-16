/**
 * Bát Tự (Four Pillars / Ba Zi) calculation API route
 */

import { NextRequest, NextResponse } from 'next/server';
import {
  BATU_SUPPORTED_YEAR_MAX,
  BATU_SUPPORTED_YEAR_MIN,
  BaziCalculator,
  type GenderType
} from '../../../../lib/battu/calculator';

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
    if (year < BATU_SUPPORTED_YEAR_MIN || year > BATU_SUPPORTED_YEAR_MAX) {
      return NextResponse.json(
        {
          error: 'Invalid year',
          detail: `Year must be between ${BATU_SUPPORTED_YEAR_MIN} and ${BATU_SUPPORTED_YEAR_MAX}`
        },
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

    if (!isValidGregorianDate(year, month, day)) {
      return NextResponse.json(
        { error: 'Invalid date', detail: 'The supplied Gregorian date does not exist' },
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
    
    // Calculate chart
    const calculator = new BaziCalculator(year, month, day, hour, normalizedGender);
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

function normalizeGender(gender: string): GenderType | null {
  const g = gender.toLowerCase().trim();
  if (['male', 'nam', '0'].includes(g)) return 'male';
  if (['female', 'nữ', 'nu', '1'].includes(g)) return 'female';
  return null;
}

function isValidGregorianDate(year: number, month: number, day: number): boolean {
  const date = new Date(Date.UTC(year, month - 1, day));
  return (
    date.getUTCFullYear() === year &&
    date.getUTCMonth() === month - 1 &&
    date.getUTCDate() === day
  );
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
  const mainPillars = rawAnalysis?.mainPillars || rawAnalysis?.pillars || {};
  const pillarKey = pillarType === 'hour' ? 'time' : pillarType;
  const pillar = mainPillars?.[pillarKey] || rawAnalysis?.[pillarType];
  return {
    thien_can: pillar?.heavenlyStem || pillar?.stem || pillar?.chinese?.[0] || '',
    dia_chi: pillar?.earthlyBranch || pillar?.branch?.name || pillar?.chinese?.[1] || '',
    nap_am: pillar?.napAm || pillar?.nayin || '',
    hidden_stems: pillar?.hiddenStems || []
  };
}

function extractElements(rawAnalysis: any) {
  const basicAnalysis = rawAnalysis?.basicAnalysis || {};
  return {
    day_master: basicAnalysis?.dayMaster || rawAnalysis?.dayMaster || '',
    elements_count: basicAnalysis?.fiveFactors || rawAnalysis?.elementsCount || {},
    strength: rawAnalysis?.strength || '',
    favorable_elements: rawAnalysis?.favorableElements || [],
    unfavorable_elements: rawAnalysis?.unfavorableElements || []
  };
}
