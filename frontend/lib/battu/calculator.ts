import dateMappingsJson from "bazi-calculator-by-alvamind/src/dates_mapping.json";

export type ElementType = "WOOD" | "FIRE" | "EARTH" | "METAL" | "WATER";
export type GenderType = "male" | "female";

export interface DateMapping {
  HYear: number | string;
  EYear: number | string;
  HMonth: number | string;
  EMonth: number | string;
  HDay: number | string;
  EDay: number | string;
}

export interface DateMappings {
  [year: string]: {
    [month: string]: {
      [day: string]: DateMapping;
    };
  };
}

export interface Pillar {
  chinese: string;
  element: ElementType | "";
  animal: string;
  branch: {
    element: ElementType | "";
  };
}

export interface Pillars {
  year: Pillar;
  month: Pillar;
  day: Pillar;
  time: Pillar;
}

export interface FiveFactors {
  WOOD: number;
  FIRE: number;
  EARTH: number;
  METAL: number;
  WATER: number;
}

export interface DayMasterAnalysis {
  stem: string;
  nature: "Yang" | "Yin";
  element: ElementType;
}

export interface CompleteAnalysis {
  mainPillars: Pillars;
  basicAnalysis: {
    lifeGua: number;
    dayMaster: DayMasterAnalysis;
    nobleman: string[];
    intelligence: string;
    skyHorse: string;
    peachBlossom: string;
    fiveFactors: FiveFactors;
    eightMansions: {
      group: "West" | "East";
      lucky: {
        wealth: string;
        health: string;
        romance: string;
        career: string;
      };
      unlucky: {
        obstacles: string;
        quarrels: string;
        setbacks: string;
        totalLoss: string;
      };
    };
  };
}

const STEMS = [
  "\u7532",
  "\u4e59",
  "\u4e19",
  "\u4e01",
  "\u620a",
  "\u5df1",
  "\u5e9a",
  "\u8f9b",
  "\u58ec",
  "\u7678",
];

const BRANCHES = [
  "\u5b50",
  "\u4e11",
  "\u5bc5",
  "\u536f",
  "\u8fb0",
  "\u5df3",
  "\u5348",
  "\u672a",
  "\u7533",
  "\u9149",
  "\u620c",
  "\u4ea5",
];

const ANIMALS = [
  "Rat",
  "Ox",
  "Tiger",
  "Rabbit",
  "Dragon",
  "Snake",
  "Horse",
  "Goat",
  "Monkey",
  "Rooster",
  "Dog",
  "Pig",
];

const ELEMENTS: Record<ElementType, string[]> = {
  WOOD: ["\u7532", "\u4e59"],
  FIRE: ["\u4e19", "\u4e01"],
  EARTH: ["\u620a", "\u5df1"],
  METAL: ["\u5e9a", "\u8f9b"],
  WATER: ["\u58ec", "\u7678"],
};

const BRANCH_ELEMENTS: Record<ElementType, string[]> = {
  WATER: ["\u5b50", "\u4ea5"],
  WOOD: ["\u5bc5", "\u536f"],
  FIRE: ["\u5df3", "\u5348"],
  METAL: ["\u7533", "\u9149"],
  EARTH: ["\u4e11", "\u8fb0", "\u672a", "\u620c"],
};

const HIDDEN_STEMS: Record<string, string[]> = {
  "\u5b50": ["\u7678"],
  "\u4e11": ["\u5df1", "\u7678", "\u8f9b"],
  "\u5bc5": ["\u7532", "\u4e19", "\u620a"],
  "\u536f": ["\u4e59"],
  "\u8fb0": ["\u620a", "\u4e59", "\u7678"],
  "\u5df3": ["\u4e19", "\u5e9a", "\u620a"],
  "\u5348": ["\u4e01", "\u5df1"],
  "\u672a": ["\u5df1", "\u4e01", "\u4e59"],
  "\u7533": ["\u5e9a", "\u58ec", "\u620a"],
  "\u9149": ["\u8f9b"],
  "\u620c": ["\u620a", "\u8f9b", "\u4e01"],
  "\u4ea5": ["\u58ec", "\u7532"],
};

