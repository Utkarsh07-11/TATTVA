/**
 * Basemap configurations for TATTVA Digital Mine Map.
 * Provides high-resolution, unauthenticated, reliable tile layer endpoints for dev/production.
 */

export const BASEMAP_OPTIONS = [
  {
    id: 'dark',
    name: 'Dark Canvas',
    shortName: 'Dark',
    category: 'Neutral',
    description: 'Boundary-neutral dark basemap optimized for high-contrast data overlays',
    icon: 'Moon',
    layers: [
      {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
        options: {
          attribution: 'Basemap &copy; Esri &mdash; Boundaries: Source: Survey of India, Government of India',
          maxZoom: 16,
        },
      },
    ],
  },
  {
    id: 'satellite',
    name: 'Satellite',
    shortName: 'Satellite',
    category: 'Imagery',
    description: 'High-resolution true-color satellite imagery for open-pit mine and terrain inspection',
    icon: 'Globe',
    layers: [
      {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        options: {
          attribution: 'Tiles &copy; Esri, Maxar, Earthstar Geographics, and the GIS User Community',
          maxZoom: 19,
        },
      },
    ],
  },
  {
    id: 'hybrid',
    name: 'Satellite + Labels',
    shortName: 'Hybrid',
    category: 'Hybrid',
    description: 'High-resolution aerial satellite imagery with administrative boundaries, place names, and roads',
    icon: 'Layers',
    layers: [
      {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        options: {
          attribution: 'Tiles &copy; Esri, Maxar, Earthstar Geographics',
          maxZoom: 19,
        },
      },
      {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        options: {
          attribution: 'Labels &copy; Esri',
          maxZoom: 19,
        },
      },
    ],
  },
  {
    id: 'streets',
    name: 'Street / Road Map',
    shortName: 'Streets',
    category: 'Roads',
    description: 'Detailed road network, transport infrastructure, and settlement cartography',
    icon: 'Map',
    layers: [
      {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
        options: {
          attribution: 'Tiles &copy; Esri &mdash; Sources: Esri, DeLorme, NAVTEQ, USGS, OpenStreetMap contributors',
          maxZoom: 19,
        },
      },
    ],
  },
  {
    id: 'terrain',
    name: 'Terrain / Topo',
    shortName: 'Terrain',
    category: 'Topography',
    description: 'Topographic contour elevation relief, hillshading, and geological drainage features',
    icon: 'Mountain',
    layers: [
      {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        options: {
          attribution: 'Tiles &copy; Esri, USGS, NOAA',
          maxZoom: 19,
        },
      },
    ],
  },
];

export const DEFAULT_BASEMAP_ID = 'dark';
