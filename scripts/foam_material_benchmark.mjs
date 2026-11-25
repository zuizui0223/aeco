// AECO v1.0, descriptive published benchmarks and idealized physics only.
import fs from 'node:fs';
const compute=function compute(d){
 const a=d.japanese_foam.amino_acid_residues_per_1000;
 const aa_total=Object.values(a).reduce((s,x)=>s+x,0);
 const essential_reported=["H","I","M","L","K","F","T","V"].reduce((s,k)=>s+a[k],0);
 const p=d.proboscis.rows;
 const gamma=d.tungara.foam_fluid_surface_tension_approx_mN_m/d.tungara.water_surface_tension_approx_mN_m;
 const ne=d.neotropical;
 if(Math.abs(aa_total-d.japanese_foam.published_total)>1)throw Error("Unexpected amino acid sum");
 if(p[0].areal_uptake_mm2_s<=p[1].areal_uptake_mm2_s)throw Error("Unexpected uptake order");
 // Lucas-Washburn idealized comparison. Same pore radius, same geometry, no active suction,
 // constant viscosity/contact angle and a liquid reservoir. Not butterfly/foam model.
 const angleRows=[0,30,45,60,75].map(theta=>{
 const c=Math.cos(theta*Math.PI/180), need=c/gamma;
 return {water_contact_angle_deg:theta,maximum_ratio_of_washburn_coefficient_equal_viscosity:gamma/c,
   foam_contact_angle_strict_improvement_possible:need<1,
   maximum_foam_contact_angle_deg_for_strict_improvement:need<1?Math.acos(need)*180/Math.PI:null};
 });
 const r={status:"published_descriptive_benchmarks_and_idealized_physics_only",japanese_foam:{sum_of_printed_residue_values:aa_total,reported_sum:d.japanese_foam.published_total,rounding_difference:aa_total-d.japanese_foam.published_total,cysteine_ratio_to_cited_frog_meat:a.C/d.japanese_foam.frog_meat_cysteine_residues_per_1000,eight_reported_essential_amino_acids_residue_fraction:essential_reported/d.japanese_foam.published_total,accessible_sodium_mM:null,free_amino_acid_mM:null,interpretation:"hydrolyzed composition only, not insect-available nutrition"},proboscis:{areal_uptake_ratio_Polygonia_over_Pieris:p[0].areal_uptake_mm2_s/p[1].areal_uptake_mm2_s,relative_reduction_Pieris_vs_Polygonia:1-p[1].areal_uptake_mm2_s/p[0].areal_uptake_mm2_s,comparison_scope:"approximate rates in a laboratory liquid-film comparison; no inference to natural foam, feeding preference, mating, or fertility"},neotropical_surface_tension:ne.table1.map(x=>({taxon:x.taxon,surface_tension_mN_m:x.surface_tension_mN_m,reduction_vs_approx_water_control:1-x.surface_tension_mN_m/ne.water_control_approx_mN_m})),tungara_surface_tension:{ratio_to_water:gamma,reduction_vs_water:1-gamma},idealized_equal_viscosity_washburn:{status:"illustration_not_calibration",threshold_water_angle_for_any_strict_increase_deg:Math.acos(gamma)*180/Math.PI,scenarios:angleRows,assumptions:"same pore radius, liquid reservoir, viscosity, geometry; constant contact angles; passive imbibition only; surface tension values from non-Japanese frog; not a prediction of butterfly suction or feeding"},ion_reference:d.ion_reference};
 if(Math.abs(r.proboscis.areal_uptake_ratio_Polygonia_over_Pieris-1.899581589958159)>1e-12)throw Error("ratio mismatch");
 if(r.idealized_equal_viscosity_washburn.scenarios[1].foam_contact_angle_strict_improvement_possible||!r.idealized_equal_viscosity_washburn.scenarios[3].foam_contact_angle_strict_improvement_possible)throw Error("physics sanity check");
 return r;
};
const d=JSON.parse(fs.readFileSync('data/literature/foam_material_evidence_v1.0.json','utf8'));
const result=compute(d);
fs.mkdirSync('results',{recursive:true});
fs.writeFileSync('results/foam_material_benchmark_v1.0.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
