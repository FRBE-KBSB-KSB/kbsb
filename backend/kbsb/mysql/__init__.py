from kbsb import settings
from sqlalchemy import create_engine, MetaData

# define a engine, 
# low pool_recycle setting: Infomaniak quickly closes the mysql connection
engine = create_engine(settings.MYSQL_URL, pool_recycle=20)

# import all table definitions via reflection
metadata = MetaData()
metadata.bind = engine
metadata.reflect()

def map_o2n(old: dict, mapping_o2n:dict) -> dict:
    """
    converts a dict with old (french) names to new names  
    using an  mapping_o2n dict
    """
    n = {}
    for k in mapping_o2n.keys():
        if k in old:
            mapping = mapping_o2n[k]
            if 'conversion' in mapping:
                n[mapping['name']] = mapping['conversion'](old[k])
            else:
                n[mapping['name']] = old[k]
    return n

from .mysql_base import DbBase