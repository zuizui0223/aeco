// AECO v0.9: reproduce published aggregate arithmetic, no new ecology data.
import fs from 'node:fs';
const compute = function(d){
 const f=d.frogfly,j=d.japanese_frog, t=f.infested_nests_by_stage.reduce((a,x)=>a+x.n,0), weighted=f.infested_nests_by_stage.reduce((a,x)=>a+x.n*x.mean_embryo_mortality,0)/t, dur=[...f.oviposition_duration_minutes].sort((a,b)=>a-b),[a,b]=j.larval_departure_days,[c,e]=j.dry_foam_residue_days_after_departure;
 if(t!==20||Math.abs(weighted-f.reported_infested_mean_embryo_mortality)>1e-12)throw Error("source arithmetic mismatch");
 return {status:"descriptive_literature_recalculation_not_new_field_data",frogfly:{n_infested:t,early_infested_count:17,early_share_among_infested:17/t,mean_embryo_mortality_infested_reconstructed:weighted,mean_embryo_mortality_uninfested_reported:f.uninfested_mean_embryo_mortality,mortality_difference_percentage_points:100*(weighted-f.uninfested_mean_embryo_mortality),mortality_mean_ratio:weighted/f.uninfested_mean_embryo_mortality,oviposition_duration_n:dur.length,oviposition_duration_mean:dur.reduce((x,y)=>x+y,0)/dur.length,oviposition_duration_median:(dur[2]+dur[3])/2,choice_trials:f.choice_experiments},japanese_frog:{illustrative_total_visible_duration_days:[a+c,b+e],illustrative_post_departure_duration_fraction_range:[c/(b+c),e/(a+e)],scope:"arithmetic endpoint combinations only; no empirical frequency or confidence interval"},caveats:[...f.caveats,...j.caveats]};
};
const input=JSON.parse(fs.readFileSync('data/literature/foam_stage_evidence_v0.9.json','utf8'));
const result=compute(input);
fs.mkdirSync('results',{recursive:true});
fs.writeFileSync('results/foam_stage_benchmark_v0.9.json',JSON.stringify(result,null,2)+'\n');
console.log(result);
