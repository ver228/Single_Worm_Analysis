USE single_worm_old;
CREATE OR REPLACE VIEW exp_annotation_full AS
SELECT exp_annotation.id AS id, experiments.wormFileName AS file_name, 
strain.strainName AS strain, allele.alleleName AS allele, gene.geneName AS gene, 
chromosome.chromosomeName AS chromosome, trackerno.trackerName AS tracker, 
sex.sexName AS sex, age.ageName AS age, ventralside.ventralSideName AS ventral_side, 
food.foodName AS food, habituation.habitName AS habituation, 
experimenters.name AS experimenters, experimenterlocation.address AS location,
genotype.genotypeName AS genotype, treatment.treatmentName AS treatment
FROM exp_annotation JOIN experiments ON experiments.id = exp_annotation.id 
LEFT JOIN strain ON strain.strainID = exp_annotation.strainID 
LEFT JOIN allele ON allele.alleleID = exp_annotation.alleleID 
LEFT JOIN gene ON gene.geneID = exp_annotation.geneID 
LEFT JOIN chromosome ON chromosome.chromosomeID = exp_annotation.chromosomeID 
LEFT JOIN trackerno ON trackerno.trackerID = exp_annotation.trackerID 
LEFT JOIN sex ON sex.sexID = exp_annotation.sexID 
LEFT JOIN age ON age.ageID = exp_annotation.ageID 
LEFT JOIN ventralside ON ventralside.ventralSideID = exp_annotation.ventralSideID 
LEFT JOIN food ON food.foodID = exp_annotation.foodID 
LEFT JOIN habituation ON habituation.habitID = exp_annotation.habitID 
LEFT JOIN experimenterlocation ON experimenterlocation.locationID = exp_annotation.locationID 
LEFT JOIN experimenters ON experimenters.expID = exp_annotation.experimenterID 
LEFT JOIN genotype ON genotype.genotypeID = exp_annotation.genotypeID 
LEFT JOIN treatment ON treatment.treatmentID = exp_annotation.treatmentID;