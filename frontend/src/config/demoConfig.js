/**
 * Phase 19: Frontend Demonstration Presentation Configuration & UI Action Mappings.
 * NOTE: All authoritative demo content (steps, mine IDs, timing, speaker notes, juror defense)
 * is served dynamically from the backend via GET /api/real/demo/config.
 * This file contains strictly client-side presentation constants and routing maps.
 */

export const DEMO_PRESENTATION_DEFAULTS = {
  totalPresentationSeconds: 300,
  initialDemoMine: 'MOIL_BALAGHAT',
  initialHorizonDays: 30,
  defaultScenarioOverrides: {
    equipment_availability_pct: 88.0,
    blasting_delay_flag: 0,
    rainfall_mm: 12.5,
    custom_target: 10000.0,
  },
};

export const SCREEN_ROUTE_MAP = {
  overview: '/',
  mine_map: '/mine-map',
  forecast: '/forecast',
  explain: '/explain',
  simulate: '/simulate',
  actions: '/actions',
  resources: '/resources',
};
