# GROBID

[![License](http://img.shields.io/:license-apache-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)
[![Build Status](https://travis-ci.org/kermitt2/grobid.svg?branch=master)](https://travis-ci.org/kermitt2/grobid)
[![Coverage Status](https://coveralls.io/repos/kermitt2/grobid/badge.svg)](https://coveralls.io/r/kermitt2/grobid)
[![Documentation Status](https://readthedocs.org/projects/grobid/badge/?version=latest)](https://readthedocs.org/projects/grobid/?badge=latest)
[![Docker Status](https://images.microbadger.com/badges/version/lfoppiano/grobid.svg)](https://hub.docker.com/r/lfoppiano/grobid/ "Latest Docker HUB image")
[![Docker Hub](https://img.shields.io/docker/pulls/lfoppiano/grobid.svg)](https://hub.docker.com/r/lfoppiano/grobid/ "Docker Pulls")
[![SWH](https://archive.softwareheritage.org/badge/origin/https://github.com/kermitt2/grobid/)](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/kermitt2/grobid)

## GROBID documentation

Visit the [GROBID documentation](http://grobid.readthedocs.org) for more detailed information.

## Purpose

GROBID (or Grobid, but not GroBid nor GroBiD) means GeneRation Of BIbliographic Data.

GROBID is a machine learning library for extracting, parsing and re-structuring raw documents such as PDF into structured XML/TEI encoded documents with a particular focus on technical and scientific publications. First developments started in 2008 as a hobby. In 2011 the tool has been made available in open source. Work on GROBID has been steady as a side project since the beginning and is expected to continue as such.

The following functionalities are available:

- __Header extraction and parsing__ from article in PDF format. The extraction here covers the usual bibliographical information (e.g. title, abstract, authors, affiliations, keywords, etc.).
- __References extraction and parsing__ from articles in PDF format, around .85 f-score against on an independent PubMed Central set of 1943 PDF containing 90,125 references. All the usual publication metadata are covered (including DOI).
- __Citation contexts recognition and linking__ to the full bibliographical references of the article. The accuracy of citation contexts resolution is around 0.75 f-score (which corresponds to both the correct identification of the citation callout and its correct association with a full bibliographical reference).
- Parsing of __references in isolation__ (around 0.89 f-score).
- __Parsing of names__ (e.g. person title, forenames, middlename, etc.), in particular author names in header, and author names in references (two distinct models).
- __Parsing of affiliation and address__ blocks.
- __Parsing of dates__, ISO normalized day, month, year.
- __Full text extraction and structuring__ from PDF articles, including a model for the overall document segmentation and models for the structuring of the text body (paragraph, section titles, reference callout, figure, table, etc.).
- __Consolidation/resolution of the extracted bibliographical references__ using the [biblio-glutton](https://github.com/kermitt2/biblio-glutton) service or the [CrossRef REST API](https://github.com/CrossRef/rest-api-doc). In both cases, DOI resolution performance is higher than 0.95 f-score from PDF extraction.
- __Extraction and parsing of patent and non-patent references in patent__ publications.
- __PDF coordinates__ for extracted information, allowing to create "augmented" interactive PDF.

In a complete PDF processing, GROBID manages 55 final labels used to build relatively fine-grained structures, from traditional publication metadata (title, author first/last/middlenames, affiliation types, detailed address, journal, volume, issue, pages, doi, pmid, etc.) to full text structures (section title, paragraph, reference markers, head/foot notes, figure headers, etc.).

GROBID includes a comprehensive web service API, batch processing, a JAVA API, a Docker image, a generic evaluation framework (precision, recall, etc., n-fold cross-evaluation) and the semi-automatic generation of training data.

GROBID can be considered as production ready. Deployments in production includes ResearchGate, HAL Research Archive, the European Patent Office, INIST-CNRS, Mendeley, CERN (Invenio), scite.ai, and many more. The tool is designed for high scalability in order to address the full scientific literature corpus.

GROBID should run properly "out of the box" on Linux (64 bits) and macOS. We cannot ensure currently support for Windows as we did before (help welcome!).

For more information on how the tool works, on its key features and [benchmarking](https://grobid.readthedocs.io/en/latest/Benchmarking/), visit the [GROBID documentation](http://grobid.readthedocs.org).

## Demo

For testing purposes, a public GROBID demo server is available at the following address: [http://grobid.science-miner.com](http://grobid.science-miner.com)

The Web services are documented [here](http://grobid.readthedocs.io/en/latest/Grobid-service/).

_Warning_: Some quota and query limitation apply to the demo server! Please be courteous and do not overload the demo server. 

## Clients

For helping to exploit GROBID service at scale, we provide clients written in Python, Java, node.js using the [web services](https://grobid.readthedocs.io/en/latest/Grobid-service/) for parallel batch processing:

- <a href="https://github.com/kermitt2/grobid-client-python" target="_blank">Python GROBID client</a>
- <a href="https://github.com/kermitt2/grobid-client-java" target="_blank">Java GROBID client</a>
- <a href="https://github.com/kermitt2/grobid-client-node" target="_blank">Node.js GROBID client</a>

All these clients will take advantage of the multi-threading for scaling large set of PDF processing. As a consequence, they will be much more efficient than the [batch command lines](https://grobid.readthedocs.io/en/latest/Grobid-batch/) (which use only one thread) and should be prefered. 

We have been able recently to run the complete fulltext processing at around 10.6 PDF per second (around 915,000 PDF per day, around 20M pages per day) with the node.js client listed above during one week on one 16 CPU machine (16 threads, 32GB RAM, no SDD, articles from mainstream publishers), see [here](https://github.com/kermitt2/grobid/issues/443#issuecomment-505208132) (11.3M PDF were processed in 6 days by 2 servers without crash).

In addition, a Java example project is available to illustrate how to use GROBID as a Java library: [https://github.com/kermitt2/grobid-example](https://github.com/kermitt2/grobid-example). The example project is using GROBID Java API for extracting header metadata and citations from a PDF and output the results in BibTeX format.  

Finally, the following python utilities can be used to create structured full text corpora of scientific articles simply by indicating a list of strong identifiers like DOI or PMID, performing the identification of online Open Access PDF, the harvesting, the metadata agreegation and the Grobid processing in one step at scale: [article-dataset-builder](https://github.com/kermitt2/article-dataset-builder)

## GROBID Modules

A series of additional modules have been developed for performing __structure aware__ text mining directly on scholar PDF, reusing GROBID's PDF processing and sequence labelling weaponery:

- [grobid-ner](https://github.com/kermitt2/grobid-ner): named entity recognition
- [grobid-quantities](https://github.com/kermitt2/grobid-quantities): recognition and normalization of physical quantities/measurements
- [software-mention](https://github.com/Impactstory/software-mentions): recognition of software mentions and attributes in scientific literature
- [grobid-astro](https://github.com/kermitt2/grobid-astro): recognition of astronomical entities in scientific papers
- [grobid-bio](https://github.com/kermitt2/grobid-bio): a bio-entity tagger using BioNLP/NLPBA 2004 dataset
- [grobid-dictionaries](https://github.com/MedKhem/grobid-dictionaries): structuring dictionaries in raw PDF format
- [grobid-superconductors](https://github.com/lfoppiano/grobid-superconductors): recognition of superconductor material and properties in scientific literature
- [entity-fishing](https://github.com/kermitt2/entity-fishing), a tool for extracting Wikidata entities from text and document, can also use Grobid to pre-process scientific articles in PDF, leading to more precise and relevant entity extraction and the capacity to annotate the PDF with interative layout. 

GROBID uses optionnally Deep Learning models relying on the [DeLFT](https://github.com/kermitt2/delft) library, a task-agnostic Deep Learning framework for sequence labelling and text classification. 

## Release and changes

See the [Changelog](CHANGELOG.md).

## License

GROBID is distributed under [Apache 2.0 license](http://www.apache.org/licenses/LICENSE-2.0). 

Main author and contact: Patrice Lopez (<patrice.lopez@science-miner.com>)

## Sponsors

ej-technologies provided us a free open-source license for its Java Profiler. Click the JProfiler logo below to learn more.

[![JProfiler](doc/img/jprofiler_medium.png)](http://www.ej-technologies.com/products/jprofiler/overview.html)

## How to cite

If you want to this work, please refer to the present GitHub project, together with the [Software Heritage](https://www.softwareheritage.org/) project-level permanent identifier. For example, with BibTeX:

```bibtex
@misc{GROBID,
    title = {GROBID},
    howpublished = {\url{https://github.com/kermitt2/grobid}},
    publisher = {GitHub},
    year = {2008--2020},
    archivePrefix = {swh},
    eprint = {1:dir:dab86b296e3c3216e2241968f0d63b68e8209d3c}
}
```

See the [GROBID documentation](http://grobid.readthedocs.org/en/latest/References) for more related resources. 

<!-- markdownlint-disable-file MD033 -->
