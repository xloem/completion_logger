import ar, ar.utils
import bundlr

import json
import threading
import urllib

from .logger import Logger

class Arweave(Logger):
    wallet = None # assigned at end of file
    bundlr_url = bundlr.node.DEFAULT_API_URL # usually provides free upload for <100KB dataitems
    gateway = ar.PUBLIC_GATEWAYS[0]
    
    bundlr_node = bundlr.Node(bundlr_url)
    peer = ar.Peer(gateway)
    current_block = peer.current_block()

    @classmethod
    def _log_completion(cls, input: list, output: str, metadata: dict):
        # wrap the data in a convenient folder.
        # making the input and output their own entries lets them get longer without triggering a fee
        entries = {
            'input': cls.__ditem(input),
            'output': cls.__ditem(output, 'text/plain'),
            'metadata': cls.__ditem(metadata),
        }
        tags = { k: v for k,v in metadata.items() if type(v) is str }
    
        # upload it
        ditemid = cls.__manifest(entries, tags)
    
        # return the url to the folder on the gateway
        # include information in the url on finding the data
        urlpart = (f'{ditemid}' +
                   f'#minblockheight={current_block["height"]}' +
                   f'&minblockhash={current_block["indep_hash"]}')
        return urllib.parse.urljoin(gateway, urlpart)
    
    @classmethod 
    def __ditem(cls, data, content_type = None, **tags):
        # convert data into a signed dataitem object
        if content_type is not None:
            tags['Content-Type'] = content_type
        if type(data) in (dict, list):
            data = json.dumps(data)
            tags.setdefault('Content-Type', 'application/json')
        data = ar.DataItem(data = data.encode())
        data.header.tags = [ar.utils.create_tag(k, v, True) for k, v in tags.items()]
        data.sign(wallet.rsa)
        return data
    
    @classmethod 
    def __manifest(cls, ditems, tags):
        # add index.html
        ditems['index.html'] = cls.__ditem('\n'.join([
            f'<p><a href="{name}">{name}</a></p>'
            for name in ditems
        ]), 'text/html')
    
        # add directory manifest
        ditems['manifest'] = cls.__ditem(dict(
            manifest = 'arweave/paths',
            version = '0.1.0',
            index = dict(
                path = 'index.html',
            ),
            paths = {
                name: dict(id = ditem.header.id)
                for name, ditem in ditems.items()
            }
        ), 'application/x.arweave-manifest+json', **tags)
    
        # store data
        threads = [threading.Thread(target=cls.__send, args=(ditem,)) for ditem in ditems.values()]
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]
    
        # return id of manifest as locator
        return ditems['manifest'].header.id
    
    @classmethod 
    def __send(cls, ditem):
        # send a dataitem to the bundlr node
        result = bundlr_node.send_tx(ditem.tobytes())
        assert result['id'] == ditem.header.id

