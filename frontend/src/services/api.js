const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

async function handleResponse(res) {
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API error ${res.status}: ${errorText}`);
  }
  return res.json();
}

export const api = {
  getHealth: async () => handleResponse(await fetch(`${API_BASE_URL}/health`)),

  getMineOverview: async (blockId = 'BLOCK_A') =>
    handleResponse(await fetch(`${API_BASE_URL}/mine/overview?selected_block=${blockId}`)),

  getMineBlocks: async () =>
    handleResponse(await fetch(`${API_BASE_URL}/mine/blocks`)),

  getForecast: async (blockId = 'BLOCK_A', horizonDays = 30, targetTonnes = null) => {
    const res = await fetch(`${API_BASE_URL}/forecast/production`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mine_block_id: blockId,
        horizon_days: horizonDays,
        target_tonnes: targetTonnes,
      }),
    });
    return handleResponse(res);
  },

  getShortfallExplanation: async (blockId = 'BLOCK_A', horizonDays = 30) =>
    handleResponse(await fetch(`${API_BASE_URL}/explain/shortfall?mine_block_id=${blockId}&horizon_days=${horizonDays}`)),

  getRecommendations: async (blockId = 'BLOCK_A', horizonDays = 30) =>
    handleResponse(await fetch(`${API_BASE_URL}/recommend/actions?mine_block_id=${blockId}&horizon_days=${horizonDays}`)),

  simulateScenario: async (blockId = 'BLOCK_A', params = {}) => {
    const res = await fetch(`${API_BASE_URL}/simulate/scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mine_block_id: blockId,
        horizon_days: params.horizon_days || 30,
        equipment_availability_pct: params.equipment_availability_pct,
        blasting_delay_flag: params.blasting_delay_flag,
        rainfall_mm: params.rainfall_mm,
      }),
    });
    return handleResponse(res);
  },

  getProspectivityMap: async () => handleResponse(await fetch(`${API_BASE_URL}/prospectivity/map`)),
  getDrillholes: async () => handleResponse(await fetch(`${API_BASE_URL}/prospectivity/drillholes`)),
  getResourceEstimate: async (cutoffGrade = 20.0) =>
    handleResponse(await fetch(`${API_BASE_URL}/prospectivity/resource-estimate?cutoff_grade_pct=${cutoffGrade}`)),
  getEquipment: async () => handleResponse(await fetch(`${API_BASE_URL}/mine/equipment`)),

  // Real Data Services (Phase 7 / Phase 11)
  getRealMines: async () => handleResponse(await fetch(`${API_BASE_URL}/real/mines`)),
  getRealMineDetail: async (mineId) => handleResponse(await fetch(`${API_BASE_URL}/real/mines/${encodeURIComponent(mineId)}`)),
  getRealMineDashboard: async (mineId) => handleResponse(await fetch(`${API_BASE_URL}/real/mine-dashboard/${encodeURIComponent(mineId)}`)),
  getRealMineLayers: async (mineId) => handleResponse(await fetch(`${API_BASE_URL}/real/mines/${encodeURIComponent(mineId)}/layers`)),
  getRealProduction: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.period) query.append('period', params.period);
    if (params.period_type) query.append('period_type', params.period_type);
    if (params.company) query.append('company', params.company);
    if (params.state) query.append('state', params.state);
    if (params.commodity) query.append('commodity', params.commodity);
    const qs = query.toString();
    return handleResponse(await fetch(`${API_BASE_URL}/real/production${qs ? `?${qs}` : ''}`));
  },
  getRealRastersSummary: async () => handleResponse(await fetch(`${API_BASE_URL}/real/rasters/summary`)),

  // Real Prospectivity Experiment Services (Phase 9B / Phase 10)
  getRealProspectivityMeta: async (mineId = 'MOIL_BALAGHAT') =>
    handleResponse(await fetch(`${API_BASE_URL}/real/prospectivity/${encodeURIComponent(mineId)}`)),
  getRealProspectivityGeoJson: async (mineId = 'MOIL_BALAGHAT') =>
    handleResponse(await fetch(`${API_BASE_URL}/real/prospectivity/${encodeURIComponent(mineId)}/geojson`)),
  getRealMineralizationEvidence: async (mineId = 'MOIL_BALAGHAT') =>
    handleResponse(await fetch(`${API_BASE_URL}/real/prospectivity/${encodeURIComponent(mineId)}/evidence`)),

  // Phase 12 Production Intelligence & Reconciliation
  getProductionReconciliation: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.mine_block_id) query.append('mine_block_id', params.mine_block_id);
    if (params.horizon_days) query.append('horizon_days', params.horizon_days);
    if (params.target_tonnes != null) query.append('target_tonnes', params.target_tonnes);
    if (params.equipment_availability_pct != null) query.append('equipment_availability_pct', params.equipment_availability_pct);
    if (params.blasting_delay_flag != null) query.append('blasting_delay_flag', params.blasting_delay_flag);
    if (params.rainfall_mm != null) query.append('rainfall_mm', params.rainfall_mm);
    const qs = query.toString();
    return handleResponse(await fetch(`${API_BASE_URL}/real/production/reconciliation${qs ? `?${qs}` : ''}`));
  },
  postProductionReconciliation: async (body = {}) => {
    const res = await fetch(`${API_BASE_URL}/real/production/reconciliation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return handleResponse(res);
  },
};



