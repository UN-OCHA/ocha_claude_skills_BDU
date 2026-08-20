/**
 * OCHA Map Styles — Single Source of Truth
 *
 * This file defines every cartographic style used in OCHA humanitarian maps.
 * It is consumed by:
 *   1. ocha_map_style_guidance.html  (reference page)
 *   2. ocha_map_style_editor.html    (curator / editor UI)
 *   3. generate_stylx.py             (ArcGIS Pro .stylx export)
 *   4. In-browser .stylx download
 *
 * BASELINE: A4 (210 x 297 mm, 794 x 1123 px at 96 dpi).
 * Other page sizes auto-scale from A4 unless an explicit override is set.
 *
 * To edit: open ocha_map_style_editor.html, make changes, click Save.
 * The editor will download an updated copy of this file.
 */

var OCHA_MAP_STYLES = {

  meta: {
    version: "1.0",
    author: "OCHA Brand and Design Unit (BDU)",
    contact: "ochavisual@un.org",
    baseline_page_size: "A4",
    baseline_width_px: 794
  },

  page_sizes: [
    { id: "A4",        label: "A4 (210 \u00d7 297 mm)",          width_px: 794,  height_px: 1123, dim_label: "210 \u00d7 297 mm" },
    { id: "A5",        label: "A5 (148 \u00d7 210 mm)",          width_px: 559,  height_px: 794,  dim_label: "148 \u00d7 210 mm" },
    { id: "A3",        label: "A3 (297 \u00d7 420 mm)",          width_px: 1123, height_px: 1587, dim_label: "297 \u00d7 420 mm" },
    { id: "IG",        label: "Instagram (1080 \u00d7 1080 px)",  width_px: 1080, height_px: 1080, dim_label: "1080 \u00d7 1080 px" },
    { id: "TW",        label: "Twitter/X (1200 \u00d7 628 px)",   width_px: 1200, height_px: 628,  dim_label: "1200 \u00d7 628 px" },
    { id: "HD",        label: "HD 16:9 (1920 \u00d7 1080 px)",    width_px: 1920, height_px: 1080, dim_label: "1920 \u00d7 1080 px" },
    { id: "WEB",       label: "Web (800 \u00d7 600 px)",          width_px: 800,  height_px: 600,  dim_label: "800 \u00d7 600 px" }
  ],

  colors: [
    { id: "un_blue",    name: "UN Blue",            hex: "#009EDB", cmyk: "80, 20, 0, 0",   usage: "Ocean labels, water features, rivers" },
    { id: "ocean_fill", name: "Ocean / sea fill",   hex: "#E1E8F6", cmyk: "10, 2, 0, 0",    usage: "Ocean and sea water fill" },
    { id: "coast",      name: "Coastline stroke",   hex: "#64BEEB", cmyk: "55, 8, 0, 0",    usage: "Coastline and water feature strokes" },
    { id: "black_100",  name: "Black 100%",         hex: "#000000", cmyk: "0, 0, 0, 100",   usage: "Capital city symbol" },
    { id: "black_85",   name: "Black 85%",          hex: "#262626", cmyk: "0, 0, 0, 85",    usage: "Featured country label, admin capital label" },
    { id: "black_70",   name: "Black 70%",          hex: "#4D4D4D", cmyk: "0, 0, 0, 70",    usage: "Town labels, town symbols" },
    { id: "black_60",   name: "Black 60%",          hex: "#666666", cmyk: "0, 0, 0, 60",    usage: "Admin 1 region labels" },
    { id: "black_55",   name: "Black 55%",          hex: "#737373", cmyk: "0, 0, 0, 55",    usage: "International boundaries" },
    { id: "black_40",   name: "Black 40%",          hex: "#999999", cmyk: "0, 0, 0, 40",    usage: "Neighbouring country labels, capital labels" },
    { id: "black_23",   name: "Black 23%",          hex: "#C7C8CA", cmyk: "0, 0, 0, 23",    usage: "Admin 1 boundary lines" },
    { id: "black_10",   name: "Black 10%",          hex: "#E6E6E6", cmyk: "0, 0, 0, 10",    usage: "Neighbouring country fill, land mass" },
    { id: "white",      name: "White",              hex: "#FFFFFF", cmyk: "0, 0, 0, 0",     usage: "Featured country fill" }
  ],

  boundaries: [
    {
      id: "intl_boundary",
      name: "International boundary",
      color_hex: "#8A8C8E",
      cmyk: "0, 0, 0, 55",
      stroke_pt: 1.3,
      dash: null,
      cap: "butt",
      notes: "",
      overrides: {}
    },
    {
      id: "disputed",
      name: "Disputed boundary",
      color_hex: "#77787B",
      cmyk: "0, 0, 0, 55",
      stroke_pt: 1.0,
      dash: [0, 2],
      cap: "round",
      notes: "Check with relevant authority",
      overrides: {}
    },
    {
      id: "admin1",
      name: "1st admin level boundary",
      color_hex: "#C7C8CA",
      cmyk: "0, 0, 0, 23",
      stroke_pt: 0.8,
      dash: [2.3, 2.3],
      cap: "butt",
      notes: "",
      overrides: {}
    },
    {
      id: "coastline",
      name: "Coastline / water edge",
      color_hex: "#64BEEB",
      cmyk: "55, 8, 0, 0",
      stroke_pt: 0.5,
      dash: null,
      cap: "butt",
      notes: "",
      overrides: {}
    },
    {
      id: "water_feature",
      name: "Water feature (river)",
      color_hex: "#64BEEB",
      cmyk: "55, 8, 0, 0",
      stroke_pt: 0.5,
      dash: null,
      cap: "butt",
      notes: "",
      overrides: {}
    }
  ],

  fills: [
    {
      id: "neighbour_fill",
      name: "Neighbouring country / Land mass",
      color_hex: "#E6E6E6",
      cmyk: "0, 0, 0, 10",
      notes: ""
    },
    {
      id: "featured_fill",
      name: "Featured country",
      color_hex: "#FFFFFF",
      cmyk: "0, 0, 0, 0",
      notes: "White or choropleth"
    },
    {
      id: "ocean_fill",
      name: "Ocean / sea water fill",
      color_hex: "#E1E8F6",
      cmyk: "10, 2, 0, 0",
      notes: ""
    }
  ],

  points: [
    {
      id: "capital",
      name: "Capital city",
      type: "star_circle",
      svg_file: "map_symbols/Capital.svg",
      size_pt: 8.5,
      fill_hex: "#231F20",
      stroke_hex: null,
      stroke_pt: 0,
      cmyk: "0, 0, 0, 100",
      notes: "Black circle with white star",
      overrides: {}
    },
    {
      id: "admin_capital",
      name: "Administrative 1 capital",
      type: "hollow_circle",
      svg_file: "map_symbols/Adm1_capital.svg",
      size_pt: 6.2,
      fill_hex: "#FFFFFF",
      stroke_hex: "#4D4D4F",
      stroke_pt: 1.0,
      cmyk: "0, 0, 0, 70",
      notes: "White circle with dark stroke",
      overrides: {}
    },
    {
      id: "town",
      name: "Town",
      type: "solid_circle",
      svg_file: "map_symbols/Town.svg",
      size_pt: 4.0,
      fill_hex: "#4D4D4F",
      stroke_hex: null,
      stroke_pt: 0,
      cmyk: "0, 0, 0, 70",
      notes: "Solid dark circle",
      overrides: {}
    }
  ],

  labels: [
    {
      id: "neighbour_label",
      name: "Neighbouring country",
      font_family: "Roboto",
      font_style: "Regular",
      font_weight: "normal",
      size_pt: 12.5,
      color_hex: "#999999",
      cmyk: "0, 0, 0, 40",
      tracking: 200,
      uppercase: true,
      sample_text: "CHAD",
      sample_bg: "#E6E6E6",
      notes: "",
      overrides: {}
    },
    {
      id: "featured_label",
      name: "Featured country",
      font_family: "Roboto",
      font_style: "Bold",
      font_weight: "bold",
      size_pt: 14,
      color_hex: "#262626",
      cmyk: "0, 0, 0, 85",
      tracking: 300,
      uppercase: true,
      sample_text: "SUDAN",
      sample_bg: null,
      notes: "",
      overrides: {}
    },
    {
      id: "admin1_label",
      name: "First admin label",
      font_family: "Roboto",
      font_style: "Regular",
      font_weight: "normal",
      size_pt: 9.5,
      color_hex: "#666666",
      cmyk: "0, 0, 0, 60",
      tracking: 0,
      uppercase: true,
      sample_text: "NORTH DARFUR",
      sample_bg: null,
      notes: "",
      overrides: {}
    },
    {
      id: "capital_label",
      name: "Capital label",
      font_family: "Roboto",
      font_style: "Regular",
      font_weight: "normal",
      size_pt: 12.5,
      color_hex: "#999999",
      cmyk: "0, 0, 0, 40",
      tracking: 100,
      uppercase: false,
      sample_text: "Khartoum",
      sample_bg: null,
      notes: "",
      overrides: {}
    },
    {
      id: "admin_cap_label",
      name: "Admin 1 capital label",
      font_family: "Roboto Condensed",
      font_style: "Regular",
      font_weight: "normal",
      size_pt: 9.5,
      color_hex: "#262626",
      cmyk: "0, 0, 0, 85",
      tracking: 0,
      uppercase: false,
      sample_text: "El Fasher",
      sample_bg: null,
      notes: "",
      overrides: {}
    },
    {
      id: "town_label",
      name: "Town label",
      font_family: "Roboto Condensed",
      font_style: "Regular",
      font_weight: "normal",
      size_pt: 8,
      color_hex: "#4D4D4D",
      cmyk: "0, 0, 0, 70",
      tracking: 0,
      uppercase: false,
      sample_text: "Nyala",
      sample_bg: null,
      notes: "",
      overrides: {}
    },
    {
      id: "ocean_label",
      name: "Ocean label",
      font_family: "Crimson Pro",
      font_style: "Italic",
      font_weight: "normal",
      size_pt: 10,
      color_hex: "#009EDB",
      cmyk: "80, 20, 0, 0",
      tracking: 300,
      uppercase: true,
      sample_text: "ATLANTIC OCEAN",
      sample_bg: "#E1E8F6",
      notes: "",
      overrides: {}
    },
    {
      id: "sea_label",
      name: "Sea / water feature label",
      font_family: "Crimson Pro",
      font_style: "Italic",
      font_weight: "normal",
      size_pt: 8,
      color_hex: "#009EDB",
      cmyk: "80, 20, 0, 0",
      tracking: 100,
      uppercase: false,
      sample_text: "Red Sea",
      sample_bg: "#E1E8F6",
      notes: "",
      overrides: {}
    },
    {
      id: "river_label",
      name: "River label",
      font_family: "Crimson Pro",
      font_style: "Italic",
      font_weight: "normal",
      size_pt: 8,
      color_hex: "#009EDB",
      cmyk: "80, 20, 0, 0",
      tracking: 100,
      uppercase: false,
      sample_text: "Blue Nile",
      sample_bg: "#E1E8F6",
      notes: "",
      overrides: {}
    }
  ]

};
