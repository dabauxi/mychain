# mychain

A PoW blockchain implementation as a prototype in python.

Based on a flask application with the endpoints:

*  `/mine`: mine a new block
* `/submit_transaction`: submit a tx
* `chain`: get chain information
* `/nodes/register`: register a node
* `/nodes/resolve`: consensus based on the longest chain rule

### How to run:

`python -m flask run`