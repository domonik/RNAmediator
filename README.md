# RIssmed  
[![PyPI Latest Release](https://img.shields.io/pypi/v/RIssmed.svg)](https://pypi.org/project/RIssmed/) [![GitHub](https://img.shields.io/github/tag/jfallmann/RIssmed.svg)](https://github.com/jfallmann/RIssmed) [![Build Status](https://github.com/jfallmann/RIssmed/.github/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/jfallmann/RIssmed/actions) [![Bioconda](https://anaconda.org/bioconda/RIssmed/badges/version.svg)](https://anaconda.org/bioconda/RIssmed)

The RNA Interaction via secondary structure mediation (RIssmed) tool suite
analyses the change of RNA secondary structure upon binding other molecules.

It is available as suite of commandline tools, the source code of RIssmed is open source and available via GitHub (License GPL-3).

### <u>Installation via bioconda - recommended</u>

RIssmed can be installed with all tool dependencies via [conda](https://conda.io/docs/install/quick.html). Once you have conda installed simply type:

    conda create -n RIssmed -c conda-forge -c bioconda RIssmed

Activate the environment in which RIssmed was installed to use it:

    conda activate RIssmed


### <u>Usage</u>
    
RIssmed provides different tools to answer different research questions. We will discuss the target application of the tools
and the required input in the following points. 

* CalcTempDiffs.py

    Analyses how the positions-wise probability of base-pairing changes for an RNA sequence upon temperature change. 
    
    * Input: Sequence string
    
    * Output: Plot of relative position-wise probability change
    

* CollectConsResults.py
 
    Computes statistics for change of position-wise probability of being base-paired, with binding constraint for a set of provided genes.
    
    * Input:
    
    * Output:


* CollectWindowResults.py 

    Computes statistics for change of position-wise probability of being base-paired, using windows, with binding constraint for a set of provided genes.
    
    * Input:
    
    * Output:



* ConstraintFold.py
    
    Computes RNA secondary structure prediction with defined hard binding constraint for a set of sequences.
    
    * Input:
    
    * Output:


* ConstraintPLFold.py

    Computes position-wise probability of being base-paired, using windows, with hard binding constraint for a set of sequences.

    * Input:
    
    * Output:


* FoldWindows.py 

    Calculate base pairing probs of given seqs or random seqs for given window size, span and region
    
    * Input:
    
    * Output:


* risvis.py

    Visualize base pairing probabilties before and after constraining.
    
    * Input:
    
    * Output:
  

## ConstraintPLFold

### Using Genes

ConstraintPLFold.py can be used for folding a list of sequences with constraints.
Therefore it is recommended to use one fasta file containing sequences and another
bed file containing the constraints. Matching between sequences and constraints is
done via the gene identifier (here **ENSG00000270742**) which has to be the same in the bed file and the fasta
and should look as follows:

#### Fasta
```
>ENSG00000270742:chr1:61124732-61125202(+)
TTTTTTCTTTATAATTATTCCCCTATTTGAAAAATCAACTTGTATATGAGGCAGCAAACACCTTGCAGAGC...
```
#### Bed
```
chr1	26	35	ENSG00000270742 .	+
```

The command line call for this simple scenario is supposed to look like this:

```shell
python ConstraintPLFold.py -s FASTA -x BedFile
```

by default the results are printed to stdout. The first output is the
folded sequence without constraints. This output can be redirected to a file
using `--unconstraint nameforunconstraint`. The following outputs are the matrices for
an unpaired constraint and for an paired constraint. These matrices can also be 
redirected to an file using `--paired nameforpaired` or `--unpaired nameforunpaired`.
The folder to which these files should be saved is determined via the `--outdir` flag.

Constraints can also be passed using the `ono` (one on one) flag like this:
```shell
python ConstraintPLFold.py -s FASTA -x ono,BedFile
```
Matching between constraints and sequences consequently ignores the gene identifiers
and instead the first sequence will use the first line in the bed file as a constraint.

If you want to construct bed files with genomic coordinates, containing information about
pairing probabilities (see [CollectConsResults](#CollectConsResults)), it is essential to
provide another bed file with genomic coordinates.
This file can be passed using the `--genes GeneBedFile` and should look like: 

##### GeneBed
```
chr1  61124732  61125202  ENSG00000270742 .	+
```

### Using Transcripts

If you plan to use transcripts, missing exons, instead of genes it is highly recommended 
changing the header of your fasta sequences as well as the constraints in the bed file as follows:

##### Fasta
```
>ENST00000240304.5::ENST00000240304.5:0-5482(.)
GUCUUGUCGGCUCCUGUGUGUAGGAGGGAUUUCGGCCUGAGAGCGGGCCGAGGAGAUUGGCGACGGUGUCGCCCGUGUUUUCGUUGGCGGGUGCCUGGGCUGGUGGGAACAGCCGCCCGAAGGAAGCACCAUGAUUUCGGCCGCGCAGUUGUUGGAUGAGUUAAUGGGCCGGGACCGAAACCUAGCCCCGGACGAGAAGCGCAGCAACGUGCGGUGGGACCACGAGAGCGUUUGUAAAUAUUAUCUCUGUGGUUUUUGUCCUGCGGAAUUGUUCACAAAUACACGUUCUGAUCUUGGUCCGUGUGAAAAAAUUCAUGAUGAAAAUCUACGAAAACAGUAUGAGAAGAGCUCUCGUUUCAUGAAAGUUGGCUAUGAGAGAGAUUUUUUGCGAUACUUACAGAGCUUACUUGCAGAAGUAGAACGUAGGAUCAGACGAGGCCAUGCUCGUUUGGCAUUAUCUCAAAACCAGCAGUCUUCUGGGGCCGCUGGCCCAACAGGCAAAAAUGAAGAAAAAAUUCAGGUUCUAACAGACAAAAUUGAUGUACUUCUGCAACAGAUUGAAGAAUUAGGGUCUGAAGGAAAAGUAGAAGAAGCCCAGGGGAUGAUGAAAUUAGUUGAGCAAUUAAAAGAAGAGAGAGAACUGCUAAGGUCCACAACGUCGACAAUUGAAAGCUUUGCUGCACAAGAAAAACAAAUGGAAGUUUGUGAAGUAUGUGGAGCCUUUUUAAUAGUAGGAGAUGCCCAGUCCCGGGUAGAUGACCAUUUGAUGGGAAAACAACACAUGGGCUAUGCCAAAAUUAAAGCUACUGUAGAAGAAUUAAAAGAAAAGUUAAGGAAAAGAACCGAAGAACCUGAUCGUGAUGAGCGUCUAAAAAAGGAGAAGCAAGAAAGAGAAGAAAGAGAAAAAGAACGGGAGAGAGAAAGGGAAGAAAGAGAAAGGAAAAGACGAAGGGAAGAGGAAGAAAGAGAAAAAGAAAGGGCUCGUGACAGAGAAAGAAGAAAGAGAAGUCGUUCACGAAGUAGACACUCAAGCCGAACAUCAGACAGAAGAUGCAGCAGGUCUCGGGACCACAAAAGGUCACGAAGUAGAGAAAGAAGGCGGAGCAGAAGUAGAGAUCGACGAAGAAGCAGAAGCCAUGAUCGAUCAGAAAGAAAACACAGAUCUCGAAGUCGGGAUCGAAGAAGAUCAAAAAGCCGGGAUCGAAAGUCAUAUAAGCACAGGAGCAAAAGUCGGGACAGAGAACAAGAUAGAAAAUCCAAGGAGAAAGAAAAGAGGGGAUCUGAUGAUAAAAAAAGUAGUGUGAAGUCCGGUAGUCGAGAAAAGCAGAGUGAAGACACAAACACUGAAUCGAAGGAAAGUGAUACUAAGAAUGAGGUCAAUGGGACCAGUGAAGACAUUAAAUCUGAAGGUGACACUCAGUCCAAUUAAAACUGAUCUGAUAAGACCUCAGAUCAGACAGAGGACUACUGUUCGAAGAUUUUUGGAAGAAUACUGAGAACGGCAUAAAGUGAAGAUCGACAUUUAAAAAAUGAGGUGAAAGAAAGCUAUAGUGGCAUAGAAAAAGUAUAAAGCUCAGUUAGUUUUUUUAUUAUUAUUAUUAUUAAAAGUUAAUUCAGGACUGAUGUGACCUACCAGAUUUCAGAACAUGUGUUAAUAGUAUAUAUGCCACUGAAAACUUAGGUCCUGUAUCAUACUUUUUUCUUUAAGACUUUUUAAGAAAUAUUACUUAAACAUGUGGCUUGCUCAGUGUUUAAUUGCAAGUUUUCAAUCUUGGACUUUGAAAACAGGAUUAAACGUUAGUAUUCGUGUGAAUCAGACUAAGUGGGAUUUCAUUUUUACAACUCUGCUCUACUUAGCCUUUGGAUUUAGAAGUAAAAAUAAAGUAUCUCUGACUUUCUGUUACAAAGUUGAUUGUCUCUGUCAUUGAAAAGUUUUAGUAUUAAUCUUUUUCUAAUAAAGUUAUUGACUCUGAACUAGUCCCCUGUUUUAAAUACAAGAGUUACACUAUUACUAGAGGUGUUGGUGUACAGUUUUAUCUGAUUUGUUCUGUUUAAGACUAAUUUUUAUAGACUUUCUAAUGUUUUAAAUAAUGGUGCUUCAAUUUUAGGUGGUUAUGAAUAAAUUUGAAUUUUGCUUUUAAUAGCAAAGAUGUGCAGUGAACUAGAAUAUAUUUUUACAUCCCUGAGAGAUUCAUUUAGUAGAAAAUUCCAAGUAUCCUGACAAGCACUCUUUAGCUGGCUAGCUAUGGGAUGAUGUAGAAAAGCAUUCAAGAGCUAGUUUUUGUUAAGUCCUGUAUCAAGAUUAACCCAGCUGUGUCAGUUUAUAAAUGUAUUUGUGUAUAGGGUGUGUAGUAUAUAUGGCAAGGGUUUUUUCCCCCCACUUAAGUGAUUAUUUUUGUGUCACAUCUAGGAAAACCGGCAGCAUGUUUCUAUCUAUAGCCAGCUUCUUCGACUGUAUAAAAGUAUUCUCUCCAGCUACGUAUAUACACACAUACAUAUAUAUCAUAGCAAUUCCUUGUGGUUUAUAACUUGCAAAUACUGCUAUCAGUUUAUAGGUAAAGAAACAGUGUGUUAAAUGACUUAUCCAGGGAGGGUCCUGUGGCUUCAUGUUUAUGGAGUUGCUAGGUCUCUGCCUCAUGGUCCAGUGCCUGUUAAGCCACUGUGUUCAUUCUAAUAGGCAUAAUGAAUUGUUAAAGAAUUUACUAAAAUCUCUUCCACCAAACUUUGAAAAAUAAUGAAGCCGCCCCCACUUUAGAGGCUCUGUAUGAAAAAAUGCUGUGGAGACAGAGCCCUCCUGGCUCCCUAGCUGAUCCUGGAGAUGCAGCAAUAGAUGAAUGGGUUAUCUCUGAAUUUGUAAGAGAUAAUUCACAUGAGGAUUAAGAUAAAAUGGGAAGUAAAAUCUAACAAACACAAAGAUAGCUCCCAGGCACUGCUUUGUGUAGUUUGACAGCAUUGUGGUUGUAGCAGCAAAGGACUUAAAGUGAUAGUUUUUAAACCAUAUUCUGUCCCUAAGUAAUAAAAAAUCUAGGAAGUUACUAAAAUACCAGAUUUGUUCUGCUCUGCCUCAUCUAGAAUCAACGUCUAACUAACUUAAAUGAAGUAUAAUAAAUGAGUUCAUAUGAAAAGGCUUCCUCUAUGGACACUUAGAUAUAUUGUAACUAUUGAAGUUACCUGGGAUGUGGGGGUGGUGGGAGGAGGACCUGCCUCCCCAGGACAUCUAUGACUAAGGCCUGGCUUUAGUUAUGGAGAGAGACGUAGAAGUUGAAUUUUACACCCAAAAUUGAUGUGACUGAAGAGGAACUGAUUGUUGCUAACCAGCUCACAAGAAUCCAGUAUUGAGACCAGUUCACUAGAAGAAACAAACAUUUCUGCCAUGCAGACCAAAAAGUUAUUAGUUGGUGAAUAUGUAUUUUCUCUUUGGAAGGUCUUUAAGGGGAGCAAACCAGUUUUAAUCAAUCAGAUUGCUUGGUAAGUUUGGAAUCUGCAAUCAGUUGGUCUUAAAAAAAAAAAAACUUUAUUUUGGAAAUUUAAAGACAUACACAAAAGAGGAACAAUAUAAUUAACCUCUGUUAACUCAUCACCAACAAGACUCAUGACCACUUUUAUACUUCAUGAGUGAUUGUAUUUGUAUCCACUGUUUUCUAUUAUUUUCGAGCAAGUCUCAGACACACCAUUUAAUCUGUAAAUAAUUCAGCAUGUAUCUCUAAAAGACAAAGACCUCUUAAAUAACAGUUCAUUAGUAUAAAACAAAUUGGGUAAACUUUUGUUGGUCAUCAAACUAUAUUAGCACUGGUCCAAUAGUUUAAUUUUCAUUGAGCCUUUCAAGAGGACCGACCAGUCUGCUGCUCAAGACAUCCUCUCCUCUGGAAUGUAGAGAUAAUACAUAUCAUGCUCCUUUUUGUUAAAACGUUUUUUUUUCCCCUUCAAACACAGUCCAUUCAUUUUUCAGUUUGGGUUGAAACAUCCUUUUCUUGAUCUUGAGCUUAUAAUAACCUAGUCAUAUUGCUCAGCUCAGAUAUUUUUACUCCCUCUCCUUAGGCAUUCUGGUUCCUUAAAUAUAGUUAGUGUCACAGAGGAUAAAUAACCAACCUUAUUUCUAAGGUCUGAGAACACUUGGACCACAUAUUGGUUGAGCUCAGCCACCUUCUGAUUAAAGUUUUCAGACUUGUAAGAACUGAAAAUUUUUAUGGUGGAAGUUCUCUGAGCCCUCAUCCAUUCUGUUUUUAAAAAUGCAUUGCAGAUGGGCUAUGUGAAUAUGUUUUUAAACAUCUGAUAUGUGCAUGAAACAAAAAACACUUGAAGUUAUUAUGUAUACAAUUCUGUGGGAUGGGACUUCAUGCAGGAUUGGUUUUCAAGUUUGAUUUCCUGAGGGAUUUUUUAGUUGUUUGUGAAAGAACCCCAGGUCUACUUUUGAAAUUUUGUAUUAUAAUUGUAAUGUUGCCCAUGGUUAAAAAAAAAAAGUGUUCAGUGAUCUAUGUCUCCUACUACUCCUAUUUCUCUGUUUUUCCUCUGCAGGAGCUUGCUGCUGUUAACAGUUAUUCUUCCAAGUUGUUUUCUUUGUGGGGAGAUGGGAGGUGGGAGGAAAUAUAAACAUAUAUGUAUAGAUCUUUCAAAAUAUAUGACGGUAUACCCGUAUGUUCUGAGUCUUGCUGUUUUUACCUGGUAAUAUUUAGAAACAUUUAUUUUGAGAUAAAGGAGAGCACUUUUAAGUUGAACCUGUAGUUUUAAAAAGUACAUUUCAAGUAAGCCAAAGCAGAGAAGUAAAUGUAUUUUUCAUUGUUGUAUCAGAAUUUUGAAUUUACUAUUUUAAAAAUUCAAGAGUUUUGUAGCUGAUCUAUUUCUUCCCCUCAGCCAUCCCAAAUAGGUCAUUUGUCAACAGAUUUAAGAAUGUUUAGAAACAACAACUUUGGGAAACGGGAAACAAUUUGGUAUAAGUGGGUGUGCCAUAACCUCUCUCGUAGCCAUUCAUUCCCGGAUACAUACCCUAGAGAAACUCUUACACAUGCGUACCAGGGGAUGGAUUUAAGCAUUUGUGUGUAAUAGGAAGAAAAGAAGAAAAAACCCGGGAAGAUCCCAAGUGUCCACCAACAGUGUGUUGGAUAAAUACUGUGGUAUAUUCCAACAGUGGAAUUCCACAGAAGUGAAACUGAACUGCAGCUGUGUAUGUGAACAUGGACAAAACUCAACAAUAGAAGGAUCAAAAAAAGCAAGUCACAGAAGAAUACAUCACUAUGGUUCCAUUUCAAUGAAAGUCAAAAACAGGCUGUCAAAUACAUGAUAAAAGGAAACGAUUAAGACAAAAUUUAAUGUUAGCCGUUUUGAUGGAGGGAGAGGUGAUCAUGAGGGCACAGGGGUCUUCAGAAGAACUGGUGAGGGUCUGUUUCUGAAGCCUGUGGGCAUUUCCUUUUUUAAUCUGUAUGUUUAUGUGCUUUUGUAUGUAUGAUAUUUCUUAAUAAAAUUUAAAAAGAAGAAUGGGAAAAAA
```
##### Bed
```
ENST00000240304.5	1178	1183	ENST00000240304.5	.	.
```
In this case you should use GeneBed files (`--genes`) which look quite similar to 
the Constraints File but have as start position 0 and end position the length of 
the sequence

##### GeneBed
```
ENST00000240304.5	0	5482	ENST00000240304.5	.	.
```

## CollectConsResults 

The methods mentioned in [ConstraintPLFold example](#ConstraintPLFold) will 
produce output that can be processed by CollectConsResults. This will generate BED
files storing the probability of being unpaired for overlapping spans of nucleotides around the 
constraint. <REWRITE> Therefore simply call:

```
python CollectConsResults.py -d path/to/ConstraintPLFold/output -u 5 -g GeneBed --outdir path/to/outdir --unconstraint name  
```

Hereby it is essential that `--unconstraint` matches the uconstraint name provided at the ConstraintPLFold call.   
Further the `-u` parameter defines the span sizes that are used for the output BED files which might
for example look like this for `-u 5`:

```
chr1	110135760	110135765	ENSG00000065135|44542-44544|110135774-110135777	0.02620831	+	9	0.05007846	0.07628677	2.2444807817789587	0.02620831000000001	0.04615814895706037	0.15227569
chr1	110135761	110135766	ENSG00000065135|44542-44544|110135774-110135777	0.019514269999999993	+	8	0.049938	0.06945227	2.426255722126518	0.019514269999999993	-0.03666320494171017	0.15227569
chr1	110135762	110135767	ENSG00000065135|44542-44544|110135774-110135777	0.09578122	+	7	0.13804191	0.23382313	1.4457214540425338	0.09578122	0.9069421599395611	0.15227569
chr1	110135763	110135768	ENSG00000065135|44542-44544|110135774-110135777	0.07929997	+	6	0.06154513	0.1408451	1.5621026141257632	0.07929996999999998	0.7030295094408919	0.15227569
chr1	110135778	110135783	ENSG00000065135|44542-44544|110135774-110135777	0.31023007	+	-7	0.14063798	0.45086805	0.7213795423617754	0.31023007	3.560189541047878	0.15227569
chr1	110135779	110135784	ENSG00000065135|44542-44544|110135774-110135777	0.2991335	+	-8	0.1657577	0.4648912	0.7438289320089759	0.2991335	3.4228983161623856	0.15227569
chr1	110135780	110135785	ENSG00000065135|44542-44544|110135774-110135777	0.29541885	+	-9	0.15833754	0.45375639	0.7515304743397738	0.29541885	3.376939173064934	0.15227569
```

A detailed description of that files columns can be found in the [Output](#output) section.

## Further steps

The BED file created by CollectConsResults can be used to intersect with other known binding sites on the 
same gene/transcript. Thus, it is possible to see whether the changes in RNA structure upon binding of one ligand might
affect the structure of binding site of other ligands. 














