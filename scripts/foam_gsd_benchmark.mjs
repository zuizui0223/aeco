// AECO v1.1: geometry, not empirical detection.
import fs from 'node:fs';
const compute=function compute(d){const s=d.axes_mm.map(x=>Math.min(...x));return {status:"nominal_projection_only",short_axis_mm_range:[Math.min(...s),Math.max(...s)],long_axis_mm_range:[Math.min(...d.axes_mm.map(x=>Math.max(...x))),Math.max(...d.axes_mm.map(x=>Math.max(...x)))],all_measured_short_axis_5px_max_gsd_mm:Math.min(...s)/5,all_measured_short_axis_10px_max_gsd_mm:Math.min(...s)/10,rows:d.gsd_mm.map(x=>({...x,short_axis_pixels_min:Math.min(...s)/x.gsd,short_axis_pixels_max:Math.max(...s)/x.gsd,n_at_least_5px:s.filter(v=>v/x.gsd>=5).length,n_at_least_10px:s.filter(v=>v/x.gsd>=10).length,typical_arboreal_pixels:d.typical_arboreal_diameter_mm.map(v=>v/x.gsd)})),limits:"Full exposure, normal view, no blur or occlusion. Five and ten pixels are planning heuristics, not validated detection thresholds. Hidden nests may be invisible at any optical resolution."};};
const r=compute(JSON.parse(fs.readFileSync('data/literature/sado_foam_dimensions_v1.1.json','utf8')));
if(r.all_measured_short_axis_10px_max_gsd_mm!==4.9||r.rows.find(x=>x.gsd===5).n_at_least_10px!==4)throw Error('geometry check');
fs.mkdirSync('results',{recursive:true});
fs.writeFileSync('results/foam_gsd_v1.1.json',JSON.stringify(r,null,2)+'\n');