const ELEMENT_RELATIONSHIPS: Record<ElementType, Record<ElementType, string>> = {
  WOOD: {
    WATER: "Resource",
    WOOD: "Companion",
    FIRE: "Output",
    EARTH: "Wealth",
    METAL: "Control",
  },
  FIRE: {
    WOOD: "Resource",
    FIRE: "Companion",
    EARTH: "Output",
    METAL: "Wealth",
    WATER: "Control",
  },
  EARTH: {
    FIRE: "Resource",
    EARTH: "Companion",
    METAL: "Output",
    WATER: "Wealth",
    WOOD: "Control",
  },
  METAL: {
    EARTH: "Resource",
    METAL: "Companion",
    WATER: "Output",
    WOOD: "Wealth",
    FIRE: "Control",
  },
  WATER: {
    METAL: "Resource",
    WATER: "Companion",
    WOOD: "Output",
    FIRE: "Wealth",
    EARTH: "Control",
  },
};

const RELATIONSHIP_WEIGHTS: Record<string, number> = {
  Resource: 3,
  Companion: 2.5,
  Output: 2,
  Wealth: 1.2,
  Control: 1.2,
};

const HOUR_MAP: [number, number, string][] = [
  [23, 1, "\u5b50"],
  [1, 3, "\u4e11"],
  [3, 5, "\u5bc5"],
  [5, 7, "\u536f"],
  [7, 9, "\u8fb0"],
  [9, 11, "\u5df3"],
  [11, 13, "\u5348"],
  [13, 15, "\u672a"],
  [15, 17, "\u7533"],
  [17, 19, "\u9149"],
  [19, 21, "\u620c"],
  [21, 23, "\u4ea5"],
];

const NOBLEMAN_MAP: Record<ElementType, string[]> = {
  WOOD: ["\u4e11", "\u672a"],
  FIRE: ["\u4ea5", "\u5df3"],
  EARTH: ["\u7533", "\u5bc5"],
  METAL: ["\u5bc5", "\u5348"],
  WATER: ["\u5df3", "\u7533"],
};

const INTELLIGENCE_MAP: Record<ElementType, string> = {
  WOOD: "\u5df3",
  FIRE: "\u7533",
  EARTH: "\u4ea5",
  METAL: "\u5b50",
  WATER: "\u5df3",
};

const PEACH_BLOSSOM_MAP: Record<ElementType, string> = {
  WOOD: "\u9149",
  FIRE: "\u536f",
  EARTH: "\u5348",
  METAL: "\u5348",
  WATER: "\u7533",
};

const GUA_DIRECTIONS: Record<number, { lucky: string[]; unlucky: string[] }> = {
  1: { lucky: ["SE", "E", "S", "N"], unlucky: ["NW", "W", "SW", "NE"] },
  2: { lucky: ["NE", "W", "NW", "SW"], unlucky: ["SE", "E", "S", "N"] },
  3: { lucky: ["S", "E", "SE", "N"], unlucky: ["NW", "W", "SW", "NE"] },
  4: { lucky: ["SE", "E", "S", "N"], unlucky: ["NW", "W", "SW", "NE"] },
  6: { lucky: ["W", "NE", "SW", "NW"], unlucky: ["SE", "E", "N", "S"] },
  7: { lucky: ["NW", "W", "NE", "SW"], unlucky: ["SE", "E", "S", "N"] },
  8: { lucky: ["W", "NE", "SW", "NW"], unlucky: ["SE", "E", "S", "N"] },
  9: { lucky: ["S", "E", "SE", "N"], unlucky: ["NW", "W", "SW", "NE"] },
};

