"""Incomplete outline of mapping iNaturalist fields to DwC terms"""
from datetime import datetime
from typing import Dict, List

import xmltodict
from pyinaturalist import get_observations, get_taxa_by_id

# Fields from observation JSON
OBSERVATION_FIELDS = {
    'id': 'dwc:catalogNumber',
    'observed_on': 'dwc:eventDate',
    'quality_grade': 'dwc:datasetName',
    'time_observed_at': 'dwc:eventDate',
    # 'annotations': [], # not found
    'positional_accuracy': 'dwc:coordinateUncertaintyInMeters',
    'license_code': 'dcterms:license',  # not exactly but seems derived from,
    'public_positional_accuracy': 'dwc:coordinateUncertaintyInMeters',
    'created_at': 'xap:CreateDate',  # not matching but probably due to UTC
    'description': 'dcterms:description',
    'updated_at': 'dcterms:modified',
    'uri': 'dcterms:references',  # or 'dwc:occurrenceDetails',
    # 'location': [
    #     'dwc:decimalLongitude',
    #     'dwc:decimalLatitude',
    # ],  # can be derived from 'dwc:decimalLatitude' and 'dwc:decimalLongitude'
    'place_guess': 'dwc:verbatimLocality',
    # 'observed_on': 'dwc:verbatimEventDate',  # but with different standart: YYYY-MM-DD HH:MM:SS-UTC
}

# Fields from taxon JSON
TAXON_FIELDS = {
    'id': 'dwc:taxonID',
    'rank': 'dwc:taxonRank',
    'name': 'dwc:scientificName',
    'kingdom': 'dwc:kingdom',
    'phylum': 'dwc:phylum',
    'class': 'dwc:class',
    'order': 'dwc:order',
    'family': 'dwc:family',
    'genus': 'dwc:genus',
}

# Fields from items in observation['photos']
PHOTO_FIELDS = {
    'url': 'dcterms:identifier',  # or ac:accessURI, media:thumbnailURL, ac:furtherInformationURL, ac:derivedFrom, ac:derivedFrom # change the host to amazon
    'license_code': 'xap:UsageTerms',  # Will need to be translated to a link to creativecommons.org
    'id': 'dcterms:identifier',  # or ac:accessURI, media:thumbnailURL, ac:furtherInformationURL, ac:derivedFrom, ac:derivedFrom
    'attribution': 'dcterms:rights',
}

# Fields that will be constant for all iNaturalist observations
CONSTANTS = {
    'dwc:basisOfRecord': 'HumanObservation',
    'dwc:institutionCode': 'iNaturalist',
    # ...
}

CC_BASE_URL = 'http://creativecommons.org/licenses'
DATETIME_FIELDS = ['observed_on', 'created_at']
XML_NAMESPACES = {
    'xsi:schemaLocation': 'http://rs.tdwg.org/dwc/xsd/simpledarwincore/  http://rs.tdwg.org/dwc/xsd/tdwg_dwc_simple.xsd',
    'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xmlns:ac': 'http://rs.tdwg.org/ac/terms/',
    'xmlns:dcterms': 'http://purl.org/dc/terms/',
    'xmlns:dwc': 'http://rs.tdwg.org/dwc/terms/',
    'xmlns:dwr': 'http://rs.tdwg.org/dwc/xsd/simpledarwincore/',
    'xmlns:eol': 'http://www.eol.org/transfer/content/1.0',
    'xmlns:geo': 'http://www.w3.org/2003/01/geo/wgs84_pos#',
    'xmlns:media': 'http://eol.org/schema/media/',
    'xmlns:ref': 'http://eol.org/schema/reference/',
    'xmlns:xap': 'http://ns.adobe.com/xap/1.0/',
}


def observation_to_dwc(observation) -> str:
    """Translate a JSON-formatted observation record from API results to DwC format"""
    # Translate observation fields
    dwc_observation = {}
    for inat_field, dwc_field in OBSERVATION_FIELDS.items():
        dwc_observation[dwc_field] = observation[inat_field]

    # Translate taxon fields
    taxon = get_taxon_with_ancestors(observation)
    for inat_field, dwc_field in TAXON_FIELDS.items():
        dwc_observation[dwc_field] = taxon.get(inat_field)

    # Translate photo fields
    photo = observation['photos'][0]
    dwc_photo = {}
    for inat_field, dwc_field in PHOTO_FIELDS.items():
        dwc_photo[dwc_field] = photo[inat_field]
    dwc_observation['eol:dataObject'] = dwc_photo

    # Add constants
    for dwc_field, value in CONSTANTS.items():
        dwc_observation[dwc_field] = value

    # Add to a complete SimpleDarwinRecordSet + namespaces and convert to XML
    dwc_records = {'dwr:SimpleDarwinRecordSet': {f'@{k}': v for k, v in XML_NAMESPACES.items()}}
    dwc_records['dwr:SimpleDarwinRecordSet']['dwr:SimpleDarwinRecord'] = dwc_observation
    return xmltodict.unparse(dwc_records, pretty=True, indent='    ')


def get_taxon_with_ancestors(observation):
    """observation['taxon'] doesn't have full ancestry, so we'll need to get that from the
    /taxa endpoint
    """
    response = get_taxa_by_id(observation['taxon']['id'])
    taxon = response['results'][0]

    # Simplify ancestor records into genus=xxxx, family=xxxx, etc.
    for ancestor in taxon['ancestors']:
        taxon[ancestor['rank']] = ancestor['name']

    return taxon


# TODO
def format_datetime(dt: datetime) -> str:
    pass


def format_license(license_code: str) -> str:
    pass


def format_location(location: List[float]) -> Dict[str, float]:
    pass


def test_observation_to_dwc():
    """Get a test observation, convert it to DwC, and write it to a file"""
    response = get_observations(id=45524803)
    observation = response['results'][0]
    dwc_xml = observation_to_dwc(observation)
    with open('obs_45524803.dwc', 'w') as f:
        f.write(dwc_xml)


if __name__ == '__main__':
    test_observation_to_dwc()
