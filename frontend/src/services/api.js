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
};