DEFAULT_WALLET_JWK = {
        'alg': 'RS256',
        'kty': 'RSA',
        'n': '4FtI5e6UCJcT1f58HKGihz988DzoO2n3lyk1NzX86wRpDAiwQGEWDI_mZXK9sHA4o6n8f80yzKXOaSX0tx6hybw1NgrlrUoaQ-3DwDtoCERG12gNttN4w9EU-LJL092tqVAyPvGhjj_I_L1-_IqpBMoOS2d600si-TDWDolJKi93VBmDCsRVLgmGeLPe7cjIDrrDLNesbP2HE3Zhdup4UWv7HP_8tvctOwCDUtf6n4QJBmx8_tmhXWO-4Y2Tuu-6Ujg9aTNTNiaFqIPzh0FzMhryA9V6-DjDjJa-A1KMnInjoV0KD-e-SBOwIxulQi7InaAIyyKNZ8iytkqk69VTQlHMAaTC2IgwcFFvm-Uag2dgM9Y_2RmUgbxWmqMpglB33atrHfixCY3iXsLRjYcC6zPXPEWvrCdRW6xxWojS7vH8YWhkmzzaMBsfORvO0pRlB0CvC0qYON_I3wiEW2YAAmq9GAXPV3SL1ZiebPwG1BKUa3NHdW9U-Dm4W1VLqp3IiCumZAqp7CWDZTRbm7XmTqAHb2HAbkdzFZ9Bee09N1VqBvxRESCETVx1W7SMUgPE2uKiinWNRqIiCzUJfqA5Rl9pnqLpNr21F7IDNpVF-P4X3u0UfZpaJjzB6Ma7zLmN1f-DBl0L1B1QTC97vbZNCAm9ayAZf3dx4mOMfZOFEBc',
        'e': 'AQAB',
        'd': 'B0W45DMf5fNiYje14DELv_nlMTMC4sIkPhMeNXmbhtFax61pwSckfChsncc4B4XBCupnU-ExOgRPNNtVG7EeKhg0BVoZvcyUHgrmoyQ0fWgb1RRQtXy_V7bpnhzGwR8DZ7nrbFzlZrislCde_A1RPeWAIcjrPflxMHCjz6QllKd7OmT6pBkJxcyV6PMI-94xQJZPM0npEz4DPd9Czi760sYpmp61m1ysa6gwRDmErIeuyeAvC7e-4km_FeKX8kxJAYHvLlTKkrZxngJrnMEYsdFrx4deTWN8UIymVhyROusWpNQLj8kW7ZEtzsWGTXyPZi9EzwjXWpDdMh7TSmMHfXmfqP3ciZa2XQNM5IU1O-7oz3xV4J07z6uaNVGfcnSIxE70KvAc48q3IZeT05w9_6e3iaO-BtJRhmX8FChop51FAYe4dJ4hMSdoUYF8dyEeDz_u5aF7ZtPa-x6ugFKnCsPL4vM3t-dAISnS2KgzOZyhh_L3fZUHB_NSEX7EkOoaFaGzFrFCtSoX4F8LufJIMG3dQEJQcucikm_BGGBOEl8F3PDC87nis56qt0co25st6eFD1yl2evygtxDnAqcZMzM3-8cOdxqr07rwjQE1mK_HRIfVQ46OAaC3LWo2laKdGYSSRTzyJQXqcbzk9QwIlnERkClrVW1MsVosrdJTDZE',
        'p': '5cKCv-c7eXjPYFO6vcDOg9bmeCfrB5Wh-CD8-XQdp7I5_Xhy4zGfDtnhknnqrvt1SsUiMyyZcq6Cl85fi_ksraSxxLCjFYYma57Xu6HPmCnejuTDddDeMoRUJ-YsRx_X_PON-I0MU0BBylFvYiQV4yy0gWf9mLFWONltt71pnz0IpT1vFod-SQftOHUGk3jbz0BGwhfy4j4tJROZ5aBMmLe19JPH3GnPzLcZnRQlZQwM3n6idcxXS26JBjDVsUH_oAWBWbwS42Pw1OR7XiMrItlzubpoPp_jvatvg6Uc2kAvDVjsUSnJjk_a1yCBpidBfnNDNyNO1zfk-Ur88joiHw',
        'q': '-frMwoeQnXH3v5dhzewwB_X0A1jZkgt1bZ5jKAeSDZIUq3CxZZ3LrG8Vv1XYlRLXRntNiSwy64vTJ4oEnBre6rrjfbRUjZ9m2L0ghoqIRxWOZ4oP3p3IG45WNzqQMRGQZf8JDhowlPBsUy4faw_0yvbZT1_ncnaGcefJpLLOZANbE8KHFpeDGD_hreE9rz7Ob4ar_XLo8ovEFaa6tEmk_dK82aNHKBgPQH0R3PdhCWO3-1Yv5--jUzPEL_Y88eA5KPl3BQUIFEoxvNSBPVR3U46PTQE4xPvqMoISa9xWyu3fTZ2cpsU-VGsiaVg6njsWpK0bDtJq4ClxHn4UF3yDCQ',
        'dp': 'p9q1-QsuuSzYnDAvgoeEmG78yxWmsFDSFtvK1VfOfoBHu3UuweqzoH7vPDrTiGjvJOPme2p-5Hi3sb40sacly-pBcUf2rTfng8J1K4AokKsuDEj2v3ELk-53KPsQqBmMiyFIPCiXs46DQhLCg_mHAAPeD5hwfgg4zKmUbaL0skA9u7KpINV2HlarKQ7d8gle1QfJae1jJYR1KNwsF8VHkF7OkNMSNWYcSRwPm2FnfG4UTMxJVjQmJlanxp0Q0UI9RaQf_vXW-sc939rYgkrBLeGdmTelBvN6x0ui2ZNcA9rWRTMM2rLjrJOMdpQqA8A0KfR9S6AA7lzIbJQrPa_Y0w',
        'dq': 'bT0TA6M4KAVorXnazKD88E2jv16xXSfSvf9r908vnOyMScrqSqylF4pHp6A9EA_2sR8q59m_ur0Unf-rOghoB4154jHOjUDuMaKcNw8MtHuQCmEDxFWQ37HYrTPTVQ4G2vuTGm2Jc1yJCeRq6F9FqvgqSIxxWMzAvb_7lxRoKr5oq37jh5TYPd2UomZ-jTlV_tiMCiqP74XyPz_n8OcJyb2wty6p5rR03cqJ5tTXu8Gu4Y9tSd6nsbE6d3cUdOJ2OBij0Ta8rBksGQeIHqPtrT7sEkuJYlNvqXi70hSsfOtsHL_Wd-5T6ZITrJNYslLB916KJ3T-LU0O2LNh1k2b-Q',
        'qi': 'khIRVObEMDDJkfKfzojUpbSxRMNIRXKM8KoxOkykw_z5EdkeF5jSa8BBcEPGmyXPdFBganJVmtyX_D1yp9BwM4QkWImuwvUo1sJwfAPD_s2B6nk7sR0XAQp14jd5syIZHtt5rgW-yTxOg7uE611kjpS1xcuScdbzvfcCLEZiSiR6MIZgw6ifS4bmiDK5I4n95VMdgtPOMStrRK3s-INSrTYd3ty7KM1aiLGF1KvktyY-1YyoZS2rfctj0RaqWzPoQfZur3Yrla01uNOwOiVgPhTWGNxEFlw90Pumzsi373VeP1GcpCGykMYLsHbGAsbhI9N2svuTaScOybfZq3Sblg',
        'p2s': ''
}
wallet = ar.Wallet.from_data(DEFAULT_WALLET_JWK)