const DATE_MAPPINGS = dateMappingsJson as DateMappings;
const SUPPORTED_YEARS = Object.keys(DATE_MAPPINGS).map(Number);

export const BATU_SUPPORTED_YEAR_MIN = Math.min(...SUPPORTED_YEARS);
export const BATU_SUPPORTED_YEAR_MAX = Math.max(...SUPPORTED_YEARS);

export class BaziCalculator {
  constructor(
    private year: number,
    private month: number,
    private day: number,
    private hour: number,
    private gender: GenderType = "male",
  ) {}

  public calculatePillars(): Pillars {
    const mapping = this.getMapping(this.year, this.month, this.day);
    const yearPillar =
      STEMS[this.toIndex(mapping.HYear)] + BRANCHES[this.toIndex(mapping.EYear)];
    const monthPillar =
      STEMS[this.toIndex(mapping.HMonth)] + BRANCHES[this.toIndex(mapping.EMonth)];
    const dayPillar =
      STEMS[this.toIndex(mapping.HDay)] + BRANCHES[this.toIndex(mapping.EDay)];
    const timePillar = this.calculateHourPillar(mapping);

    return {
      year: this.translatePillar(yearPillar),
      month: this.translatePillar(monthPillar),
      day: this.translatePillar(dayPillar),
      time: this.translatePillar(timePillar),
    };
  }

  public calculateBasicAnalysis() {
    const pillars = this.calculatePillars();
    const lifeGua = this.calculateLifeGua();
    const dayMaster = this.calculateDayMaster(pillars.day);

    return {
      lifeGua,
      dayMaster,
      nobleman: this.calculateNobleman(dayMaster.element, dayMaster.stem),
      intelligence: INTELLIGENCE_MAP[dayMaster.element],
      skyHorse: this.getSkyHorse(pillars.day.chinese[1]),
      peachBlossom: PEACH_BLOSSOM_MAP[dayMaster.element],
      fiveFactors: this.calculateFiveFactors(pillars),
      eightMansions: this.calculateEightMansions(lifeGua),
    };
  }

  public getCompleteAnalysis(): CompleteAnalysis {
    return {
      mainPillars: this.calculatePillars(),
      basicAnalysis: this.calculateBasicAnalysis(),
    };
  }

  private getMapping(year: number, month: number, day: number): DateMapping {
    const mapping = DATE_MAPPINGS[String(year)]?.[String(month)]?.[String(day)];
    if (!mapping) {
      throw new Error(`No date mapping found for ${year}-${month}-${day}`);
    }
    return mapping;
  }

  private toIndex(value: number | string): number {
    return Number(value) - 1;
  }

  private getHourBranch(): string {
    const branch = HOUR_MAP.find(
      ([start, end]) =>
        (this.hour >= start && this.hour < end) ||
        (start === 23 && (this.hour >= 23 || this.hour < 1)),
    );
    return branch ? branch[2] : "\u5b50";
  }

  private calculateHourPillar(dayMapping: DateMapping): string {
    const hourBranch = this.getHourBranch();
    const dayStem = STEMS[this.toIndex(dayMapping.HDay)];
    const stemOffset = (STEMS.indexOf(dayStem) * 2) % 10;
    const branchIndex = BRANCHES.indexOf(hourBranch);
    return STEMS[(stemOffset + branchIndex) % 10] + hourBranch;
  }

  private translatePillar(pillar: string): Pillar {
    const [stem, branch] = pillar.split("");
    return {
      chinese: pillar,
      element: this.getElementFromStem(stem),
      animal: ANIMALS[BRANCHES.indexOf(branch)] || "",
      branch: {
        element: this.getElementFromBranch(branch),
      },
    };
  }

  private getElementFromStem(stem: string): ElementType {
    const element = (Object.keys(ELEMENTS) as ElementType[]).find((key) =>
      ELEMENTS[key].includes(stem),
    );
    if (!element) {
      throw new Error(`Unknown heavenly stem: ${stem}`);
    }
    return element;
  }

