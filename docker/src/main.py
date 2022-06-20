import os
import CloudFlare
import requests
import logging

FORMAT = '%(asctime)s-%(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('DynDNS')

def get_myip():
    endpoint = 'https://ipinfo.io/json'
    try:
        response = requests.get(endpoint, verify = True)
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        quit()

    if response.status_code != 200:
        logging.error('Status: {} Problem with the request. Exiting.'.format(response.status_code))
        quit()

    data = response.json()

    return data['ip']


def main():
    myip = get_myip()
    logger.info('Current IP {}'.format(myip))

    cf = CloudFlare.CloudFlare(token=os.environ['API_KEY'])
    try:
        zones = cf.zones.get()
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        logger.error('Api call failed (GET /zones): {}'.format(e))
        quit()
    for zone in zones:
        zone_id = zone['id']
        zone_name = zone['name']
        logger.info('Viewing zone {}'.format(zone_name))

    # request the DNS records from that zone
    try:
        dns_records = cf.zones.dns_records.get(zone_id)
        for record in dns_records:
            logger.info('Records found {} {} in {}'.format(record['name'], record['type'], record['content']))
            if record['name'] == 'myzone.fr' and record['type'] == "A":
                apex_record = record
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        logger.error('Api call failed (GET /zones/dns_records): {}'.format(e))
        quit()

    # Update Apex record if any ip change detected
    if apex_record['content'] != myip:
        logger.warning('IP has change')
        logger.warning('The apex record is going to be update from {} to {}'.format(apex_record['content'], myip))
        dns_record = {'name':'myzone.fr', 'type':'A', 'proxied': True, 'content':myip}
        try:
            cf.zones.dns_records.put(zone_id, apex_record['id'], data=dns_record)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            logger.error('Api call failed (POST /zones/dns_records): {}'.format(e))
            exit(1)
        logger.warning('The apex record has been updated')
    else:
        logger.info('No change dectected')
    

if __name__ == '__main__':
    main()