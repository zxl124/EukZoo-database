# What is EukZoo
The EukZoo database is a protein database of aquatic microbial eukaryotes, or protists. [@shu251](https://github.com/shu251) and I created and curated this database so that we have a database of reasonable quality to serve as reference for both taxonomy and functional interpretation of metagenomic and metatranscriptomic studies of protists. We are sharing this to the protistan research community. Needless to say, this database is far from perfect, and we intend to improve upon it in the future, but we are sure that its quality has been greatly improved from the original sequences we downloaded.<br>
# Sources
The source of the sequences were mainly from [Marine Microbial Eukaryotes Transcriptome Sequencing Project (MMETSP)](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1001889), and supplemented with various genomes and transcriptomes of organisms that were not a part of MMETSP. For a detailed list of sequences included, please consult [the taxonomy table](https://github.com/zxl124/EukZoo-database/blob/master/EukZoo_taxonomy_table_v_0.2.tsv). The MMETSP sequences were downloaded from [Lisa Johnson's MMETSP re-assemblies](https://monsterbashseq.wordpress.com/2016/09/13/mmetsp-re-assemblies/).

  All sequences downloaded were binned by genus. For each genus, cdhit was performed on the sequences to reduce redundancy (>95% similarity).
# Cleanup
We have found in several occasions that some sequences in MMETSP are not from the organisms listed for specific MMETSP samples. Most of the cultures in MMETSP are non-axenic, and bacterial or algal prey were often added to the cultures, which could be the primary source of these sequences. The presence of these sequences from other organisms would often lead to incorrect taxonomic assignments and incorrect sequence recruitment, which are big problems in any environmental molecular study.

  I carried out steps to identify and remove these sequences of secondary sources, consisting of either contamination or prey sequences. The cleanup effort was carried out in two steps. Please see Cleanup.md for details.
# Download
Due to the size of the database files, they are hosted at [Zenodo](https://zenodo.org/record/1476236#.XB1ygM9KiGh). Please download files there. Some of the files, such as scripts to assign taxonomy or KEGG annotaiton, and taxonomy table, can be downloaded from this repository.
# How to use EukZoo
## 1. Database search
We strongly recommend using [DIAMOND](https://github.com/bbuchfink/diamond) to carry out alignment of your sequences. It is much faster than BLAST and only sacrifices a little bit of sensitivity. After downloading the files, and installing DIAMOND, first initilize the database sequence file to DIAMOND format.
```
$ cd <path/to/EukZoo>
$ <path/to/diamond>/diamond makedb --in EukZoo_v_0.2.faa -d EukZoo
```
Next, search the database using your sequences. We assume your sequence files are named Sample_R1.fastq and Sample_R2.fastq, please change the commands according to your file names. FASTA files and fastq.gz files also work.
```
$ cd <path/to/YourSamples>
$ <path/to/diamond>/diamond blastx -d </path/to/EukZoo>/EukZoo -q Sample_R1.fastq -o Sample_R1.blastx
$ <path/to/diamond>/diamond blastx -d </path/to/EukZoo>/EukZoo -q Sample_R2.fastq -o Sample_R2.blastx
```
You can use the "-t" option to specify the number of threads you want to use. In addition, you can consider adding "--sensitive" option to the search if your organisms of interest does not have any close relatives in the database (We used it in our metatranscriptome studies). It generates more hits at the sacrifice of speed.

You can use BLAST instead of DIAMOND. **If you use BLAST for the search, please make sure the outputs are in tabular format.**
## 2. Taxonomy assignment
Taxonomy assignment is done using the total LCA algorithm. All hits whose bitscore are above the cutoff (by default set as 95% of the best bitscore) are taken into account. For each taxonomy level, if there are no conflict among all those hits, then the concensus is assigned to that read. For read pairs, the one with higher best score wins. There are also restrictions on how deep the taxonomy assignment can go based on the %identity of the best hit. See assign_taxonomy.py for details.

The taxonomy assignment script has two options. The required option (-t) is the database taxonomy table you downloaded. The optional option (-c) can set the score cutoff, default is 0.95. The script is written in Python 3. 
```
$ python </path/to/EukZoo>/assign_taxonomy.py -t </path/to/EukZoo>/EukZoo_taxonomy_table_v_0.2.tsv Sample_R1.blastx Sample_R2.blastx > Sample_taxonomy.txt
```
The result of taxonomy assignment will look like this:
```
HISEQ2500:265:C5UNMANXX:6:1101:1734:1936	Rhizaria;Retaria;Polycystinea;Spumellaria;Collosphaeridae;Thalassicolla;
HISEQ2500:265:C5UNMANXX:6:1101:1836:1905	Alveolate;Dinoflagellate;Dinophyceae;Peridiniales;
```
The first column being the read name, the second column being semicolon-seperated taxonomy string.
## 3. KEGG annotation assignment
For functional annotation, we prefer to use the KEGG system, because I think it has a much better structure even though its scope is narrower than say Pfam or KOG. Therefore, pathway analysis using the KEGG system is much easier. We have generated KEGG annotations, in the form of KO IDs, for all the proteins in our database, via the [GhostKOALA server](https://www.kegg.jp/ghostkoala/). We also provide a script to assign KO IDs to your sequences based on hits to EukZoo. It works similarly to the taxonomy assignment script, in that there should be no conflicts among all hits above the score cutoff.

The KEGG annotation assignment script has two options. The required option (-a) is the database KEGG annotation table you downloaded. The optional option (-c) can set the score cutoff, default is 0.95. The script is written in Python 3.
```
$ python </path/to/EukZoo>/assign_kegg_annotation.py -a </path/to/EukZoo>/EukZoo_KEGG_annotation_v_0.2.tsv Sample_R1.blastx Sample_R2.blastx > Sample_annotation.txt
```
The result of KEGG annotation will look like this:
```
HISEQ2500:265:C5UNMANXX:6:1101:1734:1936	K00933
HISEQ2500:265:C5UNMANXX:6:1101:1761:1923	K02938
```
The first column being the read name, the second column being the KO ID assigned.
