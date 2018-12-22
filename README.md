# What is EukZoo
The EukZoo database is a protein database of aquatic microbial eukaryotes, or protists. [@shu251](https://github.com/shu251) and I created and curated this database so that we have a database of reasonable quality to serve as reference for both taxonomy and functional interpretation of metagenomic and metatranscriptomic studies of protists. We are sharing this to the protistan research community. Needless to say, this database is far from perfect, and we intend to improve upon it in the future, but we are sure that its quality has been greatly improved from the original sequences we downloaded.<br>
# Sources
The source of the sequences were mainly from [Marine Microbial Eukaryotes Transcriptome Sequencing Project (MMETSP)](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1001889), and supplemented with various genomes and transcriptomes of organisms that were not a part of MMETSP. For a detailed list of sequences included, please consult EukZoo_taxonomy_table.tsv. The MMETSP sequences were downloaded from [Lisa Johnson's MMETSP re-assemblies](https://monsterbashseq.wordpress.com/2016/09/13/mmetsp-re-assemblies/).<br>

All sequences downloaded were binned by genus. For each genus, cdhit was performed on the sequences to reduce redundancy (>95% similarity).
# Cleanup
We have found in several occasions that some sequences in MMETSP are not from the organisms listed for specific MMETSP samples. Most of the cultures in MMETSP are non-axenic, and bacterial or algal prey were often added to the cultures, which could be the primary source of these sequences. The presence of these sequences from other organisms would often lead to incorrect taxonomic assignments and incorrect sequence recruitment, which are big problems in any environmental molecular study.<br>

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
