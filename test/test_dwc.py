from pyinaturalist import get_observations

from pyinaturalist_convert import to_dwc


def test_observation_to_dwc():
    """Get a test observation, and convert it to DwC"""
    response = get_observations(id=45524803)
    observation = response['results'][0]

    # Write to a file
    to_dwc(observation, 'test/sample_data/observations.dwc')

    # Get as a dict, and just test for a few basic terms
    dwc_record = to_dwc(observation)[0]
    print(dwc_record)

    assert dwc_record['dwc:catalogNumber'] == 45524803
    assert dwc_record['dwc:scientificName'] == 'Dirona picta'
    assert dwc_record['dwc:decimalLatitude'] == 32.8430971478
    assert dwc_record['dwc:decimalLongitude'] == -117.2815829044
