// AECO v1.1: habitat predictors, NOT foam nest detections.
// Draw/import an inland survey AOI named geometry in the Earth Engine editor.
// Exclude ocean, use an authorized EE project. Not run in this update.
var aoi=geometry;
var proj=ee.Projection('EPSG:32654').atScale(10);
var year=2025;
var scenes=ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterBounds(aoi.buffer(1200));
var seasonal=scenes.filterDate(ee.Date.fromYMD(year,4,1),ee.Date.fromYMD(year,8,1));
var annual=scenes.filterDate(ee.Date.fromYMD(year,1,1),ee.Date.fromYMD(year+1,1,1));
print('Seasonal image count (not independent days)',seasonal.size());
print('Annual image count',annual.size());
var wet=seasonal.map(function(im){return im.select('water').add(im.select('flooded_vegetation')).gte(0.5).rename('wet');});
var n=wet.count().rename('wet_valid_scene_count').setDefaultProjection(proj);
var layers=wet.mean().rename('wet_scene_fraction').setDefaultProjection(proj).updateMask(n.gte(3)).addBands(n);
var tree=annual.select('label').mode().eq(1).rename('tree').setDefaultProjection(proj);
var treeN=annual.select('label').count().setDefaultProjection(proj);
tree=tree.updateMask(treeN.gte(3));
[50,100,300,1000].forEach(function(r){
  var k=ee.Kernel.circle({radius:r,units:'meters',normalize:false});
  var numerator=tree.unmask(0).reduceNeighborhood({reducer:ee.Reducer.mean(),kernel:k,skipMasked:false});
  var support=tree.mask().unmask(0).reduceNeighborhood({reducer:ee.Reducer.mean(),kernel:k,skipMasked:false});
  layers=layers.addBands(numerator.divide(support).updateMask(support.gte(0.8)).rename('tree_proxy_'+r+'m')).addBands(support.rename('tree_valid_fraction_'+r+'m'));
});
Map.centerObject(aoi,11);
Map.addLayer(layers.select('wet_scene_fraction').clip(aoi),{min:0,max:1,palette:['white','0066cc']},'Wet class scene frequency');
Map.addLayer(layers.select('tree_proxy_1000m').clip(aoi),{min:0,max:1,palette:['white','1e6331']},'Tree proxy 1 km');
Export.image.toDrive({image:layers.toFloat().clip(aoi),description:'AECO_Sado_habitat_predictors_'+year,region:aoi,crs:'EPSG:32654',scale:10,maxPixels:1e9});
// Validate inland water and paddy identity with GSI, pond records and JAXA HRLULC.
// No fitted habitat suitability index, occurrence, nest count or fertilization prediction.
