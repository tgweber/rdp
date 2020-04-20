# RDP 

Interface for Research Data Products

# Quick Start

```bash
virtualenv -p `which python3` venv
source venv/bin/activate
make
make test
```

# Design

## Research Data Product (RDP)

A research data product is a composite built out of these elements:
* a persistent identifier
* a service bundle
* a bundle of metadata (potentially same information in different formats)
* a bundle of data

### Persistent IDentifier (PID)
A Perstistent IDentifier (PID) is one of the following items:
* An DOI
* A Handle
* An URL

### Service Bundles
A service is a combination of a protocol and an endpoint.
A service can provide access to metadata and data of one or several research data products.
Services have a timestamp indicating their creation.
A service bundle is a set of services with a selection function;
the selection functions allows to pick a service for a given task or returns None if
no appropriate service is part of the RDP.

### Metadatum
A metadatum is a combination of potentially nested key-value-pairs and a schema to validate against.
Metadata have a timestamp indicating their creation.

### Data
Data are any digital information representations which are input for or output of those activities of researchers that are necessary to verify or refute scientific knowledge.
Data have a timestamp indicating their creation.