  private getElementFromBranch(branch: string): ElementType | "" {
    return (
      (Object.keys(BRANCH_ELEMENTS) as ElementType[]).find((key) =>
        BRANCH_ELEMENTS[key].includes(branch),
      ) || ""
    );
  }

  private calculateFiveFactors(pillars: Pillars): FiveFactors {
    const dayMasterElement = this.getElementFromStem(pillars.day.chinese[0]);
    const stems = [
      pillars.year.chinese[0],
      pillars.month.chinese[0],
      pillars.day.chinese[0],
      pillars.time.chinese[0],
      ...this.getHiddenStems(pillars.year.chinese[1]),
      ...this.getHiddenStems(pillars.month.chinese[1]),
      ...this.getHiddenStems(pillars.day.chinese[1]),
      ...this.getHiddenStems(pillars.time.chinese[1]),
    ];

    const weights: Record<ElementType, number> = {
      WOOD: 0,
      FIRE: 0,
      EARTH: 0,
      METAL: 0,
      WATER: 0,
    };

    for (const stem of stems) {
      const element = this.getElementFromStem(stem);
      const relationship = ELEMENT_RELATIONSHIPS[dayMasterElement][element];
      weights[element] += RELATIONSHIP_WEIGHTS[relationship] ?? 0;
    }

    const total = Object.values(weights).reduce((sum, value) => sum + value, 0);
    return {
      WOOD: Math.round((weights.WOOD * 100) / total),
      FIRE: Math.round((weights.FIRE * 100) / total),
      EARTH: Math.round((weights.EARTH * 100) / total),
      METAL: Math.round((weights.METAL * 100) / total),
      WATER: Math.round((weights.WATER * 100) / total),
    };
  }

  private getHiddenStems(branch: string): string[] {
    return HIDDEN_STEMS[branch] || [];
  }

  private calculateLifeGua(): number {
    const yearSum = String(this.year)
      .split("")
      .reduce((acc, digit) => acc + Number(digit), 0);
    let gua = 11 - (yearSum % 9) || 9;
    if (this.gender === "female") {
      gua = (yearSum % 9 || 9) + 4;
      if (gua > 9) gua -= 9;
    }
    return gua;
  }

  private calculateEightMansions(lifeGua: number) {
    const directions = GUA_DIRECTIONS[lifeGua] || GUA_DIRECTIONS[1];
    const westGroup = [2, 6, 7, 8].includes(lifeGua);
    return {
      group: westGroup ? "West" as const : "East" as const,
      lucky: {
        wealth: directions.lucky[0],
        health: directions.lucky[1],
        romance: directions.lucky[2],
        career: directions.lucky[3],
      },
      unlucky: {
        obstacles: directions.unlucky[0],
        quarrels: directions.unlucky[1],
        setbacks: directions.unlucky[2],
        totalLoss: directions.unlucky[3],
      },
    };
  }

  private calculateNobleman(
    dayMasterElement: ElementType,
    dayMasterStem: string,
  ): string[] {
    const positions = NOBLEMAN_MAP[dayMasterElement] || [];
    const isYang = STEMS.indexOf(dayMasterStem) % 2 === 0;
    return isYang ? [...positions] : [...positions].reverse();
  }

  private getStemNature(stem: string): "Yang" | "Yin" {
    return STEMS.indexOf(stem) % 2 === 0 ? "Yang" : "Yin";
  }

  private getSkyHorse(dayBranch: string): string {
    const oppositeIndex = (BRANCHES.indexOf(dayBranch) + 6) % 12;
    return BRANCHES[oppositeIndex];
  }

  private calculateDayMaster(dayPillar: Pillar): DayMasterAnalysis {
    const dayMasterStem = dayPillar.chinese[0];
    return {
      stem: dayMasterStem,
      nature: this.getStemNature(dayMasterStem),
      element: this.getElementFromStem(dayMasterStem),
    };
  }
}
